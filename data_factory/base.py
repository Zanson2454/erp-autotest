from pathlib import Path
from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil

class DataFactory:
    """
    数据工厂：统一管理测试用例所需的业务数据，支持数据获取、造数、清理等能力。
    """
    # 缓存目录
    cache_dir = Path(__file__).parent.parent / 'testdata' / 'cache'
    cache = CacheUtil(cache_dir)
    yaml_util = YamlUtil()

    @classmethod
    def get_base_data(cls, key, module='gen'):
        """
        获取基础数据（如物料、客户、组织等），优先从缓存读取。
        :param key: 数据键名，如 'material', 'customer'
        :param module: 业务模块名，对应 testdata/init/{module}.yaml
        :return: 数据字典
        """
        cache_key = f'{module}_cache'
        data = cls.cache.get(cache_key)
        if not data:
            # 读取YAML并写入缓存
            yaml_path = Path(__file__).parent.parent / 'testdata' / 'init' / f'{module}.yaml'
            data = cls.yaml_util.read_yaml(yaml_path)
            cls.cache.set(cache_key, data)
        return data.get(key)

    @classmethod
    def get_sales_order(cls, status="EFFECTIVE", so_type="STND", **kwargs):
        """
        获取指定状态的标准销售订单（骨架方法，需结合实际业务实现）
        :param status: 订单状态
        :param so_type: 订单类型
        :param kwargs: 其他业务参数
        :return: 订单数据字典
        """
        # TODO: 1. 查缓存/数据库 2. 若无则自动造数 3. 返回订单数据
        pass

    @classmethod
    def create_purchase_order(cls, material_id, qty, warehouse, **kwargs):
        """
        创建采购订单并入库（骨架方法，需结合实际业务实现）
        :param material_id: 物料ID
        :param qty: 数量
        :param warehouse: 仓库标识
        :param kwargs: 其他业务参数
        :return: 采购单/入库单数据字典
        """
        # TODO: 1. 造采购订单 2. 造入库单 3. 返回相关数据
        pass

    @classmethod
    def clear_test_data(cls, data_type, **kwargs):
        """
        清理指定类型的测试数据（骨架方法）
        :param data_type: 数据类型，如 'sales_order', 'purchase_order'
        :param kwargs: 其他参数
        """
        # TODO: 实现数据清理逻辑
        pass 