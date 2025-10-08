# 确保在 Django 启动时加载 Celery 应用
from .celery import app as celery_app

__all__ = ('celery_app',)