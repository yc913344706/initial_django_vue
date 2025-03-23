from lib.password_tools import aes_encrypt_password
from .utils import format_user_data
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import User
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

            encrypted_password = aes_encrypt_password(create_dict['password'])
            create_dict['password'] = encrypted_password

            user = User.objects.create(**create_dict)
            return pub_success_response(format_user_data(user))
        elif request.method == 'PUT':
            uuid = body.get('uuid')
            assert uuid, 'uuid 不能为空'

            user_obj = User.objects.filter(uuid=uuid).first()
            assert user_obj, '更新的用户不存在'

            update_keys = ['username', 'nickname', 'phone', 'email', 'is_active']
            update_dict = {key: value for key, value in body.items() if key in update_keys}
            for key, value in update_dict.items():
                setattr(user_obj, key, value)
            user_obj.save()

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

