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
  type RouteComponent,
  createWebHistory,
  NavigationGuardNext,
  RouteLocationNormalizedLoaded
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
import { getBackendConfig } from '@/utils/backendConfig'
import { http } from '@/utils/http'
import {config} from '@/config'

type FromRouteType = RouteLocationNormalizedLoaded;

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
  // history: createWebHistory(),
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

// 确保静态路由已注册
const staticRoutes = router.getRoutes();
logger.debug('已注册的静态路由:', staticRoutes.map(route => route.path));

/** 重置路由 */
export function resetRouter() {
  logDebug('重置路由...')
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
const routeWhiteList = [apiMap.login];
const routeWhiteMouleList = [];

const { VITE_HIDE_HOME } = import.meta.env;

// 添加日志辅助函数
const logDebug = (message: string) => {
  logger.debug(message);
};

// 处理页面标题
const handlePageTitle = (to: ToRouteType) => {
  const externalLink = isUrl(to?.name as string);
  if (!externalLink) {
    logDebug('处理外部链接...')
    to.matched.some(item => {
      if (!item.meta.title) return "";
      const Title = getConfig().Title;
      if (Title) document.title = `${item.meta.title} | ${Title}`;
      else document.title = item.meta.title as string;
    });
  }
  return externalLink;
};

// 处理页面缓存
const handlePageCache = (to: ToRouteType, from: FromRouteType) => {
  if (to.meta?.keepAlive) {
    logDebug('处理页面缓存...')
    handleAliveRoute(to, "add");
    // 页面整体刷新和点击标签页刷新
    if (from.name === undefined || from.name === "Redirect") {
      handleAliveRoute(to);
    }
  }
};

/**
 * 根据 userInfo 判断是否需要跳转到登录页
 * 1. to.path === login 页面: true
 * 2. to.path in 路由白名单: true
 * 3. to.path === 其他页面，如果 userInfo 为空: false
 * 4. to.path === 其他页面，如果 userInfo 不为空: true
*/
const checkGoLoginByHasUserInfo = (to: ToRouteType, userInfo: DataInfo<number> | null) => {
  if (!userInfo) {
    logDebug('路由拦截器，未找到用户信息...' + JSON.stringify(to, null, 2))
    if (to.path !== apiMap.login) {
      logDebug('路由拦截器，to.path 不是login...')
      return true;
    } 

    logDebug('路由拦截器，to.path 是login...')
    return false;

  }

  logDebug('路由拦截器，找到用户信息...')
  return false;
};

/**
 * 检查 access_token 是否有效
 * 
 * 1. 有access_token: true
 * 2. 没有access_token，没有refresh_token: false
 * 3. 没有access_token，有refresh_token: 刷新并设置access_token
 * 
 * @returns boolean
 */
const canGetAccessToken = async () => {
  const accessToken = Cookies.get(import.meta.env.VITE_ACCESS_TOKEN_NAME);
  if (!accessToken) {
    logDebug('未找到access_token，尝试刷新token...')

    const refreshToken = Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME);
    if (!refreshToken) {
      logDebug('未找到refresh_token，跳转到登录页...')
      return false;
    }
    
    const res = await useUserStoreHook().handRefreshToken({ 
      refreshToken: refreshToken 
    });
    
    if (res?.data) {
      logDebug('beforeEach中，刷新token成功...')
      setToken(res.data);
      return true;
    }
  }
  return true;
};

// 处理路由初始化
const handleRouteInit = async (to: ToRouteType) => {
  try {
    const router = await initRouter() as Router;
    logDebug('beforeEach中，初始化路由完成...')
    if (!useMultiTagsStoreHook().getMultiTagsCache) {
      logDebug('beforeEach中，不存在多标签页缓存...')
      const { path } = to;
      const route = findRouteByPath(
        path,
        router.options.routes[0].children
      );
      logDebug('beforeEach中，findRouteByPath完成...' + JSON.stringify(route, null, 2))
      getTopMenu(true);
      // query、params模式路由传参数的标签页不在此处处理
      if (route && route.meta?.title) {
        logDebug('beforeEach中，route && route.meta?.title...')
        if (isAllEmpty(route.parentId) && route.meta?.backstage) {
          logDebug('beforeEach中，isAllEmpty(route.parentId) && route.meta?.backstage...')
          // 此处为动态顶级路由（目录）
          const { path, name, meta } = route.children[0];
          useMultiTagsStoreHook().handleTags("push", {
            path,
            name,
            meta
          });
        } else {
          logDebug('beforeEach中，route && route.meta?.title...')
          const { path, name, meta } = route;
          useMultiTagsStoreHook().handleTags("push", {
            path,
            name,
            meta
          });
        }
      }
    }
    // 确保动态路由完全加入路由列表并且不影响静态路由
    if (isAllEmpty(to.name)) {
      logDebug('beforeEach中，isAllEmpty(to.name)...')
      router.push(to.fullPath);
    }
  } catch (error) {
    logDebug('初始化路由失败...' + error)
  }
};

router.beforeEach(async (to: ToRouteType, _from, next) => {
  logDebug('进入路由拦截器...')
  
  // 处理页面缓存
  handlePageCache(to, _from);

  // 设置页面标题
  const externalLink = handlePageTitle(to);

  // 开始进度条
  logDebug('开始进度条...')
  NProgress.start();


  // 开启隐藏首页后在浏览器地址栏手动输入首页welcome路由则跳转到404页面
  if (VITE_HIDE_HOME === "true" && to.fullPath === "/welcome") {
    next({ path: "/error/404" });
    return;
  }

  // 白名单
  if (routeWhiteList.indexOf(to.path) !== -1) {
    logDebug('路由拦截器，to.path 在routeWhiteList中...')
    next();
    return;
  }

  // 白名单模块
  const to_path_module = to.path.split('/')[1];
  if (routeWhiteMouleList.indexOf(to_path_module) !== -1) {
    logDebug('路由拦截器，to.path 在routeWhiteMouleList中...')
    next();
    return;
  }
  
  // 获取用户信息
  const userInfo = storageLocal().getItem<DataInfo<number>>(userKey);

  // 处理认证和权限验证
  const needGoLogin = checkGoLoginByHasUserInfo(to, userInfo);
  if (needGoLogin) {
    removeToken();

    next({ path: apiMap.login });
    return;
  }

  if (_from?.name) {
    logDebug('beforeEach中，from存在name...')
    // name为超链接
    if (externalLink) {
      logDebug('beforeEach中，存在超链接...')
      openLink(to?.name as string);
      NProgress.done();
    } else {
      logDebug('beforeEach中，不存在超链接...')
      next();
    }
  } else {
    logDebug('beforeEach中，不存在name...')
    if (
      usePermissionStoreHook().wholeMenus.length === 0 &&
      to.path !== apiMap.login
    ) {
      logDebug('beforeEach中，usePermissionStoreHook().wholeMenus.length === 0 && to.path !== "' + apiMap.login + '"...')

      const _canGetAccessToken = await canGetAccessToken();
      if (!_canGetAccessToken) {
        next({ path: apiMap.login });
        return;
      }

      await handleRouteInit(to);
    }
    next();
    return;
  }

  next();
});

router.afterEach(() => {
  NProgress.done();
});

export default router;
