import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))


class Loggers:
    """日志工具类（全类属性+类方法风格）
    
    优化说明：
    1. 控制台日志级别为INFO，减少输出
    2. 文件日志级别为DEBUG，保留详细信息
    3. diagnose/backtrace按需启用，通过DEBUG环境变量控制
    4. 移除未使用的导入，避免循环依赖
    5. 简化depth参数，统一日志行为
    """
    _initialized = False
    _logger = logger
    _config = {}

    @classmethod
    def init(cls, config: Optional[Dict[str, Any]] = None):
        """初始化日志系统
        
        Args:
            config: 可选的配置字典，可覆盖默认配置
                - console_level: 控制台日志级别（默认INFO）
                - file_level: 文件日志级别（默认DEBUG）
                - rotation: 日志轮转大小（默认500MB）
                - retention: 日志保留时间（默认10天）
                - enable_diagnose: 是否启用诊断模式（默认根据DEBUG环境变量）
        """
        if not cls._initialized:
            # 获取环境变量，判断是否为DEBUG模式
            is_debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
            
            # 默认配置
            default_config = {
                "console_level": "INFO",  # 控制台默认INFO级别，减少输出
                "file_level": "DEBUG",    # 文件默认DEBUG级别，保留详细信息
                "rotation": "500 MB",
                "retention": "10 days",
                "encoding": "utf-8",
                "enable_diagnose": is_debug,  # 仅 DEBUG 模式启用控制台诊断，避免堆栈刷屏
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
            logger.remove()  # 移除默认的处理器
            
            # 添加控制台处理器
            # 优化：仅在DEBUG模式或ERROR级别启用diagnose/backtrace
            logger.add(
                sys.stdout,
                format=cls._config["console_format"],
                level=cls._config["console_level"],
                diagnose=cls._config["enable_diagnose"],  # 按需启用，避免性能开销
                backtrace=cls._config["enable_diagnose"],  # 按需启用，避免日志过大
            )
            
            # 添加文件处理器
            # 文件始终保留完整诊断信息，用于问题排查
            logger.add(
                str(log_file),
                rotation=cls._config["rotation"],
                retention=cls._config["retention"],
                format=cls._config["file_format"],
                level=cls._config["file_level"],
                encoding=cls._config["encoding"],
                diagnose=True,   # 文件保留完整诊断信息
                backtrace=True,  # 文件保留完整回溯信息
            )
            
            cls._logger = logger
            cls._initialized = True
    
    @classmethod
    def _ensure_initialized(cls):
        """确保日志系统已初始化"""
        if not cls._initialized:
            cls.init()

    @classmethod
    def _compute_depth(cls, kwargs: Dict[str, Any]) -> int:
        """计算日志调用深度，确保日志源定位到业务调用方。"""
        custom_depth = kwargs.pop('depth', 0)
        try:
            custom_depth = int(custom_depth)
        except (TypeError, ValueError):
            custom_depth = 0
        # +1: 跳过当前封装方法，定位到真正的调用方
        return max(custom_depth, 0) + 1
    
    @classmethod
    def info(cls, msg: str, *args, **kwargs):
        """记录 INFO 级别日志
        
        Args:
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数（支持depth参数，向后兼容）
        """
        cls._ensure_initialized()
        depth = cls._compute_depth(kwargs)
        cls._logger.opt(depth=depth).info(msg, *args, **kwargs)
    
    @classmethod
    def debug(cls, msg: str, *args, **kwargs):
        """记录 DEBUG 级别日志
        
        Args:
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数（支持depth参数，向后兼容）
        """
        cls._ensure_initialized()
        depth = cls._compute_depth(kwargs)
        cls._logger.opt(depth=depth).debug(msg, *args, **kwargs)
    
    @classmethod
    def warning(cls, msg: str, *args, **kwargs):
        """记录 WARNING 级别日志
        
        Args:
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数（支持depth参数，向后兼容）
        """
        cls._ensure_initialized()
        depth = cls._compute_depth(kwargs)
        cls._logger.opt(depth=depth).warning(msg, *args, **kwargs)
    
    @classmethod
    def error(cls, msg: str, *args, **kwargs):
        """记录 ERROR 级别日志
        
        Args:
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数（支持depth参数，向后兼容）
        """
        cls._ensure_initialized()
        depth = cls._compute_depth(kwargs)
        # 兼容显式控制：error(..., exc_info=True/False)
        exc_info = kwargs.pop("exc_info", None)
        if exc_info is None:
            # 在 except 块中默认附带异常栈，提升排查效率
            exc_info = sys.exc_info()[0] is not None
        cls._logger.opt(depth=depth, exception=bool(exc_info)).error(msg, *args, **kwargs)
    
    @classmethod
    def critical(cls, msg: str, *args, **kwargs):
        """记录 CRITICAL 级别日志
        
        Args:
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数（支持depth参数，向后兼容）
        """
        cls._ensure_initialized()
        depth = cls._compute_depth(kwargs)
        cls._logger.opt(depth=depth).critical(msg, *args, **kwargs)
    
    @classmethod
    def exception(cls, msg: str, *args, **kwargs):
        """记录异常日志（自动包含堆栈信息）
        
        Args:
            msg: 日志消息
            *args: 格式化参数
            **kwargs: 额外参数（支持depth参数，向后兼容）
        
        Note:
            此方法会自动记录当前异常的完整堆栈信息
        """
        cls._ensure_initialized()
        depth = cls._compute_depth(kwargs)
        cls._logger.opt(depth=depth, exception=True).error(msg, *args, **kwargs)


if __name__ == '__main__':
    # 测试日志功能
    print("=" * 60)
    print("测试日志功能（默认模式：控制台INFO，文件DEBUG）")
    print("=" * 60)
    
    Loggers.init()
    Loggers.debug("这是调试消息（控制台不显示，仅文件记录）")
    Loggers.info("这是普通消息")
    Loggers.warning("这是警告消息")
    Loggers.error("这是错误消息")
    Loggers.critical("这是严重错误消息")
    
    print("\n" + "=" * 60)
    print("测试异常日志")
    print("=" * 60)
    
    try:
        result = 1 / 0
    except Exception:
        Loggers.exception("发生除零异常")
    
    print("\n" + "=" * 60)
    print("提示：设置环境变量 DEBUG=true 可启用详细诊断模式")
    print("示例：DEBUG=true python utils/log_util.py")
    print("=" * 60)
