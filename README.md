## 是什么

- 最小化全栈开发基础框架，支持 RBAC 权限管理系统。包括前端、后端、nginx、mysql、redis。
- 技术栈： `Python 3.13`、`Django 5.2`、`Vue 3.5`。
- 环境要求：`Docker Engine 18.06.0`、`Docker Compose 3.7+` 。

## 如何使用

### 启动

> 注意：
>
> - 最好在服务器使用。
> - 个人电脑使用，配置不高的情况下，前端打包时，电脑负载会很高。

```bash
docker-compose -f docker-compose.dev.yaml up -d
```

### 访问

http://localhost:8080/

### 内置用户

| 角色 | 账号 | 密码 |
| ---- | ---- | ---- |
| 管理员 | admin | Admin@123 |

### 更多命令

```bash
docker-compose -f docker-compose.dev.yaml up db_mysql -d
docker-compose -f docker-compose.dev.yaml up backend -d
docker-compose -f docker-compose.dev.yaml up frontend -d

docker-compose -f docker-compose.dev.yaml down
rm -rf ./data/
```

## 一些配置

### 环境变量配置

| 作用 | 文件 |
| ---- | ---- |
| 【前端】vue工程配置 | `code/frontend/.env.development` |
| 【前端】Pure Admin配置 | `code/frontend/public/platform-config.json` |
| 【后端】业务配置 | `code/backend/.dev.yaml` |
| 【后端】全量路由定义文件 | `code/backend/base_routes.json` |
| 【后端】docker环境变量 | `code/backend/.dev.env` |

### 前端图标

- 图标：`code/frontend/public/favicon.ico`
- logo：`code/frontend/public/logo.png`
- user-avatar：`code/frontend/src/assets/user.jpg`
