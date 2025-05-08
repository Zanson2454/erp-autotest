import os
from typing import Dict, Any

class Config:
    """配置类"""
    
    # 环境变量
    ENV = os.getenv("ENV", "test")
    
    # 认证信息
    TEST_ACCOUNT = "17376596912"
    TEST_PASSWORD = "Anson2454@"
    
    # API 域名配置
    IAM_BASE_URL = "https://t-erp-iam-test.app.terminus.io"
    API_BASE_URL = "https://t-erp-portal-test.app.terminus.io"
    
    # 日志配置
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    
    # 数据库配置
    DB_HOST = os.getenv("MYSQL_HOST", "rm-bp1f14585v00oh99t.mysql.rds.aliyuncs.com")
    DB_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    DB_USER = os.getenv("MYSQL_USERNAME", "terp_test")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "43sVPCQ2pE%g55bc")
    
    # 环境对应的数据库配置
    DB_CONFIG: Dict[str, Dict[str, Any]] = {
        "dev": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": os.getenv("MYSQL_DATABASE", "terp_dev"),
            "user": DB_USER,
            "password": DB_PASSWORD
        },
        "test": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": os.getenv("MYSQL_DATABASE", "terp_test"),
            "user": DB_USER,
            "password": DB_PASSWORD
        },
        "staging": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": os.getenv("MYSQL_DATABASE", "terp_staging"),
            "user": DB_USER,
            "password": DB_PASSWORD
        }
    }
    
    # 运行时数据库配置
    RUNTIME_DB_CONFIG: Dict[str, Dict[str, Any]] = {
        "dev": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": os.getenv("TRANTOR_RUNTIME_MYSQL_DATABASE", "trantor2_test_runtime"),
            "user": DB_USER,
            "password": DB_PASSWORD
        },
        "test": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": os.getenv("TRANTOR_RUNTIME_MYSQL_DATABASE", "trantor2_test_runtime"),
            "user": DB_USER,
            "password": DB_PASSWORD
        },
        "prod": {
            "host": DB_HOST,
            "port": DB_PORT,
            "database": os.getenv("TRANTOR_RUNTIME_MYSQL_DATABASE", "trantor2_test_runtime"),
            "user": DB_USER,
            "password": DB_PASSWORD
        }
    }
    
    @staticmethod
    def get_iam_base_url() -> str:
        """
        获取 IAM 基础 URL
        
        返回:
            IAM 基础 URL
        """
        return Config.IAM_BASE_URL
        
    @staticmethod
    def get_api_base_url() -> str:
        """
        获取业务 API 基础 URL
        
        返回:
            业务 API 基础 URL
        """
        return Config.API_BASE_URL
        
    @staticmethod
    def get_base_url() -> str:
        """
        获取基础URL
        
        返回:
            基础URL
        """
        return "https://t-erp-iam-test.app.terminus.io"
        
    @classmethod
    def get_db_config(cls, is_runtime: bool = False) -> Dict[str, Any]:
        """
        获取数据库配置
        
        参数:
            is_runtime: 是否连接运行时数据库
            
        返回:
            数据库配置字典
        """
        config_map = cls.RUNTIME_DB_CONFIG if is_runtime else cls.DB_CONFIG
        return config_map.get(cls.ENV, config_map["dev"])
            
    @classmethod
    def get_connection_url(cls, is_runtime: bool = False) -> str:
        """
        获取数据库连接URL
        
        参数:
            is_runtime: 是否连接运行时数据库
            
        返回:
            数据库连接URL
        """
        config = cls.get_db_config(is_runtime)
        return (
            f"mysql+pymysql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}"
        )
        
    @classmethod
    def get_auth_info(cls) -> tuple:
        """
        获取认证信息
        
        返回:
            账号和密码的元组
        """
        return cls.TEST_ACCOUNT, cls.TEST_PASSWORD 

    @classmethod
    def get_log_dir(cls) -> str:
        """
        获取日志目录
        
        返回:
            日志目录路径
        """
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
        return cls.LOG_DIR 