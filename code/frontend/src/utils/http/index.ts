import Axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type CustomParamsSerializer
} from "axios";
import type {
  PureHttpError,
  RequestMethods,
  PureHttpResponse,
  PureHttpRequestConfig
} from "./types.d";
import { stringify } from "qs";
import NProgress from "../progress";
import { formatToken, setToken } from "@/utils/auth";
import Cookies from "js-cookie";
import { useUserStoreHook } from "@/store/modules/user";
import { apiMap } from "@/config/api";
import logger from "@/utils/logger";

// 相关配置请参考：www.axios-js.com/zh-cn/docs/#axios-request-config-1
const defaultConfig: AxiosRequestConfig = {
  // 请求超时时间
  timeout: 10000,
  headers: {
    Accept: "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest"
  },
  // 数组格式参数序列化（https://github.com/axios/axios/issues/5142）
  paramsSerializer: {
    serialize: stringify as unknown as CustomParamsSerializer
  }
};

class PureHttp {
  constructor() {
    this.httpInterceptorsRequest();
    this.httpInterceptorsResponse();
  }

  /** `token`过期后，暂存待执行的请求 */
  private static requests = [];

  /** 防止重复刷新`token` */
  private static isRefreshing = false;

  /** 初始化配置对象 */
  private static initConfig: PureHttpRequestConfig = {};

  /** 保存当前`Axios`实例对象 */
  private static axiosInstance: AxiosInstance = Axios.create(defaultConfig);

  /** 重连原始请求 */
  private static retryOriginalRequest(config: PureHttpRequestConfig) {
    logger.debug('准备重试请求:', {
      url: config.url,
      method: config.method
    })
    return new Promise(resolve => {
      PureHttp.requests.push((token: string) => {
        logger.debug('执行重试请求回调')
        config.headers["Authorization"] = formatToken(token);
        resolve(config);
      });
    });
  }

  /** 请求拦截 */
  private httpInterceptorsRequest(): void {
    PureHttp.axiosInstance.interceptors.request.use(
      async (config: PureHttpRequestConfig): Promise<any> => {
        logger.debug('进入请求拦截器...')
        logger.debug('请求配置:', {
          url: config.url,
          method: config.method,
          headers: config.headers
        })
        
        // 开启进度条动画
        NProgress.start();
        
        // 优先判断post/get等方法是否传入回调，否则执行初始化设置等回调
        if (typeof config.beforeRequestCallback === "function") {
          logger.debug('执行请求回调...')
          config.beforeRequestCallback(config);
          return config;
        }
        if (PureHttp.initConfig.beforeRequestCallback) {
          logger.debug('执行初始化请求回调...')
          PureHttp.initConfig.beforeRequestCallback(config);
          return config;
        }
        
        /** 请求白名单，放置一些不需要`token`的接口（通过设置请求白名单，防止`token`过期后再请求造成的死循环问题） */
        const whiteList = [apiMap.refreshToken, apiMap.login];
        if (whiteList.some(url => config.url.endsWith(url))) {
          logger.debug('白名单请求，跳过token检查')
          return config;
        }

        return new Promise(resolve => {
          logger.debug('获取token...')
          const accessToken = Cookies.get(import.meta.env.VITE_ACCESS_TOKEN_NAME);
          const refreshToken = Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME);
          if (accessToken) {
            logger.debug('token未过期，直接使用')
            config.headers["Authorization"] = formatToken(
              accessToken
            );
            resolve(config);
          } else {
            logger.debug('token已过期，开始刷新流程...')
            if (!PureHttp.isRefreshing) {
              logger.debug('开始刷新token...')
              PureHttp.isRefreshing = true;
              // token过期刷新
              useUserStoreHook()
                .handRefreshToken({ refreshToken: refreshToken })
                .then(res => {
                  logger.debug('刷新token成功')
                  const token = res.data.accessToken;
                  config.headers["Authorization"] = formatToken(token);
                  logger.debug('更新请求头中的token')
                  PureHttp.requests.forEach(cb => {
                    logger.debug('执行队列中的请求回调')
                    cb(token)
                  });
                  PureHttp.requests = [];
                })
                .catch(error => {
                  logger.error('刷新token失败:', error)
                })
                .finally(() => {
                  logger.debug('刷新token流程结束')
                  PureHttp.isRefreshing = false;
                });
            } else {
              logger.debug('token正在刷新中，将请求加入队列')
            }
            resolve(PureHttp.retryOriginalRequest(config));
          }
        });
      },
      error => {
        logger.error('请求拦截器错误:', error)
        return Promise.reject(error);
      }
    );
  }

  /** 响应拦截 */
  private httpInterceptorsResponse(): void {
    const instance = PureHttp.axiosInstance;
    instance.interceptors.response.use(
      (response: PureHttpResponse) => {
        const $config = response.config;
        logger.debug('进入响应拦截器...')
        logger.debug('响应数据:', {
          url: $config.url,
          status: response.status,
          success: response.data.success,
          code: response.data.code
        })
        
        // 关闭进度条动画
        NProgress.done();

        // 处理业务错误
        if (!response.data.success) {
          logger.debug('业务处理失败:', response.data)
          // 处理token过期错误
          if (response.data.code === 99998) {
            logger.debug('检测到token过期错误(99998)')
            // 如果已经在刷新token，将请求加入队列
            if (PureHttp.isRefreshing) {
              logger.debug('token正在刷新中，将请求加入队列')
              return PureHttp.retryOriginalRequest($config).then(config => {
                logger.debug('队列中的请求开始重试')
                return instance.request(config);
              });
            }

            PureHttp.isRefreshing = true;
            const refreshToken = Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME);
            
            if (!refreshToken) {
              logger.error('未找到refreshToken，无法刷新')
              PureHttp.isRefreshing = false;
              useUserStoreHook().logOut();
              return Promise.reject(response.data);
            }

            logger.debug('开始刷新token...')
            return useUserStoreHook()
              .handRefreshToken({ refreshToken: refreshToken })
              .then(res => {
                logger.debug('刷新token响应:', {
                  success: res.success
                })
                if (res?.data) {
                  setToken(res.data);
                  logger.debug('设置新token成功')
                  // 重试所有失败的请求
                  PureHttp.requests.forEach(cb => {
                    logger.debug('执行队列中的请求回调')
                    cb(res.data.accessToken)
                  });
                  PureHttp.requests = [];
                  // 重试当前请求
                  logger.debug('重试当前请求')
                  // 直接使用新的 token 重试请求
                  $config.headers["Authorization"] = formatToken(res.data.accessToken);
                  return instance.request($config);
                }
                logger.error('刷新token响应数据异常')
                return Promise.reject(response.data);
              })
              .catch(error => {
                logger.error('刷新token失败:', error)
                // 刷新token失败，清除用户信息
                useUserStoreHook().logOut();
                return Promise.reject(response.data);
              })
              .finally(() => {
                logger.debug('刷新token流程结束')
                PureHttp.isRefreshing = false;
                // 如果队列中还有请求，执行它们
                if (PureHttp.requests.length > 0) {
                  logger.debug('队列中还有请求，开始执行')
                  const accessToken = Cookies.get(import.meta.env.VITE_ACCESS_TOKEN_NAME);
                  if (accessToken) {
                    PureHttp.requests.forEach(cb => {
                      logger.debug('执行队列中的请求回调')
                      cb(accessToken)
                    });
                    PureHttp.requests = [];
                  }
                }
              });
          }
          return Promise.reject(response.data);
        }

        // 优先判断post/get等方法是否传入回调，否则执行初始化设置等回调
        if (typeof $config.beforeResponseCallback === "function") {
          logger.debug('执行响应回调')
          $config.beforeResponseCallback(response);
          return response.data;
        }
        if (PureHttp.initConfig.beforeResponseCallback) {
          logger.debug('执行初始化响应回调')
          PureHttp.initConfig.beforeResponseCallback(response);
          return response.data;
        }
        return response.data;
      },
      (error: PureHttpError) => {
        const $error = error;
        $error.isCancelRequest = Axios.isCancel($error);
        logger.error('响应拦截器错误:', {
          isCancelRequest: $error.isCancelRequest,
          message: $error.message,
          response: $error.response?.data
        })
        // 关闭进度条动画
        NProgress.done();
        // 处理错误
        this.handleError($error);
        // 所有的响应异常 区分来源为取消请求/非取消请求
        return Promise.reject($error);
      }
    );
  }

  /** 统一错误处理 */
  private handleError(error: PureHttpError): void {
    // 处理取消请求的情况
    if (error.isCancelRequest) {
      return;
    }

    // 处理网络错误
    if (!error.response) {
      // 网络错误，可能是服务器未启动或网络连接问题
      console.error('Network error:', error.message);
      return;
    }

    const status = error.response.status;
    const data = error.response.data as any; // 添加类型断言

    // 处理401错误（未授权）
    if (status === 401) {
      // 只有在token确实无效时才清除
      if (data?.detail === 'Token is invalid or expired') {
        useUserStoreHook().logOut();
      }
      return;
    }

    // 处理403错误（禁止访问）
    if (status === 403) {
      console.error('Access forbidden:', data);
      return;
    }

    // 处理404错误（未找到）
    if (status === 404) {
      console.error('Resource not found:', data);
      return;
    }

    // 处理500错误（服务器错误）
    if (status === 500) {
      console.error('Server error:', data);
      return;
    }

    // 处理其他错误
    console.error('Request failed:', error.message);
  }

  /** 通用请求工具函数 */
  public request<T>(
    method: RequestMethods,
    url: string,
    param?: AxiosRequestConfig,
    axiosConfig?: PureHttpRequestConfig
  ): Promise<T> {
    const config = {
      method,
      url,
      ...param,
      ...axiosConfig
    } as PureHttpRequestConfig;

    // 单独处理自定义请求/响应回调
    return new Promise((resolve, reject) => {
      PureHttp.axiosInstance
        .request(config)
        .then((response: undefined) => {
          resolve(response);
        })
        .catch(error => {
          reject(error);
        });
    });
  }

  /** 单独抽离的`post`工具函数 */
  public post<T, P>(
    url: string,
    params?: AxiosRequestConfig<P>,
    config?: PureHttpRequestConfig
  ): Promise<T> {
    return this.request<T>("post", url, params, config);
  }

  /** 单独抽离的`get`工具函数 */
  public get<T, P>(
    url: string,
    params?: AxiosRequestConfig<P>,
    config?: PureHttpRequestConfig
  ): Promise<T> {
    return this.request<T>("get", url, params, config);
  }
}

export const http = new PureHttp();
