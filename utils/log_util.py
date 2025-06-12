from loguru import logger
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
import logging

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.yaml_util import YamlUtil
from utils.exception_util import safe_config_load, ConfigException

class Loggers:
    """日志工具类（全类属性+类方法风格）"""
    _initialized = False
    _logger = logger
    _config = {}

    @classmethod
    def init(cls, config: Optional[Dict[str, Any]] = None):
        if not cls._initialized:
            # 默认配置
            default_config = {
                "level": "INFO",
                "rotation": "500 MB",
                "retention": "10 days",
                "encoding": "utf-8",
                "console_format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                "file_format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
            }
            if config:
                default_config.update(config)
            cls._config = default_config

            # 日志文件路径
        project_root = Path(__file__).parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        current_date = datetime.now().strftime('%Y_%m_%d')
        log_file = log_dir / f"log_{current_date}.log"
        
            # 配置 loguru
        logger.remove()
        logger.add(
            sys.stdout,
                format=cls._config["console_format"],
            level="DEBUG"
        )
        logger.add(
            str(log_file),
                rotation=cls._config["rotation"],
                retention=cls._config["retention"],
                format=cls._config["file_format"],
            level="DEBUG",
                encoding=cls._config["encoding"]
        )
        cls._logger = logger
        cls._initialized = True
    
    @staticmethod
    def info(msg: str, *args, **kwargs):
        logging.getLogger().info(msg, stacklevel=2, *args, **kwargs)
    
    @staticmethod
    def debug(msg: str, *args, **kwargs):
        logging.getLogger().debug(msg, stacklevel=2, *args, **kwargs)
    
    @staticmethod
    def warning(msg: str, *args, **kwargs):
        logging.getLogger().warning(msg, stacklevel=2, *args, **kwargs)
    
    @staticmethod
    def error(msg: str, *args, **kwargs):
        logging.getLogger().error(msg, stacklevel=2, *args, **kwargs)
    
    @staticmethod
    def critical(msg: str, *args, **kwargs):
        logger.critical(msg, *args, **kwargs)
    
    @staticmethod
    def exception(msg: str, *args, **kwargs):
        logger.opt(exception=True).exception(msg, *args, **kwargs)


if __name__ == '__main__':
    # 测试日志功能
    Loggers.init()
    Loggers.debug("调试消息")
    Loggers.info("普通消息")
    Loggers.warning("警告消息")
    Loggers.error("错误消息")
    Loggers.critical("严重错误消息")
    
    try:
        1/0
    except Exception as e:
        Loggers.exception("发生异常")

