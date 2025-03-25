from django.shortcuts import render
from django.http import HttpResponse

from apps.user.models import User
from apps.perm.utils import get_user_perm_json_all
from .token_utils import TokenManager
from lib.route_tool import RouteTool
from lib.request_tool import get_authorization_token, pub_get_request_body, pub_success_response, pub_error_response
from lib.log import color_logger
from lib.password_tools import aes
from mock.fake_data import fake_user_login_data_list, fake_async_routes, fake_refresh_token_data

from backend.settings import config_data
from lib.time_tools import get_now_time_utc_obj, timedelta, utc_obj_to_time_zone_str
# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the auth index.")

def login(request):
    try:
        body = pub_get_request_body(request)
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return pub_error_response(f"用户名或密码不能为空")

        # color_logger.debug(f"未加密密码: {password}")
        _encrypt_password = aes.encrypt(password)
        # color_logger.debug(f"加密密码: {_encrypt_password}")
        user_obj = User.objects.filter(username=username, password=_encrypt_password).first()
        assert user_obj, f"用户名或密码错误"
        # 生成token
        token_manager = TokenManager()
        access_token, refresh_token = token_manager.generate_tokens(username)

        expires = get_now_time_utc_obj() + timedelta(seconds=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE'))
        expires_str = utc_obj_to_time_zone_str(expires)


        user_permission_json = get_user_perm_json_all(user_obj.uuid)
        color_logger.debug(f"获取用户权限JSON: {user_permission_json}")

        res = {
            # "avatar": user_obj.avatar,
            "username": user_obj.username,
            "nickname": user_obj.nickname,

            "roles": ["common"],
            "permissions": user_permission_json.get('frontend', {}).get('resources', []),

            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expires": expires,
        }

        
        return pub_success_response(data=res)
        # return pub_success_response(data=fake_user_login_data_list[1])
    except Exception as e:
        color_logger.error(f"登录失败: {e}")
        return pub_error_response(f"登录失败: {e}")

def refresh_token(request):
    try:
        body = pub_get_request_body(request)
        refresh_token = body.get('refreshToken')
        assert refresh_token, f"refreshToken不能为空"

        token_manager = TokenManager()
        new_access_token = token_manager.refresh_access_token(refresh_token)
        assert new_access_token, f"刷新token失败"

        expires = get_now_time_utc_obj() + timedelta(seconds=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE'))
        expires_str = utc_obj_to_time_zone_str(expires)
        res = {
            "accessToken": new_access_token,
            "refreshToken": refresh_token,
            "expires": expires_str,
        }
        
        return pub_success_response(data=res)
    except Exception as e:
        color_logger.error(f"刷新token失败: {e}")
        return pub_error_response(f"刷新token失败: {e}")

def get_async_routes(request):
    try:
        # color_logger.debug(f"request: {request}")
        # color_logger.debug(f"获取异步路由请求cookie: {request.COOKIES}")
        # color_logger.debug(f"获取异步路由请求headers: {request.headers}")

        body = pub_get_request_body(request)

        user_name = TokenManager().get_username_from_access_token(get_authorization_token(request))

        # color_logger.debug(f"获取异步路由请求: user_name: {user_name}")
        assert user_name, f"无法从cookie中获取用户名"

        user_obj = User.objects.filter(username=user_name).first()
        assert user_obj, f"用户名({user_name})对应用户不存在"

        user_permission_json = get_user_perm_json_all(user_obj.uuid)
        # color_logger.debug(f"获取用户权限JSON: {user_permission_json}")
        default_routes = [
            "system.user",
            "system.user.detail",
            "system.permission",
            "system.permission.detail",
            "system.role",
            "system.role.detail",
            "system.group",
            "system.group.detail",
            "permission.page",
            "permission.button.router",
            "permission.button.login"
        ]
        # user_routes = user_permission_json.get('frontend', {}).get('routes', default_routes)
        user_routes = user_permission_json.get('frontend', {}).get('routes', [])
        # color_logger.debug(f"获取异步路由成功: {user_routes}")

        route_tool = RouteTool()
        res = route_tool.generate_routes_by_user_permissions(user_routes)
        # color_logger.debug(f"获取异步路由成功: {res}")
        return pub_success_response(data=res)
    except Exception as e:
        color_logger.error(f"获取异步路由失败: {e}")
        return pub_error_response(f"获取异步路由失败: {e}")


# todo:
# - 授权crud
# - 组合、获取用户权限json
#   - frontend
#     - route
#     - page_role: admin, normal。可以参考:
#       - 当前拥有的code列表：[ "permission:btn:add", "permission:btn:edit", "permission:btn:delete" ]
#   - backend
#     - api: post, get, put, delete
# - 角色：是抽象的，是根据用户权限组合的，最终还是反映到json上
# - 不显示原本的权限管理，但是可以参考他的权限控制逻辑
# - 修改基础信息
# - 后端镜像build更新
# - 一键start/stop/status脚本
# - 数据初始化：
#   - 方案1：
#     - 有dbsqlite3文件，自行导出导入
#     - 准备 sql 脚本，执行即可
#   - 方案2：
#     - base_router.json: 增加表，存储基础路由，界面管理
#     - create permission, user