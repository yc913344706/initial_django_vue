from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import User

# Create your views here.


def user_list(request):
    """用户列表"""

    try:
        body = pub_get_request_body(request)
        user_list = User.objects.all()
    except Exception as e:
        return pub_error_response(e)

    return pub_success_response(user_list)

def user(request):
    """用户"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            user = User.objects.get(uuid=body['uuid'])
            return pub_success_response(user)
        elif request.method == 'POST':
            user = User.objects.create(**body)
            return pub_success_response(user)
        elif request.method == 'PUT':
            user = User.objects.filter(uuid=body['uuid']).update(**body)
            return pub_success_response(user)
        elif request.method == 'DELETE':
            user = User.objects.filter(uuid=body['uuid']).delete()
            return pub_success_response(user)
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        return pub_error_response(e)

