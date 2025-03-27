import json
import os
from typing import Dict, List, Any, Optional
from backend.settings import BASE_DIR
from lib.log import color_logger

class RouteTool:
    def __init__(self):
        self.base_routes = self._load_json(os.path.join(BASE_DIR, 'base_routes.json'))

    def _load_json(self, file_path: str) -> Dict:
        """加载JSON文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_routes_by_user_permissions(self, user_permissions: List[str]) -> List[Dict]:
        """根据用户权限生成路由配置
        
        根据传入的用户权限：
        [
            "system.user",
            "system.perm",
            "system.role",
            "system.grant",
            "permission.page",
            "permission.button.router",
            "permission.button.login"
        ]
        
        在base_routes.json中，根据用户权限过滤出需要的路由
        返回前端需要的路由
        """
        user_permissions = list(set(user_permissions))
        filtered_routes = []

        def has_permission(route: Dict, route_key: str) -> bool:
            """检查路由是否有权限访问"""
            # 检查路由key是否在用户权限中
            if route_key in user_permissions:
                return True
            
            # 检查父级权限
            parts = route_key.split('.')
            for i in range(len(parts) - 1):
                parent = '.'.join(parts[:i + 1])
                if parent in user_permissions:
                    return True
            
            # 检查子权限
            for permission in user_permissions:
                if permission.startswith(route_key):
                    return True
            
            return False

        def filter_route(route: Dict, route_key: str) -> Optional[Dict]:
            """过滤路由配置"""
            if not has_permission(route, route_key):
                return None

            filtered_route = route.copy()
            
            # 处理子路由
            if 'children' in filtered_route:
                filtered_children = {}
                for key, child in filtered_route['children'].items():
                    child_key = f"{route_key}.{key}" if route_key else key
                    filtered_child = filter_route(child, child_key)
                    if filtered_child:
                        filtered_children[key] = filtered_child
                if filtered_children:
                    filtered_route['children'] = list(filtered_children.values())
                else:
                    return None

            return filtered_route

        # 过滤路由
        for key, route in self.base_routes.items():
            filtered_route = filter_route(route, key)
            if filtered_route:
                filtered_routes.append(filtered_route)

        # color_logger.debug(f"用户权限: {user_permissions}")
        # color_logger.debug(f"过滤后的路由: {filtered_routes}")

        return filtered_routes

