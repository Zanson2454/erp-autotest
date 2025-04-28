"""Global pytest configuration."""
import os
import sys
import pytest
import yaml
from typing import Dict, Any
from loguru import logger
from utils.YamlUtil import YamlReader
from utils.EnvUtil import EnvManager
import allure

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(__file__))

def pytest_configure(config):
    """pytest 配置钩子函数"""
    # 添加项目根目录到 PYTHONPATH
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 确保必要的目录存在
    for dir_name in ["reports/allure-results", "reports/html", "reports/junit", "logs"]:
        os.makedirs(os.path.join(project_root, dir_name), exist_ok=True)
        
    # 生成环境变量模板（如果不存在）
    env_template_path = os.path.join(project_root, ".env.template")
    if not os.path.exists(env_template_path):
        with open(env_template_path, "w", encoding="utf-8") as f:
            f.write(EnvManager.generate_env_template())
            logger.info("已生成环境变量模板: .env.template")

def pytest_addoption(parser):
    """添加命令行参数"""
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="测试环境：dev/test/staging/prod"
    )
    
    parser.addoption(
        "--config-override",
        action="store",
        default=None,
        help="覆盖配置文件的路径"
    )
    
    parser.addoption(
        "--trantor_version",
        action="store",
        default="2.5.25.0130.0-SNAPSHOT",
        help="Trantor版本号"
    )
    
    parser.addoption(
        "--env-file",
        action="store",
        default=".env",
        help="环境变量文件路径"
    )

def load_config(env: str, config_override: str = None, env_file: str = None) -> Dict[str, Any]:
    """加载环境配置
    
    Args:
        env: 环境名称
        config_override: 覆盖配置文件的路径
        env_file: 环境变量文件路径
        
    Returns:
        配置字典
    """
    try:
        # 加载环境变量
        if env_file and os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
        # 验证环境变量
        env_vars = EnvManager.validate_env_vars()
        
        # 加载基础配置
        base_config_path = os.path.join(project_root, "config", "env", "base.yaml")
        with open(base_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 加载环境特定配置
        env_config_path = os.path.join(project_root, "config", "env", f"{env}.yaml")
        if os.path.exists(env_config_path):
            with open(env_config_path, 'r', encoding='utf-8') as f:
                env_config = yaml.safe_load(f)
                # 合并配置
                config = YamlReader.merge_dicts(config, env_config)
                
        # 加载覆盖配置
        if config_override and os.path.exists(config_override):
            with open(config_override, 'r', encoding='utf-8') as f:
                override_config = yaml.safe_load(f)
                config = YamlReader.merge_dicts(config, override_config)
                
        # 应用环境变量
        config = _apply_env_vars(config, env_vars)
        
        return config
        
    except Exception as e:
        logger.error(f"加载配置失败: {str(e)}")
        raise

def _apply_env_vars(config: Dict[str, Any], env_vars: Dict[str, Any]) -> Dict[str, Any]:
    """应用环境变量到配置
    
    Args:
        config: 配置字典
        env_vars: 环境变量字典
        
    Returns:
        更新后的配置字典
    """
    # 数据库配置
    if "DB_HOST" in env_vars:
        config["database"]["erp_db"]["host"] = env_vars["DB_HOST"]
    if "DB_PORT" in env_vars:
        config["database"]["erp_db"]["port"] = env_vars["DB_PORT"]
    if "DB_USER" in env_vars:
        config["database"]["erp_db"]["user"] = env_vars["DB_USER"]
    if "DB_PASSWORD" in env_vars:
        config["database"]["erp_db"]["password"] = env_vars["DB_PASSWORD"]
    if "DB_NAME" in env_vars:
        config["database"]["erp_db"]["name"] = env_vars["DB_NAME"]
        
    # API配置
    if "BASE_URL" in env_vars:
        config["base_url"] = env_vars["BASE_URL"]
    if "IAM_URL" in env_vars:
        config["iam_url"] = env_vars["IAM_URL"]
        
    # 认证配置
    if "AUTH_USERNAME" in env_vars:
        config["auth"]["username"] = env_vars["AUTH_USERNAME"]
    if "AUTH_PASSWORD" in env_vars:
        config["auth"]["password"] = env_vars["AUTH_PASSWORD"]
        
    # 日志配置
    if "LOG_LEVEL" in env_vars:
        config["logging"]["level"] = env_vars["LOG_LEVEL"]
        
    return config

@pytest.fixture(scope="session")
def config(request) -> Dict[str, Any]:
    """配置fixture
    
    Args:
        request: pytest请求对象
        
    Returns:
        配置字典
    """
    env = request.config.getoption("--env")
    config_override = request.config.getoption("--config-override")
    env_file = request.config.getoption("--env-file")
    return load_config(env, config_override, env_file)

@pytest.fixture(scope="session", autouse=True)
def set_test_dir():
    """设置测试目录"""
    # 设置工作目录为项目根目录
    os.chdir(project_root)
    return project_root 

@pytest.fixture(autouse=True)
def allure_env_info(request, set_test_dir):
    """Allure环境信息
    作用：添加环境信息到Allure报告
    功能：
    1. 记录测试环境
    2. 记录Python版本
    3. 记录Pytest版本
    4. 记录Allure版本
    自动执行：autouse=True，无需显式调用
    """
    # 使用 allure.environment 的正确方式
    env_info = {
        "Environment": request.config.getoption("--env"),
        "Trantor Version": request.config.getoption("--trantor_version")
    }
    
    # 添加环境信息到Allure报告
    for key, value in env_info.items():
        allure.environment(key, value)
    
    return env_info 