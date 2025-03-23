
from apps.user.utils import format_user_data


def format_permission_data(permission):
    """格式化权限数据"""
    return {
        'uuid': permission.uuid,
        'name': permission.name,
        'code': permission.code,
        'permission_json': permission.permission_json,
        'description': permission.description,
    }

def format_role_data(role):
    """格式化角色数据"""
    return {
        'uuid': role.uuid,
        'name': role.name,
    }

def format_grant_data(grant):
    """格式化授权数据"""
    return {
        'uuid': grant.uuid,
        'user': format_user_data(grant.user),
        'role': format_role_data(grant.role),
    }