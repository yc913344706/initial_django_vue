# 项目代码架构说明

## 项目概述

这是一个最小化全栈开发基础框架，支持 RBAC 权限管理系统。包括前端、后端、nginx、mysql、redis。

- **技术栈**：Python 3.13、Django 5.2（没有使用 Django RestFramework）、Vue 3.5
- **环境要求**：Docker Engine 18.06.0、Docker Compose 3.7+

## 目录结构

```
ops_arch_dashboard/
├── .gitignore
├── docker-compose.dev.yaml          # Docker Compose 开发配置
├── LICENSE
├── README.md
├── code/                           # 源代码目录
│   ├── backend/                    # 后端代码
│   └── frontend/                   # 前端代码
├── data/                           # 数据目录
├── etc/                            # 配置文件目录
├── lib/                            # 库文件目录
├── logs/                           # 日志目录
└── tools/                          # 工具目录
```

## 前端架构 (Vue 3.5)

### 位置
- 代码路径：`code/frontend/`

### 配置文件
- 【前端】vue工程配置：`code/frontend/.env.development`
- 【前端】Pure Admin配置：`code/frontend/public/platform-config.json`
- 【前端】图标：`code/frontend/public/favicon.ico`
- 【前端】logo：`code/frontend/public/logo.png`
- 【前端】用户头像：`code/frontend/src/assets/user.jpg`

## 后端架构 (Django 5.2)

### 位置
- 代码路径：`code/backend/`

### 配置文件
- 【后端】业务配置：`code/backend/.dev.yaml`
- 【后端】全量路由定义文件：`code/backend/config/base_routes.json`
- 【后端】docker环境变量：`code/backend/.dev.env`

## 环境与部署

### Docker 配置
- Docker Compose 文件：`docker-compose.dev.yaml`
- 启动命令：`docker-compose -f docker-compose.dev.yaml up -d`
- 访问地址：http://localhost:8080/

### 内置用户
| 角色 | 账号 | 密码 |
| ---- | ---- | ---- |
| 管理员 | admin | Admin@123 |

## 关键功能
- RBAC 权限管理系统
- 全栈开发框架
- Docker 容器化部署
- 支持 MySQL、Redis 数据存储