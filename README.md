## 是什么

- 基于 `Python 3.10`、`Django 4.2`、`Vue 3.5` 的微服务RBAC 权限管理系统。
- 一个最小化的管理界面。包括前端+后端。

## 如何使用

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
- docker环境变量：`etc/docker_env_files/dev.env`
- 前端：
  - `code/frontend/.env.dev`
  - `code/frontend/public/platform-config.json`

### 前端图标

- 图标：`code/frontend/public/favicon.ico`
- logo：`code/frontend/public/logo.png`
- user-avatar：`code/frontend/src/assets/user.jpg`

## todos

- [ ] 后端镜像 build 更新
- [ ] doc: 最佳实践：项目应用步骤
- [ ] 自定义表格

## 更多

### 关于接口文档

MkDocs: https://zhuanlan.zhihu.com/p/423998740
