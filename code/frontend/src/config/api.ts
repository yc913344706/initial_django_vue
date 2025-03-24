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
    roleList: "/perm/roles/",
    role: "/perm/role/",
  },

  // 权限管理
  permission: {
    permissionList: "/perm/permissions/",
    permission: "/perm/permission/",
  },

  // 用户组管理
  group: {
    groupList: '/perm/groups/',
    group: '/perm/group/',
  },

  // 授权管理
  grant: {
    grantList: "/perm/grants/",
    grant: "/perm/grant/",
  },
}
