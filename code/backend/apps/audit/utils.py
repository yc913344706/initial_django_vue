from .models import AuditLog
from lib.request_tool import get_current_request, get_client_ip
from apps.myAuth.token_utils import TokenManager
from lib.log import color_logger
from django.db import transaction
from datetime import datetime
import uuid
from decimal import Decimal


def serialize_value(value):
    """序列化值，处理特殊类型"""
    if isinstance(value, datetime):
        return str(value)
    if isinstance(value, uuid.UUID):  # 处理 UUID 类型
        return str(value)
    if hasattr(value, 'uuid'):  # 处理UUID字段
        return str(value.uuid)
    if hasattr(value, 'pk'):  # 处理外键关联对象
        return str(value.pk)
    if isinstance(value, Decimal):  # 处理 Decimal 类型
        return float(value)  # 转换为 float 类型
    return value


def add_audit_log(action, operator_username=None, model_name=None, record_id=None, detail=None, request=None):
    """
    通用审计日志记录方法

    Args:
        action: 操作类型 (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, LOGIN_FAILED)
        operator_username: 操作用户名
        model_name: 模型名称
        record_id: 记录ID
        detail: 操作详情
        request: HTTP请求对象（如果提供，会从中提取用户名和IP）
    """
    def _create():
        try:
            # 将传入的参数复制到局部变量，避免Python作用域问题
            local_operator_username = operator_username
            local_model_name = model_name
            local_record_id = record_id
            local_detail = detail
            local_request = request

            # 如果提供了request对象，从中提取用户名和IP
            ip_address = None
            if local_request:
                ip_address = get_client_ip(local_request)
                if not local_operator_username:
                    token = local_request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1] if local_request.META.get('HTTP_AUTHORIZATION') else None
                    if token:
                        username_from_token = TokenManager().get_username_from_access_token(token)
                        if username_from_token:
                            local_operator_username = username_from_token
            else:
                # 尝试获取当前请求的IP
                current_request = get_current_request()
                if current_request:
                    ip_address = get_client_ip(current_request)
                    if not local_operator_username:
                        token = current_request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1] if current_request.META.get('HTTP_AUTHORIZATION') else None
                        if token:
                            username_from_token = TokenManager().get_username_from_access_token(token)
                            if username_from_token:
                                local_operator_username = username_from_token

            # 如果仍然没有操作用户名，使用默认值
            if not local_operator_username:
                local_operator_username = 'SYSTEM'

            # 如果detail是字典类型，序列化特殊值
            if isinstance(local_detail, dict):
                processed_detail = {}
                for key, value in local_detail.items():
                    processed_detail[key] = serialize_value(value)
                local_detail = processed_detail

            audit_log = AuditLog.objects.create(
                operator_username=local_operator_username,
                model_name=local_model_name,
                record_id=local_record_id,
                action=action,
                detail=local_detail or {},
                ip_address=ip_address
            )
            color_logger.info(f"审计日志创建成功: {action} - {local_operator_username}")
            return audit_log
        except Exception as e:
            color_logger.error(f"创建审计日志失败: {str(e)}", exc_info=True)

    # 在事务提交后执行创建日志操作
    transaction.on_commit(_create)