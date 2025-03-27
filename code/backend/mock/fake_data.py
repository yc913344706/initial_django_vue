fake_user_data_list = [
    {
        "avatar": "https://avatars.githubusercontent.com/u/44761321",
        "username": "admin",
        "nickname": "小铭",
        "password": "admin@123",
        "email": "admin@example.com",
        "phone": "12345678901", 
        # "role": "admin",
        "status": "active",
        "created_time": "2021-01-01",
        "updated_time": "2025-03-23",
    }
]


fake_user_login_data_list = [
    {
        # "avatar": "https://avatars.githubusercontent.com/u/44761321",
        # "username": "admin",
        # "nickname": "小铭",

        # 一个用户可能有多个角色
        # "roles": ["admin"],
        # 按钮级别权限
        # "permissions": ["*:*:*"],
        
        # "accessToken": "eyJhbGciOiJIUzUxMiJ9.admin",
        # "refreshToken": "eyJhbGciOiJIUzUxMiJ9.adminRefresh",
        # "expires": "2024/10/30 00:00:00"
    },
    {
        "avatar": "https://avatars.githubusercontent.com/u/52823142",
        "username": "common",
        "nickname": "小林",
        "roles": ["common"],
        "permissions": ["permission:btn:add", "permission:btn:edit"],
        "accessToken": "eyJhbGciOiJIUzUxMiJ9.common",
        "refreshToken": "eyJhbGciOiJIUzUxMiJ9.commonRefresh",
        "expires": "2030/10/30 00:00:00"
    },
]

fake_refresh_token_data = {
    "accessToken": "eyJhbGciOiJIUzUxMiJ9.newAdmin",
    "refreshToken": "eyJhbGciOiJIUzUxMiJ9.newAdminRefresh",
    # `expires`选择这种日期格式是为了方便调试，后端直接设置时间戳或许更方便（每次都应该递增）。如果后端返回的是时间戳格式，前端开发请来到这个目录`src/utils/auth.ts`，把第`38`行的代码换成expires = data.expires即可。
    "expires": "2030/10/30 23:59:59"
}

# 模拟后端动态生成路由
# roles：页面级别权限，这里模拟二种 "admin"、"common"
# admin：管理员角色
# common：普通角色
fake_async_routes = [
    {
        "path": "/system",
        "meta": {
            "title": "系统管理",
            "icon": "ep:setting",
            "rank": 1
        },
        "children": [
            {
                "path": "/system/user/index",
                "name": "UserIndex",
                "meta": {
                    "title": "用户管理",
                    "roles": ["admin", "common"]
                }
            },
            {
                "path": "/system/perm/index",
                "name": "PermIndex",
                "meta": {
                    "title": "权限管理",
                    "roles": ["admin", "common"]
                }
            },
            {
                "path": "/system/role/index",
                "name": "RoleIndex",
                "meta": {
                    "title": "角色管理",
                    "roles": ["admin", "common"]
                }
            },
            {
                "path": "/system/grant/index",
                "name": "GrantIndex",
                "meta": {
                    "title": "授权管理",
                    "roles": ["admin", "common"]
                }
            }
        ]
    },
    {
        "path": "/permission",
        "meta": {
            "title": "权限管理",
            "icon": "ep:lollipop",
            "rank": 10
        },
        "children": [
            {
            "path": "/permission/page/index",
            "name": "PermissionPage",
            "meta": {
                "title": "页面权限",
                "roles": ["admin", "common"]
            }
            },
            {
            "path": "/permission/button",
            "meta": {
                "title": "按钮权限",
                "roles": ["admin", "common"]
            },
            "children": [
                {
                "path": "/permission/button/router",
                "component": "permission/button/index",
                "name": "PermissionButtonRouter",
                "meta": {
                    "title": "路由返回按钮权限",
                    "auths": [
                    "permission:btn:add",
                    "permission:btn:edit",
                    "permission:btn:delete"
                    ]
                }
                },
                {
                "path": "/permission/button/login",
                "component": "permission/button/perms",
                "name": "PermissionButtonLogin",
                "meta": {
                    "title": "登录接口返回按钮权限"
                }
                }
            ]
            }
        ]
    }
]