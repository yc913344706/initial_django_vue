export const apiMap = {
  // 登录
  login: "/auth/login/",
  // 刷新token
  refreshToken: "/auth/refresh-token/",
  // 登出
  logout: "/auth/logout/",
  
  // 获取异步路由
  getAsyncRoutes: "/auth/get-async-routes/",

  // 用户管理
  user: {
    userList: "/user/users/",
    user: "/user/user/",
  },

  // 用户组管理
  group: {
    groupList: '/user/groups/',
    group: '/user/group/',
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
    userPermissionJson: "/perm/user-permission-json/",
  },

  // 审计管理
  audit: {
    auditLogs: "/audit/audit-logs/",
  },
}
