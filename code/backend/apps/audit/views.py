from django.shortcuts import render
from django.db.models import Q
from lib.request_tool import pub_success_response, pub_error_response, pub_get_request_body
from lib.log import color_logger
from lib.paginator_tool import pub_paging_tool
from .models import AuditLog
from lib.time_tools import utc_obj_to_time_zone_str

# Create your views here.

def get_audit_logs(request):
    """获取审计日志列表"""
    try:
        if request.method != 'GET':
            return pub_error_response(10001, msg="只允许GET请求")

        body = pub_get_request_body(request)
        
        # 构建查询条件
        query = AuditLog.objects.all()
        
        # 操作人筛选
        if operator := body.get('operator'):
            query = query.filter(operator_username__icontains=operator)
            
        # 模型名称筛选
        if model_name := body.get('model_name'):
            query = query.filter(model_name__icontains=model_name)
            
        # 操作类型筛选
        if action := body.get('action'):
            query = query.filter(action=action)
            
        # IP地址筛选
        if ip_address := body.get('ip_address'):
            query = query.filter(ip_address__icontains=ip_address)
            
        # 时间范围筛选
        if start_date := body.get('start_date'):
            query = query.filter(create_time__gte=start_date)
        if end_date := body.get('end_date'):
            query = query.filter(create_time__lte=end_date)
            
        # 关键词搜索(搜索操作人和记录ID)
        if keyword := body.get('keyword'):
            query = query.filter(
                Q(operator_username__icontains=keyword) |
                Q(record_id__icontains=keyword)
            )
            
        # 分页处理
        page = int(body.get('page', 1))
        page_size = int(body.get('page_size', 20))
        
        has_next, next_page, page_list, total, records = pub_paging_tool(
            page, query.order_by('-create_time'), page_size
        )
        
        # 构建返回数据
        result = []
        for record in records:
            result.append({
                'uuid': record.uuid,
                'operator_username': record.operator_username,
                'model_name': record.model_name,
                'record_id': record.record_id,
                'action': record.action,
                'action_display': record.get_action_display(),
                'detail': record.detail,
                'ip_address': record.ip_address,
                'create_time': utc_obj_to_time_zone_str(record.create_time)
            })
        
        return pub_success_response({
            'data': result,
            'total': total,
            'has_next': has_next,
            'next_page': next_page
        })
        
    except Exception as e:
        color_logger.error(f"获取审计日志失败: {str(e)}")
        return pub_error_response(10001, msg=str(e))
