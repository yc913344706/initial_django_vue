from apps.user.models import User, UserGroup

def format_user_data(user: User):
    """格式化用户数据"""
    return {
        'uuid': user.uuid,
        'username': user.username,
        'nickname': user.nickname,
        'phone': user.phone,
        'email': user.email,
        'is_active': user.is_active,
        'roles': [{'uuid': role.uuid, 'name': role.name} for role in user.roles.all()],
        'permissions': [{'uuid': permission.uuid, 'name': permission.name} for permission in user.permissions.all()]
    }

def format_user_group_data(user_group: UserGroup):
    """格式化用户组数据"""
    return {
        'uuid': user_group.uuid,
        'name': user_group.name,
        'description': user_group.description,
        'users': [{'uuid': user.uuid, 'username': user.username} for user in user_group.users.all()],
        'roles': [{'uuid': role.uuid, 'name': role.name} for role in user_group.roles.all()],
        'permissions': [{'uuid': permission.uuid, 'name': permission.name} for permission in user_group.permissions.all()]
    }
