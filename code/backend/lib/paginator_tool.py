from django.core.paginator import Paginator, EmptyPage, InvalidPage
from typing import Union, List, Tuple
from django.db.models import QuerySet


def pub_paging_tool(page: int, query: Union[QuerySet, List], page_size: int = 20) -> Tuple[bool, int, List, int, Union[QuerySet, List]]:
    """通用分页工具
    
    Args:
        page: 当前页码
        query: 查询集或列表
        page_size: 每页数量
        
    Returns:
        Tuple[bool, int, List, int, Union[QuerySet, List]]:
        (是否有下一页, 下一页页码, 分页列表, 总数, 当前页数据)
    """
    # 处理列表类型数据
    if isinstance(query, list):
        total = len(query)
        start = (page - 1) * page_size
        end = start + page_size
        data = query[start:end]
        
        return bool(end < total), page + 1, list(range(1, (total // page_size) + 2)), total, data
    
    # 处理 QuerySet
    total = query.count()
    paginator = Paginator(query, page_size)
    
    try:
        current_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        current_page = paginator.page(1)
    
    return bool(current_page.has_next()), current_page.next_page_number() if current_page.has_next() else 1, \
           list(range(1, paginator.num_pages + 1)), total, current_page.object_list