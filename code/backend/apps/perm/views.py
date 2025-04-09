from .utils import format_permission_data, format_role_data, get_user_perm_json_all
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import Permission, Role
from lib.paginator_tool import pub_paging_tool
from lib.log import color_logger
from django.db.models import Q
# Create your views here.

def permission_list(request):
    """权限列表"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':

            page = int(body.get('page', 1))
            page_size = int(body.get('page_size', 20))
            search = body.get('search', '')
            
            permission_list = Permission.objects.all().order_by('name')
            # 添加搜索功能
            if search:
                permission_list = permission_list.filter(
                    Q(name__icontains=search) |
                    Q(code__icontains=search)
                )
                
            # 分页查询
            has_next, next_page, page_list, all_num, result = pub_paging_tool(page, permission_list, page_size)
            
            # 格式化返回数据
            result = [format_permission_data(permission) for permission in result]
            
            return pub_success_response({
                'has_next': has_next,
                'next_page': next_page,
                'all_num': all_num,
                'data': result
            })
        elif request.method == 'DELETE':
            uuids = body.get('uuids', [])
            permissions = Permission.objects.filter(uuid__in=uuids)
            for permission in permissions:
                assert permission, '删除的权限不存在'
                permission.delete()

            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"权限列表操作失败: {e.args}")
        return pub_error_response(f"权限列表操作失败: {e.args}")

def permission(request):
    """权限"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            permission = Permission.objects.get(uuid=body['uuid'])
            return pub_success_response(format_permission_data(permission))
        elif request.method == 'POST':
            create_keys = ['name', 'code', 'permission_json', 'description']
            create_dict = {key: value for key, value in body.items() if key in create_keys}

            permission = Permission.objects.create(**create_dict)
            return pub_success_response(format_permission_data(permission))
        elif request.method == 'PUT':
            uuid = body.get('uuid')
            assert uuid, 'uuid 不能为空'

            permission_obj = Permission.objects.filter(uuid=uuid).first()
            assert permission_obj, '更新的权限不存在'

            update_keys = ['name', 'code', 'permission_json', 'description']
            update_dict = {key: value for key, value in body.items() if key in update_keys}
            for key, value in update_dict.items():
                setattr(permission_obj, key, value)
            permission_obj.save()

            color_logger.debug(f"更新权限: {permission_obj.uuid} 成功")
            return pub_success_response(format_permission_data(permission_obj))
        elif request.method == 'DELETE':
            color_logger.debug(f"删除权限: {body['uuid']}")
            permission = Permission.objects.filter(uuid=body['uuid']).first()
            assert permission, '删除的权限不存在'
            permission.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"权限操作失败: {e.args}")
        return pub_error_response(f"权限操作失败: {e.args}")

def role_list(request):
    """角色列表"""

    try:
        body = pub_get_request_body(request)
        if request.method == 'GET':

            page = int(body.get('page', 1))
            page_size = int(body.get('page_size', 20))
            search = body.get('search', '')

            role_list = Role.objects.all().order_by('name')
            # 添加搜索功能
            if search:
                role_list = role_list.filter(
                    Q(name__icontains=search) |
                    Q(code__icontains=search)
                )
                
            # 分页查询
            has_next, next_page, page_list, all_num, result = pub_paging_tool(page, role_list, page_size)
            
            # 格式化返回数据
            result = [format_role_data(role) for role in result]
            
            return pub_success_response({
                'has_next': has_next,
                'next_page': next_page,
                'all_num': all_num,
                'data': result
            })
        elif request.method == 'DELETE':
            uuids = body.get('uuids', [])
            roles = Role.objects.filter(uuid__in=uuids)
            for role in roles:
                assert role, '删除的角色不存在'
                role.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"角色列表操作失败: {e.args}")
        return pub_error_response(f"角色列表操作失败: {e.args}")


def role(request):
    """角色"""
    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            role = Role.objects.get(uuid=body['uuid'])
            return pub_success_response(format_role_data(role))
        elif request.method == 'POST':
            create_keys = ['name', 'code', 'description']
            create_dict = {key: value for key, value in body.items() if key in create_keys}

            role = Role.objects.create(**create_dict)
            
            for permission in body.get('permissions', []):
                permission_obj = Permission.objects.get(uuid=permission)
                role.permissions.add(permission_obj)

            return pub_success_response(format_role_data(role))
        elif request.method == 'PUT':
            uuid = body.get('uuid')
            assert uuid, 'uuid 不能为空'

            role_obj = Role.objects.filter(uuid=uuid).first()
            assert role_obj, '更新的角色不存在'

            update_keys = ['name', 'code', 'description', 'permissions']
            update_dict = {key: value for key, value in body.items() if key in update_keys}
            for key, value in update_dict.items():
                if key == 'permissions':
                    role_obj.permissions.set(value)
                else:
                    setattr(role_obj, key, value)
            role_obj.save()

            color_logger.debug(f"更新角色: {role_obj.uuid} 成功")
            return pub_success_response(format_role_data(role_obj))
        elif request.method == 'DELETE':
            color_logger.debug(f"删除角色: {body['uuid']}")
            role = Role.objects.filter(uuid=body['uuid']).first()
            assert role, '删除的角色不存在'
            role.delete()
            return pub_success_response()
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        color_logger.error(f"角色操作失败: {e.args}")
        return pub_error_response(f"角色操作失败: {e.args}")

def user_permission_json(request):
    """用户权限JSON"""
    try:
        body = pub_get_request_body(request)
        user_uuid = body.get('uuid')
        assert user_uuid, '用户UUID不能为空'

        permission_json = get_user_perm_json_all(user_uuid)
        return pub_success_response(permission_json)
    except Exception as e:
        color_logger.error(f"用户权限JSON操作失败: {e.args}")
        return pub_error_response(f"用户权限JSON操作失败: {e.args}")
