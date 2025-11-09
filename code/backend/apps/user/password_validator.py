import re
from lib.log import color_logger

def validate_password_strength(password: str, config: dict = None) -> tuple[bool, str]:
    """
    验证密码强度
    
    Args:
        password: 要验证的密码
        config: 密码强度配置，格式如下：
        {
            "min_length": 8,  # 最小长度
            "require_uppercase": True,  # 是否需要大写字母
            "require_lowercase": True,  # 是否需要小写字母
            "require_numbers": True,  # 是否需要数字
            "require_special": True,  # 是否需要特殊字符
            "max_length": 128  # 最大长度
        }
    
    Returns:
        tuple[bool, str]: (是否通过验证, 错误信息或成功信息)
    """
    if config is None:
        # 默认配置
        config = {
            "min_length": 8,
            "max_length": 128,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special": False
        }
    
    # 检查密码长度
    if len(password) < config.get("min_length", 8):
        return False, f"密码长度至少需要{config.get('min_length', 8)}位"
    
    if len(password) > config.get("max_length", 128):
        return False, f"密码长度不能超过{config.get('max_length', 128)}位"
    
    # 检查是否需要大写字母
    if config.get("require_uppercase", False) and not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"
    
    # 检查是否需要小写字母
    if config.get("require_lowercase", False) and not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"
    
    # 检查是否需要数字
    if config.get("require_numbers", False) and not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    
    # 检查是否需要特殊字符
    if config.get("require_special", False) and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        return False, "密码必须包含至少一个特殊字符(!@#$%^&*()_+-=[]{};\':\"\\|,.<>\/?)"
    
    return True, "密码强度符合要求"


def get_password_strength_config() -> dict:
    """获取默认密码强度配置"""
    return {
        "min_length": 8,
        "max_length": 128,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special": False
    }