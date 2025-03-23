from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import Permission, Role, Grant

# Create your views here.

def permission_list(request):
    """权限列表"""

    try:
        body = pub_get_request_body(request)
        permission_list = Permission.objects.all()
    except Exception as e:
        return pub_error_response(e)

    return pub_success_response(permission_list)

def permission(request):
    """权限"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            permission = Permission.objects.get(uuid=body['uuid'])
            return pub_success_response(permission)
        elif request.method == 'POST':
            permission = Permission.objects.create(**body)
            return pub_success_response(permission)
        elif request.method == 'PUT':
            permission = Permission.objects.filter(uuid=body['uuid']).update(**body)
            return pub_success_response(permission)
        elif request.method == 'DELETE':
            permission = Permission.objects.filter(uuid=body['uuid']).delete()
            return pub_success_response(permission)
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        return pub_error_response(e)

def role_list(request):
    """角色列表"""

    try:
        body = pub_get_request_body(request)
        role_list = Role.objects.all()
    except Exception as e:
        return pub_error_response(e)

    return pub_success_response(role_list)

def role(request):
    """角色"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            role = Role.objects.get(uuid=body['uuid'])
            return pub_success_response(role)
        elif request.method == 'POST':
            role = Role.objects.create(**body)
            return pub_success_response(role)
        elif request.method == 'PUT':
            role = Role.objects.filter(uuid=body['uuid']).update(**body)
            return pub_success_response(role)
        elif request.method == 'DELETE':
            role = Role.objects.filter(uuid=body['uuid']).delete()
            return pub_success_response(role)
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        return pub_error_response(e)

def grant_list(request):
    """授权列表"""

    try:
        body = pub_get_request_body(request)
        grant_list = Grant.objects.all()
    except Exception as e:
        return pub_error_response(e)

    return pub_success_response(grant_list)

def grant(request):
    """授权"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            grant = Grant.objects.get(uuid=body['uuid'])
            return pub_success_response(grant)
        elif request.method == 'POST':
            grant = Grant.objects.create(**body)
            return pub_success_response(grant)
        elif request.method == 'PUT':
            grant = Grant.objects.filter(uuid=body['uuid']).update(**body)
            return pub_success_response(grant)
        elif request.method == 'DELETE':
            grant = Grant.objects.filter(uuid=body['uuid']).delete()
            return pub_success_response(grant)
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        return pub_error_response(e)