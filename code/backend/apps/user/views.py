from lib.password_tools import aes
from .utils import format_user_data, format_user_group_data
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from .models import User, UserGroup
from apps.perm.models import Role, Permission
from lib.paginator_tool import pub_paging_tool
from lib.log import color_logger
from django.db.models import Q
from django.contrib.auth.hashers import check_password, make_password
from .password_validator import validate_password_strength
import json

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
            return pub_error_response(13001, msg='请求方法错误')
    except Exception as e:
        color_logger.error(f"用户列表操作失败: {e.args}")
        return pub_error_response(13002, msg=f"用户列表操作失败: {e.args}")


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
            return pub_error_response(13003, msg='请求方法错误')
    except Exception as e:
        color_logger.error(f"用户操作失败: {e.args}")
        return pub_error_response(13004, msg=f"用户操作失败: {e.args}")


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
            return pub_error_response(13008, msg='请求方法错误')
    except Exception as e:
        color_logger.error(f"获取用户组列表失败: {e.args}")
        return pub_error_response(13005, msg=f"获取用户组列表失败: {e.args}")


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
            return pub_error_response(13006, msg='请求方法错误')
    except Exception as e:
        color_logger.error(f"用户组操作失败: {e.args}")
        return pub_error_response(13007, msg=f"用户组操作失败: {e.args}")


def change_password(request):
    """用户修改自己密码"""
    try:
        body = pub_get_request_body(request)

        if request.method != 'POST':
            return pub_error_response(13009, msg='请求方法错误')

        # 验证必需参数
        current_password = body.get('current_password')
        new_password = body.get('new_password')
        confirm_password = body.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return pub_error_response(13010, msg='缺少必需参数：current_password, new_password, confirm_password')

        if new_password != confirm_password:
            return pub_error_response(13011, msg='新密码与确认密码不一致')

        # 获取当前用户
        current_username = request.user_name
        if not current_username:
            return pub_error_response(13013, msg='无效的认证令牌')

        user = User.objects.filter(username=current_username).first()
        if not user:
            return pub_error_response(13014, msg='用户不存在')

        # 检查LDAP用户不能修改密码
        if user.is_ldap:
            return pub_error_response(13015, msg='LDAP用户无法修改本地密码')

        # 验证当前密码
        decrypted_password = aes.decrypt(user.password)
        if decrypted_password != current_password:
            return pub_error_response(13016, msg='当前密码不正确')

        # 验证新密码强度
        is_valid, msg = validate_password_strength(new_password)
        if not is_valid:
            return pub_error_response(13017, msg=msg)

        # 更新密码
        encrypted_new_password = aes.encrypt(new_password)
        user.password = encrypted_new_password
        user.save()

        color_logger.info(f"用户 {user.username} 修改密码成功")
        return pub_success_response(msg='密码修改成功')

    except Exception as e:
        color_logger.error(f"用户修改密码失败: {e.args}")
        return pub_error_response(13018, msg=f"密码修改失败: {e.args}")


def reset_password(request):
    """管理员重置用户密码"""
    try:
        body = pub_get_request_body(request)

        if request.method != 'POST':
            return pub_error_response(13019, msg='请求方法错误')

        # 验证必需参数
        user_uuid = body.get('user_uuid')
        new_password = body.get('new_password')
        confirm_password = body.get('confirm_password')

        if not user_uuid or not new_password or not confirm_password:
            return pub_error_response(13020, msg='缺少必需参数：user_uuid, new_password, confirm_password')

        if new_password != confirm_password:
            return pub_error_response(13021, msg='新密码与确认密码不一致')

        # 获取当前用户
        current_username = request.user_name
        if not current_username:
            return pub_error_response(13013, msg='无效的认证令牌')

        current_user = User.objects.filter(username=current_username).first()
        if not current_user:
            return pub_error_response(13024, msg='当前用户不存在')

        # 检查当前用户权限（这里简单检查是否为管理员，实际项目中应该有更详细的权限验证）
        # 在当前系统中，我们假设所有用户都可以重置其他用户密码，实际项目中应有权限检查
        target_user = User.objects.filter(uuid=user_uuid).first()
        if not target_user:
            return pub_error_response(13025, msg='目标用户不存在')

        # 检查LDAP用户不能重置密码
        if target_user.is_ldap:
            return pub_error_response(13026, msg='无法重置LDAP用户的密码')

        # 验证新密码强度
        is_valid, msg = validate_password_strength(new_password)
        if not is_valid:
            return pub_error_response(13027, msg=msg)

        # 更新密码
        encrypted_new_password = aes.encrypt(new_password)
        target_user.password = encrypted_new_password
        target_user.save()

        color_logger.info(f"用户 {current_user.username} 为用户 {target_user.username} 重置密码成功")
        return pub_success_response(msg='密码重置成功')

    except Exception as e:
        color_logger.error(f"管理员重置密码失败: {e.args}", exc_info=True)
        return pub_error_response(13028, msg=f"密码重置失败: {e.args}")


def get_password_config(request):
    """获取密码配置"""
    try:
        body = pub_get_request_body(request)

        if request.method != 'GET':
            return pub_error_response(13029, msg='请求方法错误')

        # 返回默认密码配置
        from .password_validator import get_password_strength_config
        config = get_password_strength_config()

        return pub_success_response(config)

    except Exception as e:
        color_logger.error(f"获取密码配置失败: {e.args}")
        return pub_error_response(13030, msg=f"获取密码配置失败: {e.args}")


def update_password_config(request):
    """更新密码配置"""
    try:
        body = pub_get_request_body(request)

        if request.method != 'POST':
            return pub_error_response(13031, msg='请求方法错误')

        # 验证密码配置参数
        min_length = body.get('min_length', 8)
        max_length = body.get('max_length', 128)
        require_uppercase = body.get('require_uppercase', True)
        require_lowercase = body.get('require_lowercase', True)
        require_numbers = body.get('require_numbers', True)
        require_special = body.get('require_special', False)
        allowed_special_chars = body.get('allowed_special_chars', "!@#$%^&*()_+-=[]{};':\"\\|,.<>\/?")

        # 验证参数范围
        if min_length < 1 or min_length > max_length:
            return pub_error_response(13033, msg='最小长度必须大于0且小于等于最大长度')
        if max_length < min_length or max_length > 256:
            return pub_error_response(13034, msg='最大长度必须大于等于最小长度且小于等于256')

        # 保存配置到数据库
        from .password_validator import save_password_strength_config
        config = {
            "min_length": min_length,
            "max_length": max_length,
            "require_uppercase": require_uppercase,
            "require_lowercase": require_lowercase,
            "require_numbers": require_numbers,
            "require_special": require_special,
            "allowed_special_chars": allowed_special_chars
        }

        save_password_strength_config(config)

        color_logger.info(f"密码配置已更新: {config}")
        return pub_success_response(config, msg='密码配置更新成功')

    except Exception as e:
        color_logger.error(f"更新密码配置失败: {e.args}")
        return pub_error_response(13032, msg=f"更新密码配置失败: {e.args}")

def password_config(request):
    """处理密码配置的GET和POST请求"""
    try:
        if request.method == 'GET':
            return get_password_config(request)
        elif request.method == 'POST':
            return update_password_config(request)
        else:
            return pub_error_response(13037, msg='请求方法错误')
    except Exception as e:
        color_logger.error(f"处理密码配置请求失败: {e.args}")
        return pub_error_response(13038, msg=f"处理密码配置请求失败: {e.args}")