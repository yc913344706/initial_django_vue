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

### 支持的  OAuth2客户端配置字段详解

***********

1. 授权类型还有一个 Implicit，这个授权类型怎么理解？
2. 响应类型，code对应Authorization Code，token对应Implicit，那授权类型是 Client Credentials 和 Refresh Token时候，响应类型为空？
3. scope的openid, email, profile，填了代表什么意思，会影响什么？是不是还有其他支持的选项？
4. 令牌认证方式，三种方式，具体有什么区别？

***********

1. 但是我看现在的代码，授权类型、响应类型，都支持多选，这个是正确的吗？
2. scope，看你的解释，它主要是2个作用：
   1. oauth系统，会根据标准scope，来返回给客户端scope允许的信息，比如openid，email，profile，但是我有个问题，这些信息，是从哪里拿到的呢？因为我们现在的架构，oauth系统，并不存储用户信息。
   2. 自定义scope，比如：api:read，这个会怎么给客户端使用呢？jwt拆开后有这个？那如果是这样，就是说，客户端获取到了scope，其实是客户端的权限list？那岂不是这个应该在某个地方预定义好都有哪些权限list？这个对吗？
3. 令牌认证方式，我见过header中有 Authorization: Bearer <token> 的方式，这个，我们的ory hydra，支持吗？


***********

1. 那假如我们的权限列表很复杂，通过scope来配置显得不足，我们当前有一个接口 @code/backend/apps/perm/urls.py 中的 user-permission-json/ ，可以获取用户的权限json。那是不是我们就配置基础scope，就行了？
2. Authorization: Basic 和 Authorization: Bearer 有什么区别？
3. 我看你说，在现在的 Django的AuthMiddleware会验证Authorization头中的Bearer token，说的是 @code/backend/apps/myAuth/middleware.py 这个里面的process_request方法吗？如果是，我没有看到验证的代码啊？

***********

@code/frontend/src/views/system/oauth2/index.vue 客户端id和客户端密码，是不是不要在前端填写，直接创建后显示uuid，密码只显示一次？这样是不是比较友好？

***********

我们有详情页面，但是现在的逻辑，在查看和编辑时候，并没有跳转到详情页面，而是在一个弹出框中进行，这块可以修改下，只有新建在弹出框中进行，编辑、查看，均跳转到详情页进行。

***********
***********







#### 客户端ID (Client ID)  
 - 作用：OAuth2系统的唯一标识符，类似用户名
 - 用途：外部应用使用此ID向OAuth2服务器表明身份
 - 示例：my-web-app、mobile-client-1

#### 客户端名称 (Client Name)  

 - 作用：便于管理员识别的友好名称
 - 用途：在管理界面显示，不参与认证流程
 - 示例：我的网站应用、移动端APP

#### 客户端密钥 (Client Secret)  
 - 作用：用于验证客户端身份的密码
 - 安全：仅在创建时显示一次，需妥善保管
 - 用途：在某些授权类型中用于验证客户端身份

#### 授权类型 (Grant Types)  
指定该客户端可以使用的OAuth2授权方式：

 - Authorization Code（授权码模式）
   - 最安全的标准模式
   - 适用于有后端服务器的Web应用
   - 用户登录→获取授权码→后端交换token

 - Client Credentials（客户端凭证模式）
   - 适用于服务间通信
   - 不涉及用户，仅验证客户端身份

 - Refresh Token（刷新令牌）
   - 允许客户端刷新过期的访问令牌

 - Implicit（隐式授权）模式
   - 特点：不使用授权码，直接返回访问令牌
   - 流程：
     1. 用户被重定向到授权服务器
     2. 用户登录并授权
     3. 授权服务器直接在URL片段中返回访问令牌
     4. 客户端浏览器获取令牌
   - 适用场景：纯前端单页应用（SPA）
   - 安全考虑：由于令牌直接暴露在URL中，安全性较低
   - 注意：现代应用中较少使用，推荐Authorization Code + PKCE

   1 # 举例：用户访问
   2 https://your-app.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=token&scope=...
   3 # 授权后重定向
   4 https://your-app.com/callback#access_token=...&token_type=...&expires_in=...


授权类型多选：

1 # 一个客户端可能支持多种授权方式
2 grant_types: ["authorization_code", "refresh_token"]
3 # 或
4 grant_types: ["authorization_code", "client_credentials"] 
- 例如：Web应用通常需要authorization_code进行用户登录，也需要client_credentials进行后台服务调用

#### 响应类型 (Response Types)  

指定OAuth2服务器在授权流程中返回的内容：

 - Code：返回授权码（配合Authorization Code使用）
 - Token：直接返回访问令牌（配合Implicit使用）

不同授权类型的响应类型：

   - Authorization Code → 响应类型为 code
   - Implicit → 响应类型为 token
   - Client Credentials → 无需重定向，无响应类型
     - 这是服务对服务的认证，客户端直接用凭证向服务器请求访问令牌
   - Refresh Token → 无响应类型
     - 用于刷新已有的访问令牌，通常不涉及用户交互

响应类型多选：

1 # 某些高级场景支持多个响应类型
2 response_types: ["code", "token"]  # 非标准用法，通常不建议
3 response_types: ["code"]  # 标准用法，但系统可能为兼容设计了多选
- 理论上不同授权类型对应不同响应类型，但在实现中可能为了兼容性支持多选

#### 重定向URI (Redirect URIs)  
 - 作用：OAuth2服务器将用户重定向到的地址
 - 安全：防止授权码被恶意截获
 - 格式：每行一个URI，例如：

 1   https://myapp.com/callback
 2   http://localhost:3000/callback

#### 授权范围 (Scope)  

- 作用：定义客户端请求的权限范围
- 常用：
 - openid：基本身份信息
 - profile：用户资料
 - email：邮箱信息
- 格式：空格分隔，如 openid profile email

填写scope的意义：
   - 控制客户端可以访问的用户信息范围
   - 实现最小权限原则，提高安全性

  常用标准scope：
   - openid：获取用户唯一标识（sub字段）
   - profile：获取用户基本信息（姓名、头像等）
   - email：获取邮箱信息
   - address：获取地址信息
   - phone：获取电话信息

  自定义scope：

   1 # 您可以根据业务需求自定义scope
   2 api:read          # 仅读取权限
   3 api:write         # 写入权限
   4 user:profile      # 访问用户资料
   5 admin:users       # 管理员访问用户权限

  影响：
   - 决定了访问令牌可以访问的API资源范围
   - 影响授权页面显示给用户的权限说明
   - 限制了外部应用能获取的用户数据量

a) 标准Scope（openid, profile, email）信息来源：

1 您的架构：
2 外部应用 → Hydra → Django后端 → 用户数据
3 
4 Hydra的UserInfo端点(/userinfo)返回的数据来源于：
5 Django的/api/v1/hydra/userinfo/ → 获取当前用户信息 → 返回给Hydra

具体流程：
1. 外部应用用访问令牌访问Hydra的UserInfo端点
2. Hydra向您的/api/v1/hydra/userinfo/端点验证令牌并获取用户信息
3. 您的后端验证令牌并获取用户信息，返回给Hydra
4. Hydra根据scope过滤信息后返回给外部应用

b) 自定义Scope（api:read等）的使用方式：

JWT中的scope处理：

1 # 访问令牌可能包含：
2 {
3   "sub": "user123",
4   "client_id": "my_client", 
5   "scope": "api:read api:write openid profile email",
6   "exp": 1234567890,
7   "iat": 1234567890
8 }

权限验证：
1. 外部应用访问受保护资源时携带访问令牌
2. 服务端验证JWT中的scope字段
3. 根据scope决定是否允许访问特定API

权限预定义：
是的，需要在系统中预定义权限：

1 # 权限系统中定义
2 {
3   "api:read": "允许读取API",
4   "api:write": "允许写入API", 
5   "user:profile": "访问用户资料"
6 }

实际使用：
- scope确实可以理解为客户端的权限列表
- 但更准确地说，是用户授权给客户端的权限范围
- 这些权限需要在您的权限系统中预定义好

对于复杂权限，确实应该采用基础scope + 自定义权限系统的混合方式：

推荐做法：
- 基础scope：只配置openid profile email等标准信息
- 权限验证：通过您现有的user-permission-json接口获取详细权限
- 架构分工：
    - Hydra：处理标准OAuth2流程和基础用户信息
    - 您的系统：处理复杂权限验证

实际使用场景：

1 外部应用 → 获取基础用户信息（通过Hydra + scope）
2          → 获取详细权限（通过您的/user-permission-json/接口）

#### 令牌认证方式 (Token Authentication Method)  

客户端如何向OAuth2服务器证明身份：

 - Client Secret Post：通过请求体发送密钥
 - Client Secret Basic：通过HTTP Basic认证发送
 - None：公开客户端（如移动APP），无需密钥

Client Secret Post：
- 方式：通过POST请求体发送客户端凭证
- 请求示例：

1 POST /oauth2/token
2 Content-Type: application/x-www-form-urlencoded
3 
4 grant_type=authorization_code&
5 code=...&
6 client_id=my_client&
7 client_secret=my_secret&
8 redirect_uri=https://myapp.com/callback
- 安全性：中等，凭证在请求体中传输

Client Secret Basic：
- 方式：通过HTTP Basic认证头发送
- 编码方式：base64(client_id:client_secret)
- 请求示例：

1 POST /oauth2/token
2 Authorization: Basic base64encoded_clientid_secret
3 Content-Type: application/x-www-form-urlencoded
4 
5 grant_type=authorization_code&code=...&redirect_uri=...
- 安全性：较高，凭证在认证头中传输，不暴露在请求体中

None（公开客户端）：
- 使用场景：移动APP、单页应用（SPA）
- 原因：无法安全保存客户端密钥
- 安全机制：依赖PKCE（Proof Key for Code Exchange）防止授权码劫持
- 请求示例：

1 POST /oauth2/token
2 Content-Type: application/x-www-form-urlencoded
3 
4 grant_type=authorization_code&
5 code=...&
6 client_id=my_public_client&
7 redirect_uri=https://myapp.com/callback&
8 code_verifier=... # PKCE验证器

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