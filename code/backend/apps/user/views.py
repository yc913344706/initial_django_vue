from .utils import format_user_data
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import User
from lib.paginator_tool import pub_paging_tool

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
        return pub_error_response(e)


def user(request):
    """用户"""

    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            user = User.objects.get(uuid=body['uuid'])
            return pub_success_response(format_user_data(user))
        elif request.method == 'POST':
            user = User.objects.create(**body)
            return pub_success_response(format_user_data(user))
        elif request.method == 'PUT':
            user = User.objects.filter(uuid=body['uuid']).update(**body)
            return pub_success_response(format_user_data(user))
        elif request.method == 'DELETE':
            user = User.objects.filter(uuid=body['uuid']).delete()
            return pub_success_response(format_user_data(user))
        else:
            return pub_error_response('请求方法错误')
    except Exception as e:
        return pub_error_response(e)

