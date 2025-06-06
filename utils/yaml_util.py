import yaml
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger

class YamlUtil:
    """YAML 配置管理工具类（全类属性+类方法风格）
    
    使用示例:
        YamlUtil.init(config_dir="config")
        config = YamlUtil.read_yaml("env/test.yaml")
    """
    _config_dir = Path("config")
    _initialized = False

    @classmethod
    def init(cls, config_dir: str = "config"):
        if not cls._initialized:
            cls._config_dir = Path(config_dir)
            cls._initialized = True

    @classmethod
    def read_yaml(cls, file_path: str) -> Dict[str, Any]:
        # 支持绝对路径和相对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(cls._config_dir, file_path)
        print(f"[DEBUG] 实际加载的YAML路径: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"YAML文件不存在: {file_path}")
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                print(f"[DEBUG] 加载YAML内容repr: {repr(data)}")
                return data if data else {}
        except Exception as e:
            logger.error(f"读取YAML文件失败: {file_path}, 错误: {e}")
            return {}



if __name__ == "__main__":
    yaml_util = YamlUtil()
    yaml_util.init()
    print(yaml_util.read_yaml("env/test.yaml"))
