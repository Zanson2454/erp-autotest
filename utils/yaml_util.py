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
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = cls._config_dir / file_path
        if not file_path.exists():
            logger.error(f"YAML文件不存在: {file_path}")
            raise FileNotFoundError(f"YAML文件不存在: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    logger.warning(f"YAML文件为空: {file_path}")
                    return {}
                logger.info(f"读取YAML文件: {file_path}")
                return config
        except yaml.YAMLError as e:
            logger.error(f"YAML解析错误: {str(e)}")
            raise

    @classmethod
    def get_project_config(cls, project: str, config_name: str) -> dict:
        """
        加载指定项目下的配置文件
        :param project: 项目名（如 'erp'）
        :param config_name: 配置文件名（如 'id_mappings.yaml'）
        :return: 配置字典
        """
        file_path = Path(project) / config_name
        return cls.read_yaml(str(file_path))

if __name__ == "__main__":
    yaml_util = YamlUtil()
    yaml_util.init()
    print(yaml_util.read_yaml("env/test.yaml"))
