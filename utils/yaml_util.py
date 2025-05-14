import yaml
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger

class YamlUtil:
    """YAML 配置管理工具类
    
    使用示例:
        # 基础用法
        yaml_util = YamlUtil()
        config = yaml_util.read_yaml("env/test.yaml")
        
        # 自定义配置目录
        yaml_util = YamlUtil(config_dir="custom_config")
        config = yaml_util.read_yaml("settings.yaml")
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_dir: str = "config"):
        """初始化YAML工具类
        
        Args:
            config_dir: 配置目录路径，默认为"config"
        """
        if not hasattr(self, 'initialized'):
            self.config_dir = Path(config_dir)
            self.initialized = True

    def read_yaml(self, file_path: str) -> Dict[str, Any]:
        """读取YAML文件
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            Dict[str, Any]: 解析后的配置数据
            
        Raises:
            FileNotFoundError: 文件不存在时抛出
            yaml.YAMLError: YAML解析错误时抛出
        """
        file_path = self.config_dir / file_path
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


