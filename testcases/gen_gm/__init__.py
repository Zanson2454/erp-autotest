from pathlib import Path
from utils.yaml_util import YamlUtil

def init_gen_gm_config(cls):
    """初始化 gen_gm 模块的通用配置
    
    Args:
        cls: 测试类实例
    """
    # 初始化 API 配置
    project_root = Path(__file__).resolve().parent.parent.parent
    api_path_yaml = project_root / "testdata" / "gen_gm" / "gm_api_path.yaml"
    api_params_yaml = project_root / "testdata" / "gen_gm" / "gm_api_params.yaml"
    
    # 读取 API 配置
    cls.apis = YamlUtil.read_yaml(str(api_path_yaml))["apis"]
    cls.api_params = YamlUtil.read_yaml(str(api_params_yaml))["api_params"]
