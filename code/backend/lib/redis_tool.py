import json
import uuid
from django_redis import get_redis_connection
from lib.json_tools import DateTimeEncoder
from lib.log import color_logger
from celery import shared_task

def get_redis_value(redis_db_name, redis_key_name):
    redis_conn = get_redis_connection(redis_db_name)
    redis_data = redis_conn.get(redis_key_name)
    
    if redis_data:
        return json.loads(redis_data)
    
    return None

def get_redis_value_with_prefix(redis_db_name, redis_key_prefix):
    redis_conn = get_redis_connection(redis_db_name)
    redis_data = redis_conn.keys(redis_key_prefix)
    # color_logger.debug(f'redis_key_prefix: {redis_key_prefix}')
    # color_logger.debug(f'redis_data: {redis_data}')
    
    if redis_data:
        return {key.decode('utf-8') if isinstance(key, bytes) else key: json.loads(redis_conn.get(key)) for key in redis_data}
    
    return None
        

@shared_task
def set_redis_value(redis_db_name, redis_key_name, redis_key_value, set_expire=3600):
    """
    设置 Redis 键值
    :param redis_db_name: Redis 数据库名
    :param redis_key_name: 键名
    :param redis_key_value: 键值
    :param set_expire: 过期时间（秒），默认为 3600 秒，None 表示永不过期
    """
    redis_conn = get_redis_connection(redis_db_name)
    
    # 更新 Redis
    if set_expire is not None:
        # 设置带过期时间的键值
        redis_conn.set(
            redis_key_name,
            json.dumps(redis_key_value, cls=DateTimeEncoder),
            ex=set_expire
        )
    else:
        # 设置永不过期的键值
        redis_conn.set(
            redis_key_name,
            json.dumps(redis_key_value, cls=DateTimeEncoder)
        )


def delete_redis_value(redis_db_name, redis_key_name):
    redis_conn = get_redis_connection(redis_db_name)
    redis_conn.delete(redis_key_name)


def can_get_work_lock(redis_db_name, work_flag, lock_time=10, need_expire=False):
    redis_conn = get_redis_connection(redis_db_name)
    redis_key_name = f'work_lock_{work_flag}'
    if redis_conn.exists(redis_key_name):
        _key_expire = redis_conn.ttl(redis_key_name)
        color_logger.info(f'获取锁失败: {work_flag}, 剩余时间: {_key_expire}秒')
        if need_expire:
            return False, _key_expire
        else:
            return False
    else:
        color_logger.info(f'获取锁成功: {work_flag}')
        redis_conn.set(redis_key_name, uuid.uuid4().hex, lock_time)
        if need_expire:
            return True, 0
        else:
            return True


def release_work_lock(redis_db_name, work_flag):
    redis_conn = get_redis_connection(redis_db_name)
    color_logger.info(f'释放锁: {work_flag}')
    redis_key_name = f'work_lock_{work_flag}'
    redis_conn.delete(redis_key_name)
