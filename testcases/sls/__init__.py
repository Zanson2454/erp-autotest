from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from data_factory.sls_factory import SlsDataFactory
from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil
from testcases.comm.base_test import BaseTest

class SlsBase(BaseTest):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 路径
        cls.sls_api_path_yaml = project_root / "testdata" / "sls" / "sls_api_path.yaml"
        cls.sls_prams_path_yaml = project_root / "testdata" / "sls" / "sls_api_params.yaml"
        cls.sls_init_path = project_root / "testdata" / "init" / "sls_init.yaml"
        cls.sls_cache_path = project_root / "testdata" / "cache" / "sls_cache.json"
        cls.sls_cache_dir = cls.sls_cache_path.parent

        # 读取API配置
        cls.sls_api_paths = YamlUtil.read_yaml(str(cls.sls_api_path_yaml))["销售订单"]
        cls.sls_api_params = YamlUtil.read_yaml(str(cls.sls_prams_path_yaml))["api_params"]

        # 缓存初始化
        CacheUtil.init(str(cls.sls_cache_dir))
        if not cls.sls_cache_path.exists():
            SlsDataFactory.cache_sls_data()
        data = CacheUtil.get("sls_cache")
        if not data:
            SlsDataFactory.cache_sls_data()
            data = CacheUtil.get("sls_cache")
            if not data:
                raise RuntimeError("sls_cache.json 读取失败或内容为空，请检查数据工厂写入逻辑和缓存文件内容！")

        cls.ORDER_TYPES = data["ORDER_TYPES"]
        cls.ORDER_LINE_TYPES = data["ORDER_LINE_TYPES"]
        cls.ORDER_TYPE_LINE_COMBINATIONS = data["ORDER_TYPE_LINE_COMBINATIONS"]

        # 提取ID映射
        cls.ORDER_TYPE_IDS = {}
        cls.ORDER_LINE_TYPE_IDS = {}
        for combo in cls.ORDER_TYPE_LINE_COMBINATIONS:
            order_line_type_code = combo.get("so_item_type_code")
            order_line_type_id = combo.get("so_item_type_id")
            if order_line_type_code and order_line_type_id:
                cls.ORDER_LINE_TYPE_IDS[order_line_type_code] = order_line_type_id
            for detm_info in combo.get("so_item_detm_info", []):
                order_type_code = detm_info.get("so_type_code")
                order_type_id = detm_info.get("so_type_id")
                if order_type_code and order_type_id:
                    cls.ORDER_TYPE_IDS[order_type_code] = order_type_id

    @classmethod
    def get_order_type_id(cls, order_type_code: str):
        """通过订单类型编码获取订单类型ID"""
        if order_type_code in cls.ORDER_TYPE_IDS:
            return cls.ORDER_TYPE_IDS[order_type_code]
        raise ValueError(f"未找到订单类型: {order_type_code}")

    @classmethod
    def get_order_type_name(cls, order_type_code: str):
        """通过订单类型编码获取订单类型名称"""
        return cls.ORDER_TYPES.get(order_type_code) or f"未找到订单类型: {order_type_code}"

    @classmethod
    def get_order_line_type_id(cls, order_line_type_code: str):
        """通过订单行类型编码获取订单行类型ID"""
        if order_line_type_code in cls.ORDER_LINE_TYPE_IDS:
            return cls.ORDER_LINE_TYPE_IDS[order_line_type_code]
        raise ValueError(f"未找到订单行类型: {order_line_type_code}")

    @classmethod
    def get_order_line_type_name(cls, order_line_type_code: str):
        """通过订单行类型编码获取订单行类型名称"""
        return cls.ORDER_LINE_TYPES.get(order_line_type_code) or f"未找到订单行类型: {order_line_type_code}"
    
if __name__ == "__main__":
    SlsBase.setup_class()
    print(SlsBase.ORDER_TYPES)
    print(SlsBase.ORDER_LINE_TYPES)
    print(SlsBase.ORDER_TYPE_LINE_COMBINATIONS)