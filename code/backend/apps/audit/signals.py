from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.dispatch import receiver
from django.db.models import Model

from apps.myAuth.token_utils import TokenManager
from lib.time_tools import utc_obj_to_time_zone_str
from .models import AuditLog
from lib.request_tool import get_authorization_token, get_current_request, get_client_ip
from lib.log import color_logger
from datetime import datetime
import uuid
from django.db import transaction
from threading import local
from decimal import Decimal

# https://docs.djangoproject.com/zh-hans/5.1/ref/signals/
# 创建一个线程本地存储来存储临时变更
_thread_locals = local()

def get_thread_locals():
    """获取线程本地存储"""
    if not hasattr(_thread_locals, 'changes'):
        _thread_locals.changes = {}
    return _thread_locals.changes

def clear_thread_locals():
    """清除线程本地存储"""
    if hasattr(_thread_locals, 'changes'):
        del _thread_locals.changes

def get_operator_info():
    """获取操作者信息"""
    username = 'UNKNOWN'
    ip_address = 'UNKNOWN'

    request = get_current_request()
    if request is not None:
        username = TokenManager().get_username_from_access_token(get_authorization_token(request))
        if username is None:
            color_logger.warning("当前请求中没有获取到用户名")
            return None, None
        ip_address = get_client_ip(request)
    else:
        color_logger.warning("当前请求中没有获取到请求对象")
        return None, None

    return username, ip_address

def create_audit_log(username, model_name, record_id, action, detail, ip_address):
    """创建审计日志"""
    def _create():
        try:
            AuditLog.objects.create(
                operator_username=username,
                model_name=model_name,
                record_id=record_id,
                action=action,
                detail=detail,
                ip_address=ip_address
            )
        except Exception as e:
            color_logger.error(f"创建审计日志失败: {str(e)}")

    transaction.on_commit(_create)

def serialize_value(value):
    """序列化值，处理特殊类型"""
    if isinstance(value, datetime):
        return utc_obj_to_time_zone_str(value)
    if isinstance(value, uuid.UUID):  # 处理 UUID 类型
        return str(value)
    if hasattr(value, 'uuid'):  # 处理UUID字段
        return str(value.uuid)
    if hasattr(value, 'pk'):  # 处理外键关联对象
        return str(value.pk)
    if isinstance(value, Decimal):  # 处理 Decimal 类型
        return float(value)  # 转换为 float 类型
    return value

def get_relation_changes(field, old_instance, new_instance):
    """获取关系字段的变更"""
    if field.many_to_many:
        # 多对多关系由 m2m_changed 信号处理
        return None
        
    if field.one_to_many or field.many_to_one or field.one_to_one:
        # 处理其他关系字段
        old_value = getattr(old_instance, field.name) if old_instance else None
        new_value = getattr(new_instance, field.name)
        if old_value != new_value:
            return {
                'old': serialize_value(old_value),
                'new': serialize_value(new_value)
            }
    return None

def get_changes(old_instance, new_instance):
    """获取实例变更的字段"""
    changes = {}
    if not old_instance:
        # 新建记录
        for field in new_instance._meta.fields:
            # 跳过 update_time 字段
            if field.name == 'update_time':
                continue
            if field.is_relation:
                relation_changes = get_relation_changes(field, None, new_instance)
                if relation_changes:
                    changes[field.name] = relation_changes
            else:
                changes[field.name] = {
                    'old': None,
                    'new': serialize_value(getattr(new_instance, field.name))
                }
    else:
        # 更新记录
        for field in new_instance._meta.fields:
            # 跳过 update_time 字段
            if field.name == 'update_time':
                continue
            if field.is_relation:
                relation_changes = get_relation_changes(field, old_instance, new_instance)
                if relation_changes:
                    changes[field.name] = relation_changes
            else:
                old_value = getattr(old_instance, field.name)
                new_value = getattr(new_instance, field.name)
                if old_value != new_value:
                    changes[field.name] = {
                        'old': serialize_value(old_value),
                        'new': serialize_value(new_value)
                    }
    return changes

@receiver(pre_save)
def model_pre_save(sender, instance, **kwargs):
    """保存前记录原始数据"""
    if not issubclass(sender, Model) or sender == AuditLog:
        return
        
    try:
        # 获取原始实例
        original_instance = type(instance).objects.get(pk=instance.pk)
        instance._original_state = original_instance
        color_logger.debug(f"pre_save: 获取到原始实例 {instance._meta.model_name}_{instance.pk}")
        
        # 记录多对多关系的原始状态
        instance._original_m2m_state = {}
        for field in instance._meta.many_to_many:
            original_value = set(getattr(original_instance, field.name).all())
            instance._original_m2m_state[field.name] = original_value
            color_logger.debug(f"pre_save: 记录多对多字段 {field.name} 的原始状态: {[serialize_value(item) for item in original_value]}")

        # 初始化多对多操作的标记
        if hasattr(instance, '_m2m_add_pending'):
            delattr(instance, '_m2m_add_pending')
        if hasattr(instance, '_m2m_clear_pending'):
            delattr(instance, '_m2m_clear_pending')
        if hasattr(instance, '_m2m_remove_pending'):
            delattr(instance, '_m2m_remove_pending')
    except (type(instance).DoesNotExist, AttributeError):
        instance._original_state = None
        instance._original_m2m_state = {}
        color_logger.debug(f"pre_save: 无法获取原始实例 {instance._meta.model_name}_{instance.pk}")

@receiver(post_save)
def model_post_save(sender, instance, created, **kwargs):
    """处理模型保存后的审计日志记录"""
    if not issubclass(sender, Model) or sender == AuditLog:
        return

    try:
        username, ip_address = get_operator_info()
        if not username:
            return

        color_logger.debug(f"post_save: 开始处理实例 {instance._meta.model_name}_{instance.pk}")

        # 获取普通字段的变更
        changes = get_changes(getattr(instance, '_original_state', None), instance)
        color_logger.debug(f"post_save: 获取到普通字段变更: {changes}")
        
        # 过滤掉没有实际变化的字段
        changes = {k: v for k, v in changes.items() if v['old'] != v['new']}
        
        if not changes:
            color_logger.warning(f"保存审计日志时，当前数据库变更请求中没有获取到变更字段，跳过记录")
            return
    
        color_logger.info(f"保存审计日志时，当前数据库变更请求中获取到变更字段，开始记录审计日志: {changes}")

        create_audit_log(
            username=username,
            model_name=instance._meta.model_name,
            record_id=str(instance.pk),
            action='CREATE' if created else 'UPDATE',
            detail=changes,
            ip_address=ip_address
        )
    except Exception as e:
        color_logger.error(f"审计日志记录失败(外层): {str(e)}")
        color_logger.error(f"错误详情: {str(e.__class__.__name__)}")
        import traceback
        color_logger.error(f"堆栈跟踪: {traceback.format_exc()}")

@receiver(pre_delete)
def model_pre_delete(sender, instance, **kwargs):
    """删除前记录"""
    if not issubclass(sender, Model) or sender == AuditLog:
        return

    try:
        username, ip_address = get_operator_info()
        if not username:
            return

        color_logger.info(f"删除模型数据时，当前数据库变更请求的请求对象中获取到用户名，开始记录审计日志")
        
        detail = {}
        for field in instance._meta.fields:
            if field.is_relation:
                relation_changes = get_relation_changes(field, None, instance)
                if relation_changes:
                    detail[field.name] = relation_changes['old']
            else:
                detail[field.name] = serialize_value(getattr(instance, field.name))

        create_audit_log(
            username=username,
            model_name=instance._meta.model_name,
            record_id=str(instance.pk),
            action='DELETE',
            detail=detail,
            ip_address=ip_address
        )
    except Exception as e:
        color_logger.error(f"审计日志记录失败: {str(e)}")

@receiver(m2m_changed)
def model_m2m_changed(sender, instance, action, pk_set, **kwargs):
    """处理多对多关系变更"""
    if not issubclass(sender, Model) or sender == AuditLog:
        return

    try:
        username, ip_address = get_operator_info()
        if not username:
            return

        # 获取变更的字段名
        model_name = kwargs.get('model')._meta.model_name
        color_logger.debug(f"m2m_changed: 当前处理的模型名: {model_name}")
        color_logger.debug(f"m2m_changed: 当前实例类型: {instance._meta.model_name}")
        color_logger.debug(f"m2m_changed: 当前动作: {action}")
        color_logger.debug(f"m2m_changed: 变更的ID集合: {pk_set}")
        
        # 遍历实例的所有字段，找到对应的多对多字段
        field_name = None
        color_logger.debug(f"m2m_changed: 实例的所有字段: {[field.name for field in instance._meta.fields]}")
        color_logger.debug(f"m2m_changed: 实例的所有多对多字段: {[field.name for field in instance._meta.many_to_many]}")
        
        # 遍历多对多字段而不是所有字段
        for field in instance._meta.many_to_many:
            related_model = field.related_model
            color_logger.debug(f"m2m_changed: 检查字段: {field.name}, 关联模型: {related_model._meta.model_name}")
            # 检查关联模型是否匹配
            if related_model._meta.model_name == model_name:
                field_name = field.name
                color_logger.debug(f"m2m_changed: 找到匹配的字段: {field_name}")
                break
        
        if not field_name:
            color_logger.warning(f"未找到对应的多对多字段: {model_name}")
            color_logger.debug(f"m2m_changed: 当前实例: {instance}")
            return

        field = getattr(instance, field_name)
        
        # 获取原始状态
        original_m2m_state = getattr(instance, '_original_m2m_state', {})
        original_value = original_m2m_state.get(field_name, set())
        current_value = set(field.all())
        
        color_logger.debug(f"m2m_changed: 原始值: {[serialize_value(item) for item in original_value]}")
        color_logger.debug(f"m2m_changed: 当前值: {[serialize_value(item) for item in current_value]}")
        
        # # 检查是否有实际变化
        # 在 Django 的多对多关系处理中，当我们修改一个多对多字段时，Django 会先清空所有关系，然后重新添加。
        # if original_value == current_value:
        #     color_logger.debug(f"m2m_changed: 字段 {field_name} 没有实际变化，跳过记录")
        #     return

        # 获取线程本地存储
        changes = get_thread_locals()
        instance_key = f"{instance._meta.model_name}_{instance.pk}"
        
        # 初始化字段的状态记录
        if instance_key not in changes:
            changes[instance_key] = {}
        if field_name not in changes[instance_key]:
            changes[instance_key][field_name] = {
                'original': original_value,
                'states': [],
                'audit_logs': []  # 记录每个字段创建的 audit log 对象
            }
        
        # 记录当前状态
        changes[instance_key][field_name]['states'].append({
            'action': action,
            'value': current_value
        })
        
        # 在最后一个操作时记录变更
        if action in ["post_add", "post_clear"]:
            field_changes = changes[instance_key][field_name]
            final_value = field_changes['states'][-1]['value']
            
            # 记录最终变更
            changes = {
                field_name: {
                    'old': [serialize_value(item) for item in field_changes['original']],
                    'new': [serialize_value(item) for item in final_value]
                }
            }
            color_logger.debug(f"m2m_changed: 记录最终变更 - 旧值: {changes[field_name]['old']}")
            color_logger.debug(f"m2m_changed: 记录最终变更 - 新值: {changes[field_name]['new']}")
            color_logger.info(f"多对多关系变更，开始记录审计日志: {changes}")

            # 创建 audit log 对象
            audit_log = AuditLog(
                operator_username=username,
                model_name=instance._meta.model_name,
                record_id=str(instance.pk),
                action='UPDATE',
                detail=changes,
                ip_address=ip_address
            )
            audit_log.save()
            
            # 记录 audit log 对象
            field_changes['audit_logs'].append(audit_log)
            
            # 如果是 post_add，删除所有之前的记录
            if action == "post_add":
                for log in field_changes['audit_logs'][:-1]:  # 删除除最后一个之外的所有记录
                    log.delete()
                field_changes['audit_logs'] = [field_changes['audit_logs'][-1]]  # 只保留最后一个记录
            
                if final_value == original_value:
                    color_logger.debug(f"m2m_changed: 字段 {field_name} 没有实际变化，删除审计日志")
                    for log in field_changes['audit_logs']:
                        log.delete()
                    field_changes['audit_logs'] = []
            
            # 清理线程本地存储
            try:
                if instance_key in changes:
                    if field_name in changes[instance_key]:
                        del changes[instance_key][field_name]
                    if not changes[instance_key]:
                        del changes[instance_key]
            except Exception as e:
                color_logger.error(f"清理线程本地存储失败: {str(e)}")

    except Exception as e:
        color_logger.error(f"审计日志记录失败(外层): {str(e)}")
        color_logger.error(f"错误详情: {str(e.__class__.__name__)}")
        import traceback
        color_logger.error(f"堆栈跟踪: {traceback.format_exc()}")