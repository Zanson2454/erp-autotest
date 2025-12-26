import traceback
import inspect
import sys
from typing import Any, Callable, Optional, Type, Union, Tuple, Dict
from functools import wraps
from loguru import logger
from datetime import datetime

# ============================================================================
# 异常类定义
# ============================================================================

class TestException(Exception):
    """测试异常基类"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)

    def __str__(self) -> str:
        """返回格式化的异常信息"""
        error_info = [
            f"错误时间: {self.timestamp}",
            f"错误信息: {self.message}"
        ]
        if self.details:
            error_info.append("错误详情:")
            for key, value in self.details.items():
                # 限制详情长度，避免日志过长
                value_str = str(value)
                if len(value_str) > 200:
                    value_str = value_str[:200] + "..."
                error_info.append(f"  {key}: {value_str}")
        return "\n".join(error_info)

    def to_dict(self) -> Dict[str, Any]:
        """将异常信息转换为字典格式"""
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "details": self.details
        }

class APIException(TestException):
    """API调用异常"""
    pass

class DatabaseException(TestException):
    """数据库操作异常"""
    pass

class ValidationException(TestException):
    """数据验证异常"""
    pass

class ConfigException(TestException):
    """配置相关异常"""
    pass

class FileException(TestException):
    """文件操作异常"""
    pass

class DataFactoryException(TestException):
    """数据工厂异常（用于测试数据准备失败）"""
    pass

class TimeoutException(TestException):
    """超时异常（用于异步等待超时）"""
    pass

class AssertionException(TestException):
    """断言异常（用于测试断言失败）"""
    pass

class LoginException(TestException):
    """登录异常（用于登录失败场景）"""
    pass

class CacheException(TestException):
    """缓存异常（用于缓存操作失败）"""
    pass

# ============================================================================
# 辅助函数
# ============================================================================

def _get_caller_info(include_locals: bool = False) -> Dict[str, Any]:
    """
    获取调用者信息
    
    Args:
        include_locals: 是否包含局部变量（默认False，避免性能问题）
    
    Returns:
        调用者信息字典
    """
    frame = inspect.currentframe()
    if frame is None:
        return {}
    
    # 获取调用栈信息
    caller_frame = frame.f_back
    if caller_frame is None:
        return {}
    
    # 获取调用者信息
    caller_info = {
        "filename": caller_frame.f_code.co_filename,
        "line_number": caller_frame.f_lineno,
        "function": caller_frame.f_code.co_name,
    }
    
    # 仅在需要时记录 locals（性能优化）
    if include_locals:
        caller_info["locals"] = {
            k: str(v)[:100] for k, v in caller_frame.f_locals.items() 
            if not k.startswith('_') and not callable(v)
        }
    
    return caller_info

def _build_simple_context(
    func: Callable,
    args: tuple,
    kwargs: dict,
    error: Exception,
    error_key: str,
    error_message: str,
    log_args: bool = False
) -> Dict[str, Any]:
    """
    构建简化的错误上下文信息
    
    Args:
        func: 函数对象
        args: 位置参数
        kwargs: 关键字参数
        error: 异常对象
        error_key: 错误键名（如 "api_error", "db_error"）
        error_message: 错误消息
        log_args: 是否记录参数（默认False，避免日志过大）
    
    Returns:
        简化的上下文字典
    """
    context = {
        "function": func.__name__,
        "module": func.__module__,
        "error_type": type(error).__name__,
        error_key: {
            "message": error_message,
            "original_error": str(error)[:200]  # 限制长度
        }
    }
    
    # 可选：仅在需要时记录参数（性能优化）
    if log_args:
        context["arguments"] = {
            "args": [str(arg)[:100] for arg in args[:3]],  # 限制数量和长度
            "kwargs": {k: str(v)[:100] for k, v in list(kwargs.items())[:5]}  # 限制数量和长度
        }
    
    return context

# ============================================================================
# 装饰器工厂函数（消除重复代码）
# ============================================================================

def _create_exception_decorator(
    exception_class: Type[TestException],
    error_key: str,
    default_message: str
) -> Callable:
    """
    创建异常装饰器的工厂函数
    
    Args:
        exception_class: 异常类
        error_key: 错误键名
        default_message: 默认错误消息
    
    Returns:
        装饰器函数
    """
    def decorator(
        error_message: str = default_message,
        reraise: bool = True,
        log_level: str = "ERROR",
        log_args: bool = False
    ) -> Callable:
        def wrapper(func: Callable) -> Callable:
            @wraps(func)
            def inner(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 构建简化的上下文信息
                    context = _build_simple_context(
                        func, args, kwargs, e, error_key, error_message, log_args
                    )
                    
                    # 使用 logger.opt(exception=True) 自动记录堆栈，避免重复
                    log_func = getattr(logger, log_level.lower())
                    log_func(
                        f"{error_message}: {str(e)[:200]} | "
                        f"函数: {func.__name__} | "
                        f"模块: {func.__module__}"
                    )
                    
                    if reraise:
                        # 如果已经是自定义异常，直接抛出
                        if isinstance(e, TestException):
                            raise
                        # 否则包装为自定义异常
                        raise exception_class(f"{error_message}: {str(e)}", context) from e
                    return None
            return inner
        return wrapper
    return decorator

# ============================================================================
# 通用异常处理装饰器
# ============================================================================

def handle_exception(
    exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_level: str = "ERROR",
    re_raise: bool = True,
    error_context: Optional[Dict[str, Any]] = None,
    log_args: bool = False
) -> Callable:
    """
    通用异常处理装饰器
    
    Args:
        exception_types: 需要捕获的异常类型，可以是单个异常类型或异常类型元组
        log_level: 日志级别，默认为ERROR
        re_raise: 是否重新抛出异常，默认为True
        error_context: 额外的错误上下文信息
        log_args: 是否记录参数，默认为False（性能优化）
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # 构建简化的上下文
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "error_type": type(e).__name__,
                }
                
                # 可选：记录参数
                if log_args:
                    context["arguments"] = {
                        "args": [str(arg)[:100] for arg in args[:3]],
                        "kwargs": {k: str(v)[:100] for k, v in list(kwargs.items())[:5]}
                    }
                
                if error_context:
                    context.update(error_context)
                
                # 简化日志输出（一行，logger会自动记录堆栈）
                log_func = getattr(logger, log_level.lower())
                log_func(
                    f"函数 {func.__name__} 执行出错: {str(e)[:200]} | "
                    f"类型: {type(e).__name__} | "
                    f"模块: {func.__module__}"
                )
                
                # 如果需要重新抛出异常
                if re_raise:
                    if isinstance(e, TestException):
                        raise
                    raise TestException(str(e), context) from e
                return None
        return wrapper
    return decorator

def handle_class_method_exception(
    exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_level: str = "ERROR",
    re_raise: bool = True,
    error_context: Optional[Dict[str, Any]] = None,
    log_args: bool = False
) -> Callable:
    """
    类方法异常处理装饰器
    
    Args:
        exception_types: 需要捕获的异常类型，可以是单个异常类型或异常类型元组
        log_level: 日志级别，默认为ERROR
        re_raise: 是否重新抛出异常，默认为True
        error_context: 额外的错误上下文信息
        log_args: 是否记录参数，默认为False（性能优化）
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            try:
                return func(cls, *args, **kwargs)
            except exception_types as e:
                # 构建简化的上下文
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "error_type": type(e).__name__,
                    "class_info": {
                        "name": cls.__name__,
                        "module": cls.__module__,
                        "bases": [base.__name__ for base in cls.__bases__]
                    }
                }
                
                # 可选：记录参数
                if log_args:
                    context["arguments"] = {
                        "args": [str(arg)[:100] for arg in args[:3]],
                        "kwargs": {k: str(v)[:100] for k, v in list(kwargs.items())[:5]}
                    }
                
                if error_context:
                    context.update(error_context)
                
                # 简化日志输出（一行）
                log_func = getattr(logger, log_level.lower())
                log_func(
                    f"类方法 {cls.__name__}.{func.__name__} 执行出错: {str(e)[:200]} | "
                    f"类型: {type(e).__name__} | "
                    f"模块: {cls.__module__}"
                )
                
                # 如果需要重新抛出异常
                if re_raise:
                    if isinstance(e, TestException):
                        raise
                    raise TestException(str(e), context) from e
                return None
        return wrapper
    return decorator

# ============================================================================
# 专用异常处理装饰器（使用工厂函数创建）
# ============================================================================

def safe_api_call(
    error_message: str = "API调用失败",
    reraise: bool = True,
    log_level: str = "ERROR",
    log_args: bool = False
) -> Callable:
    """
    API调用安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
        log_args: 是否记录参数
    
    Returns:
        装饰器函数
    """
    return _create_exception_decorator(
        APIException, "api_error", error_message
    )(error_message, reraise, log_level, log_args)

def safe_db_operation(
    error_message: str = "数据库操作失败",
    reraise: bool = True,
    log_level: str = "ERROR",
    log_args: bool = False
) -> Callable:
    """
    数据库操作安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
        log_args: 是否记录参数
    
    Returns:
        装饰器函数
    """
    return _create_exception_decorator(
        DatabaseException, "db_error", error_message
    )(error_message, reraise, log_level, log_args)

def validate_data(
    error_message: str = "数据验证失败",
    reraise: bool = True,
    log_level: str = "ERROR",
    log_args: bool = False
) -> Callable:
    """
    数据验证装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
        log_args: 是否记录参数
    
    Returns:
        装饰器函数
    """
    return _create_exception_decorator(
        ValidationException, "validation_error", error_message
    )(error_message, reraise, log_level, log_args)

def safe_config_load(
    error_message: str = "配置加载失败",
    reraise: bool = True,
    log_level: str = "ERROR",
    log_args: bool = False
) -> Callable:
    """
    配置加载安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
        log_args: 是否记录参数
    
    Returns:
        装饰器函数
    """
    return _create_exception_decorator(
        ConfigException, "config_error", error_message
    )(error_message, reraise, log_level, log_args)

def safe_file_operation(
    error_message: str = "文件操作失败",
    reraise: bool = True,
    log_level: str = "ERROR",
    log_args: bool = False
) -> Callable:
    """
    文件操作安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
        log_args: 是否记录参数
    
    Returns:
        装饰器函数
    """
    return _create_exception_decorator(
        FileException, "file_error", error_message
    )(error_message, reraise, log_level, log_args)
