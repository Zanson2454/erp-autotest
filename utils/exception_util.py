import traceback
import inspect
import sys
from typing import Any, Callable, Optional, Type, Union, Tuple, Dict
from functools import wraps
from loguru import logger
from datetime import datetime

class TestException(Exception):
    """测试异常基类"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        self.traceback = traceback.format_exc()
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
                error_info.append(f"  {key}: {value}")
        error_info.append(f"堆栈信息:\n{self.traceback}")
        return "\n".join(error_info)

    def to_dict(self) -> Dict[str, Any]:
        """将异常信息转换为字典格式"""
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "details": self.details,
            "traceback": self.traceback
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

def _get_caller_info() -> Dict[str, Any]:
    """获取调用者信息"""
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
        "locals": {k: str(v) for k, v in caller_frame.f_locals.items() 
                  if not k.startswith('_') and not callable(v)}
    }
    
    return caller_info

def _enrich_error_context(
    func: Callable,
    args: tuple,
    kwargs: dict,
    error: Exception,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """丰富错误上下文信息"""
    context = {
        "timestamp": datetime.now().isoformat(),
        "function": {
            "name": func.__name__,
            "module": func.__module__,
            "signature": str(inspect.signature(func))
        },
        "arguments": {
            "args": [str(arg) for arg in args],
            "kwargs": {k: str(v) for k, v in kwargs.items()}
        },
        "error": {
            "type": type(error).__name__,
            "message": str(error)
        },
        "caller": _get_caller_info()
    }
    
    if additional_context:
        context.update(additional_context)
    
    return context

def handle_exception(
    exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_level: str = "ERROR",
    re_raise: bool = True,
    error_context: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    通用异常处理装饰器
    
    Args:
        exception_types: 需要捕获的异常类型，可以是单个异常类型或异常类型元组
        log_level: 日志级别，默认为ERROR
        re_raise: 是否重新抛出异常，默认为True
        error_context: 额外的错误上下文信息
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 构建错误上下文
                context = _enrich_error_context(func, args, kwargs, e, error_context)
                
                # 记录错误信息
                log_func(f"函数 {func.__name__} 执行出错: {str(e)}")
                log_func(f"错误上下文: {context}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                # 如果需要重新抛出异常
                if re_raise:
                    if isinstance(e, TestException):
                        raise
                    raise TestException(str(e), context) from e
                return None
        return wrapper
    return decorator

def safe_api_call(
    error_message: str = "API调用失败",
    reraise: bool = True,
    log_level: str = "ERROR"
) -> Callable:
    """
    API调用安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 构建错误上下文
                context = _enrich_error_context(func, args, kwargs, e)
                context["api_error"] = {
                    "message": error_message,
                    "original_error": str(e)
                }
                
                # 记录错误信息
                log_func(f"API调用失败: {error_message}")
                log_func(f"错误上下文: {context}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                if reraise:
                    raise APIException(f"{error_message}: {str(e)}", context) from e
                return None
        return wrapper
    return decorator

def safe_db_operation(
    error_message: str = "数据库操作失败",
    reraise: bool = True,
    log_level: str = "ERROR"
) -> Callable:
    """
    数据库操作安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 构建错误上下文
                context = _enrich_error_context(func, args, kwargs, e)
                context["db_error"] = {
                    "message": error_message,
                    "original_error": str(e)
                }
                
                # 记录错误信息
                log_func(f"数据库操作失败: {error_message}")
                log_func(f"错误上下文: {context}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                if reraise:
                    raise DatabaseException(f"{error_message}: {str(e)}", context) from e
                return None
        return wrapper
    return decorator

def validate_data(
    error_message: str = "数据验证失败",
    reraise: bool = True,
    log_level: str = "ERROR"
) -> Callable:
    """
    数据验证装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 构建错误上下文
                context = _enrich_error_context(func, args, kwargs, e)
                context["validation_error"] = {
                    "message": error_message,
                    "original_error": str(e)
                }
                
                # 记录错误信息
                log_func(f"数据验证失败: {error_message}")
                log_func(f"错误上下文: {context}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                if reraise:
                    raise ValidationException(f"{error_message}: {str(e)}", context) from e
                return None
        return wrapper
    return decorator

def safe_config_load(
    error_message: str = "配置加载失败",
    reraise: bool = True,
    log_level: str = "ERROR"
) -> Callable:
    """
    配置加载安全处理装饰器
    
    Args:
        error_message: 错误信息前缀
        reraise: 是否重新抛出异常
        log_level: 日志级别
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 构建错误上下文
                context = _enrich_error_context(func, args, kwargs, e)
                context["config_error"] = {
                    "message": error_message,
                    "original_error": str(e)
                }
                
                # 记录错误信息
                log_func(f"配置加载失败: {error_message}")
                log_func(f"错误上下文: {context}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                if reraise:
                    raise ConfigException(f"{error_message}: {str(e)}", context) from e
                return None
        return wrapper
    return decorator

def handle_class_method_exception(
    exception_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_level: str = "ERROR",
    re_raise: bool = True,
    error_context: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    类方法异常处理装饰器
    
    Args:
        exception_types: 需要捕获的异常类型，可以是单个异常类型或异常类型元组
        log_level: 日志级别，默认为ERROR
        re_raise: 是否重新抛出异常，默认为True
        error_context: 额外的错误上下文信息
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            try:
                return func(cls, *args, **kwargs)
            except exception_types as e:
                # 获取日志函数
                log_func = getattr(logger, log_level.lower())
                
                # 构建错误上下文
                context = _enrich_error_context(func, args, kwargs, e, error_context)
                context["class_info"] = {
                    "name": cls.__name__,
                    "module": cls.__module__,
                    "bases": [base.__name__ for base in cls.__bases__]
                }
                
                # 记录错误信息
                log_func(f"类方法 {cls.__name__}.{func.__name__} 执行出错: {str(e)}")
                log_func(f"错误上下文: {context}")
                log_func(f"异常堆栈:\n{traceback.format_exc()}")
                
                # 如果需要重新抛出异常
                if re_raise:
                    if isinstance(e, TestException):
                        raise
                    raise TestException(str(e), context) from e
                return None
        return wrapper
    return decorator 