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
import { getToken, formatToken } from "@/utils/auth";
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
    return new Promise(resolve => {
      PureHttp.requests.push((token: string) => {
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
        logger.debug('config: ', config)
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
        return whiteList.some(url => config.url.endsWith(url))
          ? config
          : new Promise(resolve => {
              logger.debug('获取token...')
              const data = getToken();
              if (data) {
                logger.debug('token存在...')
                const now = new Date().getTime();
                const expired = parseInt(data.expires) - now <= 0;
                if (expired) {
                  logger.debug('token过期...')
                  if (!PureHttp.isRefreshing) {
                    logger.debug('刷新token...')
                    PureHttp.isRefreshing = true;
                    // token过期刷新
                    useUserStoreHook()
                      .handRefreshToken({ refreshToken: data.refreshToken })
                      .then(res => {
                        logger.debug('刷新token成功...')
                        const token = res.data.accessToken;
                        config.headers["Authorization"] = formatToken(token);
                        PureHttp.requests.forEach(cb => cb(token));
                        PureHttp.requests = [];
                      })
                      .catch(error => {
                        logger.debug('刷新token失败...')
                        return Promise.reject(error);
                      })
                      .finally(() => {
                        logger.debug('刷新token完成...')
                        PureHttp.isRefreshing = false;
                      });
                  }
                  resolve(PureHttp.retryOriginalRequest(config));
                } else {
                  logger.debug('token未过期...')
                  config.headers["Authorization"] = formatToken(
                    data.accessToken
                  );
                  resolve(config);
                }
              } else {
                logger.debug('token不存在...')
                resolve(config);
              }
            });
      },
      error => {
        logger.debug('请求拦截器错误...')
        return Promise.reject(error);
      }
    );
  }

  /** 响应拦截 */
  private httpInterceptorsResponse(): void {
    // logger.debug('enter httpInterceptorsResponse...')
    const instance = PureHttp.axiosInstance;
    instance.interceptors.response.use(
      (response: PureHttpResponse) => {
        // logger.debug('enter PureHttpResponse...')
        // logger.debug('response: ', response)

        const responseSuccess = response.data.success
        if (!responseSuccess) {
          // 关闭进度条动画
          NProgress.done();
          return Promise.reject(response.data)
        }

        const $config = response.config;
        // 关闭进度条动画
        NProgress.done();
        // 优先判断post/get等方法是否传入回调，否则执行初始化设置等回调
        if (typeof $config.beforeResponseCallback === "function") {
          $config.beforeResponseCallback(response);
          return response.data;
        }
        if (PureHttp.initConfig.beforeResponseCallback) {
          PureHttp.initConfig.beforeResponseCallback(response);
          return response.data;
        }
        return response.data;
      },
      (error: PureHttpError) => {
        const $error = error;
        $error.isCancelRequest = Axios.isCancel($error);
        // 关闭进度条动画
        NProgress.done();
        // 所有的响应异常 区分来源为取消请求/非取消请求
        return Promise.reject($error);
      }
    );
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
