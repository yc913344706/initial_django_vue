from django.db import models
from lib.model_tools import BaseModel

class AuditLog(BaseModel):
    """操作审计日志"""
    ACTION_CHOICES = (
        ('CREATE', '创建'),
        ('UPDATE', '更新'),
        ('DELETE', '删除')
    )

    operator_username = models.CharField(max_length=100, verbose_name='操作人')
    model_name = models.CharField(max_length=100, verbose_name='模型名称')
    record_id = models.CharField(max_length=100, verbose_name='记录ID')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    detail = models.JSONField(verbose_name='操作详情')
    ip_address = models.GenericIPAddressField(null=True, verbose_name='IP地址')

    class Meta:
        db_table = 'audit_log'
        verbose_name = '审计日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']