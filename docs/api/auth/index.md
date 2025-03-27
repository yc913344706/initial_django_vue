# 用户认证模块

## 概述

用户认证模块提供用户登录、令牌刷新、路由获取等基础认证功能。

## API 列表

### 用户登录

**请求信息：**

- 请求路径：`/api/v1/auth/login`
- 请求方法：`POST`
- 请求头：
  ```http
  Content-Type: application/json
  ```

**请求参数：**

```json
{
    "username": "string",  // 用户名
    "password": "string"   // 密码
}
```

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "token": "string",        // JWT token
        "user": {
            "uuid": "string",      // 用户ID
            "username": "string", // 用户名
            "email": "string",    // 邮箱
            "is_active": "boolean" // 是否激活
        }
    }
}
```

### 刷新令牌

**请求信息：**

- 请求路径：`/api/v1/auth/refresh-token`
- 请求方法：`POST`
- 请求头：
  ```http
  Content-Type: application/json
  Authorization: Bearer your-token
  ```

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "token": "string"  // 新的JWT token
    }
}
```

### 获取异步路由

**请求信息：**

- 请求路径：`/api/v1/auth/get-async-routes`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "routes": [  // 路由列表
            {
                "path": "string",      // 路由路径
                "name": "string",      // 路由名称
                "component": "string", // 组件路径
                "meta": {              // 路由元信息
                    "title": "string",  // 标题
                    "icon": "string",   // 图标
                    "roles": [          // 允许的角色
                        "string"
                    ]
                }
            }
        ]
    }
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或认证失败 |
| 403 | 无权限访问 |
| 404 | 用户不存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. 密码必须包含大小写字母和数字，长度至少8位
2. 用户名只能包含字母、数字和下划线
3. 邮箱必须是有效的邮箱格式
4. Token 有效期为 24 小时
5. 刷新令牌需要在原令牌过期前进行
6. 异步路由会根据用户角色动态生成 