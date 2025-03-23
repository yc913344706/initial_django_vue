from django.db import models
from lib.model_tools import BaseModel

# Create your models here.


class User(BaseModel):
    """用户模型"""
    username = models.CharField(max_length=100, unique=True, verbose_name='用户名')
    nickname = models.CharField(max_length=100, verbose_name='昵称')
    avatar_url = models.CharField(max_length=255, verbose_name='头像url')
    password = models.CharField(max_length=128, verbose_name='密码')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    phone = models.CharField(max_length=11, verbose_name='手机号')
    status = models.CharField(max_length=10, verbose_name='状态')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
