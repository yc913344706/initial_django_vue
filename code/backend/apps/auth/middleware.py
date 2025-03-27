import re
from apps.auth.token_utils import TokenManager
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
            
            # 如果是公开路径，直接放行
            current_path_prefix = current_path.split('?')[0]
            if current_path_prefix in config_data.get('MIDDLEWARE_WHITE_LIST', {}) and \
                current_method in config_data.get('MIDDLEWARE_WHITE_LIST', {}).get(current_path, []):
                color_logger.debug(f'白名单，跳过中间件校验token：{current_path}, {current_method}')
                return None
            
            color_logger.debug(f'开始中间件校验：{current_path}, {current_method}')


            try:
                # 获取token
                access_token = get_authorization_token(request)
                if (access_token is None) or (access_token in ['', 'undefined', 'null']):
                    return pub_error_response(99999, msg='未登录')
                    
                # 验证token
                token_manager = TokenManager()
                payload = token_manager.verify_token(access_token)
                if not payload:
                    return pub_error_response(99998, msg='登录已过期')
                
                user_name = payload.get('username')
                if not user_name:
                    return pub_error_response(99995, msg='payload中没有用户名')
                color_logger.debug(f'中间件校验token成功：{current_path}, {current_method}')
                
                check_res = check_user_api_permission(
                    user_name, {current_path_prefix: current_method.upper()}, is_user_name=True)
                if not check_res:
                    color_logger.debug(f'没有权限：{user_name}, {current_path}, {current_method}')
                    return pub_error_response(99994, msg=f'没有接口权限: {current_path_prefix}: {current_method}')
                
                color_logger.debug(f'中间件校验权限成功：{current_path}, {current_method}')
                
                return None
            except Exception as e:
                return pub_error_response(99997, msg=f"检查登录状态失败: {e.args}")


        except Exception as e:
            color_logger.error(f'中间件校验token错误: {str(e)}')
            return pub_error_response(99996, msg=f"中间件错误: {e.args}")
        
