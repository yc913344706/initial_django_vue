# API 文档

欢迎使用我们的 API 文档。本文档将帮助您更好地理解和使用我们的 API。

## 项目结构

我们的后端项目基于 Django 框架开发，主要包含以下应用模块：

- [用户认证模块](api/auth/index.md) - 处理用户登录、令牌刷新等认证相关功能
- [权限管理模块](api/perm/index.md) - 处理系统权限和角色管理
- [用户管理模块](api/user/index.md) - 处理用户信息和用户组管理
- [示例模块](api/demo/index.md) - 示例功能模块

## 快速开始

### 环境要求

- Python 3.8+
- Django 4.2+
- 其他依赖见 requirements.txt

### 安装步骤

1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 配置数据库
4. 运行迁移：`python manage.py migrate`
5. 启动服务：`python manage.py runserver`

### 认证方式

所有 API 请求都需要进行身份认证。请在请求头中包含认证信息：

```http
Authorization: Bearer your-token
```

## API 规范

### 响应格式

所有 API 响应都遵循以下格式：

```json
{
    "code": 200,
    "success": true,
    "msg": "success",
    "data": {
        // 响应数据
    }
}
```

### 错误码说明

- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器内部错误

## 开发指南

### 本地开发

1. 创建虚拟环境
2. 安装开发依赖
3. 配置开发环境变量
4. 启动开发服务器

### 测试

运行测试用例：

```bash
python manage.py test
```

## 部署

详细的部署文档请参考 [部署指南](deployment.md)

## 支持

如果您在使用过程中遇到任何问题，请：

1. 查看 [常见问题](faq.md)
2. 提交 Issue
3. 联系技术支持团队 