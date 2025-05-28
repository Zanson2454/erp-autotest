from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))


from data_factory.sls_factory import SlsDataFactory
from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil

class SlsBase:
    read_yaml = YamlUtil.read_yaml
    sls_api_path_yaml = project_root / "testdata" / "sls" / "sls_api_path.yaml"
    sls_prams_path_yaml = project_root / "testdata" / "sls" / "sls_api_params.yaml"
    sls_init_path= project_root / "testdata" / "init" / "sls_init.yaml"
    sls_cache_path = project_root / "testdata" / "cache" / "sls_cache.json"
    
    sls_api_paths = read_yaml(str(sls_api_path_yaml))["销售订单"]
    # print(sls_api_paths)
    sls_api_params = read_yaml(str(sls_prams_path_yaml))["api_params"]
    # print(sls_api_params)
    
    sls_cache_dir = sls_cache_path.parent
    if not sls_cache_path.exists():
        SlsDataFactory.cache_sls_data()

    CacheUtil.init(str(sls_cache_dir))
    data = CacheUtil.get("sls_cache")
    if not data:
        # 缓存过期或读取失败，自动刷新
        SlsDataFactory.cache_sls_data()
        data = CacheUtil.get("sls_cache")
        if not data:
            raise RuntimeError("sls_cache.json 读取失败或内容为空，请检查数据工厂写入逻辑和缓存文件内容！")
    ORDER_TYPES = data["ORDER_TYPES"]
    ORDER_LINE_TYPES = data["ORDER_LINE_TYPES"]
    ORDER_TYPE_LINE_COMBINATIONS = data["ORDER_TYPE_LINE_COMBINATIONS"]
    
    # 从 ORDER_TYPE_LINE_COMBINATIONS 中提取订单类型和订单行类型的 ID
    ORDER_TYPE_IDS = {}
    ORDER_LINE_TYPE_IDS = {}
    
    for combo in ORDER_TYPE_LINE_COMBINATIONS:
        # 提取订单行类型 ID
        order_line_type_code = combo.get("so_item_type_code")
        order_line_type_id = combo.get("so_item_type_id")
        if order_line_type_code and order_line_type_id:
            ORDER_LINE_TYPE_IDS[order_line_type_code] = order_line_type_id
        
        # 提取订单类型 ID
        for detm_info in combo.get("so_item_detm_info", []):
            order_type_code = detm_info.get("so_type_code")
            order_type_id = detm_info.get("so_type_id")
            if order_type_code and order_type_id:
                ORDER_TYPE_IDS[order_type_code] = order_type_id
    
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
   sls_base = SlsBase()
   print(sls_base.ORDER_TYPES)
   print(sls_base.ORDER_LINE_TYPES)
   print(sls_base.ORDER_TYPE_LINE_COMBINATIONS)