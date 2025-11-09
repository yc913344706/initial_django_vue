from ldap3 import Server, Connection, SUBTREE
from lib.log import color_logger

class LDAPBackend:

    def __init__(self, config):
        self.server = config.get('HOST')
        self.port = config.get('PORT')
        self.manager_user = config.get('USER_DN')
        self.manager_password = config.get('PASSWORD')
        self.user_search_dn = config.get('USER_SEARCH_BASE')
        self.username_key = config.get('USERNAME_KEY')
        self.email_key = config.get('EMAIL_KEY')


    def auth_ldap_user_password(self, username, password):
        """
        验证ldap用户名、密码是否正确
        @param server: 服务域名
        @param port: 端口号
        @param manager_user: 管理用户名
        @param manager_password: 管理密码
        @param user_search_dn: 用户搜索目录
        @param username_key: 搜索文件标签
        @param email_key: 搜索邮件标签
        @param username: 用户名
        @param password: 密码
        @return:
        """
        ser = Server(host=self.server, port=self.port, use_ssl=False, get_info='ALL')
        # 连接ldap服务器
        ldapz_admin_connection = Connection(ser, user=self.manager_user, password=self.manager_password, auto_bind='NONE', version=3,
                                            authentication='SIMPLE', client_strategy='SYNC', auto_referrals=True,
                                            check_names=True, read_only=False, lazy=False, raise_exceptions=False)
        try:
            # 连上以后必须bind才能有值
            ldapz_admin_connection.bind()
            search_base = self.user_search_dn
            # 这个是为了查询你输入的用户名的入口搜索地址
            resp = ldapz_admin_connection.search(search_base=search_base,
                                                search_filter='({}={})'.format(self.username_key, username),
                                                search_scope=SUBTREE, attributes=['*'])
        except Exception as e:
            return {'status': False, 'message': f'{e}', 'data': ''}

        try:
            if resp:
                color_logger.debug(f'ldap search resp: {resp}')
                
                entry = ldapz_admin_connection.response[0]
                email = entry['attributes'].get(self.email_key) if self.email_key else None
                email = email[0] if email else email
                dn = entry['dn']
                try:
                    # 这个connect是通过用户名和密码还有上面搜到的入口搜索来查询的
                    conn2 = Connection(ser, user=dn, password=password, check_names=True, lazy=False,
                                    raise_exceptions=False)
                    conn2.bind()

                    # 正确-success 不正确-invalidCredentials
                    if conn2.result["description"] == "success":
                        return {'status': True, 'message': 'success', 'data': email}
                    else:
                        return {'status': False, 'message': 'username or password error', 'data': ''}
                except Exception as e:
                    return {'status': False, 'message': e.args, 'data': ''}
            return {'status': False, 'message': 'ldap response is empty', 'data': ''}
        except Exception as e:
            return {'status': False, 'message': e.args, 'data': ''}
        finally:
            try:
                ldapz_admin_connection.unbind()
            except:
                pass
        
    def get_all_users(self):
        """
        获取LDAP中的所有用户信息
        @return: list[dict] 用户信息列表，每个用户包含username和email
        """
        ser = Server(host=self.server, port=self.port, use_ssl=False, get_info='ALL')
        
        # 连接ldap服务器
        ldap_connection = Connection(
            ser, 
            user=self.manager_user, 
            password=self.manager_password, 
            auto_bind='NONE', 
            version=3,
            authentication='SIMPLE', 
            client_strategy='SYNC', 
            auto_referrals=True,
            check_names=True, 
            read_only=False, 
            lazy=False, 
            raise_exceptions=False
        )
        
        try:
            # 连接并绑定
            ldap_connection.bind()
            
            # 搜索所有用户
            search_filter = f'({self.username_key}=*)'  # 匹配所有用户
            attributes = [self.username_key]
            if self.email_key:
                attributes.append(self.email_key)
                
            resp = ldap_connection.search(
                search_base=self.user_search_dn,
                search_filter=search_filter,
                search_scope=SUBTREE, 
                attributes=attributes
            )
            
            if not resp:
                color_logger.error('LDAP search failed')
                return []
                
            users = []
            for entry in ldap_connection.response:
                try:
                    attrs = entry.get('attributes', {})
                    username = attrs.get(self.username_key)
                    if isinstance(username, list):
                        username = username[0] if username else None
                        
                    email = attrs.get(self.email_key)
                    if isinstance(email, list):
                        email = email[0] if email else None
                        
                    if username:
                        users.append({
                            'username': username,
                            'email': email
                        })
                except Exception as e:
                    color_logger.error(f'Parse LDAP user error: {str(e)}', exc_info=True)
                    continue
                    
            return users
            
        except Exception as e:
            color_logger.error(f'Get all LDAP users error: {str(e)}', exc_info=True)
            return []
            
        finally:
            try:
                ldap_connection.unbind()
            except:
                pass

    def test_connection(self):
        """
        测试OpenLDAP连接是否正常
        @return: dict, {'status': bool, 'message': str}
        """
        ser = Server(host=self.server, port=self.port, use_ssl=False, get_info='ALL')
        
        # 连接ldap服务器
        ldap_connection = Connection(
            ser,
            user=self.manager_user,
            password=self.manager_password,
            auto_bind='NONE',
            version=3,
            authentication='SIMPLE',
            client_strategy='SYNC',
            auto_referrals=True,
            check_names=True,
            read_only=False,
            lazy=False,
            raise_exceptions=False
        )
        
        try:
            # 连接并绑定
            ldap_connection.bind()
            
            # 尝试搜索一个用户以验证连接
            search_filter = f'({self.username_key}=*)'  # 匹配所有用户
            attributes = [self.username_key]
            
            resp = ldap_connection.search(
                search_base=self.user_search_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )

            if resp:
                entry_count = len(ldap_connection.response) if ldap_connection.response else 0
                color_logger.debug(f"OpenLDAP连接测试成功，找到 {entry_count} 个用户")
                return {'status': True, 'message': 'OpenLDAP连接测试成功'}
            else:
                color_logger.error('OpenLDAP连接测试失败：无法搜索到任何用户')
                return {'status': False, 'message': '无法搜索到任何用户'}
                
        except Exception as e:
            error_msg = f'OpenLDAP连接测试失败: {str(e)}'
            color_logger.error(error_msg)
            return {'status': False, 'message': error_msg}
        finally:
            try:
                ldap_connection.unbind()
            except:
                pass
        