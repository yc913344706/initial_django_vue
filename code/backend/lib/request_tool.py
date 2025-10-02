import json
import uuid

from django.http import HttpRequest, QueryDict, JsonResponse
from schema import Schema, Use
from datetime import datetime

import xmltodict

from apps.myAuth.token_utils import TokenManager
from lib.log import color_logger
from backend.settings import config_data
import threading

_thread_locals = threading.local()

def set_current_request(request):
    """设置当前请求到线程本地存储"""
    _thread_locals.request = request

def get_current_request():
    """从线程本地存储获取当前请求"""
    return getattr(_thread_locals, 'request', None)

def get_client_ip(request):
    """获取客户端IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_authorization_token(request: HttpRequest):
    """获取Authorization头中的token"""
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        auth_header_list = auth_header.split(" ")
        if len(auth_header_list) == 2:
            return auth_header_list[1]
    return None

def pub_get_request_body(request: HttpRequest, format_dict = None):
    """
    从请求中提取请求体数据，支持 JSON、表单（QueryDict）和 XML 格式，同时包含 URL 查询参数
    
    Args:
        request: HTTP请求对象
        format_dict: 格式化字典，key为字段名，value为转换函数
        例如: {'order_uuid': str, 'is_edit': int}
    """
    # color_logger.debug("enter pub_get_request_body")

    content_type = request.headers.get("Content-Type", "")
    request_data = {}

    try:
        if len(request.GET) > 0:
            request_data.update(request.GET.dict())
            # color_logger.debug(f"request.GET: {request.GET}")

        if len(request.POST) > 0:
            request_data.update(request.POST.dict())
            # color_logger.debug(f"request.POST: {request.POST}")

        body_data = {}
        if "application/json" in content_type:
            # POST + JSON 格式
            _body_data = request.body.decode()
            if _body_data:
                body_data = json.loads(_body_data)
        elif content_type in ("text/xml", "application/xml"):
            # POST + XML 类型
            _body_data = request.body.decode()
            if _body_data:
                body_data = xmltodict.parse(_body_data)  # 将 XML 转换为字典
        # else:
        #     # POST + 表单数据（如 application/x-www-form-urlencoded 或 multipart/form-data）
        #     body_data = request.POST.dict()
        request_data.update(body_data)

        # 如果是 QueryDict，转换为标准字典格式
        if isinstance(request_data, QueryDict):
            x_copy = QueryDict('', mutable=True)
            x_copy.update(request_data)
            request_data = x_copy.dict()

        # 去除值为空的字段，并对字符串类型字段进行 strip 操作
        request_data = {
            k: v.strip() if isinstance(v, str) else v
            for k, v in request_data.items()
            if v is not None
        }

    except Exception as e:
        color_logger.error(f"请求预处理报错：{type(e)}: {e.args}")
        request_data = {}

    if format_dict:
        for k, v in format_dict.items():
            try:
                if k in request_data and request_data[k] not in (None, ''):
                    request_data[k] = v(request_data[k])
            except Exception as e:
                color_logger.error(f"字段 {k} 格式化失败: {str(e)}")
                # request_data[k] = None

    return request_data


def pub_bool_check(param, default_value=True):
    """
    true/false => True/False
    """
    if param is None:
        return False

    if isinstance(param, str):
        if param == "null":
            return None
        try:
            a = float(param)
            return bool(a)
        except Exception:
            pass

    if isinstance(param, float):
        return bool(param)

    if isinstance(param, bool):
        return param

    if str(param) in ['False', 'false']:
        return False

    if str(param) in ['True', 'true']:
        return True

    if default_value is not None:
        return default_value

    else:
        raise Exception(f"无法识别该 bool 类型值: {param}")


def pub_success_response(data=None, msg='success'):
    res_dict = {
        'success': True,
        'data': data,
        'msg': msg,
        'code': 200
    }

    return JsonResponse(res_dict)


def pub_error_response(res_code, data=None, status_code=200, msg="failed"):
    res_dict = {
        'success': False,
        'data': data,
        'msg': msg,
        'code': res_code
    }

    return JsonResponse(res_dict,
                        status=status_code)


def pub_int_check(status, error_msg=None):
    """int类型检查"""
    error_msg = '参数类型异常，不支持非int类型!' if not error_msg else error_msg
    int_check = Schema(Use(int), error=error_msg)
    return int_check.validate(status)


def pub_float_check(status, error_msg=None):
    """float类型检查"""
    error_msg = '参数类型异常，不支持非float类型!' if not error_msg else error_msg
    float_check = Schema(Use(float), error=error_msg)
    return float_check.validate(status)


def pub_str_check(value, value_name):
    """int类型检查"""
    assert value is not None, f"{value_name} 为空"
    value = str(value)
    assert len(value) > 0, f'{value_name} 长度应大于0'
    return value


def pub_check_uuid(uuid_str):
    """
    检查uuid是否合法
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except Exception as e:
        return False


date_allow_format = [
    '%Y-%m-%d',           # 2023-09-08
    '%Y%m%d',             # 20230908
    '%Y/%m/%d',           # 2023/09/08
    '%Y.%m.%d',           # 2023.09.08
    '%Y-%m-%d %H:%M:%S',  # 2023-09-08 14:59:29
    '%Y%m%d %H%M%S',      # 20230908 145929
    '%Y/%m/%d %H:%M:%S',  # 2023/09/08 14:59:29
    '%Y.%m.%d %H.%M.%S'   # 2023.09.08 14.59.29
]


def is_valid_date(input_string):
    for date_format in date_allow_format:
        try:
            datetime.strptime(input_string, date_format)
            return True
        except ValueError:
            continue
    return False


def get_request_param(request, param_name):
    body = pub_get_request_body(request)

    body_res = body.get(param_name)

    if body_res is None :
        get_res = request.GET.get(param_name)
        if get_res is None:
            post_res = request.POST.get(param_name)
            if post_res is None:
                return None
            else:
                return post_res
        else:
            return get_res
    else:
        return body_res


def pub_json_check(json_data, required_fields=None, optional_fields=None):
    """校验JSON数据
    
    Args:
        json_data (dict): 要校验的JSON数据
        required_fields (list): 必需字段列表，每个元素是 (字段名, 字段类型, 字段描述)
        optional_fields (list): 可选字段列表，每个元素是 (字段名, 字段类型, 字段描述)
    
    Returns:
        tuple: (是否通过, 错误信息)
        
    Example:
        required = [
            ('name', str, '名称'),
            ('age', int, '年龄'),
        ]
        optional = [
            ('email', str, '邮箱'),
        ]
        is_valid, error_msg = pub_json_check(data, required, optional)
    """
    if not isinstance(json_data, dict):
        color_logger.error(f"json_data: {json_data}")
        return False, "数据格式必须是JSON对象"
        
    # 校验必需字段
    if required_fields:
        for field_name, field_type, field_desc in required_fields:
            if field_name not in json_data:
                color_logger.error(f"json_data: {json_data}")
                return False, f"缺少必需参数: {field_desc}({field_name})"
            if not isinstance(json_data[field_name], field_type):
                color_logger.error(f"json_data: {json_data}")
                return False, f"参数类型错误: {field_desc}({field_name})必须是{field_type.__name__}类型"
                
    # 校验可选字段
    if optional_fields:
        for field_name, field_type, field_desc in optional_fields:
            if field_name in json_data and not isinstance(json_data[field_name], field_type):
                color_logger.error(f"json_data: {json_data}")
                return False, f"参数类型错误: {field_desc}({field_name})必须是{field_type.__name__}类型"
                
    return True, None
