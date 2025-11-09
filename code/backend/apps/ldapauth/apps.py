from django.apps import AppConfig


class LdapauthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ldapauth'
    verbose_name = 'LDAP认证管理'
