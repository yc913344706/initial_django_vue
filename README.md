## 是什么

一个最小化的管理界面。包括前端+后端。

前端 Vue，后端 Django。

## 如何使用

### 单独启动（用于调试）

```bash
# 启动后端
./bin/start_debug_backend.sh

# 启动前端
./bin/start_debug_frontend.sh

# 启动api文档
./bin/start_backend_api_doc.sh
```

### 一键启动

> 注意，生产环境使用。个人电脑使用，配置不高的情况下，会卡住。

```bash
./bin/prod/start_all_in_one.sh
```

## todos

- [x] 一键start/stop/status脚本
- [ ] 修改基础信息
- [ ] 后端镜像build更新
- [ ] HAS_REDIS 配置设置
- [ ] 操作审计表
- [ ] sqlite3 数据导出脚本

## 一些说明

### 环境变量配置

- 后端：配置文件：`etc/config_dir/dev.yaml`
- docker环境变量：`etc/docker_env_files/dev.env`
- 前端：
  - `code/frontend/.env.dev`
  - `code/frontend/public/platform-config.json`

## 更多

### 关于接口文档

MkDocs: https://zhuanlan.zhihu.com/p/423998740
