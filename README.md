[English](./README.md) | [中文](./README_CN.md)

## Table of Contents

- [Table of Contents](#table-of-contents)
- [📖 Project Description](#-project-description)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
  - [Requirements](#requirements)
  - [Start](#start)
  - [Access](#access)
  - [Built-in User](#built-in-user)
  - [More Commands](#more-commands)
- [Some Configurations](#some-configurations)
  - [Environment Variable Configuration](#environment-variable-configuration)
  - [Frontend Icon Configuration](#frontend-icon-configuration)
  - [System Title Configuration](#system-title-configuration)
  - [i18n](#i18n)
- [Reference Documents:](#reference-documents)

## 📖 Project Description

- Minimal full-stack development framework with RBAC permission management system. Includes frontend, backend, nginx, mysql, redis.
- Technology stack: `Python 3.13`, `Django 5.2`, `Vue 3.5`.
- Code structure can be found [here](./docs/code_arch.md).

## ✨ Features

**User System**

- ✅ Local Users: Create, read, update, delete
- ✅ Local Users: Self-service password change, admin password reset
- ✅ Local Users: Password complexity configuration, login lock configuration
- ✅ Encrypted password storage (local user passwords cannot be reverse-engineered)
- ✅ LDAP user integration support (LDAP users are recorded but passwords are not stored or modified)

**Permission System**

- ✅ Basic RBAC: Manage permissions (JSON format), roles, user groups (inheritance supported)
- ✅ JSON format permissions, can refer to existing system default permissions for new permission configurations. (Frontend and backend permissions can be configured)
- ✅ System permissions cannot be deleted

**Audit Logs**

- ✅ Login logs: User login, logout, failed login
- ✅ Operation logs: Record all model additions, deletions, and modifications by model dimension.

**Frontend Features**

- ✅ Dynamic menu (dynamically generated based on permissions)
- ✅ Chinese/English switch

## 🚀 Quick Start

### Requirements

- `Docker Engine 18.06.0`
- `Docker Compose 3.7+`

### Start

> Note:
>
> - Best used on a server.
> - When using on a personal computer, the computer load will be very high during frontend package building if the configuration is not high.

```bash
docker-compose -f docker-compose.prod.yaml up -d
```

### Access

http://localhost:8080/

### Built-in User

| Role | Account | Password |
| ---- | ------- | -------- |
| Administrator | admin | Admin@123 |

### More Commands

```bash
# Stop
docker-compose -f docker-compose.prod.yaml down

# Clean data
./clean.sh
```

## Some Configurations

### Environment Variable Configuration

| Purpose | File |
| ----- | ---- |
| 【Frontend】Vue project configuration | [./code/frontend/.env.production](./code/frontend/.env.production) |
| 【Frontend】Pure Admin configuration | [./code/frontend/public/platform-config.json](./code/frontend/public/platform-config.json) <br/> [./code/frontend/public/platform-config.json.explain](./code/frontend/public/platform-config.json.explain) |
| 【Backend】Business configuration | [code/backend/.prod.yaml](code/backend/.prod.yaml) |
| 【Backend】Full route definition file | [code/backend/base_routes.json](code/backend/base_routes.json) |
| 【Backend】Docker environment variables | `code/backend/.prod.env` |

### Frontend Icon Configuration

- Favicon: `code/frontend/public/favicon.ico`
- Logo: `code/frontend/public/logo.png`
- User avatar: `code/frontend/src/assets/user.jpg`

### System Title Configuration

- `code/frontend/public/platform-config.json`: Title
- `code/frontend/src/views/monitor/dashboard/index.vue`: title

### i18n

- [This is the i18n English file](./code/frontend/src/i18n/locales/en-US.json)
- [This is the i18n Chinese file](./code/frontend/src/i18n/locales/zh-CN.json)

## Reference Documents:
- [Sample readme](https://blog.csdn.net/gitblog_00002/article/details/150695762)
- [README writing](https://github.com/guodongxiaren/README)
- [README writing: icons](https://github.com/guodongxiaren/README/blob/master/emoji.md)
- [Generate table of contents for markdown files](https://zhuanlan.zhihu.com/p/126353341)