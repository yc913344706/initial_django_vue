from django.core.management.base import BaseCommand
from apps.user.models import User, UserGroup
from apps.perm.models import Permission
from lib.password_tools import aes
from lib.log import color_logger


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
            # Encrypt the password using the AES encryption used by the application
            encrypted_password = aes.encrypt(admin_password)
            
            # Create the admin user
            admin_user = User.objects.create(
                username=admin_username,
                password=encrypted_password,
                email='admin@example.com',
                nickname='Admin',
                phone='12345678901',
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user "{admin_username}" with password "Admin@123"'
                )
            )
        
        admin_group = UserGroup.objects.filter(code='system_admin_group').first()
        if admin_group is None:
            admin_group = UserGroup.objects.create(
                name='系统管理员组',
                code='system_admin_group',
                description='系统管理员组',
            )
            admin_group.users.add(admin_user)
            color_logger.info(f'创建系统管理员组成功')

        for perm in [
            (
                "everyone_base_perm", 
                "【不用授权】所有登录用户拥有的默认权限", 
                '此权限不用授予任何人。权限代码为"everyone_base_perm"，默认会给所有登录用户都加上。',
                {
                    "backend": {
                        "api": {
                            "/api/v1/auth/get-async-routes/": [
                                "GET"
                            ]
                        }
                    }
                }
            ),
            (
                "system_admin", 
                "【系统模块】管理员", 
                '初始化创建系统管理员权限',
                {
                    "backend": {
                        "api": {
                            "/api/v1/perm/role/": [
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE"
                            ],
                            "/api/v1/user/user/": [
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE"
                            ],
                            "/api/v1/perm/roles/": [
                                "GET",
                                "DELETE"
                            ],
                            "/api/v1/user/group/": [
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE"
                            ],
                            "/api/v1/user/users/": [
                                "GET",
                                "DELETE"
                            ],
                            "/api/v1/user/groups/": [
                                "GET",
                                "DELETE"
                            ],
                            "/api/v1/perm/permission/": [
                                "GET",
                                "POST",
                                "PUT",
                                "DELETE"
                            ],
                            "/api/v1/perm/permissions/": [
                                "GET",
                                "DELETE"
                            ],
                            "/api/v1/perm/user-permission-json/": [
                                "GET"
                            ]
                        }
                    },
                    "frontend": {
                        "routes": [
                            "system.user",
                            "system.user.detail",
                            "system.permission",
                            "system.permission.detail",
                            "system.role",
                            "system.role.detail",
                            "system.group",
                            "system.group.detail"
                        ],
                        "resources": [
                            "system.userList:read",
                            "system.userList:create",
                            "system.userList:delete",
                            "system.user:read",
                            "system.user:create",
                            "system.user:update",
                            "system.user:delete",
                            "system.permissionList:read",
                            "system.permissionList:create",
                            "system.permissionList:delete",
                            "system.permission:read",
                            "system.permission:create",
                            "system.permission:update",
                            "system.permission:delete",
                            "system.roleList:read",
                            "system.roleList:create",
                            "system.roleList:delete",
                            "system.role:read",
                            "system.role:create",
                            "system.role:update",
                            "system.role:delete",
                            "system.groupList:read",
                            "system.groupList:create",
                            "system.groupList:delete",
                            "system.group:read",
                            "system.group:create",
                            "system.group:update",
                            "system.group:delete"
                        ]
                    }
                }
            ),
            (
                "system_reader",
                "【系统模块】查看权限",
                "初始化创建系统查看权限",
                {
                    "backend": {
                        "api": {
                            "/api/v1/perm/role/": [
                                "GET"
                            ],
                            "/api/v1/user/user/": [
                                "GET"
                            ],
                            "/api/v1/perm/roles/": [
                                "GET"
                            ],
                            "/api/v1/user/group/": [
                                "GET"
                            ],
                            "/api/v1/user/users/": [
                                "GET"
                            ],
                            "/api/v1/user/groups/": [
                                "GET"
                            ],
                            "/api/v1/perm/permission/": [
                                "GET"
                            ],
                            "/api/v1/perm/permissions/": [
                                "GET"
                            ],
                            "/api/v1/perm/user-permission-json/": [
                                "GET"
                            ]
                        }
                    },
                    "frontend": {
                        "routes": [
                            "system.user",
                            "system.user.detail",
                            "system.permission",
                            "system.permission.detail",
                            "system.role",
                            "system.role.detail",
                            "system.group",
                            "system.group.detail"
                        ],
                        "resources": [
                            "system.userList:read",
                            "system.user:read",
                            "system.permissionList:read",
                            "system.permission:read",
                            "system.roleList:read",
                            "system.role:read",
                            "system.groupList:read",
                            "system.group:read"
                        ]
                    }
                }
            ),
            (
                "system_audit",
                "【系统模块】审计日志查看权限",
                "初始化创建系统审计日志查看权限",
                {
                    "backend": {
                        "api": {
                            "/api/v1/audit/audit-logs/": [
                                "GET"
                            ]
                        }
                    },
                    "frontend": {
                        "routes": [
                            "system.audit"
                        ],
                        "resources": [
                            "system.auditList:read"
                        ]
                    }
                }
            )
        ]:
            perm_obj = Permission.objects.filter(code=perm[0]).first()
            if perm_obj is None:
                perm_obj = Permission.objects.create(
                    code=perm[0],
                    name=perm[1],
                    description=perm[2],
                    permission_json=perm[3]
                )
            if perm[0] in ['system_admin', 'system_audit']:
                admin_group.permissions.add(perm_obj)

        color_logger.info(f'Admin user check completed. User exists: {admin_user is not None}')