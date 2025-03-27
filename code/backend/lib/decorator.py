# 定义一个简单的装饰器
from lib.log import color_logger


def try_except_decorator(prompt=""):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                color_logger.error("{}。错误：{}".format(prompt, e.args))
        return wrapper
    return decorator



def decorator(func):
    def wrapper():
        print(f"Decorator")
        return func()

    return wrapper



