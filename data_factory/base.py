from pathlib import Path
from dotenv import load_dotenv
import sys
from typing import Dict, Any, List
import os

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil
from utils.mysql_util import DBManager
from utils.log_util import Loggers

class SQLInitializer:
    """
    通用SQL初始化器：负责从YAML配置读取SQL，执行数据库查询，初始化基础数据，并缓存。
    仅做通用数据加载，不做结构化、ID提取、分类等业务处理。
    """
    @classmethod
    def init_sql(cls, sql_config: dict, db_config: Dict[str, Any], cache_key: str = None) -> Dict[str, Any]:
        """
        初始化SQL数据，优先从缓存获取，否则执行SQL并写入缓存。
        :param sql_config: SQL配置（已加载的dict）
        :param db_config: 数据库连接配置
        :param cache_key: 缓存key（可选）
        :return: 原始业务数据
        """
        if cache_key:
            CacheUtil.init(str(project_root / 'testdata' / 'cache'))
            cache_data = CacheUtil.get(cache_key)
            if cache_data:
                Loggers.info("从缓存获取数据成功")
                return cache_data
            Loggers.info("缓存数据不存在或已过期，开始初始化数据")
        DBManager.init(db_config)
        result_data = {}
        for key, item in sql_config.items():
            sql = item.get('sql', '')
            Loggers.info(f"准备执行SQL: {key} -> {sql}")
            if not sql:
                continue
            try:
                result = DBManager.query(sql)
                Loggers.info(f"SQL执行结果: {key} -> {result}")
                result_data[key] = result
            except Exception as e:
                Loggers.error(f"执行查询 {key} 时出错: {str(e)}")
                result_data[key] = None
        if not result_data:
            Loggers.warning("所有SQL查询均未返回数据，请检查数据库连接和SQL配置！")
        if cache_key:
            CacheUtil.set(cache_key, result_data)
            Loggers.info(f"数据初始化完成并写入缓存: testdata/cache/{cache_key}.json")
        return result_data

class DataFactory:
    """
    通用数据工厂，仅负责数据加载、SQL执行、缓存、环境配置加载。
    结构化、ID提取、分类等业务逻辑由业务工厂实现。
    """
    _initialized = False
    _env_config = None

   
    @classmethod
    def __init__(cls, env_name="test", db_config_name="erp_db"):
        if not cls._initialized:
            env_file = project_root / '.env'
            yaml_file = project_root / 'config' / 'env' / f'{env_name}.yaml'
            # 加载.env环境变量
            if env_file.exists():
                load_dotenv(env_file, override=True)
                Loggers.info(f"已加载环境变量文件: {env_file}")
            else:
                Loggers.error(f"环境变量文件不存在: {env_file}")
            # 加载YAML配置
            if yaml_file.exists():
                YamlUtil.init("config")
                config = YamlUtil.read_yaml(f"env/{env_name}.yaml")
                DataFactory._replace_env_vars(config)  # 递归替换
                Loggers.info(f"已加载YAML配置文件: {yaml_file}")
                cls._env_config = config
            else:
                Loggers.warning(f"YAML配置文件不存在: {yaml_file}")
                config = {}
                cls._env_config = config
            cls._initialized = True


    @staticmethod
    def _replace_env_vars(config: dict):
        """
        递归替换配置中的${ENV_VAR}为实际环境变量值。
        :param config: 配置字典
        """
        for key, value in config.items():
            if isinstance(value, dict):
                DataFactory._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if env_value is not None:
                    config[key] = env_value
                    Loggers.debug(f"替换环境变量: {env_var} -> {env_value}")
                else:
                    Loggers.warning(f"环境变量未定义: {env_var}")



    @classmethod
    def get_env_config(cls):
        """
        获取全局环境配置（含db_config），便于用例和工厂方法统一调用。
        :return: 环境配置字典
        """
        return cls._env_config

    @classmethod
    def get_base_data(cls, project="erp", db_config_name="erp_db", cache_key="init_cache"):
        """
        获取指定项目的基础数据，优先读缓存，否则自动初始化并写入缓存。
        :param project: 项目名（如erp/other_project）
        :param db_config_name: 数据库配置名
        :param cache_key: 缓存key
        :return: 原始业务数据（未结构化）
        """
        data = CacheUtil.get(cache_key)
        if not data:
            sql_config_full = YamlUtil.get_project_config(project, "base_init_sql.yaml")
            sql_config = sql_config_full.get("base_info", {})  # 只取 base_info 层
            Loggers.info(f"加载SQL配置keys: {list(sql_config.keys())}")
            db_config = cls._env_config["database"][db_config_name]
            data = SQLInitializer.init_sql(sql_config, db_config, cache_key=cache_key)
            CacheUtil.set(cache_key, data)
            Loggers.info(f"写入缓存成功，路径为: {CacheUtil._cache_dir / f'{cache_key}.json'}")
        return data

    @classmethod
    def get_env_config_by_name(cls, env_name="test"):
        """
        获取指定环境的配置
        :param env_name: 环境名
        :return: 环境配置字典
        """
        return YamlUtil.read_yaml(f"env/{env_name}.yaml")

    @classmethod
    def set_cache_data(cls, cache_key, data):
        """
        写入缓存数据。
        :param cache_key: 缓存key
        :param data: 要写入的数据
        """
        CacheUtil.set(cache_key, data)

if __name__ == "__main__":
    # 示例：初始化数据工厂并获取基础数据
    data = DataFactory()
    data = data.get_base_data()
    print(data)
    
    