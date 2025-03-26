# 权限管理模块

## 概述

权限管理模块提供系统角色和权限的管理功能，包括角色创建、权限分配、权限验证等。

## API 列表

### 获取权限列表

**请求信息：**

- 请求路径：`/api/v1/perm/permissions/`
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
        "total": "integer",  // 总数
        "items": [           // 权限列表
            {
                "uuid": "string",    // 权限ID
                "name": "string",   // 权限名称
                "code": "string",   // 权限编码
                "description": "string", // 权限描述
                "type": "string",   // 权限类型
                "parent_id": "integer" // 父权限ID
            }
        ]
    }
}
```

### 获取单个权限

**请求信息：**

- 请求路径：`/api/v1/perm/permission/`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uuid | integer | 是 | 权限ID |

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "uuid": "integer",    // 权限ID
        "name": "string",   // 权限名称
        "code": "string",   // 权限编码
        "description": "string", // 权限描述
        "type": "string",   // 权限类型
        "parent_id": "integer" // 父权限ID
    }
}
```

### 获取用户权限

**请求信息：**

- 请求路径：`/api/v1/perm/user-permission-json/`
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
        "permissions": [    // 权限列表
            "string"       // 权限编码
        ],
        "roles": [         // 角色列表
            "string"       // 角色编码
        ]
    }
}
```

### 获取角色列表

**请求信息：**

- 请求路径：`/api/v1/perm/roles/`
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
        "total": "integer",  // 总数
        "items": [           // 角色列表
            {
                "uuid": "integer",      // 角色ID
                "name": "string",     // 角色名称
                "code": "string",     // 角色编码
                "description": "string", // 角色描述
                "created_at": "string",  // 创建时间
                "updated_at": "string"   // 更新时间
            }
        ]
    }
}
```

### 获取单个角色

**请求信息：**

- 请求路径：`/api/v1/perm/role/`
- 请求方法：`GET`
- 请求头：
  ```http
  Authorization: Bearer your-token
  ```

**查询参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uuid | integer | 是 | 角色ID |

**响应结果：**

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "uuid": "integer",      // 角色ID
        "name": "string",     // 角色名称
        "code": "string",     // 角色编码
        "description": "string", // 角色描述
        "permissions": [         // 权限列表
            {
                "uuid": "integer",    // 权限ID
                "name": "string",   // 权限名称
                "code": "string"    // 权限编码
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

1. 角色编码必须唯一
2. 系统预设角色（如超级管理员）不能被删除
3. 权限编码必须唯一
4. 权限支持树形结构，通过 parent_id 关联
5. 用户可以被分配多个角色
6. 角色可以被分配多个权限
7. 用户权限接口会返回当前用户的所有权限和角色 