from django.shortcuts import render
from lib.request_tool import pub_success_response, pub_error_response, pub_get_request_body
from lib.log import color_logger
from .models import LdapConfig, SecurityConfig
from .ldap_utils import LdapUtils
from lib.redis_tool import get_redis_value, set_redis_value
from datetime import datetime, timedelta


def ldap_config(request):
    """处理LDAP配置的GET和POST请求"""
    try:
        if request.method == 'GET':
            # 获取LDAP配置
            ldap_config = LdapConfig.objects.first()
            if ldap_config:
                response_data = {
                    'enabled': ldap_config.enabled,
                    'server_host': ldap_config.server_host,
                    'server_port': ldap_config.server_port,
                    'base_dn': ldap_config.base_dn,
                    'admin_dn': ldap_config.admin_dn,
                    'admin_password': '',  # 不返回密码
                    'user_search_filter': ldap_config.user_search_filter,
                    'username_attr': ldap_config.username_attr,
                    'display_name_attr': ldap_config.display_name_attr,
                    'email_attr': ldap_config.email_attr,
                    'ldap_type': ldap_config.ldap_type,
                }
            else:
                # 返回默认配置
                response_data = {
                    'enabled': False,
                    'server_host': '',
                    'server_port': 389,
                    'base_dn': '',
                    'admin_dn': '',
                    'admin_password': '',
                    'user_search_filter': '(objectClass=user)',
                    'username_attr': 'sAMAccountName',
                    'display_name_attr': 'displayName',
                    'email_attr': 'mail',
                    'ldap_type': 'ad',  # 默认为Active Directory
                }

            return pub_success_response(response_data)
        
        elif request.method == 'POST':
            # 保存LDAP配置
            body = pub_get_request_body(request)

            server_host = body.get('server_host', '')
            server_port = body.get('server_port', 389)
            
            ldap_config, created = LdapConfig.objects.get_or_create(
                uuid=1,  # 使用固定ID确保只有一个配置
                defaults={
                    'enabled': body.get('enabled', False),
                    'server_host': server_host,
                    'server_port': server_port,
                    'base_dn': body.get('base_dn', ''),
                    'admin_dn': body.get('admin_dn', ''),
                    'admin_password': body.get('admin_password', ''),
                    'user_search_filter': body.get('user_search_filter', '(objectClass=user)'),
                    'username_attr': body.get('username_attr', 'sAMAccountName'),
                    'display_name_attr': body.get('display_name_attr', 'displayName'),
                    'email_attr': body.get('email_attr', 'mail'),
                    'ldap_type': body.get('ldap_type', 'ad'),
                }
            )

            if not created:
                # 更新现有配置
                ldap_config.enabled = body.get('enabled', False)
                ldap_config.server_host = server_host
                ldap_config.server_port = server_port
                ldap_config.base_dn = body.get('base_dn', '')
                ldap_config.admin_dn = body.get('admin_dn', '')
                ldap_config.admin_password = body.get('admin_password', '')
                ldap_config.user_search_filter = body.get('user_search_filter', '(objectClass=user)')
                ldap_config.username_attr = body.get('username_attr', 'sAMAccountName')
                ldap_config.display_name_attr = body.get('display_name_attr', 'displayName')
                ldap_config.email_attr = body.get('email_attr', 'mail')
                ldap_config.ldap_type = body.get('ldap_type', 'ad')
                ldap_config.save()

            return pub_success_response("LDAP配置保存成功")
        else:
            return pub_error_response(11001, msg="不支持的请求方法")

    except Exception as e:
        color_logger.error(f"处理LDAP配置失败: {str(e)}")
        return pub_error_response(11002, msg=str(e))


def test_ldap_connection(request):
    """测试LDAP连接"""
    try:
        if request.method != 'POST':
            return pub_error_response(11003, msg="只允许POST请求")

        color_logger.debug(f"enter request: test_ldap_connection")
        body = pub_get_request_body(request)

        success, message = LdapUtils.test_connection(body)
        
        if success:
            return pub_success_response(message)
        else:
            return pub_error_response(11004, msg=message)

    except Exception as e:
        color_logger.error(f"测试LDAP连接失败: {str(e)}")
        return pub_error_response(11005, msg=str(e))


def security_config(request):
    """处理安全配置的GET和POST请求"""
    try:
        if request.method == 'GET':
            # 获取安全配置
            security_config = SecurityConfig.objects.first()
            if security_config:
                response_data = {
                    'max_login_attempts': security_config.max_login_attempts,
                    'lockout_duration': security_config.lockout_duration,
                }
            else:
                # 返回默认配置
                response_data = {
                    'max_login_attempts': 5,
                    'lockout_duration': 60,
                }

            return pub_success_response(response_data)
        
        elif request.method == 'POST':
            # 保存安全配置
            body = pub_get_request_body(request)

            security_config, created = SecurityConfig.objects.get_or_create(
                uuid=1,  # 使用固定ID确保只有一个配置
                defaults={
                    'max_login_attempts': body.get('max_login_attempts', 5),
                    'lockout_duration': body.get('lockout_duration', 60),
                }
            )

            if not created:
                # 更新现有配置
                security_config.max_login_attempts = body.get('max_login_attempts', 5)
                security_config.lockout_duration = body.get('lockout_duration', 60)
                security_config.save()

            return pub_success_response("安全配置保存成功")
        else:
            return pub_error_response(11006, msg="不支持的请求方法")

    except Exception as e:
        color_logger.error(f"处理安全配置失败: {str(e)}")
        return pub_error_response(11007, msg=str(e))


def record_user_login_failed(user_name):
    """记录用户登录失败"""
    redis_key_name = f"user_login_frequency_{user_name}"

    login_times = get_redis_value(
        redis_db_name='AUTH',
        redis_key_name=redis_key_name
    )
    if login_times is not None:
        current_login_failed_num = int(login_times) + 1
    else:
        current_login_failed_num = 1

    # 获取安全配置中的最大尝试次数
    security_config = SecurityConfig.objects.first()
    max_attempts = security_config.max_login_attempts if security_config else 5
    
    set_redis_value(
        redis_db_name='AUTH',
        redis_key_name=redis_key_name,
        redis_key_value=current_login_failed_num,
    )


def get_user_is_lock(user_name):
    """检查用户是否被锁定"""
    # 获取安全配置
    security_config = SecurityConfig.objects.first()
    max_attempts = security_config.max_login_attempts if security_config else 5
    lockout_duration = security_config.lockout_duration if security_config else 60  # 分钟

    redis_key_name = f"user_login_frequency_{user_name}"

    already_login_failed_times = get_redis_value(
        redis_db_name='AUTH',
        redis_key_name=redis_key_name
    )
    if already_login_failed_times is not None:
        already_login_failed_times = int(already_login_failed_times)
    else:
        already_login_failed_times = 0

    if already_login_failed_times >= max_attempts:
        return True

    return False
