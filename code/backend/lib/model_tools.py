from django.db import models
import uuid
from lib.log import color_logger
from copy import deepcopy

class BaseManager(models.Manager):
    """
    自定义管理器，用于默认过滤掉 is_del=True 的数据
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_del=False)

class BaseModel(models.Model):
    """
    通用的基类模型，包含 is_del 字段和自定义管理器
    """
    uuid = models.UUIDField(primary_key=True, auto_created=True, default=uuid.uuid4, editable=False)
    is_del = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # 自定义管理器
    objects = BaseManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self):
        """
        覆盖 delete 方法，实现软删除
        """
        color_logger.debug(f"删除模型: {self.__class__.__name__} {self.uuid}")
        self.is_del = True
        self.save()


class BaseTypeTree(BaseModel):
    """通用类型树模型
    
    使用示例:
    1. 工单类型树:
    {
        "code": "incident",  # 业务编码，用于程序引用
        "name": "故障",      # 显示名称
        "children": [...]
    }
    """
    code = models.CharField(max_length=64, unique=True, verbose_name='类型编码')
    name = models.CharField(max_length=64, verbose_name='类型名称')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父级类型')
    level = models.IntegerField(default=1, verbose_name='层级')
    sort = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        abstract = True

    def get_full_path(self):
        """获取完整路径"""
        if not self.parent:
            return [{'code': self.code, 'name': self.name}]
        return self.parent.get_full_path() + [{'code': self.code, 'name': self.name}]

    @classmethod
    def import_from_json(cls, json_data):
        """从JSON导入类型树"""
        def create_node(data, parent=None, level=1):
            node = cls.objects.create(
                code=data['code'],
                name=data['name'],
                parent=parent,
                level=level
            )
            for idx, child in enumerate(data.get('children', [])):
                create_node(child, node, level + 1)
            return node

        return create_node(json_data)
    
    @classmethod
    def build_tree(cls, node, **kwargs):
        """构建类型树
        
        Args:
            node: 节点对象
            **kwargs: 可选参数
                need_del (bool): 是否包含已删除节点
                extra_fields (list): 需要额外包含的字段列表
        """
        data = {
            'uuid': node.uuid,
            'code': node.code,
            'name': node.name,
        }
        
        # 处理额外字段
        extra_fields = kwargs.get('extra_fields', [])
        if extra_fields:
            for field in extra_fields:
                data[field] = getattr(node, field)

        # 处理删除标记
        need_del = kwargs.get('need_del', False)
        if need_del:
            data['is_del'] = node.is_del
            children = cls.all_objects.filter(parent=node)
        else:
            children = cls.objects.filter(parent=node)
        
        if children:
            data['children'] = [cls.build_tree(child, **kwargs) for child in children]
        return data

    @classmethod
    def get_root_type(cls, need_del=False):
        """获取根类型"""
        if need_del:
            return cls.all_objects.filter(parent__isnull=True).first()
        else:
            return cls.objects.filter(parent__isnull=True).first()

    @classmethod
    def export_to_json(cls, need_del=False, **kwargs):
        """导出类型树为JSON"""
        root_type = cls.get_root_type(need_del)
        assert root_type is not None, "未找到根类型树"

        kwargs['need_del'] = need_del
        return cls.build_tree(root_type, **kwargs)
    
    def get_type_all_parent_type(self):
        """获取所有父级类型"""
        parent_type_list = []
        parent_type = self.parent

        while parent_type:
            parent_type_list.append(parent_type)
            parent_type = parent_type.parent

        return list(parent_type_list)
    
    @classmethod
    def get_type_all_children_uuid_list(cls, node, **kwargs):
        """获取所有子级类型"""
        node_type_tree = cls.build_tree(node, **kwargs)

        def _get_one_node_tree_all_uuids(node_tree):
            res = []
            res.append(node_tree.get('uuid'))
            _children_type_list = node_tree.get('children', [])
            if _children_type_list:
                for child in _children_type_list:
                    res.extend(_get_one_node_tree_all_uuids(child))
            return res

        children_type_list = _get_one_node_tree_all_uuids(node_type_tree)

        return list(children_type_list)
    
    @classmethod
    def update_nodes(cls, type_tree, extra_fields={}):
        """更新节点"""
        # # 获取所有现有节点
        existing_nodes = {
            node.code: node 
            for node in cls.all_objects.all()
        }
        
        # 递归更新或创建节点
        def update_or_create_node(
                node_data, 
                parent=None, 
                level=0, 
                extra_fields={}
            ):
            code = node_data['code']
            name = node_data['name']
            children = node_data.get('children', [])

            update_dict = {
                'name': name,
                'parent': parent,
                'level': level,
            }
            if extra_fields:
                for field, default_value in extra_fields.items():
                    update_dict[field] = node_data.get(field, default_value)
            
            if code in existing_nodes:
                color_logger.debug(f"更新现有节点: {code}, {name}, {children}")
                # 更新现有节点
                node = existing_nodes[code]
                # 只更新可变属性,保持 code 和 uuid 不变
                for key, value in update_dict.items():
                    setattr(node, key, value)

                node.is_del = False
                # node.name = name
                # node.parent = parent
                # node.level = level
                node.save()
                # 从现有节点字典中移除已处理的节点
                del existing_nodes[code]
            else:
                color_logger.debug(f"创建新节点: {code}, {name}, {children}")
                create_dict = {
                    'code': code,
                }
                create_dict.update(update_dict)
                
                # 创建新节点
                node = cls.objects.create(**create_dict)
                # node = cls.objects.create(
                #     code=code,
                #     name=name,
                #     parent=parent,
                #     level=level
                # )
            
            # 递归处理子节点
            for child in children:
                update_or_create_node(
                    child, parent=node, level=level+1, extra_fields=extra_fields)
        
        # 开始更新
        update_or_create_node(type_tree, extra_fields=extra_fields)
        
        # 处理未使用的节点
        unused_nodes = list(existing_nodes.values())
        if unused_nodes:
            # 只删除未被引用的节点
            for node in unused_nodes:
                color_logger.debug(f"删除未被引用的节点: {node.code}")
                # 检查节点是否被工单引用
                node.delete()
                # if not WkWxOrder.objects.filter(type=node).exists():
                #     node.delete()
                # else:
                #     color_logger.warning(f"类型节点 {node.code} 已被工单引用,跳过删除")
        
        
