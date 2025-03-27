from django.db import models
from lib.model_tools import BaseModel, BaseTypeTree
import uuid

# Create your models here.


class User(BaseModel):
    """用户模型"""
    username = models.CharField(max_length=100, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=128, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱', null=True, blank=True)
    nickname = models.CharField(max_length=100, verbose_name='昵称')
    # avatar_url = models.CharField(max_length=255, verbose_name='头像url', null=True, blank=True)
    phone = models.CharField(max_length=11, verbose_name='手机号', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    permissions = models.ManyToManyField('perm.Permission', verbose_name='权限列表')
    roles = models.ManyToManyField('perm.Role', verbose_name='角色列表')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class UserGroup(BaseTypeTree):
    """用户组模型"""
    code = models.CharField(default=uuid.uuid4, max_length=64, unique=True, verbose_name='类型编码')
    description = models.TextField(verbose_name='描述', null=True, blank=True)
    
    users = models.ManyToManyField('User', verbose_name='用户列表')
    permissions = models.ManyToManyField('perm.Permission', verbose_name='权限列表')
    roles = models.ManyToManyField('perm.Role', verbose_name='角色列表')

    class Meta:
        verbose_name = '用户组'
        verbose_name_plural = verbose_name

