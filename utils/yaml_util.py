import yaml
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger

# 优先使用 C 扩展加载器，大文件解析可提速 10-30 倍
try:
    from yaml import CSafeLoader as _YamlLoader
except ImportError:
    from yaml import SafeLoader as _YamlLoader


class YamlUtil:
    """YAML 配置管理工具类（全类属性+类方法风格）
    
    使用示例:
        YamlUtil.init(config_dir="config")
        config = YamlUtil.read_yaml("env/test.yaml")
    """
    _config_dir = Path("config")
    _initialized = False
    _cache: Dict[str, Any] = {}  # 配置缓存
    _max_cache_size: int = 50   # 最大缓存文件数

    @classmethod
    def clear_cache(cls) -> None:
        """清空配置缓存"""
        cls._cache.clear()
        logger.info("YAML配置缓存已清空")

    @classmethod
    def set_max_cache_size(cls, max_size: int) -> None:
        """设置最大缓存数量"""
        cls._max_cache_size = max_size
        logger.info(f"YAML配置缓存最大数量设置为: {max_size}")


    @classmethod
    def init(cls, config_dir: str = "config"):
        if not cls._initialized:
            cls._config_dir = Path(config_dir)
            cls._initialized = True

    @classmethod
    def read_yaml(cls, file_path: Any, use_cache: bool = True) -> Dict[str, Any]:
        # 支持绝对路径和相对路径
        file_path = Path(file_path)
        if not file_path.is_absolute():
            file_path = cls._config_dir / file_path
        
        # 转换为字符串作为缓存键
        cache_key = str(file_path.resolve())
        
        # 使用缓存
        if use_cache and cache_key in cls._cache:
            logger.debug(f"从缓存读取YAML文件: {file_path}")
            return cls._cache[cache_key]
        
        # 缓存大小限制：超过上限时清空旧缓存
        if use_cache and len(cls._cache) >= cls._max_cache_size:
            logger.warning(f"YAML配置缓存已达到上限({cls._max_cache_size})，清空缓存")
            cls._cache.clear()
        
        if not file_path.exists():
            logger.error(f"YAML文件不存在: {file_path}")
            raise FileNotFoundError(f"YAML文件不存在: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.load(f, Loader=_YamlLoader)
                if config is None:
                    logger.warning(f"YAML文件为空: {file_path}")
                    return {}
                logger.info(f"读取YAML文件: {file_path}")
                # 存入缓存
                if use_cache:
                    cls._cache[cache_key] = config
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