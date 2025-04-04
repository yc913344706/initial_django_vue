// import "@/utils/sso";
import Cookies from "js-cookie";
import { getConfig } from "@/config";
import NProgress from "@/utils/progress";
import { buildHierarchyTree } from "@/utils/tree";
import remainingRouter from "./modules/remaining";
import { useMultiTagsStoreHook } from "@/store/modules/multiTags";
import { usePermissionStoreHook } from "@/store/modules/permission";
import { isUrl, openLink, storageLocal, isAllEmpty } from "@pureadmin/utils";
import {
  ascending,
  getTopMenu,
  initRouter,
  isOneOfArray,
  getHistoryMode,
  findRouteByPath,
  handleAliveRoute,
  formatTwoStageRoutes,
  formatFlatteningRoutes
} from "./utils";
import {
  type Router,
  createRouter,
  type RouteRecordRaw,
  type RouteComponent
} from "vue-router";
import {
  type DataInfo,
  userKey,
  removeToken,
  multipleTabsKey,
  setToken
} from "@/utils/auth";
import { apiMap } from "@/config/api";
import logger from '@/utils/logger'
import { useUserStoreHook } from "@/store/modules/user";

/** 自动导入全部静态路由，无需再手动引入！匹配 src/router/modules 目录（任何嵌套级别）中具有 .ts 扩展名的所有文件，除了 remaining.ts 文件
 * 如何匹配所有文件请看：https://github.com/mrmlnc/fast-glob#basic-syntax
 * 如何排除文件请看：https://cn.vitejs.dev/guide/features.html#negative-patterns
 */
const modules: Record<string, any> = import.meta.glob(
  ["./modules/**/*.ts", "!./modules/**/remaining.ts"],
  {
    eager: true
  }
);

/** 原始静态路由（未做任何处理） */
const routes = [];

Object.keys(modules).forEach(key => {
  routes.push(modules[key].default);
});

/** 导出处理后的静态路由（三级及以上的路由全部拍成二级） */
export const constantRoutes: Array<RouteRecordRaw> = formatTwoStageRoutes(
  formatFlatteningRoutes(buildHierarchyTree(ascending(routes.flat(Infinity))))
);

/** 用于渲染菜单，保持原始层级 */
export const constantMenus: Array<RouteComponent> = ascending(
  routes.flat(Infinity)
).concat(...remainingRouter);

/** 不参与菜单的路由 */
export const remainingPaths = Object.keys(remainingRouter).map(v => {
  return remainingRouter[v].path;
});

/** 创建路由实例 */
export const router: Router = createRouter({
  history: getHistoryMode(import.meta.env.VITE_ROUTER_HISTORY),
  routes: constantRoutes.concat(...(remainingRouter as any)),
  strict: true,
  scrollBehavior(to, from, savedPosition) {
    return new Promise(resolve => {
      if (savedPosition) {
        return savedPosition;
      } else {
        if (from.meta.saveSrollTop) {
          const top: number =
            document.documentElement.scrollTop || document.body.scrollTop;
          resolve({ left: 0, top });
        }
      }
    });
  }
});

/** 重置路由 */
export function resetRouter() {
  router.getRoutes().forEach(route => {
    const { name, meta } = route;
    if (name && router.hasRoute(name) && meta?.backstage) {
      router.removeRoute(name);
      router.options.routes = formatTwoStageRoutes(
        formatFlatteningRoutes(
          buildHierarchyTree(ascending(routes.flat(Infinity)))
        )
      );
    }
  });
  usePermissionStoreHook().clearAllCachePage();
}

/** 路由白名单 */
const whiteList = [apiMap.login];

const { VITE_HIDE_HOME } = import.meta.env;

async function refres_access_token() {
  
  
  return res;
}

router.beforeEach(async (to: ToRouteType, _from, next) => {
  logger.debug('进入路由拦截器...')
    // 处理页面缓存
  if (to.meta?.keepAlive) {
    logger.debug('处理页面缓存...')
    handleAliveRoute(to, "add");
    if (_from.name === undefined || _from.name === "Redirect") {
      handleAliveRoute(to);
    }
  }

  // 设置页面标题
  const externalLink = isUrl(to?.name as string);
  if (!externalLink) {
    logger.debug('处理外部链接...')
    to.matched.some(item => {
      if (!item.meta.title) return "";
      const Title = getConfig().Title;
      if (Title) document.title = `${item.meta.title} | ${Title}`;
      else document.title = item.meta.title as string;
    });
  }

  // 开始进度条
  logger.debug('开始进度条...')
  NProgress.start();

  // 获取用户信息
  const userInfo = storageLocal().getItem<DataInfo<number>>(userKey);
  const accessToken = Cookies.get(import.meta.env.VITE_ACCESS_TOKEN_NAME);

  // 处理外部链接
  if (externalLink) {
    logger.debug('处理外部链接，跳过token检查')
    openLink(to?.name as string);
    NProgress.done();
    return;
  }

  // 处理白名单路由
  if (whiteList.includes(to.fullPath)) {
    logger.debug('白名单路由，跳过token检查')
    next();
    return;
  }

  // 未登录处理
  if (!accessToken) {
    logger.debug('未登录，尝试刷新token...')

    const refreshToken = Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME);
    if (!refreshToken) {
      logger.debug('未找到refresh_token，跳转到登录页...')
      next({ path: apiMap.login });
      return;
    }

    try {
      const res = await useUserStoreHook().handRefreshToken({ 
        refreshToken: refreshToken 
      });

      if (res?.data) {
        logger.debug('!accessToken 刷新token成功...')
        setToken(res.data);
        // 重新初始化路由
        await initRouter();
        // 重新导航到目标路由
        next({ ...to, replace: true });
      } else {
        logger.debug('刷新token失败...')
        next({ path: apiMap.login });
      }
    } catch (error) {
      logger.error('刷新token出错:', error);
      next({ path: apiMap.login });
    }
    return;
  }

  try {
    logger.debug('检查是否需要初始化路由...')
    // 检查是否需要初始化路由
    if (usePermissionStoreHook().wholeMenus.length === 0) {
      try {
        logger.debug('初始化路由...')
        await initRouter();
      } catch (error) {
        logger.debug('初始化路由失败...' + error)
        // 如果是token过期错误，尝试刷新token
        if (error.code === 99998) {
          logger.debug('尝试刷新token...')

          const refreshToken = Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME);
          if (!refreshToken) {
            logger.debug('未找到refresh_token，跳转到登录页...')
            next({ path: apiMap.login });
            return;
          }
      
          const res = await useUserStoreHook().handRefreshToken({ 
            refreshToken: refreshToken 
          });
          
          if (res?.data) {
            logger.debug('初始化路由，刷新token成功...')
            setToken(res.data);
            // 重新初始化路由
            await initRouter();
          } else {
            logger.debug('刷新token失败...')
            throw new Error('Failed to refresh token');
          }
        } else {
          logger.debug('初始化路由失败...' + error)
          throw error;
        }
      }
    }

    // 权限检查
    if (to.meta?.roles) {
      const hasPermission = isOneOfArray(to.meta.roles, userInfo?.roles ?? []);
      if (!hasPermission) {
        next({ path: "/error/403" });
        return;
      }
    }

    // 处理首页隐藏
    if (VITE_HIDE_HOME === "true" && to.fullPath === "/welcome") {
      next({ path: "/error/404" });
      return;
    }

    // 检查路由是否存在
    if (!router.hasRoute(to.name as string) && !to.matched.length) {
      logger.warn(`路由不存在: ${to.fullPath}`);
      next({ path: "/error/404" });
      return;
    }

    // 正常导航
    logger.debug('正常导航...')
    next();
  } catch (error) {
    logger.error('路由导航错误:', error);
    
    // 处理token相关错误
    if (error.code === 99998 || error.code === 401) {
      logger.debug('处理token相关错误...')
      useUserStoreHook().logOut();
      next({ 
        path: apiMap.login,
        query: { redirect: to.fullPath }
      });
      return;
    }

    // 其他错误处理
    next({ path: "/error/500" });
  } finally {
    NProgress.done();
  }
});

router.afterEach(() => {
  NProgress.done();
});

export default router;
