from lib.password_tools import aes
from .utils import format_user_data, format_user_group_data
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import User, UserGroup
from apps.perm.models import Role, Permission
from lib.paginator_tool import pub_paging_tool
from lib.log import color_logger

# Create your views here.


def user_list(request):
    """用户列表"""

    try:
        body = pub_get_request_body(request)

        page = int(body.get('page', 1))
        page_size = int(body.get('page_size', 20))
        
        user_list = User.objects.all()
            
        # 分页查询
        has_next, next_page, page_list, all_num, result = pub_paging_tool(page, user_list, page_size)
        
        # 格式化返回数据
        result = [format_user_data(user) for user in result]
        
        return pub_success_response({
            'has_next': has_next,
            'next_page': next_page,
            'all_num': all_num,
            'data': result
        })
    except Exception as e:
        color_logger.error(f"获取用户列表失败: {e.args}")
        return pub_error_response(f"获取用户列表失败: {e.args}")


def user(request):
    """用户"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            user = User.objects.get(uuid=body['uuid'])
            return pub_success_response(format_user_data(user))
        elif request.method == 'POST':
            create_keys = ['username', 'nickname', 'phone', 'email', 'password']
            create_dict = {key: value for key, value in body.items() if key in create_keys}

            encrypted_password = aes.encrypt(create_dict['password'])
            create_dict['password'] = encrypted_password

            user = User.objects.create(**create_dict)
            return pub_success_response(format_user_data(user))
        elif request.method == 'PUT':
            uuid = body.get('uuid')
            assert uuid, 'uuid 不能为空'

            user_obj = User.objects.filter(uuid=uuid).first()
            assert user_obj, '更新的用户不存在'

            # 更新基本信息
            update_keys = ['username', 'nickname', 'phone', 'email', 'is_active']
            update_dict = {key: value for key, value in body.items() if key in update_keys}
            for key, value in update_dict.items():
                setattr(user_obj, key, value)
            user_obj.save()

            # 更新角色
            if 'roles' in body:
                user_obj.roles.clear()
                for role_uuid in body['roles']:
                    role = Role.objects.get(uuid=role_uuid)
                    user_obj.roles.add(role)

            # 更新权限
            if 'permissions' in body:
                user_obj.permissions.clear()
                for permission_uuid in body['permissions']:
                    permission = Permission.objects.get(uuid=permission_uuid)
                    user_obj.permissions.add(permission)

            color_logger.debug(f"更新用户: {user_obj.uuid} 成功")
            return pub_success_response(format_user_data(user_obj))
        elif request.method == 'DELETE':
            color_logger.debug(f"删除用户: {body['uuid']}")
            user = User.objects.filter(uuid=body['uuid']).first()
            assert user, '删除的用户不存在'
            user.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"用户操作失败: {e.args}")
        return pub_error_response(f"用户操作失败: {e.args}")


def user_group_list(request):
    """用户组列表"""

    try:
        body = pub_get_request_body(request)

        page = int(body.get('page', 1))
        page_size = int(body.get('page_size', 20))

        # 分页查询
        has_next, next_page, page_list, all_num, result = pub_paging_tool(page, UserGroup.objects.all(), page_size)

        # 格式化返回数据
        result = [format_user_group_data(user_group) for user_group in result]

        return pub_success_response({
            'has_next': has_next,
            'next_page': next_page,
            'all_num': all_num,
            'data': result
        })
    except Exception as e:
        color_logger.error(f"获取用户组列表失败: {e.args}")
        return pub_error_response(f"获取用户组列表失败: {e.args}")


def user_group(request):
    """用户组"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            user_group = UserGroup.objects.get(uuid=body['uuid'])
            return pub_success_response(format_user_group_data(user_group))
        elif request.method == 'POST':
            create_keys = ['name', 'code', 'parent', 'level', 'sort']
            create_dict = {key: value for key, value in body.items() if key in create_keys}

            user_group = UserGroup.objects.create(**create_dict)
            return pub_success_response(format_user_group_data(user_group))
        elif request.method == 'PUT':
            uuid = body.get('uuid')
            assert uuid, 'uuid 不能为空'

            user_group_obj = UserGroup.objects.filter(uuid=uuid).first()
            assert user_group_obj, '更新的用户组不存在'

            # 更新基本信息
            update_keys = ['name', 'code', 'parent', 'level', 'sort']
            update_dict = {key: value for key, value in body.items() if key in update_keys}
            for key, value in update_dict.items():
                setattr(user_group_obj, key, value)
            user_group_obj.save()

            # 更新用户
            if 'users' in body:
                user_group_obj.users.clear()
                for user_uuid in body['users']:
                    user = User.objects.get(uuid=user_uuid)
                    user_group_obj.users.add(user)

            # 更新角色
            if 'roles' in body:
                user_group_obj.roles.clear()
                for role_uuid in body['roles']:
                    role = Role.objects.get(uuid=role_uuid)
                    user_group_obj.roles.add(role)

            # 更新权限
            if 'permissions' in body:
                user_group_obj.permissions.clear()
                for permission_uuid in body['permissions']:
                    permission = Permission.objects.get(uuid=permission_uuid)
                    user_group_obj.permissions.add(permission)

            color_logger.debug(f"更新用户组: {user_group_obj.uuid} 成功")
            return pub_success_response(format_user_group_data(user_group_obj))
        elif request.method == 'DELETE':
            color_logger.debug(f"删除用户组: {body['uuid']}")
            user_group = UserGroup.objects.filter(uuid=body['uuid']).first()
            assert user_group, '删除的用户组不存在'
            user_group.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"用户组操作失败: {e.args}")
        return pub_error_response(f"用户组操作失败: {e.args}")
