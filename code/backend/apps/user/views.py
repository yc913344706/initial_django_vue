from lib.password_tools import aes
from .utils import format_user_data, format_user_group_data
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import User, UserGroup
from apps.perm.models import Role, Permission
from lib.paginator_tool import pub_paging_tool
from lib.log import color_logger
from django.db.models import Q

# Create your views here.

def user_list(request):
    """用户列表"""

    try:
        body = pub_get_request_body(request)
        if request.method == 'GET':

            page = int(body.get('page', 1))
            page_size = int(body.get('page_size', 20))
            search = body.get('search', '')

            user_list = User.objects.all()
            # 添加搜索功能
            if search:
                user_list = user_list.filter(
                    Q(username__icontains=search) |
                    Q(nickname__icontains=search) |
                    Q(phone__icontains=search) |
                    Q(email__icontains=search)
                )

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
        elif request.method == 'DELETE':
            uuids = body.get('uuids', [])
            users = User.objects.filter(uuid__in=uuids)
            for user in users:
                assert user, '删除的用户不存在'
                user.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"用户列表操作失败: {e.args}")
        return pub_error_response(f"用户列表操作失败: {e.args}")


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

        if request.method == 'GET':

            page = int(body.get('page', 1))
            page_size = int(body.get('page_size', 20))
            search = body.get('search', '')

            # 分页查询
            user_group_list = UserGroup.objects.all()
            # 添加搜索功能
            if search:
                user_group_list = user_group_list.filter(
                    Q(name__icontains=search) |
                    Q(code__icontains=search)
                )
            has_next, next_page, page_list, all_num, result = pub_paging_tool(page, user_group_list, page_size)
            # 格式化返回数据
            result = [format_user_group_data(user_group) for user_group in result]

            return pub_success_response({
                'has_next': has_next,
                'next_page': next_page,
                'all_num': all_num,
                'data': result
            })
        elif request.method == 'DELETE':
            uuids = body.get('uuids', [])
            user_groups = UserGroup.objects.filter(uuid__in=uuids)
            for user_group in user_groups:
                assert user_group, '删除的用户组不存在'
                user_group.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"获取用户组列表失败: {e.args}")
        return pub_error_response(f"获取用户组列表失败: {e.args}")


def user_group(request):
    """用户组"""

    try:
        body = pub_get_request_body(request)
        color_logger.debug(f"用户组请求: {body}")

        if request.method == 'GET':
            user_group = UserGroup.objects.get(uuid=body['uuid'])
            return pub_success_response(format_user_group_data(user_group))
        elif request.method == 'POST':
            create_keys = ['name', 'code', 'parent', 'level', 'sort', 'description']
            create_dict = {key: value for key, value in body.items() if key in create_keys}

            # 创建用户组
            if 'parent' in create_dict:
                parent_user_group = UserGroup.objects.get(uuid=create_dict['parent'])
                create_dict['parent'] = parent_user_group

            user_group = UserGroup.objects.create(**create_dict)
            return pub_success_response(format_user_group_data(user_group))
        elif request.method == 'PUT':
            uuid = body.get('uuid')
            assert uuid, 'uuid 不能为空'

            user_group_obj = UserGroup.objects.filter(uuid=uuid).first()
            assert user_group_obj, '更新的用户组不存在'

            # 更新基本信息
            update_keys = ['name', 'code', 'parent', 'level', 'sort', 'description']
            update_dict = {key: value for key, value in body.items() if key in update_keys}

            # 更新父级
            if 'parent' in update_dict:
                if update_dict['parent'] == 'undefined':
                    update_dict['parent'] = None
                else:
                    parent_user_group = UserGroup.objects.get(uuid=update_dict['parent'])
                    update_dict['parent'] = parent_user_group

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
