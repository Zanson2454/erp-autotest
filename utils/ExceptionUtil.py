import traceback
from typing import Any, Callable, Optional, Type, Union, Tuple
from functools import wraps
from loguru import logger

class TestException(Exception):
    """测试异常基类"""
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

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

def handle_exception(exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
                    log_level: str = "ERROR",
                    re_raise: bool = True):
    """
    通用异常处理装饰器
    
    Args:
        exception_types: 需要捕获的异常类型，可以是单个异常类型或异常类型元组
        log_level: 日志级别，默认为ERROR
        re_raise: 是否重新抛出异常，默认为True
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 检查是否是类方法
                if hasattr(func, '__self__'):
                    # 如果是类方法，确保传递cls参数
                    return func(args[0] if args else func.__self__, *args[1:], **kwargs)
                return func(*args, **kwargs)
            except exception_types as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 记录错误信息
                log_func(f"函数 {func.__name__} 执行出错: {str(e)}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                # 如果需要重新抛出异常
                if re_raise:
                    raise
                return None
        return wrapper if not isinstance(func, classmethod) else classmethod(wrapper)
    return decorator

def safe_api_call(
    error_message: str = "API调用失败",
    reraise: bool = True
) -> Callable:
    """
    API调用安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise APIException(f"{error_message}: {str(e)}", {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }) from e
        return wrapper
    return decorator

def safe_db_operation(
    error_message: str = "数据库操作失败",
    reraise: bool = True
) -> Callable:
    """
    数据库操作安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise DatabaseException(f"{error_message}: {str(e)}", {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }) from e
        return wrapper
    return decorator

def validate_data(
    error_message: str = "数据验证失败",
    reraise: bool = True
) -> Callable:
    """
    数据验证装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise ValidationException(f"{error_message}: {str(e)}", {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }) from e
        return wrapper
    return decorator

def safe_config_load(
    error_message: str = "配置加载失败",
    reraise: bool = True
) -> Callable:
    """
    配置加载安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                raise ConfigException(f"{error_message}: {str(e)}", {
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }) from e
        return wrapper
    return decorator

def handle_class_method_exception(exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
                           log_level: str = "ERROR",
                           re_raise: bool = True):
    """
    类方法异常处理装饰器
    
    Args:
        exception_types: 需要捕获的异常类型，可以是单个异常类型或异常类型元组
        log_level: 日志级别，默认为ERROR
        re_raise: 是否重新抛出异常，默认为True
    """
    def decorator(func):
        def wrapper(cls, *args, **kwargs):
            try:
                return func(cls, *args, **kwargs)
            except exception_types as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 记录错误信息
                log_func(f"类方法 {func.__name__} 执行出错: {str(e)}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                # 如果需要重新抛出异常
                if re_raise:
                    raise
                return None
        return classmethod(wrapper)
    return decorator 