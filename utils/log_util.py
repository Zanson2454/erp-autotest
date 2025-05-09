from loguru import logger
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.yaml_util import YamlUtil
from utils.exception_util import safe_config_load, ConfigException

class Loggers:
    """日志工具类，提供统一的日志记录功能
    
    主要功能：
    1. 支持控制台和文件日志输出
    2. 支持日志级别动态配置
    3. 支持日志文件自动轮转
    4. 支持日志格式自定义
    5. 支持异常日志记录
    
    使用示例：
    ```python
    # 创建日志实例
    log = Loggers()
    
    # 记录不同级别的日志
    log.debug("调试信息")
    log.info("普通信息")
    log.warning("警告信息")
    log.error("错误信息")
    log.critical("严重错误信息")
    ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化日志工具类
        
        Args:
            config: 日志配置，如果为None则使用默认配置
        """
        self.config = self._load_config(config)
        self._setup_logger()
    
    @safe_config_load(error_message="日志配置加载失败")
    def _load_config(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """加载日志配置
        
        Args:
            config: 自定义配置
            
        Returns:
            Dict[str, Any]: 日志配置
        """
        if config:
            return config
            
        # 从配置文件加载
        yaml_config = YamlUtil().get_logging_config()
        
        # 默认配置
        default_config = {
            "path": "logs",
            "level": "INFO",
            "rotation": "00:00",
            "retention": "7 days",
            "encoding": "utf-8",
            "console_format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            "file_format": "<yellow>{time:YYYY-MM-DD HH:mm:ss.SSS}</yellow> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
        }
        
        # 合并配置
        return {**default_config, **yaml_config}
    
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        # 确保日志目录存在
        log_path = Path(self.config["path"])
        log_path.mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名
        log_file = log_path / f"log_{datetime.now().strftime('%Y_%m_%d')}.log"
        
        # 移除所有已存在的处理器
        logger.remove()
        
        # 添加控制台输出
        logger.add(
            sys.stderr,
            format=self.config["console_format"],
            level="DEBUG",
            filter=lambda record: record["extra"].get("console", True),
            backtrace=True,
            diagnose=True
        )
        
        # 添加文件输出
        logger.add(
            str(log_file),
            format=self.config["file_format"],
            level=self.config["level"],
            rotation=self.config["rotation"],
            retention=self.config["retention"],
            encoding=self.config["encoding"],
            enqueue=True,
            backtrace=True,
            diagnose=True
        )
    
    @staticmethod
    def info(msg: str, *args: Any, **kwargs: Any) -> None:
        """记录信息级别日志
        
        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        logger.info(msg, *args, **kwargs)
    
    @staticmethod
    def debug(msg: str, *args: Any, **kwargs: Any) -> None:
        """记录调试级别日志
        
        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        logger.debug(msg, *args, **kwargs)
    
    @staticmethod
    def warning(msg: str, *args: Any, **kwargs: Any) -> None:
        """记录警告级别日志
        
        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        logger.warning(msg, *args, **kwargs)
    
    @staticmethod
    def error(msg: str, *args: Any, **kwargs: Any) -> None:
        """记录错误级别日志
        
        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        logger.error(msg, *args, **kwargs)
    
    @staticmethod
    def critical(msg: str, *args: Any, **kwargs: Any) -> None:
        """记录严重错误级别日志
        
        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        logger.critical(msg, *args, **kwargs)
    
    @staticmethod
    def exception(msg: str, *args: Any, **kwargs: Any) -> None:
        """记录异常日志
        
        Args:
            msg: 日志消息
            *args: 位置参数
            **kwargs: 关键字参数
        """
        logger.opt(exception=True).exception(msg, *args, **kwargs)


if __name__ == '__main__':
    # 测试日志功能
    log = Loggers()
    log.debug("调试消息")
    log.info("普通消息")
    log.warning("警告消息")
    log.error("错误消息")
    log.critical("严重错误消息")
    
    try:
        1/0
    except Exception as e:
        log.exception("发生异常")

