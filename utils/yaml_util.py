import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv

class YamlUtil:
    """YAML 配置管理工具类，负责加载和管理所有配置"""
    
    def __init__(self, config_dir: str = "config", env: str = "test"):
        self.config_dir = Path(config_dir)
        self.env = env
        self.base_config: Dict[str, Any] = {}
        self.env_config: Dict[str, Any] = {}
        self.db_config: Dict[str, Any] = {}
        self.biz_config: Dict[str, Any] = {}
        
        # 加载环境变量
        self._load_env_vars()
        # 确保配置目录存在
        self._ensure_config_dir()
        # 加载基础配置
        self._load_base_config()
    
    def _load_env_vars(self):
        """加载环境变量"""
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            logger.info("已加载 .env 文件")
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        (self.config_dir / "env").mkdir(parents=True, exist_ok=True)
        (self.config_dir / "biz").mkdir(parents=True, exist_ok=True)
    
    def _load_base_config(self):
        """加载基础配置"""
        base_config_file = self.config_dir / "env" / "base.yaml"
        if not base_config_file.exists():
            logger.error(f"基础配置文件不存在: {base_config_file}")
            raise FileNotFoundError(f"基础配置文件不存在: {base_config_file}")
            
        with open(base_config_file, 'r', encoding='utf-8') as f:
            self.base_config = yaml.safe_load(f)
    
    def _replace_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """替换配置中的环境变量占位符
        
        Args:
            config: 配置字典
            
        Returns:
            替换环境变量后的配置字典
        """
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            # 根据当前环境构建环境变量名
            env_prefix = self.env.upper()
            env_var_with_prefix = f"{env_prefix}_{env_var}"
            # 尝试获取带环境前缀的变量，如果不存在则尝试不带前缀的变量
            value = os.getenv(env_var_with_prefix) or os.getenv(env_var)
            return value if value is not None else config
        return config
    
    def load_env_config(self, env: str = None) -> Dict[str, Any]:
        """加载环境配置
        
        Args:
            env: 环境名称，默认为初始化时指定的环境
            
        Returns:
            环境配置字典
        """
        env = env or self.env
        if env in self.env_config:
            return self.env_config[env]
            
        config_file = self.config_dir / "env" / f"{env}.yaml"
        if not config_file.exists():
            logger.error(f"环境配置文件不存在: {config_file}")
            raise FileNotFoundError(f"环境配置文件不存在: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            # 替换环境变量
            config = self._replace_env_vars(config)
            # 合并基础配置和环境特定配置
            merged_config = self._merge_configs(self.base_config, config)
            self.env_config[env] = merged_config
            return merged_config
    
    def get_biz_config(self, module: str) -> Dict[str, Any]:
        """获取业务配置
        
        Args:
            module: 业务模块名称，如 'crm', 'inv', 'sls' 等
            
        Returns:
            业务配置字典
        """
        if module in self.biz_config:
            return self.biz_config[module]
            
        config_file = self.config_dir / "biz" / f"{module}.yaml"
        if not config_file.exists():
            logger.error(f"业务配置文件不存在: {config_file}")
            raise FileNotFoundError(f"业务配置文件不存在: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.biz_config[module] = config
            return config
    
    def _merge_configs(self, base_config: Dict[str, Any], env_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并基础配置和环境特定配置
        
        Args:
            base_config: 基础配置
            env_config: 环境特定配置
            
        Returns:
            合并后的配置字典
        """
        merged = base_config.copy()
        for key, value in env_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
    
    def get_base_url(self, env: str = None) -> str:
        """获取基础URL"""
        config = self.load_env_config(env)
        return config.get("base_url", "")
    
    def get_iam_url(self, env: str = None) -> str:
        """获取IAM URL"""
        config = self.load_env_config(env)
        return config.get("iam_url", "")
    
    def get_api_version(self, env: str = None) -> str:
        """获取API版本"""
        config = self.load_env_config(env)
        return config.get("api_version", "v1")
    
    def get_db_config(self, db_name: str = "erp_db", env: str = None) -> Dict[str, Any]:
        """获取数据库配置"""
        config = self.load_env_config(env)
        return config.get("database", {}).get(db_name, {})
    
    def get_auth_config(self, env: str = None) -> Dict[str, Any]:
        """获取认证配置"""
        config = self.load_env_config(env)
        return config["tenants"]["terp"]["auth"]
    
    def get_timeout_config(self, env: str = None) -> Dict[str, int]:
        """获取超时配置"""
        config = self.load_env_config(env)
        return config.get("base", {}).get("timeouts", {})
    
    def get_logging_config(self, env: str = None) -> Dict[str, Any]:
        """获取日志配置"""
        return self.base_config["base"]["logging"]
    
    def get_trantor_version(self, env: str = None) -> str:
        """获取Trantor版本"""
        config = self.load_env_config(env)
        return config.get("trantor_version", "")
    
    def save_yaml(self, data: Dict[str, Any], file_path: str):
        """保存配置到YAML文件
        
        Args:
            data: 要保存的配置数据
            file_path: 文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True)
    
    def read_yaml(self, file_path: str) -> Dict[str, Any]:
        """读取YAML文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            YAML文件内容
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
