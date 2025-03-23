
def format_user_data(user):
    """格式化用户数据"""
    return {
        'uuid': user.uuid,
        'username': user.username,
        'nickname': user.nickname,
    }