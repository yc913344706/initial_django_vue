
def format_user_data(user):
    """格式化用户数据"""
    return {
        'uuid': user.uuid,
        'username': user.username,
        'nickname': user.nickname,
        'phone': user.phone,
        'email': user.email,
        'is_active': user.is_active,
    }

def format_user_group_data(user_group):
    """格式化用户组数据"""
    return {
        'uuid': user_group.uuid,
        'name': user_group.name,
    }
