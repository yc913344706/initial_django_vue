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
        color_logger.debug(f"用户权限: {user_permissions}")
        filtered_routes = []

        def has_permission(route_key: str) -> bool:
            """检查路由是否有权限访问 - 精确匹配，不考虑父子权限关系"""
            return route_key in user_permissions

        def filter_route(route: Dict, route_key: str) -> Optional[Dict]:
            """过滤路由配置"""
            filtered_route = route.copy()
            
            # 处理子路由
            has_accessible_children = False
            if 'children' in filtered_route:
                filtered_children = {}
                for key, child in filtered_route['children'].items():
                    child_key = f"{route_key}.{key}" if route_key else key
                    filtered_child = filter_route(child, child_key)
                    if filtered_child:
                        filtered_children[key] = filtered_child
                        has_accessible_children = True
                if filtered_children:
                    filtered_route['children'] = list(filtered_children.values())

            # 如果路由本身有权限 或者 有权限访问的子路由，则返回该路由
            route_has_permission = has_permission(route_key)
            color_logger.debug(f"检查权限: {route}, {route_key}, 有权限: {route_has_permission}, 有子路由权限: {has_accessible_children}")
            
            if route_has_permission or has_accessible_children:
                color_logger.debug(f"有权限访问: {route}, {route_key}")
                return filtered_route
            else:
                color_logger.debug(f"无权限访问: {route}, {route_key}")
                return None

        # 过滤路由
        for key, route in self.base_routes.items():
            filtered_route = filter_route(route, key)
            if filtered_route:
                filtered_routes.append(filtered_route)

        # color_logger.debug(f"用户权限: {user_permissions}")
        # color_logger.debug(f"过滤后的路由: {filtered_routes}")

        return filtered_routes

