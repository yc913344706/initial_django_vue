import json
from datetime import datetime, timezone
from lib.log import color_logger

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

        return super(DateTimeEncoder, self).default(o)

def merge_jsons(jsons):
    """合并多个JSON
    
    合并规则：
    1. 如果是字符串，尝试解析为JSON
    2. 如果是字典，则递归合并
    3. 如果是列表，则合并列表并去重
    4. 如果是其他类型（int, float, bool等），则保留最后一个值
    """
    if not jsons:
        return {}
    
    result = {}
    for _json in jsons:
        if _json is None:
            continue
            
        # 如果是字符串，尝试解析为JSON
        if isinstance(_json, str):
            try:
                import json
                _json = json.loads(_json)
            except json.JSONDecodeError:
                color_logger.warning(f"无法解析JSON字符串: {_json}")
                continue
        
        # 如果是字典，递归合并
        if isinstance(_json, dict):
            for key, value in _json.items():
                if key not in result:
                    result[key] = value
                else:
                    # 递归合并值
                    result[key] = merge_jsons([result[key], value])
        # 如果是列表，合并并去重
        elif isinstance(_json, list):
            if not result:
                result = _json
            else:
                # 如果结果不是列表，转换为列表
                if not isinstance(result, list):
                    result = [result]
                # 合并列表并去重
                result = list(set(result + _json))
        # 其他类型（int, float, bool等）直接覆盖
        else:
            result = _json
    
    return result