import re
from apps.myAuth.token_utils import TokenManager
from apps.perm.utils import check_user_api_permission
from lib.request_tool import get_authorization_token, pub_error_response, set_current_request
from backend.settings import config_data
from lib.log import color_logger


class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        """处理请求"""
        try:
            # 获取当前请求路径
            current_path = request.path
            current_method = request.method
            
            # 如果开发环境配置了不需要登录验证，直接放行
            if not config_data.get('NEED_LOGIN', False):
                color_logger.debug('process_request: 不需要校验token')
                return None
            
            # 如果是公开路径，直接放行
            current_path_prefix = current_path.split('?')[0]
            if current_path_prefix in config_data.get('MIDDLEWARE_WHITE_LIST', []):
                color_logger.debug(f'白名单，跳过中间件校验token：{current_path}')
                return None

            # 处理Django admin相关路径
            if current_path.startswith('/admin/'):
                color_logger.debug(f'admin路径，跳过中间件校验token：{current_path}')
                return None
            
            color_logger.debug(f'开始中间件校验token：{current_path}, {request.method}')

            # 调用token检查方法
            try:
                # 获取token
                access_token = get_authorization_token(request)
                if (access_token is None) or (access_token in ['', 'undefined', 'null']):
                    return pub_error_response(99999, msg='未登录')
                    
                # 验证token
                token_manager = TokenManager()
                payload = token_manager.verify_token(access_token)
                if not payload:
                    return pub_error_response(99999, msg='access_token校验失败')
                
                user_name = payload.get('username')
                if not user_name:
                    return pub_error_response(99999, msg='payload中没有用户名')
                color_logger.debug(f'中间件校验token成功：{current_path}, {current_method}')
                
                check_res = check_user_api_permission(
                    user_name, {current_path_prefix: current_method.upper()}, is_user_name=True)
                if not check_res:
                    color_logger.debug(f'没有权限：{user_name}, {current_path}, {current_method}')
                    return pub_error_response(99987, msg=f'没有接口权限: {current_path_prefix}: {current_method}')
                
                color_logger.debug(f'中间件校验权限成功：{current_path}, {current_method}')

                # 将用户名和用户类型设置到request中
                request.user_name = user_name

                return None
            except Exception as e:
                return pub_error_response(99999, msg=f"检查登录状态失败: {e.args}")

        except Exception as e:
            color_logger.error(f'中间件process_request错误: {str(e)}')
            return pub_error_response(99989, msg=f"中间件错误: {e.args}")
        
