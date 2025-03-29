from celery import shared_task
from lib.log import color_logger
from lib.redis_tool import get_redis_value, set_redis_value


@shared_task
def say_hello():
    try:
        color_logger.info("test redis")
        redis_key_name = 'initial_django_vue_demo_test'

        # 获取redis值
        redis_key_value = get_redis_value(
            redis_db_name='default',
            redis_key_name=redis_key_name,
        )
        if redis_key_value:
            color_logger.info(f"success get value from redis: {redis_key_value}")
        else:
            redis_key_value = 'test_value'
            color_logger.info("get value from redis is None, start set value to redis")

            # 设置redis值
            set_redis_value(
                redis_db_name='default',
                redis_key_name=redis_key_name,
                redis_key_value=redis_key_value,
                set_expire=None
            )
            color_logger.info(f"success set value to redis: {redis_key_value}")
    
    except Exception as e:
        color_logger.error(f"say_hello 失败: {str(e)}")
