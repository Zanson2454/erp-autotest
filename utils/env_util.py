import os
import sys
from typing import Dict, Any, List, Optional
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class EnvVarType(Enum):
    """环境变量类型"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"

@dataclass
class EnvVarDefinition:
    """环境变量定义"""
    name: str
    type: EnvVarType
    required: bool
    default: Any = None
    description: str = ""
    allowed_values: Optional[List[Any]] = None
    validation_regex: Optional[str] = None

class EnvManager:
    """环境变量管理器"""
    
    # 环境变量定义
    ENV_VARS = {
        # 数据库配置
        "DB_HOST": EnvVarDefinition(
            name="DB_HOST",
            type=EnvVarType.STRING,
            required=True,
            description="数据库主机地址"
        ),
        "DB_PORT": EnvVarDefinition(
            name="DB_PORT",
            type=EnvVarType.INTEGER,
            required=True,
            default=3306,
            description="数据库端口"
        ),
        "DB_USER": EnvVarDefinition(
            name="DB_USER",
            type=EnvVarType.STRING,
            required=True,
            description="数据库用户名"
        ),
        "DB_PASSWORD": EnvVarDefinition(
            name="DB_PASSWORD",
            type=EnvVarType.STRING,
            required=True,
            description="数据库密码"
        ),
        "DB_NAME": EnvVarDefinition(
            name="DB_NAME",
            type=EnvVarType.STRING,
            required=True,
            description="数据库名称"
        ),
        
        # API配置
        "BASE_URL": EnvVarDefinition(
            name="BASE_URL",
            type=EnvVarType.STRING,
            required=True,
            description="API基础URL",
            validation_regex=r"^https?://.+$"
        ),
        "IAM_URL": EnvVarDefinition(
            name="IAM_URL",
            type=EnvVarType.STRING,
            required=True,
            description="IAM服务URL",
            validation_regex=r"^https?://.+$"
        ),
        
        # 认证配置
        "AUTH_USERNAME": EnvVarDefinition(
            name="AUTH_USERNAME",
            type=EnvVarType.STRING,
            required=True,
            description="认证用户名"
        ),
        "AUTH_PASSWORD": EnvVarDefinition(
            name="AUTH_PASSWORD",
            type=EnvVarType.STRING,
            required=True,
            description="认证密码"
        ),
        
        # 日志配置
        "LOG_LEVEL": EnvVarDefinition(
            name="LOG_LEVEL",
            type=EnvVarType.STRING,
            required=False,
            default="INFO",
            description="日志级别",
            allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        ),
        
        # 测试配置
        "TEST_ENV": EnvVarDefinition(
            name="TEST_ENV",
            type=EnvVarType.STRING,
            required=False,
            default="test",
            description="测试环境",
            allowed_values=["dev", "test", "staging", "prod"]
        )
    }
    
    @classmethod
    def validate_env_vars(cls) -> Dict[str, Any]:
        """验证环境变量
        
        Returns:
            验证后的环境变量字典
        """
        env_vars = {}
        missing_vars = []
        invalid_vars = []
        
        for name, definition in cls.ENV_VARS.items():
            value = os.getenv(name)
            
            # 检查必需变量
            if definition.required and not value:
                if definition.default is None:
                    missing_vars.append(name)
                    continue
                value = definition.default
                
            # 类型转换和验证
            try:
                if value is not None:
                    value = cls._convert_type(value, definition.type)
                    cls._validate_value(value, definition)
                    env_vars[name] = value
            except (ValueError, TypeError) as e:
                invalid_vars.append(f"{name}: {str(e)}")
                
        # 报告验证结果
        if missing_vars:
            logger.warning(f"缺少必需的环境变量: {', '.join(missing_vars)}")
        if invalid_vars:
            logger.warning(f"环境变量值无效: {', '.join(invalid_vars)}")
            
        return env_vars
        
    @classmethod
    def _convert_type(cls, value: str, var_type: EnvVarType) -> Any:
        """转换环境变量类型
        
        Args:
            value: 环境变量值
            var_type: 目标类型
            
        Returns:
            转换后的值
        """
        if var_type == EnvVarType.STRING:
            return str(value)
        elif var_type == EnvVarType.INTEGER:
            return int(value)
        elif var_type == EnvVarType.FLOAT:
            return float(value)
        elif var_type == EnvVarType.BOOLEAN:
            return value.lower() in ("true", "1", "yes")
        elif var_type == EnvVarType.LIST:
            return [item.strip() for item in value.split(",")]
        elif var_type == EnvVarType.DICT:
            return dict(item.split("=") for item in value.split(","))
        else:
            raise ValueError(f"不支持的类型: {var_type}")
            
    @classmethod
    def _validate_value(cls, value: Any, definition: EnvVarDefinition) -> None:
        """验证环境变量值
        
        Args:
            value: 环境变量值
            definition: 环境变量定义
        """
        # 检查允许值
        if definition.allowed_values and value not in definition.allowed_values:
            raise ValueError(
                f"值 '{value}' 不在允许的范围内: {definition.allowed_values}"
            )
            
        # 检查正则表达式
        if definition.validation_regex and isinstance(value, str):
            import re
            if not re.match(definition.validation_regex, value):
                raise ValueError(
                    f"值 '{value}' 不符合正则表达式: {definition.validation_regex}"
                )
                
    @classmethod
    def generate_env_template(cls) -> str:
        """生成环境变量模板
        
        Returns:
            环境变量模板字符串
        """
        template = "# 环境变量模板\n"
        template += "# 复制此文件为 .env 并填写相应的值\n\n"
        
        for name, definition in cls.ENV_VARS.items():
            template += f"# {definition.description}\n"
            if definition.allowed_values:
                template += f"# 允许的值: {definition.allowed_values}\n"
            if definition.validation_regex:
                template += f"# 格式要求: {definition.validation_regex}\n"
            template += f"{name}="
            if definition.default is not None:
                template += str(definition.default)
            template += "\n\n"
            
        return template 