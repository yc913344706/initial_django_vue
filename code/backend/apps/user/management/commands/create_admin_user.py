from django.core.management.base import BaseCommand
from apps.user.models import User, UserGroup
from apps.perm.models import Permission
from django.contrib.auth.hashers import make_password
from lib.log import color_logger

from backend.settings import BASE_DIR
import os
import json
PERM_JSON_DIR = os.path.join(BASE_DIR, 'etc', 'perm_jsons')

def get_permissions_from_json(json_file_path):
    res = {}
    with open(json_file_path, 'r') as file:
        res = json.load(file)
    
    return res

class Command(BaseCommand):
    help = 'Create admin user if not exists'

    def handle(self, *args, **options):
        admin_username = 'admin'
        admin_password = 'Admin@123'
        
        # Check if admin user already exists
        admin_user = User.objects.filter(username=admin_username).first()
        
        if admin_user:
            self.stdout.write(
                self.style.WARNING(f'Admin user "{admin_username}" already exists')
            )
        else:
            # 使用Django的密码哈希创建用户
            admin_user = User.objects.create(
                username=admin_username,
                email='admin@example.com',
                nickname='Admin',
                phone='12345678901',
                is_active=True
            )
            admin_user.set_password(admin_password)  # 使用Django的密码哈希
            admin_user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user "{admin_username}" with password "Admin@123"'
                )
            )
        
        system_admin_group = UserGroup.objects.filter(code='system_admin_group').first()
        if system_admin_group is None:
            system_admin_group = UserGroup.objects.create(
                name='【系统模块】管理员组',
                code='system_admin_group',
                description='初始化创建系统管理员组',
            )
            system_admin_group.users.add(admin_user)
            color_logger.info(f'创建系统管理员组成功')

        for perm in [
            (
                "everyone_base_perm", 
                "【不用授权】所有登录用户拥有的默认权限", 
                '此权限不用授予任何人。权限代码为"everyone_base_perm"，默认会给所有登录用户都加上。',
                {
                    "backend": {
                        "api": {
                            "/api/v1/auth/get-async-routes/": ["GET"],
                            "/api/v1/user/change-password/": ["POST"]
                        }
                    }
                }
            ),
            (
                "system_admin", 
                "【系统模块】管理员", 
                '初始化创建系统管理员权限',
                get_permissions_from_json(os.path.join(PERM_JSON_DIR, 'system_admin.json'))
            ),
            (
                "system_reader",
                "【系统模块】查看权限",
                "初始化创建系统查看权限",
                get_permissions_from_json(os.path.join(PERM_JSON_DIR, 'system_reader.json'))
            ),
            (
                "system_audit",
                "【系统模块】审计日志查看权限",
                "初始化创建系统审计日志查看权限",
                get_permissions_from_json(os.path.join(PERM_JSON_DIR, 'system_audit.json'))
            )
        ]:
            perm_obj = Permission.objects.filter(code=perm[0]).first()
            if perm_obj is None:
                # 标记核心权限为系统权限
                is_system_perm = perm[0] in ['everyone_base_perm', 'system_admin', 'system_reader', 'system_audit']
                perm_obj = Permission.objects.create(
                    code=perm[0],
                    name=perm[1],
                    description=perm[2],
                    permission_json=perm[3],
                    is_system=is_system_perm
                )
            if perm[0] in ['system_admin', 'system_audit']:
                system_admin_group.permissions.add(perm_obj)

        color_logger.info(f'Admin user check completed. User exists: {admin_user is not None}')