from django.urls import path
from . import views

app_name = 'ldapauth'

urlpatterns = [
    # LDAP配置相关 - 使用单个视图函数处理GET和POST
    path('config/', views.ldap_config, name='ldap_config'),
    path('test-connection/', views.test_ldap_connection, name='test_ldap_connection'),
    
    # 安全配置相关 - 使用单个视图函数处理GET和POST
    path('security/config/', views.security_config, name='security_config'),
]