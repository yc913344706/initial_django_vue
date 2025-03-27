from django.db import models
from lib.model_tools import BaseModel

class Permission(BaseModel):
    """权限模型"""
    name = models.CharField(max_length=100, verbose_name='权限名称')
    code = models.CharField(max_length=100, unique=True, verbose_name='权限代码')
    permission_json = models.JSONField(verbose_name='权限JSON')
    description = models.TextField(blank=True, null=True, verbose_name='描述')

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Role(BaseModel):
    """角色模型"""
    name = models.CharField(max_length=100, verbose_name='角色名称')
    code = models.CharField(max_length=100, unique=True, verbose_name='角色代码')
    permissions = models.ManyToManyField(Permission, verbose_name='权限列表')
    description = models.TextField(blank=True, null=True, verbose_name='描述')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
