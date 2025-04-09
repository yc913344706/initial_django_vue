## 是什么

- 基于 `Python 3.10`、`Django 4.2`、`Vue 3.5` 的微服务RBAC 权限管理系统。
- 一个最小化的管理界面。包括前端+后端。

## 如何使用

### 内置用户

| 角色 | 账号 | 密码 |
| ---- | ---- | ---- |
| 管理员 | admin | admin123 |
| 普通用户 | normal | normal123 |


### 单独启动（用于调试）

#### 前端

```bash
# 启动前端（docker形式，run dev, 推荐）
./bin/debug_frontend_docker.sh -E dev

# 启动前端（非docker, run dev）
./bin/debug_frontend.sh
```

#### 后端

```bash
# 启动后端（docker形式，推荐）
./bin/debug_backend_docker.sh -E dev
# 如果实在pnpm install失败，可以尝试本地 pnpm install，然后再用docker启动

# 启动后端（非docker）
./bin/debug_backend.sh
```

### 正式环境一键启动

> 注意：
>
> - 最好在生产环境使用。
> - 个人电脑使用，配置不高的情况下，电脑负载会很高。

```bash
./bin/prod/start_all_in_one.sh -E dev
```

### 启动api文档

```bash
./bin/start_backend_api_doc.sh
```

## 一些配置

### 环境变量配置

- 后端：配置文件：`etc/config_dir/dev.yaml`
  - 注：后端日志级别：`LOG_LEVEL`
- docker环境变量：`etc/docker_env_files/dev.env`
- 前端：
  - `code/frontend/.env.development`
    - 注：前端日志级别：`VITE_LOG_LEVEL`
  - `code/frontend/public/platform-config.json`

### 前端图标

- 图标：`code/frontend/public/favicon.ico`
- logo：`code/frontend/public/logo.png`
- user-avatar：`code/frontend/src/assets/user.jpg`

## todos

- [ ] doc: 最佳实践：项目应用步骤
- [ ] logout
- [ ] 后端设置 access_token, refresh_token
- [ ] django admin
- [ ] 自定义表格

## 更多

### 关于接口文档

MkDocs: https://zhuanlan.zhihu.com/p/423998740
