from typing import Tuple, List, Dict, Optional, Any
from lib.time_tools import utc_obj_to_time_zone_str
from apps.user.models import User, UserGroup


def format_user_data(user_data: Dict[str, Any], 
                     from_ldap: bool = False,
                     only_basic: bool = False
                     ) -> Dict[str, Any]:
    """统一用户数据格式
    
    Args:
        user_data: 用户数据字典
        from_ldap: 是否来自LDAP搜索结果
        
    Returns:
        统一格式的用户数据字典
    """
    if from_ldap:
        return {
            'username': user_data.get('sAMAccountName'),
            'display_name': user_data.get('displayName'),
            'nickname': user_data.get('displayName'),
            'email': user_data.get('mail'),
            # 'last_sync': None  # LDAP搜索结果没有同步时间
        }
    else:
        # 数据库模型对象转字典
        res = {
            'uuid': user_data.uuid,
            'username': user_data.username,
            # 'display_name': user_data.display_name,
            'nickname': user_data.nickname,
            'email': user_data.email,
            'is_active': user_data.is_active,
            # 'last_sync': utc_obj_to_time_zone_str(user_data.last_sync) if user_data.last_sync else None,
            
        }

        if not only_basic:
            from apps.perm.utils import format_role_data, format_permission_data
            res.update({
                'roles': [format_role_data(role, only_basic=True) for role in user_data.roles.all()],
                'permissions': [format_permission_data(permission, only_basic=True) for permission in user_data.permissions.all()],
                'groups': [format_user_group_data(group, only_basic=True) for group in user_data.usergroup_set.all()]
            })

        return res


def format_user_group_data(user_group: UserGroup, only_basic: bool = False):
    """格式化用户组数据"""
    res = {
        'uuid': user_group.uuid,
        'created_time': utc_obj_to_time_zone_str(user_group.create_time),
        'updated_time': utc_obj_to_time_zone_str(user_group.update_time),

        'name': user_group.name,
        'description': user_group.description,
        'parent': user_group.parent.uuid if user_group.parent else None,
    }

    if not only_basic:
        from apps.perm.utils import format_role_data, format_permission_data
        res.update({
            'users': [format_user_data(user, from_ldap=False, only_basic=True) for user in user_group.users.all()],
            'roles': [format_role_data(role, only_basic=True) for role in user_group.roles.all()],
            'permissions': [format_permission_data(permission, only_basic=True) for permission in user_group.permissions.all()]
        })
    
    return res

