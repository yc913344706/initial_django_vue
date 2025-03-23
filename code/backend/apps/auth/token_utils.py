import time
import jwt
from backend.settings import config_data
from lib.log import color_logger

HAS_REDIS = False
if HAS_REDIS:
    from lib.redis_tool import delete_redis_value, get_redis_value, set_redis_value

class TokenManager:
        
    def _generate_token(self, username, expire_time):
        """生成JWT token"""
        payload = {
            'username': username,
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
        
    def generate_tokens(self, username):
        """生成access token和refresh token"""
        access_token = self._generate_token(
            username,
            config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
        )
        refresh_token = self._generate_token(
            username,
            config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')
        )

        if HAS_REDIS:
            # 存储到Redis
            set_redis_value(
                redis_db_name='AUTH',
                redis_key_name=f"access_token:{username}",
                redis_key_value=access_token,
                set_expire=config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
            )
            set_redis_value(
                redis_db_name='AUTH',
                redis_key_name=f"refresh_token:{username}",
                redis_key_value=refresh_token,
                set_expire=config_data.get('AUTH', {}).get('REFRESH_TOKEN_EXPIRE')
            )
        
        return access_token, refresh_token
        
    def verify_token(self, token):
        """验证token"""
        try:
            payload = jwt.decode(
                token,
                config_data.get('AUTH', {}).get('JWT_SECRET'),
                algorithms=[config_data.get('AUTH', {}).get('JWT_ALGORITHM')]
            )
            
            # 检查Redis中是否存在
            if HAS_REDIS:
                stored_token = get_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"access_token:{payload['username']}"
                )
                if not stored_token or stored_token != token:
                    return None
                
            return payload
        except Exception as e:
            color_logger.error(f"verify_token error: {e}")
            return None
            
    def refresh_access_token(self, refresh_token):
        """使用refresh token刷新access token"""
        try:
            payload = jwt.decode(
                refresh_token,
                config_data.get('AUTH', {}).get('JWT_SECRET'),
                algorithms=[config_data.get('AUTH', {}).get('JWT_ALGORITHM')]
            )
            
            # 验证refresh token
            if HAS_REDIS:
                stored_refresh = get_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"refresh_token:{payload['username']}"
                )
                if not stored_refresh or stored_refresh != refresh_token:
                    return None
                
            # 生成新的access token
            access_token = self._generate_token(
                payload['username'],
                config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
            )
            
            if HAS_REDIS:
                # 更新Redis
                set_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"access_token:{payload['username']}",
                    redis_key_value=access_token,
                    set_expire=config_data.get('AUTH', {}).get('ACCESS_TOKEN_EXPIRE')
                )
            
            return access_token
        except Exception as e:
            color_logger.error(f"refresh_access_token error: {e}")
            return None

    def invalidate_tokens(self, username):
        """使指定用户的所有token失效"""
        try:
            if HAS_REDIS:
                delete_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"access_token:{username}"
                )
                delete_redis_value(
                    redis_db_name='AUTH',
                    redis_key_name=f"refresh_token:{username}"
                ) 
        except Exception as e:
            color_logger.error(f"invalidate_tokens error: {e}")
            return None
        
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
    
