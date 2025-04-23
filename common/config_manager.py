from pathlib import Path
import yaml
from typing import Dict, Any, Optional
from loguru import logger

class ConfigManager:
    """配置管理类，负责加载和管理所有配置"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.env_config: Dict[str, Any] = {}
        self.api_config: Dict[str, Any] = {}
        self.db_config: Dict[str, Any] = {}
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        (self.config_dir / "env").mkdir(parents=True, exist_ok=True)
        (self.config_dir / "api").mkdir(parents=True, exist_ok=True)
    
    def load_env_config(self, env: str = "test") -> Dict[str, Any]:
        """加载环境配置
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            环境配置字典
        """
        if env in self.env_config:
            return self.env_config[env]
            
        config_file = self.config_dir / "env" / f"{env}.yaml"
        if not config_file.exists():
            logger.error(f"环境配置文件不存在: {config_file}")
            raise FileNotFoundError(f"环境配置文件不存在: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.env_config[env] = config
            return config
    
    def get_base_url(self, env: str = "test") -> str:
        """获取基础URL
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            基础URL
        """
        config = self.load_env_config(env)
        return config.get("base_url", "")
    
    def get_iam_url(self, env: str = "test") -> str:
        """获取IAM URL
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            IAM URL
        """
        config = self.load_env_config(env)
        return config.get("iam_url", "")
    
    def get_api_version(self, env: str = "test") -> str:
        """获取API版本
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            API版本
        """
        config = self.load_env_config(env)
        return config.get("api_version", "v1")
    
    def get_db_config(self, db_name: str = "erp_db", env: str = "test") -> Dict[str, Any]:
        """获取数据库配置
        
        Args:
            db_name: 数据库名称，默认为 'erp_db'
            env: 环境名称，默认为 'test'
            
        Returns:
            数据库配置字典
        """
        config = self.load_env_config(env)
        return config.get("database", {}).get(db_name, {})
    
    def get_api_config(self, service: str) -> Dict[str, Any]:
        """获取API配置
        
        Args:
            service: 服务名称，如 'SCM', 'SO'
            
        Returns:
            API配置字典
        """
        if service in self.api_config:
            return self.api_config[service]
            
        config_file = self.config_dir / "api" / "api_config.yaml"
        if not config_file.exists():
            logger.error(f"API配置文件不存在: {config_file}")
            raise FileNotFoundError(f"API配置文件不存在: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.api_config = config
            return config.get(service, {})
    
    def get_auth_config(self, env: str = "test") -> Dict[str, Any]:
        """获取认证配置
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            认证配置字典
        """
        config = self.load_env_config(env)
        return config.get("auth", {})
    
    def get_timeout_config(self, env: str = "test") -> Dict[str, int]:
        """获取超时配置
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            超时配置字典
        """
        config = self.load_env_config(env)
        return config.get("timeouts", {})
    
    def get_logging_config(self, env: str = "test") -> Dict[str, Any]:
        """获取日志配置
        
        Args:
            env: 环境名称，默认为 'test'
            
        Returns:
            日志配置字典
        """
        config = self.load_env_config(env)
        return config.get("logging", {}) 

    def get_trantor_version(self, env: str = "test") -> str:
        """获取Trantor版本
        
        Args:
            env: 环境名称，默认为 'test'

        Returns:
            Trantor版本
        """
        config = self.load_env_config(env)
        return config.get("trantor_version", "")
