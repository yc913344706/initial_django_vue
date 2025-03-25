from apps.user.models import User, UserGroup
from lib.time_tools import utc_obj_to_time_zone_str

def format_user_data(user: User):
    """格式化用户数据"""
    return {
        'uuid': user.uuid,
        'created_time': utc_obj_to_time_zone_str(user.create_time),
        'updated_time': utc_obj_to_time_zone_str(user.update_time),

        'username': user.username,
        'nickname': user.nickname,
        'phone': user.phone,
        'email': user.email,
        'is_active': user.is_active,

        'roles': [{'uuid': role.uuid, 'name': role.name, 'description': role.description} for role in user.roles.all()],
        'permissions': [{'uuid': permission.uuid, 'name': permission.name, 'description': permission.description} for permission in user.permissions.all()],
        'groups': [{'uuid': group.uuid, 'name': group.name, 'description': group.description} for group in user.usergroup_set.all()]
    }

def format_user_group_data(user_group: UserGroup):
    """格式化用户组数据"""
    return {
        'uuid': user_group.uuid,
        'created_time': utc_obj_to_time_zone_str(user_group.create_time),
        'updated_time': utc_obj_to_time_zone_str(user_group.update_time),

        'name': user_group.name,
        'description': user_group.description,
        'parent': user_group.parent.uuid if user_group.parent else None,

        'users': [{'uuid': user.uuid, 'username': user.username, 'nickname': user.nickname, 'is_active': user.is_active} for user in user_group.users.all()],
        'roles': [{'uuid': role.uuid, 'name': role.name, 'description': role.description} for role in user_group.roles.all()],
        'permissions': [{'uuid': permission.uuid, 'name': permission.name, 'description': permission.description} for permission in user_group.permissions.all()]
    }
