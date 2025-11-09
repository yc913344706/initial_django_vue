from django.db import models
from lib.model_tools import BaseModel


class LdapConfig(BaseModel):
    """LDAP配置模型"""
    LDAP_TYPE_CHOICES = [
        ('openldap', 'OpenLDAP'),
        ('ad', 'Active Directory'),
    ]
    
    server_host = models.CharField(max_length=255, verbose_name='服务器主机')
    server_port = models.IntegerField(default=389, verbose_name='服务器端口')
    base_dn = models.CharField(max_length=255, verbose_name='基础DN')
    admin_dn = models.CharField(max_length=255, verbose_name='管理员DN')
    admin_password = models.CharField(max_length=255, verbose_name='管理员密码')
    user_search_filter = models.CharField(max_length=255, verbose_name='用户搜索过滤器', default='(objectClass=user)')
    username_attr = models.CharField(max_length=100, verbose_name='用户名属性', default='sAMAccountName')
    display_name_attr = models.CharField(max_length=100, verbose_name='显示名属性', default='displayName')
    email_attr = models.CharField(max_length=100, verbose_name='邮箱属性', default='mail')
    ldap_type = models.CharField(max_length=20, choices=LDAP_TYPE_CHOICES, default='ad', verbose_name='LDAP类型')
    enabled = models.BooleanField(default=False, verbose_name='是否启用')
    
    class Meta:
        verbose_name = 'LDAP配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"LDAP配置 - {self.server_host}"


class SecurityConfig(BaseModel):
    """安全配置模型"""
    max_login_attempts = models.IntegerField(default=5, verbose_name='最大登录尝试次数')
    lockout_duration = models.IntegerField(default=60, verbose_name='锁定持续时间(分钟)')

    class Meta:
        verbose_name = '安全配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"安全配置 - 最大尝试次数: {self.max_login_attempts}"
