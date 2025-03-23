export const apiMap = {
  // 登录
  login: "/auth/login",
  // 刷新token
  refreshToken: "/auth/refresh-token",
  
  // 获取异步路由
  getAsyncRoutes: "/auth/get-async-routes",

  // 用户管理
  user: {
    userList: "/user/users/",
    user: "/user/user/",
  },

  // 角色管理
  role: {
    roleList: "/role/roles/",
    role: "/role/role/",
  },

  // 权限管理
  permission: {
    permissionList: "/permission/permissions/",
    permission: "/permission/permission/",
  },

  // 授权管理
  grant: {
    grantList: "/grant/grants/",
    grant: "/grant/grant/",
  },
}
