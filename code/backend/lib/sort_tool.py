from lib.log import color_logger

def sort_exact_first(results, search_key, search_value):
    def score(value_dict):
        value = value_dict.get(search_key, '')

        if value == search_value:
            # color_logger.debug(f'{value}: 0')
            return 0  # 完全匹配最优
        if value.startswith(search_value):
            # color_logger.debug(f'{value}: 1')
            return 1  # 前缀匹配
        if search_value in value:
            # color_logger.debug(f'{value}: 2')
            return 2  # 包含
        # color_logger.debug(f'{value}: 3')
        return 3  # 其他
    
    return sorted(results, key=score)