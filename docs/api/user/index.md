# 用户管理模块

## 概述

用户管理模块提供用户信息和用户组的管理功能，包括用户列表、用户组管理等。

## API 列表

### 获取用户列表

**请求信息：**

- 请求路径：`/api/v1/user/users/`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |
| username | string | 否 | 用户名搜索 |
| email | string | 否 | 邮箱搜索 |
| status | integer | 否 | 用户状态：0-禁用，1-启用 |
| group_id | integer | 否 | 用户组ID筛选 |

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": "integer",  // 总数
        "items": [           // 用户列表
            {
                "uuid": "integer",      // 用户ID
                "username": "string", // 用户名
                "email": "string",    // 邮箱
                "phone": "string",    // 手机号
                "status": "integer",  // 状态：0-禁用，1-启用
                "created_at": "string", // 创建时间
                "last_login": "string", // 最后登录时间
                "groups": [           // 用户组列表
                    {
                        "uuid": "integer",    // 用户组ID
                        "name": "string",   // 用户组名称
                        "code": "string"    // 用户组编码
                    }
                ]
            }
        ]
    }
}
```

### 获取单个用户

**请求信息：**

- 请求路径：`/api/v1/user/user/`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uuid | integer | 是 | 用户ID |

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "uuid": "integer",      // 用户ID
        "username": "string", // 用户名
        "email": "string",    // 邮箱
        "phone": "string",    // 手机号
        "status": "integer",  // 状态
        "created_at": "string", // 创建时间
        "last_login": "string", // 最后登录时间
        "groups": [           // 用户组列表
            {
                "uuid": "integer",    // 用户组ID
                "name": "string",   // 用户组名称
                "code": "string"    // 用户组编码
            }
        ]
    }
}
```

### 获取用户组列表

**请求信息：**

- 请求路径：`/api/v1/user/groups/`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20 |
| name | string | 否 | 用户组名称搜索 |

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": "integer",  // 总数
        "items": [           // 用户组列表
            {
                "uuid": "integer",      // 用户组ID
                "name": "string",     // 用户组名称
                "code": "string",     // 用户组编码
                "description": "string", // 用户组描述
                "created_at": "string",  // 创建时间
                "updated_at": "string",  // 更新时间
                "user_count": "integer"  // 用户数量
            }
        ]
    }
}
```

### 获取单个用户组

**请求信息：**

- 请求路径：`/api/v1/user/group/`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uuid | integer | 是 | 用户组ID |

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "uuid": "integer",      // 用户组ID
        "name": "string",     // 用户组名称
        "code": "string",     // 用户组编码
        "description": "string", // 用户组描述
        "created_at": "string",  // 创建时间
        "updated_at": "string",  // 更新时间
        "users": [            // 用户列表
            {
                "uuid": "integer",    // 用户ID
                "username": "string", // 用户名
                "email": "string",    // 邮箱
                "status": "integer"   // 状态
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
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 注意事项

1. 用户名不能重复
2. 邮箱不能重复
3. 手机号不能重复
4. 超级管理员用户不能被删除
5. 用户状态变更会立即生效
6. 用户组编码必须唯一
7. 用户可以被分配到多个用户组
8. 用户组可以包含多个用户 