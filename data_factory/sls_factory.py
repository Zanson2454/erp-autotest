from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))


from data_factory.base import DataFactory
from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil
from utils.mysql_util import DBManager

class SlsDataFactory:
    """
    销售（SLS）专用数据工厂：负责初始化销售域相关的业务常量数据，结构与 sc.json 一致。
    """
    
    sls_init_path = project_root / "testdata" / "init" / "sls_init.yaml"
    sls_cache_path = project_root / "testdata" / "cache" / "sls_cache.json"
    read_yaml = YamlUtil.read_yaml
    @classmethod
    def cache_sls_data(cls):
        """
        读取 sls_init.yaml，执行 SQL，生成业务常量结构并写入 cache/sls_cache.json
        结构与 sc.json 一致。
        """
        cls.sls_cache_path.parent.mkdir(exist_ok=True)
        data_factory = DataFactory() 
        db_config = data_factory.get_env_config()['database']['erp_db']
        DBManager.init(db_config)
        sls_config = cls.read_yaml(str(cls.sls_init_path))["sls_config"]
        result = {}
        
        # 1. 订单类型
        order_types = {}
        so_type_id_map = {}
        rows = DBManager.query(sls_config["ORDER_TYPES"]["sql"])
        for row in rows:
            code = row.get("so_type_code") or row.get("so_type_id") or row.get("id")
            name = row.get("so_type_name") or row.get("name")
            so_type_id = row.get("id")
            if code and name:
                order_types[code] = name
            if so_type_id:
                so_type_id_map[so_type_id] = {"so_type_code": code, "so_type_name": name}
        result["ORDER_TYPES"] = order_types
        
        # 2. 订单行类型
        order_line_types = {}
        so_item_type_id_map = {}
        rows = DBManager.query(sls_config["ORDER_LINE_TYPES"]["sql"])
        for row in rows:
            code = row.get("so_item_type_code") or row.get("so_item_type_id") or row.get("id")
            name = row.get("so_item_type_name") or row.get("name")
            so_item_type_id = row.get("id")
            if code and name:
                order_line_types[code] = name
            if so_item_type_id:
                so_item_type_id_map[so_item_type_id] = {"so_item_type_code": code, "so_item_type_name": name}
        result["ORDER_LINE_TYPES"] = order_line_types
        
        # 3. 订单行类型组
        so_item_type_group_map = {}
        if "ORDER_ITEM_TYPE_GROUP" in sls_config:
            rows = DBManager.query(sls_config["ORDER_ITEM_TYPE_GROUP"]["sql"])
            for row in rows:
                group_id = row.get("id")
                group_name = row.get("so_item_type_group_name")
                if group_id:
                    so_item_type_group_map[group_id] = group_name
        # 4. 物料类型
        mat_type_map = {}
        if "MATERIAL_TYPE" in sls_config:
            rows = DBManager.query(sls_config["MATERIAL_TYPE"]["sql"])
            for row in rows:
                mat_type_id = row.get("id")
                mat_type_name = row.get("mat_type_name")
                if mat_type_id:
                    mat_type_map[mat_type_id] = mat_type_name
        # 5. 订单类型和订单行类型分配
        order_type_line_combos = {}
        rows = DBManager.query(sls_config["ORDER_TYPE_LINE_COMBINATIONS"]["sql"])
        for row in rows:
            so_item_type_id = row.get("so_item_type_id")
            if not so_item_type_id:
                continue
            detm_info = {
                "so_type_id": row.get("so_type_id"),
                "so_type_code": so_type_id_map.get(row.get("so_type_id"), {}).get("so_type_code"),
                "so_type_name": so_type_id_map.get(row.get("so_type_id"), {}).get("so_type_name"),
                "mat_type_id": row.get("mat_type_id"),
                "mat_type_name": mat_type_map.get(row.get("mat_type_id")),
                "parent_so_item_type_id": row.get("parent_so_item_type_id"),
                "parent_so_item_type_name": so_item_type_id_map.get(row.get("parent_so_item_type_id"), {}).get("so_item_type_name"),
                "usage_type": row.get("usage_type"),
                "so_item_type_group_id": row.get("so_item_type_group_id"),
                "so_item_type_group_name": so_item_type_group_map.get(row.get("so_item_type_group_id"))
            }
            order_type_line_combos.setdefault(so_item_type_id, []).append(detm_info)
        # 转换为 list 格式，提升可读性
        order_type_line_combos_list = [
            {
                "so_item_type_id": so_item_type_id,
                "so_item_type_code": so_item_type_id_map.get(so_item_type_id, {}).get("so_item_type_code"),
                "so_item_type_name": so_item_type_id_map.get(so_item_type_id, {}).get("so_item_type_name"),
                "so_item_detm_info": detm_infos
            }
            for so_item_type_id, detm_infos in order_type_line_combos.items()
        ]
        result["ORDER_TYPE_LINE_COMBINATIONS"] = order_type_line_combos_list
        CacheUtil.init(str(cls.sls_cache_path.parent))
        CacheUtil.set("sls_cache", result)
        print(result)
        return result
    
    def get_stnd_so(slef):
        """
        获取标准销售订单
        """
        pass

if __name__ == "__main__":
    SlsDataFactory.cache_sls_data() 