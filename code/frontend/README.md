<h1>vue-pure-admin精简版（非国际化版本）</h1>

[![license](https://img.shields.io/github/license/pure-admin/vue-pure-admin.svg)](LICENSE)


## 介绍

精简版是基于 [vue-pure-admin](https://github.com/pure-admin/vue-pure-admin) 提炼出的架子，包含主体功能，更适合实际项目开发，打包后的大小在全局引入 [element-plus](https://element-plus.org) 的情况下仍然低于 `2.3MB`，并且会永久同步完整版的代码。开启 `brotli` 压缩和 `cdn` 替换本地库模式后，打包大小低于 `350kb`

## 使用

```bash
pnpm install -g @pureadmin/cli
pure create
# frontend
# thin

cd frontend
rm -rf .git .husky
pnpm i
pnpm dev
```

## 一些代码

### 登录
- 位置: src/store/modules/user.ts: loginByUsername
- 登陆完成后：
  - 设置token: accessToken, expires, refreshToken
  - 进入菜单: getTopMenu


### 路由

- 位置：code/frontend/src/router/index.ts
- 自动导入全部静态路由，无需再手动引入！匹配 src/router/modules 目录（任何嵌套级别）中具有 .ts 扩展名的所有文件，除了 remaining.ts 文件


请求/响应拦截器: src/utils/http/index.ts