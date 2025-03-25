from apps.user.utils import format_user_data
from apps.user.models import User, UserGroup
from .models import Permission, Role
from lib.log import color_logger
from lib.json_tools import merge_jsons
from lib.time_tools import utc_obj_to_time_zone_str

def format_permission_data(permission: Permission):
    """格式化权限数据"""
    return {
        'uuid': permission.uuid,
        'created_time': utc_obj_to_time_zone_str(permission.create_time),
        'updated_time': utc_obj_to_time_zone_str(permission.update_time),

        'name': permission.name,
        'code': permission.code,
        'permission_json': permission.permission_json,
        'description': permission.description,

        'roles': [{'uuid': role.uuid, 'name': role.name, 'description': role.description} for role in permission.role_set.all()],
        'users': [{'uuid': user.uuid, 'username': user.username, 'nickname': user.nickname, 'is_active': user.is_active} for user in permission.user_set.all()],
        'groups': [{'uuid': group.uuid, 'name': group.name, 'description': group.description} for group in permission.usergroup_set.all()]
    }

def format_role_data(role: Role):
    """格式化角色数据"""
    return {
        'uuid': role.uuid,
        'created_time': utc_obj_to_time_zone_str(role.create_time),
        'updated_time': utc_obj_to_time_zone_str(role.update_time),

        'name': role.name,
        'code': role.code,
        'description': role.description,

        'permissions': [{'uuid': permission.uuid, 'name': permission.name, 'description': permission.description} for permission in role.permissions.all()],
        'users': [{'uuid': user.uuid, 'username': user.username, 'nickname': user.nickname, 'is_active': user.is_active} for user in role.user_set.all()],
        'groups': [{'uuid': group.uuid, 'name': group.name, 'description': group.description} for group in role.usergroup_set.all()]
    }

def get_user_perm_json_all(user_uuid):
    """获取所有用户权限组成的json
    
    包括：
    - 授予给用户的权限
    - 授予给用户的角色包含的权限
    - 用户所在用户组的权限
    - 用户所在用户组的角色包含的权限
    - 用户所在用户组的所有父级用户组的权限
    - 用户所在用户组的所有父级用户组的角色包含的权限
    """
    try:
        # color_logger.debug(f"获取用户权限JSON: {user_uuid}")
        user = User.objects.get(uuid=user_uuid)
        assert user, '用户不存在'
        
        # 1. 获取用户直接拥有的权限JSON
        # color_logger.debug(f"获取用户直接拥有的权限JSON: {user.permissions.all()}")
        user_permission_jsons = [p.permission_json for p in user.permissions.all()]
        
        # 2. 获取用户角色包含的权限JSON
        # color_logger.debug(f"获取用户角色包含的权限JSON: {user.roles.all()}")
        role_permission_jsons = []
        for role in user.roles.all():
            role_permission_jsons.extend([p.permission_json for p in role.permissions.all()])
            
        # 3. 获取用户所在用户组的权限JSON
        # color_logger.debug(f"获取用户所在用户组的权限JSON: {UserGroup.objects.filter(users=user)}")
        group_permission_jsons = []
        user_direct_groups = UserGroup.objects.filter(users=user)
        # color_logger.debug(f"获取用户直接用户组: {user_direct_groups}")

        all_groups = list(user_direct_groups)
        for group in user_direct_groups:
            all_groups.extend(group.get_type_all_parent_type())
        # color_logger.debug(f"获取用户所有用户组: {all_groups}")
        
        for group in all_groups:
            # 用户组直接拥有的权限
            # color_logger.debug(f"获取用户组直接拥有的权限JSON: {group.permissions.all()}")
            group_permission_jsons.extend([p.permission_json for p in group.permissions.all()])
            # 用户组角色包含的权限
            for role in group.roles.all():
                # color_logger.debug(f"获取用户组角色包含的权限JSON: {role.permissions.all()}")
                group_permission_jsons.extend([p.permission_json for p in role.permissions.all()])
        
        # 合并所有权限JSON
        # color_logger.debug(f"合并所有权限JSON: {user_permission_jsons + role_permission_jsons + group_permission_jsons}")
        all_permission_jsons = user_permission_jsons + role_permission_jsons + group_permission_jsons
        merged_permission_json = merge_jsons(all_permission_jsons)
        # color_logger.debug(f"合并后的权限JSON: {merged_permission_json}")
        
        return merged_permission_json
        
    except User.DoesNotExist:
        color_logger.error(f"用户不存在: {user_uuid}")
        return {}
    except Exception as e:
        color_logger.error(f"获取用户权限JSON失败: {e}")
        return {}
