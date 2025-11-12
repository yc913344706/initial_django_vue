from django.conf import settings
from lib.log import color_logger
from apps.ldapauth.models import LdapConfig
from apps.user.models import User
from lib.ad_ldap_tool import ADLDAPClient
from lib.openldap_tool import LDAPBackend


class LdapAuthBackend:
    """LDAP认证后端"""

    def authenticate(self, username=None, password=None):
        """
        LDAP认证方法
        """
        try:
            # 获取LDAP配置
            ldap_config = LdapConfig.objects.filter(enabled=True).first()
            if not ldap_config:
                color_logger.debug("LDAP未启用或未配置")
                return None

            color_logger.debug(f"LDAP认证参数: server={ldap_config.server_host}, admin_dn={ldap_config.admin_dn}, base_dn={ldap_config.base_dn}")
            color_logger.debug(f"LDAP类型: {ldap_config.ldap_type}, 用户名: {username}")

            # 根据LDAP类型选择相应的工具类
            if ldap_config.ldap_type == 'ad':
                # 构建AD LDAP配置
                ad_config = LdapUtils.construct_ldap_config(ldap_config)
                
                ad_client = ADLDAPClient(ad_config)
                success, result = ad_client.verify_user(username, password)
                color_logger.debug(f"LDAP认证结果: {success} {result}")
                
                if success:
                    user_info = result
                    user_dn = user_info.get('dn', '')
                    display_name = user_info.get('displayName', username) or username
                    email = user_info.get('mail', '')
                    
                    # 用户验证成功，检查是否已在本地数据库中存在
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'nickname': display_name,
                            'email': email,
                            'is_ldap': True,
                            'ldap_dn': user_dn,
                            'password': ''  # LDAP用户不设置本地密码
                        }
                    )

                    if not created and user.is_ldap:
                        # 更新用户信息
                        user.nickname = display_name
                        user.email = email
                        user.ldap_dn = user_dn
                        user.save()

                    return user
                else:
                    color_logger.error(f"AD LDAP认证失败: {result}")
                    return None
            
            elif ldap_config.ldap_type == 'openldap':
                # 构建OpenLDAP配置
                openldap_config = LdapUtils.construct_ldap_config(ldap_config)
                
                ldap_backend = LDAPBackend(openldap_config)
                result = ldap_backend.auth_ldap_user_password(username, password)
                color_logger.debug(f"LDAP认证结果: {result}")
                
                if result['status']:
                    # 用户验证成功，检查是否已在本地数据库中存在
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'nickname': username,  # OpenLDAP可能不直接返回display name，先用用户名
                            'email': result.get('data', ''),
                            'is_ldap': True,
                            'ldap_dn': username,  # OpenLDAP可能需要特别处理DN
                            'password': ''  # LDAP用户不设置本地密码
                        }
                    )

                    if not created and user.is_ldap:
                        # 更新用户信息
                        user.email = result.get('data', user.email)
                        user.save()

                    return user
                else:
                    color_logger.error(f"OpenLDAP认证失败: {result['message']}")
                    return None
            else:
                color_logger.error(f"不支持的LDAP类型: {ldap_config.ldap_type}")
                return None

        except Exception as e:
            color_logger.error(f"LDAP认证异常: {str(e)}")
            return None

    def get_user(self, user_id):
        """根据用户ID获取用户"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class LdapUtils:
    """LDAP工具类"""

    @classmethod
    def construct_ldap_config(cls, ldap_config: LdapConfig|dict):
        """
        构造LDAP配置
        """
        if type(ldap_config) == dict:
            ldap_type = ldap_config.get('ldap_type')
            if ldap_type == 'ad':
                return {
                    "SERVER": ldap_config['server_host'],
                    "PORT": ldap_config['server_port'],
                    "BASE_DN": ldap_config['base_dn'],
                    "USER": ldap_config.get('username_attr', 'sAMAccountName'),
                    "PASSWORD": ldap_config.get('admin_password', ''),  # 从配置中获取的密码应该是已解密的，如果是新配置则为空
                    "METHOD": "plain",
                    "BIND_DN": ldap_config['admin_dn'],
                    "SEARCH_ATTRIBUTE": ldap_config.get('username_attr'),
                    "SEARCH_FILTER": ldap_config.get('user_search_filter')
                }
            if ldap_type == 'openldap':
                return {
                    'HOST': ldap_config['server_host'],
                    'PORT': ldap_config['server_port'],
                    'USER_DN': ldap_config['admin_dn'],
                    'PASSWORD': ldap_config.get('admin_password', ''),  # 从配置中获取的密码应该是已解密的，如果是新配置则为空
                    'USER_SEARCH_BASE': ldap_config['base_dn'],
                    'USERNAME_KEY': ldap_config.get('username_attr', 'uid'),
                    'EMAIL_KEY': ldap_config.get('email_attr', 'mail')
                }
        elif type(ldap_config) == LdapConfig:
            ldap_type = ldap_config.ldap_type
            if ldap_type == 'ad':
                return {
                    "SERVER": ldap_config.server_host,
                    "BASE_DN": ldap_config.base_dn,
                    "USER": ldap_config.username_attr,
                    "PASSWORD": ldap_config.get_admin_password(),
                    "PORT": ldap_config.server_port,
                    "METHOD": "plain",
                    "BIND_DN": ldap_config.admin_dn,
                    "SEARCH_ATTRIBUTE": ldap_config.username_attr,
                    "SEARCH_FILTER": ldap_config.user_search_filter
                }
            elif ldap_type == 'openldap':
                return {
                    'HOST': ldap_config.server_host,
                    'PORT': ldap_config.server_port,
                    'USER_DN': ldap_config.admin_dn,
                    'PASSWORD': ldap_config.get_admin_password(),
                    'USER_SEARCH_BASE': ldap_config.base_dn,
                    'USERNAME_KEY': ldap_config.username_attr,
                    'EMAIL_KEY': ldap_config.email_attr
                }

    @staticmethod
    def test_connection(ldap_config_data):
        """
        测试LDAP连接
        """
        try:
            ldap_type = ldap_config_data.get('ldap_type', 'ad')
            color_logger.debug(f"测试LDAP连接，类型: {ldap_type}, 服务器: {ldap_config_data['server_host']}")
            
            if ldap_type == 'ad':
                # 构建AD LDAP配置
                ad_config = LdapUtils.construct_ldap_config(ldap_config_data)
                
                ad_client = ADLDAPClient(ad_config)
                success, message = ad_client.test_connection()
                return success, message
            
            elif ldap_type == 'openldap':
                # 构建OpenLDAP配置
                openldap_config = LdapUtils.construct_ldap_config(ldap_config_data)
                
                ldap_backend = LDAPBackend(openldap_config)
                result = ldap_backend.test_connection()
                return result['status'], result['message']
            
            else:
                error_msg = f"不支持的LDAP类型: {ldap_type}"
                color_logger.error(error_msg)
                return False, error_msg

        except Exception as e:
            error_msg = f"LDAP连接测试失败: {str(e)}"
            color_logger.error(error_msg)
            return False, error_msg