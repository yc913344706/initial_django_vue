from datetime import datetime, timedelta, timezone as dt_timezone
from lib.redis_tool import get_redis_value, set_redis_value
from lib.time_tools import get_now_time_utc_obj
from lib.request_tool import get_authorization_token, pub_success_response, pub_error_response
from lib.request_tool import pub_get_request_body
from apps.user.models import User
from backend.settings import config_data
from .token_utils import TokenManager
from lib.log import color_logger
from apps.perm.utils import get_user_perm_json_all
from lib.route_tool import RouteTool
from apps.user.utils import format_user_data
from django.contrib.auth.hashers import check_password
from apps.ldapauth.models import LdapConfig
from apps.ldapauth.views import record_user_login_failed, get_user_is_lock
from apps.ldapauth.ldap_utils import LdapAuthBackend

# Create your views here.

def record_user_login_failed(user_name):
    """只有有redis时，才会生效
    """
    redis_key_name = f"user_login_frequency_{user_name}"

    login_times = get_redis_value(
        redis_db_name='AUTH',
        redis_key_name=redis_key_name
    )
    if login_times is not None:
        current_login_failed_num = int(login_times) + 1
    else:
        current_login_failed_num = 1
    
    set_redis_value(
        redis_db_name='AUTH',
        redis_key_name=redis_key_name,
        redis_key_value=current_login_failed_num,
        # set_expire=3600*24*7
    )

def login(request):
    """登录接口"""
    try:
        if request.method != 'POST':
            return pub_error_response(10001, msg="仅支持POST请求")

        body = pub_get_request_body(request)
        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return pub_error_response(10002, msg=f"用户名或密码不能为空")

        if get_user_is_lock(username):
            return pub_error_response(10003, msg="错误过多，被锁定，请联系管理员")

        # 检查LDAP配置是否启用
        ldap_config = LdapConfig.objects.filter(enabled=True).first()
        user_obj = None

        if ldap_config:
            # 首先检查本地数据库中是否已有该用户
            local_user = User.objects.filter(username=username).first()

            if local_user and local_user.is_ldap:
                # 该用户是LDAP用户，使用LDAP认证
                ldap_backend = LdapAuthBackend()
                user_obj = ldap_backend.authenticate(username=username, password=password)

                if not user_obj:
                    # LDAP认证失败，记录失败次数
                    record_user_login_failed(username)
                    return pub_error_response(10004, msg=f"用户名或密码错误")
            elif local_user and not local_user.is_ldap:
                # 该用户是本地用户，使用本地认证
                # 直接使用User模型的check_password方法验证密码
                if local_user.check_password(password):
                    user_obj = local_user
                else:
                    # 本地认证失败，记录失败次数
                    record_user_login_failed(username)
                    return pub_error_response(10005, msg=f"用户名或密码错误")
            else:
                # 用户在本地数据库中不存在，尝试LDAP认证
                ldap_backend = LdapAuthBackend()
                user_obj = ldap_backend.authenticate(username=username, password=password)

                if not user_obj:
                    # LDAP认证失败，记录失败次数
                    record_user_login_failed(username)
                    return pub_error_response(10006, msg=f"用户名或密码错误")
        else:
            # 没有启用LDAP，只使用本地认证
            local_user = User.objects.filter(username=username).first()
            if local_user and not local_user.is_ldap and local_user.check_password(password):
                user_obj = local_user
            else:
                # 本地认证失败，记录失败次数
                record_user_login_failed(username)
                return pub_error_response(10007, msg=f"用户名或密码错误")

        # 认证成功后，重置登录失败计数
        reset_user_login_failed(username)
        
        # 生成token
        color_logger.debug(f"generate_tokens: {username}")
        token_manager = TokenManager()
        access_token, refresh_token, session_id = token_manager.generate_tokens(username)

        color_logger.debug(f"get_user_perm_json_all: {user_obj.uuid}")
        user_permission_json = get_user_perm_json_all(user_obj.uuid)

        # 使用新的is_ldap属性来区分用户类型
        res = format_user_data(user_obj, from_ldap=user_obj.is_ldap, only_basic=True)

        res.update({
            "permissions": user_permission_json.get('frontend', {}).get('resources', []),

            "accessToken": access_token,
            "refreshToken": refresh_token,
            "accessTokenExpires": config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE'),
            "refreshTokenExpires": config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE'),
        })

        response = pub_success_response(res)

        # 设置cookie
        cookie_options = {
            'max_age': config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE'),
            'httponly': config_data.get('AUTH', {}).get('COOKIE_HTTPONLY', True),
            'secure': config_data.get('AUTH', {}).get('COOKIE_SECURE', True),
            'path': '/'
        }
        if config_data.get('AUTH', {}).get('COOKIE_SAMESITE'):
            cookie_options['samesite'] = config_data.get('AUTH', {}).get('COOKIE_SAMESITE')
        if config_data.get('AUTH', {}).get('COOKIE_DOMAIN'):
            cookie_options['domain'] = config_data.get('AUTH', {}).get('COOKIE_DOMAIN')

        # 调试日志
        color_logger.debug(f'Setting cookie with options: {cookie_options}')
        color_logger.debug(f'Access token: {access_token[:10]}...')

        response.set_cookie(
            config_data.get('AUTH', {}).get('COOKIE_ACCESS_TOKEN_NAME'),
            access_token,
            **cookie_options
        )
        response.set_cookie(
            config_data.get('AUTH', {}).get('COOKIE_REFRESH_TOKEN_NAME'),
            refresh_token,
            **{**cookie_options, 'max_age': config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')}
        )

        # 设置用户名cookie
        response.set_cookie(
            config_data.get('AUTH', {}).get('COOKIE_USERNAME_NAME'),
            username,
            **{**cookie_options, 'max_age': config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')}
        )

        return response

    except Exception as e:
        color_logger.error(f"登录失败: {str(e)}", exc_info=True)
        return pub_error_response(10008, msg=f"登录失败: {str(e)}")

def logout(request):
    """退出登录"""
    try:
        if request.method != 'POST':
            return pub_error_response(10009, msg="仅支持POST请求")
            
        # 获取当前用户
        token_manager = TokenManager()
        access_token = request.COOKIES.get(config_data.get('AUTH', {}).get('COOKIE_ACCESS_TOKEN_NAME'))
        username = token_manager.get_username_from_access_token(access_token)
        
        if username:
            # 使当前会话的token失效
            # 需要从token中提取session_id
            payload = token_manager.verify_token(access_token)
            if payload and 'session_id' in payload:
                token_manager.invalidate_tokens(username, session_id=payload['session_id'])
            else:
                # 如果无法获取session_id，则使用户的所有token失效
                token_manager.invalidate_tokens(username)
            
        # 创建响应
        response = pub_success_response('退出成功')
        
        # 删除所有认证相关的cookie
        response.delete_cookie(config_data.get('AUTH', {}).get('COOKIE_ACCESS_TOKEN_NAME'))
        response.delete_cookie(config_data.get('AUTH', {}).get('COOKIE_REFRESH_TOKEN_NAME'))
        response.delete_cookie(config_data.get('AUTH', {}).get('COOKIE_USERNAME_NAME'))
        
        response.content = pub_success_response("退出成功").content
        return response
        
    except Exception as e:
        color_logger.error(f"退出失败: {str(e)}")
        return pub_error_response(10010, msg=f"退出失败: {str(e)}")

def refresh_token(request):
    """刷新token"""
    try:
        if request.method != 'POST':
            return pub_error_response(10011, msg='仅支持POST请求')
        
        color_logger.debug(f"enter request: refresh_token")
        body = pub_get_request_body(request)
        
        color_logger.debug(f"获取 request中的refresh_token")
        refresh_token = request.COOKIES.get(config_data.get('AUTH', {}).get('COOKIE_REFRESH_TOKEN_NAME'))
        if not refresh_token:
            return pub_error_response(10012, msg='refresh token不存在')
            
        color_logger.debug(f"开始刷新token")
        token_manager = TokenManager()
        new_access_token, user_name = token_manager.refresh_access_token(refresh_token)
        assert new_access_token, f"刷新token失败"

        color_logger.debug(f"刷新token成功")
        access_expires = get_now_time_utc_obj() + timedelta(seconds=config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE'))
        refresh_expires = get_now_time_utc_obj() + timedelta(seconds=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE'))
        
        user_obj = User.objects.filter(username=user_name).first()
        assert user_obj, f"用户名({user_name})对应用户不存在"

        color_logger.debug(f"获取用户权限JSON")
        user_permission_json = get_user_perm_json_all(user_obj.uuid)
        # color_logger.debug(f"获取用户权限JSON: {user_permission_json}")

        res = format_user_data(user_obj, from_ldap=False, only_basic=True)

        res.update({
            "permissions": user_permission_json.get('frontend', {}).get('resources', []),

            "accessToken": new_access_token,
            "refreshToken": refresh_token,
            "accessTokenExpires": access_expires,
            "refreshTokenExpires": refresh_expires,
        })

        color_logger.debug(f"准备返回response")
        response = pub_success_response(res)

        color_logger.debug(f"设置cookie")
        cookie_options = {
            'max_age': config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE'),
            'httponly': config_data.get('AUTH', {}).get('COOKIE_HTTPONLY', True),
            'secure': config_data.get('AUTH', {}).get('COOKIE_SECURE', False),
            'path': '/'
        }
        if config_data.get('AUTH', {}).get('COOKIE_SAMESITE'):
            cookie_options['samesite'] = config_data.get('AUTH', {}).get('COOKIE_SAMESITE')
        if config_data.get('AUTH', {}).get('COOKIE_DOMAIN'):
            cookie_options['domain'] = config_data.get('AUTH', {}).get('COOKIE_DOMAIN')

        response.set_cookie(
            config_data.get('AUTH', {}).get('COOKIE_ACCESS_TOKEN_NAME'),
            new_access_token,
            **cookie_options
        )
        
        # 设置用户名cookie
        response.set_cookie(
            config_data.get('AUTH', {}).get('COOKIE_USERNAME_NAME'),
            user_name,
            **{**cookie_options, 'max_age': config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')}
        )
        
        color_logger.debug(f"返回response")
        return response
    except Exception as e:
        return pub_error_response(99998, msg=f"刷新token失败: {e.args}")


def reset_user_login_failed(user_name):
    """重置用户登录失败次数"""
    redis_key_name = f"user_login_frequency_{user_name}"

    # 将失败次数重置为0（也重置过期时间）
    set_redis_value(
        redis_db_name='AUTH',
        redis_key_name=redis_key_name,
        redis_key_value=0,
    )


def get_async_routes(request):
    try:
        if request.method != "GET":
            return pub_error_response(10013, msg=f"请求方法错误")

        # color_logger.debug(f"request: {request}")
        # color_logger.debug(f"获取异步路由请求cookie: {request.COOKIES}")
        # color_logger.debug(f"获取异步路由请求headers: {request.headers}")

        body = pub_get_request_body(request)

        user_name = TokenManager().get_username_from_access_token(get_authorization_token(request))

        if user_name is None:
            return pub_success_response(data=[])

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
        routes_res = route_tool.generate_routes_by_user_permissions(user_routes)

        resources_res = user_permission_json.get('frontend', {}).get('resources', [])
        # color_logger.debug(f"获取异步路由成功: {res}")
        return pub_success_response(data={
            "routes": routes_res,
            "resources": resources_res
        })
    except Exception as e:
        color_logger.error(f"获取异步路由失败: {e}")
        return pub_error_response(10014, msg=f"获取异步路由失败: {e}")
    
