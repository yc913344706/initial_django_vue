from apps.user.models import User, UserGroup
from .models import Permission, Role
from lib.log import color_logger
from lib.json_tools import merge_jsons
from lib.time_tools import utc_obj_to_time_zone_str
from backend.settings import config_data
from lib.redis_tool import get_redis_value, set_redis_value

def format_permission_data(permission: Permission, only_basic=False):
    """格式化权限数据"""
    res = {
        'uuid': permission.uuid,
        'created_time': utc_obj_to_time_zone_str(permission.create_time),
        'updated_time': utc_obj_to_time_zone_str(permission.update_time),

        'name': permission.name,
        'code': permission.code,
        'permission_json': permission.permission_json,
        'description': permission.description,
    }

    if not only_basic:
        from apps.user.utils import format_user_data, format_user_group_data
        res.update({
            'roles': [format_role_data(role, only_basic=True) for role in permission.role_set.all()],
            'users': [format_user_data(user, from_ldap=False, only_basic=True) for user in permission.user_set.all()],
            'groups': [format_user_group_data(group, only_basic=True) for group in permission.usergroup_set.all()]
        })
    return res

def format_role_data(role: Role, only_basic=False):
    """格式化角色数据"""
    res = {
        'uuid': role.uuid,
        'created_time': utc_obj_to_time_zone_str(role.create_time),
        'updated_time': utc_obj_to_time_zone_str(role.update_time),

        'name': role.name,
        'code': role.code,
        'description': role.description,
    }

    if not only_basic:
        from apps.user.utils import format_user_data, format_user_group_data
        res.update({
            'permissions': [format_permission_data(permission, only_basic=True) for permission in role.permissions.all()],
            'users': [format_user_data(user, from_ldap=False, only_basic=True) for user in role.user_set.all()],
            'groups': [format_user_group_data(group, only_basic=True) for group in role.usergroup_set.all()]
        })
    return res

def get_user_perm_json_all(user_uuid, is_user_name=False):
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
        redis_key = f"user_perm_json_all:{user_uuid}"
        
        user_perm_json_all = get_redis_value(
            redis_db_name='default',
            redis_key_name=redis_key
        )
        if user_perm_json_all:
            return user_perm_json_all

        # color_logger.debug(f"获取用户权限JSON: {user_uuid}")
        if is_user_name:
            user = User.objects.get(username=user_uuid)
        else:
            user = User.objects.get(uuid=user_uuid)
        assert user, '用户不存在'
        
        # 1. 获取用户直接拥有的权限JSON
        # color_logger.debug(f"获取用户直接拥有的权限JSON: {user.permissions.all()}")
        user_permission_jsons = [p.permission_json for p in user.permissions.all()]
        
        # 所有用户都拥有的权限
        everyone_base_perm = Permission.objects.filter(code='everyone_base_perm').first()
        if everyone_base_perm:
            user_permission_jsons.append(everyone_base_perm.permission_json)

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
        # color_logger.debug(f"({user_uuid})合并所有权限JSON: {user_permission_jsons + role_permission_jsons + group_permission_jsons}")
        all_permission_jsons = user_permission_jsons + role_permission_jsons + group_permission_jsons
        merged_permission_json = merge_jsons(all_permission_jsons)
        # color_logger.debug(f"({user_uuid})合并后的权限JSON: {merged_permission_json}")
        
        set_redis_value(
            redis_db_name='default',
            redis_key_name=redis_key,
            redis_key_value=merged_permission_json,
            set_expire=60
        )

        return merged_permission_json
        
    except User.DoesNotExist:
        color_logger.error(f"用户不存在: {user_uuid}")
        return {}
    except Exception as e:
        color_logger.error(f"获取用户权限JSON失败: {e}")
        return {}


def check_user_api_permission(user_uuid, check_permission_dict, is_user_name=False):
    """
    检查用户是否具有api权限

    check_permission_dict: {
        'api_path': ['GET', 'POST', 'PUT', 'DELETE'],
        'api_path2': 'GET'
    }
    """
    user_api_permission_in_server = get_user_perm_json_all(user_uuid, is_user_name)
    user_api_permission_in_server = user_api_permission_in_server.get('backend', {}).get('api', {})
    # color_logger.debug(f"用户api权限JSON: {user_api_permission_in_server}")

    for check_api, check_methods in check_permission_dict.items():
        if check_api not in user_api_permission_in_server:
            return False
        
        allow_methods = user_api_permission_in_server[check_api]
        if isinstance(check_methods, str):
            check_methods = [check_methods]
        if len(set(check_methods) - set(allow_methods)) > 0:
            return False

    return True

