# OAuth2集成文档

## 概述

本项目集成了ORY Hydra作为OAuth2/OIDC提供者，允许外部应用通过标准OAuth2流程与本系统进行认证和授权。

## 架构

```
外部应用 → Hydra OAuth2 Endpoints → Django后端认证 → Hydra返回token
```

- **ORY Hydra**: 负责OAuth2协议处理和令牌管理
- **Django后端**: 负责用户认证、权限验证
- **现有系统**: 保留原有用户、角色和权限系统

## 部署配置

### Docker Compose
```yaml
hydra:
  image: oryd/hydra:v2.2.0
  container_name: initial_django_vue_hydra
  ports:
    - "4444:4444" # Public port
    - "4445:4445" # Admin port
  environment:
    - DSN=mysql://root:Admin@123@tcp(db_mysql:3306)/hydra?parseTime=true
    - SECRETS_SYSTEM=your-secret-key-change-this-in-production
    - URLS_SELF_ISSUER=http://localhost:4444
    - URLS_CONSENT=http://localhost:8080/api/v1/hydra/consent
    - URLS_LOGIN=http://localhost:8080/api/v1/hydra/login
    - URLS_LOGOUT=http://localhost:8080/api/v1/hydra/logout
  command: 
    - serve
    - all
    - --dev
```

### Nginx配置
```nginx
# OAuth2 endpoints
location /oauth2/ {
    proxy_pass http://hydra:4444/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Hydra admin endpoints (for management)
location /hydra-admin/ {
    proxy_pass http://hydra:4445/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## OAuth2流程

### 1. 用户认证流程
当外部应用发起OAuth2授权请求时：

1. Hydra重定向到 `/api/v1/hydra/login`
2. 用户在此端点完成认证（支持本地用户和LDAP用户）
3. Django后端验证用户凭据
4. 返回认证结果给Hydra
5. Hydra继续OAuth2流程

### 2. 权限授权流程
1. Hydra重定向到 `/api/v1/hydra/consent`
2. 显示需要授权的权限范围
3. 用户确认授权
4. 返回授权结果给Hydra

## API端点

### 后端Hydra端点
- `GET/POST /api/v1/hydra/login` - 用户认证
- `GET/POST /api/v1/hydra/consent` - 用户授权确认
- `GET /api/v1/hydra/userinfo` - OIDC用户信息
- `GET /api/v1/hydra/logout` - OAuth2登出
- `GET/POST/PUT/DELETE /api/v1/hydra/manage-client` - OAuth2客户端管理

### Hydra公共API端点
- `/oauth2/auth` - OAuth2授权端点
- `/oauth2/token` - OAuth2令牌端点
- `/oauth2/revoke` - OAuth2令牌撤销端点
- `/userinfo` - OIDC用户信息端点

### Hydra管理API端点
- `http://localhost:4445/` - Hydra Admin API

## 客户端管理

### 创建OAuth2客户端
直接使用Hydra Admin API:

```bash
curl -X POST http://localhost:4445/clients \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "my-client",
    "client_name": "My Application",
    "grant_types": ["authorization_code", "refresh_token"],
    "response_types": ["code"],
    "redirect_uris": ["https://myapp.com/callback"],
    "scope": "openid profile email"
  }'
```

### 客户端配置参数
- `client_id`: 客户端唯一标识
- `client_name`: 客户端名称
- `grant_types`: 支持的授权类型（如 `authorization_code`, `refresh_token`）
- `response_types`: 支持的响应类型（如 `code`）
- `redirect_uris`: 重定向URI白名单
- `scope`: 允许的权限范围

## 与现有系统集成

### 用户系统
- 外部应用用户认证通过Django后端，支持：
  - 本地用户认证
  - LDAP用户认证
- 认证成功后，外部应用获得标准OAuth2 token

### 权限系统
- OAuth2 token验证与现有权限系统集成
- 通过现有RBAC系统控制外部应用访问权限

## 安全考虑

1. **密钥管理**: `SECRETS_SYSTEM`应使用强密钥并定期更换
2. **HTTPS**: 生产环境应使用HTTPS
3. **客户端安全**: 严格管理OAuth2客户端的重定向URI
4. **权限控制**: 限制外部应用的权限范围

## 常见用法

### 1. 外部应用集成
外部应用使用标准OAuth2授权码流程与本系统集成：

1. 重定向用户到: `http://localhost:8080/oauth2/auth?client_id=xxx&redirect_uri=xxx&response_type=code&scope=openid`
2. 用户完成认证和授权
3. 获得授权码
4. 通过授权码换取token: `http://localhost:8080/oauth2/token`

### 2. OIDC支持
系统支持OpenID Connect，外部应用可获取用户信息：
- 用户信息端点: `http://localhost:8080/api/v1/hydra/userinfo`

## 管理界面

### 前端管理界面
本项目提供了OAuth2客户端的前端管理界面，位于系统管理菜单下：

1. **OAuth2客户端管理**: `/system/oauth2/index` - 管理OAuth2客户端
2. **客户端详情**: `/system/oauth2/detail` - 查看和编辑客户端详情

### 权限控制
- **管理员权限** (`system_admin`): 可完全管理OAuth2客户端
- **只读权限** (`system_reader`): 可查看OAuth2客户端信息
- **API权限**: 通过`/api/v1/hydra/manage-client/`端点进行管理

## 故障排除

### 服务健康检查
- Hydra正常: `curl http://localhost:4444/health/ready`
- Hydra管理正常: `curl http://localhost:4445/health/ready`

### 常见问题
1. **数据库连接问题**: 确保DSN格式正确
2. **网络问题**: 确保容器间网络连通
3. **权限问题**: 检查RBAC配置
4. **前端访问问题**: 确保用户具有相应权限访问管理界面