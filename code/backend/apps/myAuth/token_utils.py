import time
import jwt
import uuid
from backend.settings import config_data
from apps.user.models import User
from lib.log import color_logger

from lib.redis_tool import delete_redis_value, get_redis_value, set_redis_value
import requests


class TokenManager:
    def _generate_token(self, user_id, username, session_id, expire_time):
        """生成JWT token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'session_id': session_id,
            'exp': int(time.time()) + expire_time,
            'iat': int(time.time())
        }
        try:
            return jwt.encode(
                payload,
                config_data.get('AUTH', {}).get('JWT_SECRET'),
                algorithm=config_data.get('AUTH', {}).get('JWT_ALGORITHM')
            )
        except Exception as e:
            color_logger.error(f"_generate_token error: {e}")
            return None

    def is_jwt_token(self, token):
        """检查是否为JWT格式的token"""
        try:
            # JWT格式是 header.payload.signature
            parts = token.split('.')
            return len(parts) == 3
        except:
            return False

    def verify_oauth2_token_via_hydra(self, token):
        """通过Hydra验证OAuth2 token"""
        try:
            # 从配置获取Hydra管理凭据，如果未配置则不使用认证
            from backend.settings import config_data
            hydra_client_id = config_data.get('HYDRA', {}).get('CLIENT_ID', 'admin')
            hydra_client_secret = config_data.get('HYDRA', {}).get('CLIENT_SECRET', '')

            auth = None
            if hydra_client_id and hydra_client_secret:
                auth = (hydra_client_id, hydra_client_secret)

            # 调用Hydra的introspection端点验证token
            response = requests.post(
                "http://hydra:4445/admin/oauth2/introspect",
                data={"token": token},
                auth=auth  # 可选的认证，取决于Hydra配置
            )
            if response.status_code == 200:
                token_info = response.json()
                if token_info.get("active"):
                    # Token有效，返回用户信息
                    return {
                        'username': token_info.get('sub'),  # OAuth2中的subject通常对应username
                        'scope': token_info.get('scope', '').split(),
                        'client_id': token_info.get('client_id'),
                        'exp': token_info.get('exp'),
                        'iat': token_info.get('iat')
                    }
        except Exception as e:
            color_logger.error(f"Error verifying OAuth2 token with Hydra: {e}")
        return None

    def generate_tokens(self, user_obj: User):
        """生成access token和refresh token"""
        # 生成唯一的会话ID
        session_id = str(uuid.uuid4())
        
        access_token = self._generate_token(
            str(user_obj.uuid),
            user_obj.username,
            session_id,
            config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
        )
        refresh_token = self._generate_token(
            str(user_obj.uuid),
            user_obj.username,
            session_id,
            config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')
        )

        # 存储到Redis - 使用用户名和会话ID的组合键
        set_redis_value(
            redis_db_name='AUTH',
            redis_key_name=f"access_token:{user_obj.username}:{session_id}",
            redis_key_value=access_token,
            set_expire=config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
        )
        set_redis_value(
            redis_db_name='AUTH',
            redis_key_name=f"refresh_token:{user_obj.username}:{session_id}",
            redis_key_value=refresh_token,
            set_expire=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')
        )
        
        # 将会话ID添加到用户的活跃会话列表
        self._add_user_session(user_obj.username, session_id)

        return access_token, refresh_token, session_id

    def _add_user_session(self, username, session_id):
        """将用户会话添加到活跃会话列表"""
        try:
            # 获取当前活跃会话列表
            sessions_key = f"user_sessions:{username}"
            current_sessions = get_redis_value(redis_db_name='AUTH', redis_key_name=sessions_key)
            if current_sessions:
                # 如果已有会话列表，添加新会话ID
                sessions_list = current_sessions.split(',')
                if session_id not in sessions_list:
                    sessions_list.append(session_id)
                    new_sessions = ','.join(sessions_list)
                else:
                    new_sessions = current_sessions
            else:
                # 如果没有会话列表，创建一个包含新会话ID的列表
                new_sessions = session_id
            
            # 存储更新后的会话列表，设置为与refresh token相同的过期时间
            set_redis_value(
                redis_db_name='AUTH',
                redis_key_name=sessions_key,
                redis_key_value=new_sessions,
                set_expire=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')
            )
        except Exception as e:
            color_logger.error(f"_add_user_session error: {e}")

    def verify_token(self, token):
        """验证token - 支持内部JWT和外部OAuth2 token"""
        try:
            color_logger.debug(f"verify_token")
            # 首先检查是否为内部JWT token
            if self.is_jwt_token(token):
                color_logger.debug(f"verify_token - is jwt token")
                # 这是内部JWT token，使用原有逻辑验证
                payload = jwt.decode(
                    token,
                    config_data.get('AUTH', {}).get('JWT_SECRET'),
                    algorithms=[config_data.get('AUTH', {}).get('JWT_ALGORITHM')]
                )

                # 检查Redis中是否存在该特定会话的token
                stored_token = get_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"access_token:{payload['username']}:{payload['session_id']}"
                )
                if not stored_token or stored_token != token:
                    return None

                return payload
            else:
                color_logger.debug(f"verify_token - is not jwt token")
                # 这可能是OAuth2 token，通过Hydra验证
                return self.verify_oauth2_token_via_hydra(token)
        except jwt.ExpiredSignatureError:
            color_logger.debug("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            color_logger.debug(f"Invalid JWT token: {e}")
            # 尝试作为OAuth2 token验证
            return self.verify_oauth2_token_via_hydra(token)
        except Exception as e:
            # color_logger.error(f"verify_token error: {e}")
            # 如果JWT验证失败，尝试OAuth2验证
            oauth2_result = self.verify_oauth2_token_via_hydra(token)
            if oauth2_result:
                return oauth2_result
            return None

    def refresh_access_token(self, refresh_token):
        """使用refresh token刷新access token"""
        try:
            # 检查是否为内部JWT refresh token
            if self.is_jwt_token(refresh_token):
                # 这是内部JWT refresh token，使用原有逻辑
                color_logger.debug(f"开始refresh_access_token: {refresh_token}")
                payload = jwt.decode(
                    refresh_token,
                    config_data.get('AUTH', {}).get('JWT_SECRET'),
                    algorithms=[config_data.get('AUTH', {}).get('JWT_ALGORITHM')]
                )
                color_logger.debug(f"refresh_access_token payload: {payload}")

                # 验证refresh token - 检查特定会话的refresh token
                stored_refresh = get_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"refresh_token:{payload['username']}:{payload['session_id']}"
                )
                if not stored_refresh or stored_refresh != refresh_token:
                    color_logger.error(f"refresh_access_token refresh_token校验失败: 与redis中不一致")
                    return None, None

                # 生成新的access token，保持相同的会话ID
                access_token = self._generate_token(
                    payload['user_id'],
                    payload['username'],
                    payload['session_id'],  # 保持相同的会话ID
                    config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
                )
                color_logger.debug(f"refresh_access_token 生成access_token")

                # 更新Redis中特定会话的access token
                set_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"access_token:{payload['username']}:{payload['session_id']}",
                    redis_key_value=access_token,
                    set_expire=config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
                )
                color_logger.debug(f"refresh_access_token 更新Redis")

                return access_token, payload['username']
            else:
                # 这可能是OAuth2 refresh token，需要通过Hydra处理
                # 但通常OAuth2的刷新流程由客户端直接与Hydra通信
                # 我们这里返回错误，建议客户端直接与Hydra交互
                color_logger.warning("OAuth2 refresh token should be handled directly with Hydra")
                return None, None
        except jwt.ExpiredSignatureError:
            color_logger.debug("JWT refresh token expired")
            return None, None
        except jwt.InvalidTokenError as e:
            color_logger.debug(f"Invalid JWT refresh token: {e}")
            # 如果是无效的JWT token，仍然返回错误
            return None, None
        except Exception as e:
            color_logger.error(f"refresh_access_token error: {e}")
            return None, None

    def invalidate_tokens(self, username, session_id=None):
        """使指定用户的token失效"""
        try:
            # 如果指定了session_id，则只使特定会话失效
            if session_id:
                delete_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"access_token:{username}:{session_id}"
                )
                delete_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"refresh_token:{username}:{session_id}"
                )
                # 从活跃会话列表中移除该会话
                self._remove_user_session(username, session_id)
            else:
                # 如果没有指定session_id，则使该用户的所有会话失效
                sessions_key = f"user_sessions:{username}"
                current_sessions = get_redis_value(redis_db_name='AUTH', redis_key_name=sessions_key)
                if current_sessions:
                    sessions_list = current_sessions.split(',')
                    for session in sessions_list:
                        delete_redis_value(
                            redis_db_name='AUTH',
                            redis_key_name=f"access_token:{username}:{session}"
                        )
                        delete_redis_value(
                            redis_db_name='AUTH',
                            redis_key_name=f"refresh_token:{username}:{session}"
                        )
                
                # 删除会话列表
                delete_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=sessions_key
                )
        except Exception as e:
            color_logger.error(f"invalidate_tokens error: {e}")
            return None

    def _remove_user_session(self, username, session_id):
        """从活跃会话列表中移除会话"""
        try:
            sessions_key = f"user_sessions:{username}"
            current_sessions = get_redis_value(redis_db_name='AUTH', redis_key_name=sessions_key)
            if current_sessions:
                sessions_list = current_sessions.split(',')
                if session_id in sessions_list:
                    sessions_list.remove(session_id)
                    if sessions_list:
                        new_sessions = ','.join(sessions_list)
                        # 更新会话列表
                        set_redis_value(
                            redis_db_name='AUTH',
                            redis_key_name=sessions_key,
                            redis_key_value=new_sessions,
                            set_expire=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')
                        )
                    else:
                        # 如果没有活跃会话了，删除会话列表
                        delete_redis_value(
                            redis_db_name='AUTH',
                            redis_key_name=sessions_key
                        )
        except Exception as e:
            color_logger.error(f"_remove_user_session error: {e}")

    def get_username_from_access_token(self, token):
        """从access token中获取username"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            return payload.get('username')
        except Exception as e:
            color_logger.error(f"get_username_from_access_token error: {e}")
            return None

    def get_all_user_sessions(self, username):
        """获取用户的所有活跃会话"""
        try:
            sessions_key = f"user_sessions:{username}"
            current_sessions = get_redis_value(redis_db_name='AUTH', redis_key_name=sessions_key)
            if current_sessions:
                return current_sessions.split(',')
            return []
        except Exception as e:
            color_logger.error(f"get_all_user_sessions error: {e}")
            return []

    def invalidate_all_user_sessions_except_current(self, username, current_session_id):
        """使用户除当前会话外的所有会话失效"""
        try:
            all_sessions = self.get_all_user_sessions(username)
            for session in all_sessions:
                if session != current_session_id:
                    # 删除该会话的tokens
                    delete_redis_value(
                        redis_db_name='AUTH',
                        redis_key_name=f"access_token:{username}:{session}"
                    )
                    delete_redis_value(
                        redis_db_name='AUTH',
                        redis_key_name=f"refresh_token:{username}:{session}"
                    )
                    # 从会话列表中移除该会话
                    self._remove_user_session(username, session)
        except Exception as e:
            color_logger.error(f"invalidate_all_user_sessions_except_current error: {e}")