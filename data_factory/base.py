from pathlib import Path
from dotenv import load_dotenv
import sys
from typing import Dict, Any, List, Optional
import os
from decimal import Decimal

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil
from utils.mysql_util import DBManager
from utils.log_util import Loggers


class ConfigLoader:
    """
    专门负责配置加载和环境变量替换
    新增组件，职责单一化
    """

    def __init__(self, env_name: str = "test"):
        self.env_name = env_name
        self._env_config: Optional[Dict[str, Any]] = None

    def load_env_config(self) -> Dict[str, Any]:
        """
        加载环境配置，包含环境变量替换
        :return: 处理后的配置字典
        """
        if self._env_config is not None:
            return self._env_config

        env_file = project_root / '.env'
        yaml_file = project_root / 'config' / 'env' / f'{self.env_name}.yaml'

        # 加载.env环境变量
        if env_file.exists():
            load_dotenv(env_file, override=True)
            Loggers.info(f"已加载环境变量文件: {env_file}")
        else:
            Loggers.warning(f"环境变量文件不存在: {env_file}")

        # 加载YAML配置
        if yaml_file.exists():
            YamlUtil.init("config")
            config = YamlUtil.read_yaml(f"env/{self.env_name}.yaml")
            self._replace_env_vars(config)  # 递归替换
            Loggers.info(f"已加载YAML配置文件: {yaml_file}")
            self._env_config = config
        else:
            Loggers.warning(f"YAML配置文件不存在: {yaml_file}")
            self._env_config = {}

        return self._env_config

    @staticmethod
    def _replace_env_vars(config: dict) -> None:
        """
        递归替换配置中的${ENV_VAR}为实际环境变量值。
        :param config: 配置字典
        """
        for key, value in config.items():
            if isinstance(value, dict):
                ConfigLoader._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if env_value is not None:
                    config[key] = env_value
                    Loggers.debug(f"替换环境变量: {env_var} -> {env_value}")
                else:
                    Loggers.warning(f"环境变量未定义: {env_var}")


class SQLExecutor:
    """
    专门负责SQL执行的新组件
    职责：执行SQL查询、数据转换、结果处理
    """

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self._db_manager: Optional[DBManager] = None

    def get_db_manager(self) -> DBManager:
        """获取数据库管理器实例（延迟初始化）"""
        if self._db_manager is None:
            self._db_manager = DBManager(**self.db_config)
        return self._db_manager

    def execute_sql_config(self, sql_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行SQL配置，返回结果字典
        :param sql_config: SQL配置字典
        :return: 执行结果
        """
        result = {}
        for key, value in sql_config.items():
            if isinstance(value, dict) and 'sql' in value:
                sql = value['sql']
                try:
                    db_manager = self.get_db_manager()
                    query_result = db_manager.query(sql)
                    # 转换Decimal类型为float
                    converted_result = self._convert_decimal_to_float(query_result)
                    result[key] = converted_result
                    Loggers.info(f"SQL执行结果: {key} -> {len(converted_result) if isinstance(converted_result, list) else 'success'}")
                except Exception as e:
                    Loggers.error(f"执行查询 {key} 时出错: {str(e)}")
                    result[key] = None
            elif isinstance(value, dict):
                # 递归处理嵌套配置
                result[key] = self.execute_sql_config(value)
        return result

    @staticmethod
    def _convert_decimal_to_float(obj: Any) -> Any:
        """递归转换字典和列表中的Decimal类型为float"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: SQLExecutor._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [SQLExecutor._convert_decimal_to_float(item) for item in obj]
        return obj


class SQLInitializer:
    """
    通用SQL初始化器：负责从YAML配置读取SQL，执行数据库查询，初始化基础数据，并缓存。
    仅做通用数据加载，不做结构化、ID提取、分类等业务处理。

    兼容性说明：保留原有API，支持向后兼容
    """
    @classmethod
    def init_sql(cls, sql_config: dict, db_config: Dict[str, Any], cache_key: str = "init_cache", expire_minutes: int = None) -> Dict[str, Any]:
        """
        初始化SQL数据，递归遍历yaml，遇到sql字段就执行，最终返回结构与yaml一致。
        :param sql_config: SQL配置（已加载的dict）
        :param db_config: 数据库连接配置
        :param cache_key: 缓存key（可选）
        :param expire_minutes: 缓存过期时间（分钟），None时自动根据环境判断：
            - 测试环境：5分钟（考虑用例执行时间）
            - 生产环境：1440分钟（24小时）
        :return: 原始业务数据
        """
        # 如果未指定过期时间，根据环境自动判断
        if expire_minutes is None:
            import os
            env = os.getenv("TEST_ENV", "test")
            # 测试环境使用5分钟，生产环境使用24小时
            expire_minutes = 5 if env in ["test", "dev", "uat"] else 1440
        # 缓存检查
        if cache_key:
            CacheUtil.init(str(project_root / 'testdata' / 'cache'), expire_minutes=expire_minutes)
            cache_data = CacheUtil.get(cache_key)
            if cache_data:
                Loggers.info(f"从缓存获取数据成功 (过期时间: {expire_minutes}分钟)")
                return cache_data
            Loggers.info(f"缓存数据不存在或已过期（超过{expire_minutes}分钟），开始初始化数据")

        # 使用新的SQLExecutor执行查询
        sql_executor = SQLExecutor(db_config)
        result_data = sql_executor.execute_sql_config(sql_config)

        if not result_data:
            Loggers.warning("所有SQL查询均未返回数据，请检查数据库连接和SQL配置！")

        # 缓存结果
        if cache_key:
            CacheUtil.set(cache_key, result_data)
            Loggers.info(f"数据初始化完成并写入缓存: testdata/cache/{cache_key}.json (过期时间: {expire_minutes}分钟)")

        return result_data

class DataFactory:
    """
    通用数据工厂，仅负责数据加载、SQL执行、缓存、环境配置加载。
    结构化、ID提取、分类等业务逻辑由业务工厂实现。

    重构说明：内部使用新的组件类（ConfigLoader, SQLExecutor），但保持原有API向后兼容
    """
    _initialized = False
    _env_config = None
    _config_loader = None  # 新增：配置加载器实例


    @classmethod
    def __init__(cls, env_name="test", db_config_name="erp_db"):
        """
        向后兼容的初始化方法
        内部使用新的ConfigLoader组件，但保持原有行为
        """
        if not cls._initialized:
            # 使用新的ConfigLoader
            cls._config_loader = ConfigLoader(env_name)
            cls._env_config = cls._config_loader.load_env_config()
            cls._initialized = True



    @classmethod
    def get_env_config(cls):
        """
        获取全局环境配置（含db_config），便于用例和工厂方法统一调用。
        :return: 环境配置字典
        """
        return cls._env_config

    @classmethod
    def get_base_data(cls, project="erp", db_config_name="erp_db", cache_key="init_cache", expire_minutes: int = None):
        """
        获取指定项目的基础数据，优先读缓存，否则自动初始化并写入缓存。
        :param project: 项目名（如erp/other_project）
        :param db_config_name: 数据库配置名
        :param cache_key: 缓存key
        :param expire_minutes: 缓存过期时间（分钟），None时自动根据环境判断：
            - 测试环境：5分钟（考虑用例执行时间）
            - 生产环境：1440分钟（24小时）
        :return: 原始业务数据（未结构化）
        """
        # 如果未指定过期时间，根据环境自动判断
        if expire_minutes is None:
            import os
            env = os.getenv("TEST_ENV", "test")
            # 测试环境使用5分钟，生产环境使用24小时
            expire_minutes = 5 if env in ["test", "dev", "uat"] else 1440
        sql_config_full = YamlUtil.get_project_config(project, "base_init_sql.yaml")
        sql_config = sql_config_full.get("base_info", {})  # 只取 base_info 层
        Loggers.info(f"加载SQL配置keys: {list(sql_config.keys())}")

        # 获取数据库配置
        if cls._env_config:
            db_config = cls._env_config["database"][db_config_name]
        else:
            db_config = {}

        # SQLInitializer内部已处理缓存逻辑
        return SQLInitializer.init_sql(sql_config, db_config, cache_key=cache_key, expire_minutes=expire_minutes)

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

    @classmethod
    def init_sql_cache(
        cls,
        sql_config_path: str,
        db_config_name: str = "erp_db",
        cache_key: str = "init_cache",
        cache_dir: str = "testdata/cache",
        expire_minutes: int = None
    ) -> dict:
        """
        通用SQL缓存初始化入口
        :param sql_config_path: SQL配置文件路径（绝对或相对）
        :param db_config_name: 数据库配置名
        :param cache_key: 缓存key
        :param cache_dir: 缓存目录
        :param expire_minutes: 缓存过期时间（分钟），None时自动根据环境判断：
            - 测试环境：5分钟（考虑用例执行时间）
            - 生产环境：1440分钟（24小时）
        :return: 查询结果
        """
        # 如果未指定过期时间，根据环境自动判断
        if expire_minutes is None:
            import os
            env = os.getenv("TEST_ENV", "test")
            # 测试环境使用5分钟，生产环境使用24小时
            expire_minutes = 5 if env in ["test", "dev", "uat"] else 1440
        # 1. 读取SQL配置
        sql_config = YamlUtil.read_yaml(sql_config_path)
        # 2. 获取数据库配置
        env_config = cls.get_env_config()
        if env_config:
            db_config = env_config["database"][db_config_name]
        else:
            db_config = {}
        # 3. 初始化缓存目录（使用指定的过期时间）
        CacheUtil.init(cache_dir, expire_minutes=expire_minutes)
        # 4. 初始化SQL并缓存
        return SQLInitializer.init_sql(sql_config, db_config, cache_key=cache_key, expire_minutes=expire_minutes)
    
    @classmethod
    def refresh_expired_cache(
        cls,
        refresh_configs: Dict[str, Dict[str, Any]],
        cache_dir: str = "testdata/cache",
        expire_minutes: int = None
    ) -> Dict[str, bool]:
        """
        方案2：重新拉取并覆盖过期的缓存
        
        :param refresh_configs: 刷新配置字典，格式为:
            {
                "cache_key": {
                    "sql_config_path": "config/erp/base_init_sql.yaml",
                    "db_config_name": "erp_db",
                    "sql_config": {...}  # 可选，如果提供则直接使用，否则从sql_config_path读取
                },
                ...
            }
        :param cache_dir: 缓存目录
        :param expire_minutes: 缓存过期时间（分钟），None时自动根据环境判断：
            - 测试环境：5分钟（考虑用例执行时间）
            - 生产环境：1440分钟（24小时）
        :return: 刷新结果字典，key为缓存key，value为是否成功刷新
        """
        # 如果未指定过期时间，根据环境自动判断
        if expire_minutes is None:
            import os
            env = os.getenv("TEST_ENV", "test")
            # 测试环境使用5分钟，生产环境使用24小时
            expire_minutes = 5 if env in ["test", "dev", "uat"] else 1440
        CacheUtil.init(cache_dir, expire_minutes=expire_minutes)
        
        # 构建刷新回调函数字典
        refresh_callbacks = {}
        env_config = cls.get_env_config()
        
        for cache_key, config in refresh_configs.items():
            sql_config_path = config.get("sql_config_path")
            db_config_name = config.get("db_config_name", "erp_db")
            sql_config = config.get("sql_config")
            
            # 如果没有提供sql_config，从文件读取
            if sql_config is None and sql_config_path:
                sql_config = YamlUtil.read_yaml(sql_config_path)
            
            if not sql_config:
                Loggers.warning(f"缓存 {cache_key} 的刷新配置缺少sql_config或sql_config_path，跳过")
                continue
            
            # 获取数据库配置
            if env_config:
                db_config = env_config["database"].get(db_config_name, {})
            else:
                db_config = {}
            
            # 创建刷新回调函数（使用闭包捕获当前循环的变量）
            def make_refresh_callback(sql_cfg, db_cfg):
                def refresh_callback(cache_key: str) -> Dict[str, Any]:
                    Loggers.info(f"执行刷新回调: {cache_key}")
                    sql_executor = SQLExecutor(db_cfg)
                    result_data = sql_executor.execute_sql_config(sql_cfg)
                    return result_data
                return refresh_callback
            
            refresh_callbacks[cache_key] = make_refresh_callback(sql_config, db_config)
        
        # 执行刷新
        return CacheUtil.refresh_expired_cache(refresh_callbacks)

if __name__ == "__main__":
    # 示例：初始化数据工厂并获取基础数据
    data = DataFactory()
    data = data.get_base_data()
    print(data)
    
    