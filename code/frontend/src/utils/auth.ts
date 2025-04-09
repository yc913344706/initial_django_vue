import Cookies from "js-cookie";
import { useUserStoreHook } from "@/store/modules/user";
import { storageLocal, isString, isIncludeAllChildren } from "@pureadmin/utils";
import logger from "@/utils/logger";

export interface DataInfo<T> {
  /** token */
  accessToken: string;
  /** `accessToken`的过期时间（时间戳） */
  accessTokenExpires: T;
  /** 用于调用刷新accessToken的接口时所需的token */
  refreshToken: string;
  /** refreshToken的过期时间（时间戳） */
  refreshTokenExpires: T;
  /** 头像 */
  avatar?: string;
  /** 用户名 */
  username?: string;
  /** 昵称 */
  nickname?: string;
  /** 当前登录用户的角色 */
  roles?: Array<string>;
  /** 当前登录用户的按钮级别权限 */
  permissions?: Array<string>;
}

export const userKey = "user-info";
/**
 * 通过`multiple-tabs`是否在`cookie`中，判断用户是否已经登录系统，
 * 从而支持多标签页打开已经登录的系统后无需再登录。
 * 浏览器完全关闭后`multiple-tabs`将自动从`cookie`中销毁，
 * 再次打开浏览器需要重新登录系统
 * */
export const multipleTabsKey = "multiple-tabs";


/**
 * @description 设置`token`以及一些必要信息并采用无感刷新`token`方案
 * 无感刷新：后端返回`accessToken`（访问接口使用的`token`）、`refreshToken`（用于调用刷新`accessToken`的接口时所需的`token`，`refreshToken`的过期时间（比如30天）应大于`accessToken`的过期时间（比如2小时））、`expires`（`accessToken`的过期时间）
 * 将`accessToken`、`expires`、`refreshToken`这三条信息放在key值为authorized-token的cookie里（过期自动销毁）
 * 将`avatar`、`username`、`nickname`、`roles`、`permissions`、`refreshToken`、`expires`这七条信息放在key值为`user-info`的localStorage里（利用`multipleTabsKey`当浏览器完全关闭后自动销毁）
 */
export function setToken(data: DataInfo<Date>) {
  let expires = 0;
  const { accessToken, accessTokenExpires, refreshToken, refreshTokenExpires } = data;
  const { isRemembered, loginDay } = useUserStoreHook();

  // const _accessTokenExpires = new Date(accessTokenExpires).getTime();
  // const _refreshTokenExpires = new Date(refreshTokenExpires).getTime();

  // Cookies.set(import.meta.env.VITE_ACCESS_TOKEN_NAME, accessToken, {
  //   expires: (_accessTokenExpires - Date.now()) / 86400000
  // })
  // Cookies.set(import.meta.env.VITE_REFRESH_TOKEN_NAME, refreshToken, {
  //   expires: (_refreshTokenExpires - Date.now()) / 86400000
  // })

  Cookies.set(
    multipleTabsKey,
    "true",
    isRemembered
      ? {
          expires: loginDay
        }
      : {}
  );

  function setUserKey({ avatar, username, nickname, permissions }) {
    useUserStoreHook().SET_AVATAR(avatar);
    useUserStoreHook().SET_USERNAME(username);
    useUserStoreHook().SET_NICKNAME(nickname);
    useUserStoreHook().SET_PERMS(permissions);
    storageLocal().setItem(userKey, {
      refreshToken,
      expires,
      avatar,
      username,
      nickname,
      permissions
    });
  }

  if (data.username) {
    const { username } = data;
    setUserKey({
      avatar: data?.avatar ?? "",
      username,
      nickname: data?.nickname ?? "",
      permissions: data?.permissions ?? []
    });
  } else {
    const avatar =
      storageLocal().getItem<DataInfo<number>>(userKey)?.avatar ?? "";
    const username =
      storageLocal().getItem<DataInfo<number>>(userKey)?.username ?? "";
    const nickname =
      storageLocal().getItem<DataInfo<number>>(userKey)?.nickname ?? "";
    const permissions =
      storageLocal().getItem<DataInfo<number>>(userKey)?.permissions ?? [];
    setUserKey({
      avatar,
      username,
      nickname,
      permissions
    });
  }
}

/** 删除`token`以及key值为`user-info`的localStorage信息 */
export function removeToken() {
  logger.debug('removeToken')
  if (import.meta.env.VITE_COOKIE_DOMAIN) {
    Cookies.remove(import.meta.env.VITE_ACCESS_TOKEN_NAME, { domain: import.meta.env.VITE_COOKIE_DOMAIN, path: '/' });
    Cookies.remove(import.meta.env.VITE_REFRESH_TOKEN_NAME, { domain: import.meta.env.VITE_COOKIE_DOMAIN, path: '/' });
    Cookies.remove(import.meta.env.VITE_COOKIE_USERNAME_NAME, { domain: import.meta.env.VITE_COOKIE_DOMAIN, path: '/' });
  } else {
    Cookies.remove(import.meta.env.VITE_ACCESS_TOKEN_NAME);
    Cookies.remove(import.meta.env.VITE_REFRESH_TOKEN_NAME);
    Cookies.remove(import.meta.env.VITE_COOKIE_USERNAME_NAME);
  }
  Cookies.remove(multipleTabsKey);
  logger.debug('after remove token. accessToken', Cookies.get(import.meta.env.VITE_ACCESS_TOKEN_NAME))
  logger.debug('after remove token. refreshToken', Cookies.get(import.meta.env.VITE_REFRESH_TOKEN_NAME))
  logger.debug('after remove token. cookieUsername', Cookies.get(import.meta.env.VITE_COOKIE_USERNAME_NAME))

  storageLocal().removeItem(userKey);
}

/** 格式化token（jwt格式） */
export const formatToken = (token: string): string => {
  return "Bearer " + token;
};

/** 是否有按钮级别的权限（根据登录接口返回的`permissions`字段进行判断）*/
export const hasPerms = (value: string | Array<string>): boolean => {
  if (!value) return false;
  const { permissions } = useUserStoreHook();
  if (!permissions) return false;
  const isAuths = isString(value)
    ? permissions.includes(value)
    : isIncludeAllChildren(value, permissions);
  return isAuths ? true : false;
};
