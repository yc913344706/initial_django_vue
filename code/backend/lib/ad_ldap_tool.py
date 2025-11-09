from datetime import datetime, timedelta, timezone as dt_timezone
import time
import ldap
import ldap.filter
import ssl
import os
import sys
from typing import Tuple, List, Dict, Optional, Any
from celery import shared_task
from django.utils import timezone
from apps.user.models import User
from django.db import transaction

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BACKEND_DIR)

from lib.sort_tool import sort_exact_first
from lib.time_tools import utc_obj_to_time_zone_str, utc_obj_to_timezone_obj
from lib.log import color_logger


class ADLDAPClient:
    """AD LDAP 客户端类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化 AD LDAP 客户端

        Args:
            config: LDAP 配置字典，如果不提供则使用默认配置
        """
        self.config = config
        self._init_config()
        self._init_ldap_options()

    def _init_config(self) -> None:
        """初始化 LDAP 配置"""
        self.server = self.config.get("SERVER")
        self.base_dn = self.config.get("BASE_DN")
        self.port = self.config.get("PORT", 389)


        self.bind_dn = self.config.get("BIND_DN")
        self.admin_password = self.config.get("PASSWORD")
        self.method = self.config.get("METHOD", "plain")

        self.user_attr = self.config.get("USER")
        self.search_filter = self.config.get("SEARCH_FILTER")
        
        self.search_attribute_list = ['sAMAccountName', 'displayName']
        self.return_attribute_list = [
                'cn',
                'sAMAccountName', 
                'mail', 
                'displayName', 
                'userPrincipalName',
                "department",
                "title",
                "telephoneNumber"]
        
        # 验证必要的配置
        required_fields = ["SERVER", "BASE_DN", "BIND_DN", "PASSWORD"]
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        if missing_fields:
            raise ValueError(f"Missing required LDAP configuration: {', '.join(missing_fields)}")

    def _init_ldap_options(self) -> None:
        """初始化 LDAP 选项"""
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        ldap.set_option(ldap.OPT_REFERRALS, 0)

    def _get_connection(self) -> ldap.ldapobject.LDAPObject:
        """
        获取 LDAP 连接

        Returns:
            LDAP 连接对象
        """
        server_url = f"ldap://{self.server}:{self.port}"
        return ldap.initialize(server_url)

    @staticmethod
    def _escape_filter(filter_str: str) -> str:
        """
        转义 LDAP 过滤器字符串中的特殊字符

        Args:
            filter_str: 需要转义的字符串

        Returns:
            转义后的字符串
        """
        escape_dict = {
            '\\': r'\5c',
            '*': r'\2a',
            '(': r'\28',
            ')': r'\29',
            '\x00': r'\00'
        }
        return ''.join(escape_dict.get(char, char) for char in filter_str)

    @staticmethod
    def _decode_attr(value: Any) -> Optional[str]:
        """
        解码 LDAP 属性值

        Args:
            value: LDAP 属性值

        Returns:
            解码后的字符串或 None
        """
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value

    def _process_search_result(self, results: List[Tuple[str, Dict]], search_user_name=None) -> List[Dict[str, Any]]:
        """
        处理 LDAP 搜索结果

        Args:
            results: LDAP 搜索结果列表
            search_user_name: 搜索的用户名，会根据这个字段，对结果进行排序

        Returns:
            处理后的用户信息列表
        """
        valid_results = [(dn, attrs) for dn, attrs in results if isinstance(attrs, dict)]
        users = []

        for dn, attributes in valid_results:
            def get_attr(attr_name: str) -> Optional[str]:
                if attr_name not in attributes:
                    return None
                values = attributes[attr_name]
                if not values:
                    return None
                return self._decode_attr(values[0])

            user = {
                "dn": self._decode_attr(dn),
                "name": get_attr("cn"),
                "sAMAccountName": get_attr("sAMAccountName"),
                "mail": get_attr("mail"),
                "displayName": get_attr("displayName"),
                "userPrincipalName": get_attr("userPrincipalName"),
            }
            users.append(user)
        
        if search_user_name is None:
            return users

        return sort_exact_first(users, 'sAMAccountName', search_user_name)

    def _search_users(
            self,
            search_term: str = None,
            limit_num: int = -1,
            need_escape_search_term: bool = True,
            page_size: int = 1000,  # 添加分页大小参数
            exact_match: bool = False # 添加精确匹配参数
        ) -> List[Dict[str, Any]]:
        """
        搜索 AD 用户

        Args:
            search_term: 搜索关键词
            search_attribute_list: 定义在哪些属性中搜索关键词，默认为 ['sAMAccountName', 'displayName']
            limit_num: 限制返回的用户数量
            need_escape_search_term: 是否需要转义搜索词
            page_size: 分页大小，用于避免LDAP大小限制

        Returns:
            匹配的用户信息列表
            [{'dn': 'CN=yul6,OU=奥体经营大区102745,OU=南京经营战区101099,OU=南京业务战区103824,OU=城市业务中心101846,OU=自如总部100001,DC=ziroom,DC=com', 'name': 'yul6', 'sAMAccountName': 'yul6', 'mail': 'yul6@ziroom.com', 'displayName': '于磊', 'userPrincipalName': 'yul6@ziroom.com'}]
        """

        if search_term is None:
            search_filter = f"(objectClass=user)"
        else:
            escaped_term = search_term
            if need_escape_search_term:
                # 转义搜索关键词
                escaped_term = self._escape_filter(search_term)

            # 构建OR条件的搜索过滤器
            if exact_match:
                conditions = [f"({attr}={escaped_term})" for attr in self.search_attribute_list]
            else:
                conditions = [f"({attr}=*{escaped_term}*)" for attr in self.search_attribute_list]
            
            search_filter = f"(&(objectClass=user)(|{''.join(conditions)}))"

        color_logger.debug(f"LDAP search filter: {search_filter}")

        conn = None
        try:
            conn = self._get_connection()
            conn.simple_bind_s(self.bind_dn, self.admin_password)

            # 使用分页控件解决大小限制问题
            all_results = []
            page_control = ldap.controls.SimplePagedResultsControl(True, size=page_size, cookie='')
            
            index = 0
            while True:
                time.sleep(0.1)
                index += 1
                color_logger.debug(f"searching page {index} ...")
                # 执行分页搜索
                # attr_list: 定义需要从LDAP服务器返回的属性
                msgid = conn.search_ext(
                    self.base_dn,
                    ldap.SCOPE_SUBTREE,
                    search_filter,
                    self.return_attribute_list,
                    serverctrls=[page_control]
                )

                # 获取结果
                rtype, rdata, rmsgid, serverctrls = conn.result3(msgid)
                
                # 添加当前页结果
                all_results.extend(rdata)
                color_logger.debug(f"page: {index}, all_results len: {len(all_results)}")

                # 检查是否还有更多页面
                controls = [ctrl for ctrl in serverctrls
                          if ctrl.controlType == ldap.controls.SimplePagedResultsControl.controlType]
                

                if not controls or not controls[0].cookie:
                    color_logger.debug(f"page: {index}, no more pages")
                    break  # 没有更多页面
                
                # 更新分页控件的cookie以获取下一页
                page_control.cookie = controls[0].cookie


                # 如果已经获取足够的结果，则停止
                if limit_num > 0:
                    if len(all_results) >= limit_num * 2:  # 多获取一些用于排序
                        color_logger.debug(f"page: {index}, limit_num reached")
                        break

            if search_term:
                results = self._process_search_result(all_results, search_user_name=search_term)
            else:
                results = self._process_search_result(all_results)

            # 限制返回数量
            if limit_num > 0:
                return results[:limit_num]

            return results

        except ldap.LDAPError as e:
            color_logger.error(f"LDAP search error: {e.args}")
            if hasattr(e, 'desc'):
                color_logger.error(f"Error description: {e.desc}")
            return []
        finally:
            if conn:
                conn.unbind_s()

    def verify_user(self, username: str, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        验证用户凭据

        Args:
            username: 用户名
            password: 密码

        Returns:
            (验证是否成功, 用户信息)
        """
        conn = None
        try:
            # 搜索用户
            users = self._search_users(username)
            if not users:
                color_logger.warn(f"User {username} not found")
                return False, f"用户名或密码错误: {username}"

            user = users[0]
            user_dn = user['dn']

            # 验证密码
            conn = self._get_connection()
            try:
                conn.simple_bind_s(user_dn, password)
                color_logger.debug(f"验证成功: {username}")
                return True, user
            except ldap.INVALID_CREDENTIALS:
                return False, f"用户名或密码错误: {username}"

        except ldap.LDAPError as e:
            color_logger.error(f"LDAP验证错误: {str(e)}")
            return False, f"用户名或密码错误: {username}"
        finally:
            if conn:
                conn.unbind_s()

    def get_all_users(self, page_size: int = 1000) -> List[Dict[str, Any]]:
        """
        获取所有 AD 用户列表

        Args:
            page_size: 每次查询的用户数量，默认 1000
            attributes: 要获取的用户属性列表，默认为 None (使用标准属性集)

        Returns:
            用户信息列表
        """
        all_ldap_users = self._search_users()
        all_users = [i for i in all_ldap_users if i['mail']]
        color_logger.debug(f"获取所有用户: {len(all_users)}")
        return all_users

    def test_connection(self) -> Tuple[bool, str]:
        """
        测试AD LDAP连接是否正常

        Returns:
            (连接是否成功, 消息)
        """
        try:
            color_logger.debug("开始测试AD LDAP连接...")
            results = self._search_users(limit_num=1)
            results = self._search_users(search_term='yuc7', limit_num=1)
            # results = self.get_all_users()
            
            color_logger.debug(f"LDAP连接测试成功，找到 {len(results)} 个用户。{results}")
            return True, "AD LDAP连接测试成功"
            
        except ldap.INVALID_CREDENTIALS:
            error_msg = "LDAP管理员凭据无效"
            color_logger.error(error_msg)
            return False, error_msg
        except ldap.SERVER_DOWN:
            error_msg = "LDAP服务器无法连接"
            color_logger.error(error_msg)
            return False, error_msg
        except ldap.LDAPError as e:
            error_msg = f"LDAP连接测试失败: {str(e)}"
            color_logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"连接测试异常: {str(e)}"
            color_logger.error(error_msg)
            return False, error_msg


def test_search_users(client: ADLDAPClient, search_term: str) -> None:
    """测试搜索用户"""
    users = client._search_users(search_term)
    if users:
        print("找到以下用户:")
        for user in users:
            print(f"user: {user}")


def test_verify_user(client: ADLDAPClient, username: str, password: str) -> None:
    """测试验证用户"""
    success, user_info = client.verify_user(username, password)
    if success:
        print("验证成功!")
        print("用户信息:", user_info)
    else:
        print("验证失败: 用户名或密码错误")


def test_get_all_users(client: ADLDAPClient) -> None:
    """测试获取所有用户"""
    color_logger.info("正在获取所有用户...")
    users = client.get_all_users()
    color_logger.info(f"共获取到 {len(users)} 个用户")
    
    # 打印前 5 个用户的信息作为示例
    for i, user in enumerate(users[:5], 1):
        print(f"\n用户 {i}:")
        print(f"  DN: {user['dn']}")
        print(f"  Name: {user['name']}")
        print(f"  SAM: {user['sAMAccountName']}")
        print(f"  Mail: {user['mail']}")
        print(f"  Display Name: {user['displayName']}")
        print("  " + "-" * 30)


@shared_task
def update_users_to_db_task(users_data):
    """将用户数据更新到数据库的异步任务
    
    Args:
        users_data: LDAP用户数据列表
    
    Returns:
        更新统计信息
    """
    try:
        stats = {
            "total": len(users_data),
            "created": 0,
            "updated": 0
        }
        
        with transaction.atomic():
            db_users = User.all_objects.filter(username__in=[i.get('sAMAccountName') for i in users_data])
            for user_data in users_data:
                username = user_data.get('sAMAccountName')
                if not username:
                    continue
                    
                # 更新或创建用户
                db_user_obj = db_users.filter(username=username).first()
                if db_user_obj and (( utc_obj_to_timezone_obj(datetime.now(dt_timezone.utc)) - utc_obj_to_timezone_obj(db_user_obj.last_sync)) <= timedelta(days=1)):
                    # 如果用户同步时间在1天以内，则不更新
                    continue
                
                user, created = User.all_objects.update_or_create(
                    username=username,
                    defaults={
                        'display_name': user_data.get('displayName', ''),
                        'email': user_data.get('mail', ''),
                        'dn': user_data.get('dn', ''),
                        'principal_name': user_data.get('userPrincipalName', ''),
                        'is_del': False,
                        'last_sync': datetime.now(dt_timezone.utc)
                    }
                )
                
                if created:
                    stats['created'] += 1
                else:
                    stats['updated'] += 1
                    
        return stats
        
    except Exception as e:
        color_logger.error(f"更新用户到数据库失败: {str(e)}")
        raise


def search_ldap_and_save_db(search_term: str, limit_num: int = 10, async_exec: bool = True) -> Tuple[List[Dict[str, Any]], str]:
    """搜索LDAP用户并异步保存到数据库
    
    Args:
        search_term: 搜索关键词
        limit_num: 限制返回数量
        async_exec: 是否异步执行
    Returns:
        Tuple[List[Dict[str, Any]], str]: (用户列表, 任务ID)
    """
    try:
        # 搜索LDAP用户
        client = ADLDAPClient()
        users = client._search_users(search_term, limit_num=limit_num)
        
        if users:
            if async_exec:
                # 启动异步任务更新数据库
                task = update_users_to_db_task.delay(users)
                return users, task.id
            else:
                # 同步更新数据库
                update_users_to_db_task(users)
                return users, ''
        
        return [], ''
        
    except Exception as e:
        color_logger.error(f"搜索LDAP并保存失败: {str(e)}", exc_info=True)
        raise



if __name__ == "__main__":
    try:
        client = ADLDAPClient()
        test_search_users(client, '于梦')
        # test_verify_user(client, 'yuc7', 'XXXXXXXX')
        # test_get_all_users(client)
    except Exception as e:
        color_logger.error(f"Error: {str(e)}", exc_info=True)
