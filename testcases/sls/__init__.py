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
    ORDER_TYPES = data["ORDER_TYPES"]
    ORDER_LINE_TYPES = data["ORDER_LINE_TYPES"]
    ORDER_TYPE_LINE_COMBINATIONS = data["ORDER_TYPE_LINE_COMBINATIONS"]
    
    
if __name__ == "__main__":
   sls_base = SlsBase()
   print(sls_base.ORDER_TYPES)
   print(sls_base.ORDER_LINE_TYPES)
   print(sls_base.ORDER_TYPE_LINE_COMBINATIONS)