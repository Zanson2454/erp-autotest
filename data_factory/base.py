from pathlib import Path
from dotenv import load_dotenv
import sys
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal
import os

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil
from utils.mysql_util import DBManager
from utils.log_util import Loggers

class SQLInitializer:
    """
    SQL初始化器：负责从YAML配置读取SQL，执行数据库查询，初始化基础数据，并缓存。
    用于数据工厂的底层数据准备。
    """
    @classmethod
    def init_sql(cls, config_path: Path, db_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        初始化SQL数据，优先从缓存获取，否则从YAML读取SQL并执行，写入缓存。
        :param config_path: SQL配置YAML路径
        :param db_config: 数据库连接配置
        :return: 结构化业务数据
        """
        cache_key = str(config_path.stem) + '_cache'
        CacheUtil.init(str(project_root / 'testdata' / 'cache'))
        Loggers.init()
        cache_data = CacheUtil.get(cache_key)
        if cache_data:
            Loggers.info("从缓存获取数据成功")
            return cache_data
        Loggers.info("缓存数据不存在或已过期，开始初始化数据")
        init_data = cls._init_sql_impl(config_path, db_config)
        CacheUtil.set(cache_key, init_data)
        Loggers.info(f"数据初始化完成并写入缓存: testdata/cache/{cache_key}.json")
        return init_data

    @staticmethod
    def _init_sql_impl(config_path: Path, db_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        实际执行SQL并分类结果，返回结构化数据。
        :param config_path: SQL配置YAML路径
        :param db_config: 数据库连接配置
        :return: 结构化业务数据
        """
        config = YamlUtil.read_yaml(str(config_path))
        if not config:
            raise ValueError(f"配置文件为空: {config_path}")
        # 初始化各业务分类
        init_data = {
            "user_info": {},
            "base_info": {},
            "org_info": {},
            "partner_info": {},
            "material_info": {}
        }
        DBManager.init(db_config)
        for query_key, query_config in config.get('base_info', {}).items():
            try:
                sql = query_config.get('sql', '')
                if not sql:
                    continue
                # 只支持无参数SQL，如需参数化可扩展
                result = DBManager.query(sql)
                formatted_result = SQLInitializer._format_result(result)
                category = SQLInitializer._get_result_category(query_key)
                init_data[category][query_key] = formatted_result[0] if formatted_result else None
            except Exception as e:
                Loggers.error(f"执行查询 {query_key} 时出错: {str(e)}")
                raise
        return init_data

    @staticmethod
    def _format_result(result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化SQL查询结果，处理Decimal和datetime类型，便于序列化。
        :param result: 查询结果
        :return: 格式化后的结果
        """
        if not result:
            return []
        return [{
            key: float(value) if isinstance(value, Decimal)
            else value.isoformat() if isinstance(value, datetime)
            else value
            for key, value in row.items()
        } for row in result]

    @staticmethod
    def _get_result_category(query_key: str) -> str:
        """
        根据key归类到base_info/org_info/partner_info/material_info等。
        :param query_key: 查询key
        :return: 分类名
        """
        if any(x in query_key for x in [
            'group_org', 'adm_org', 'com_org', 'pur_org', 'inv_org', 'sls_org', 'dept_org', 'pln_org']):
            return 'org_info'
        elif any(x in query_key for x in [
            'vend', 'cust', 'partner', 'cust_tax_type']):
            return 'partner_info'
        elif any(x in query_key for x in [
            'mat', 'atp', 'inv_loc', 'inv_type', 'mat_tax_type']):
            return 'material_info'
        return 'base_info'

class DataFactory:
    """
    通用数据工厂，统一管理测试用例所需的业务数据，支持数据获取、造数、清理、结构化、ID提取等能力。
    用例、BaseTest、业务工厂均可通过本类统一获取和管理数据。
    """
    _initialized = False
    _env_config = None

    @classmethod
    def __init__(cls, env_name="test",db_config_name="erp_db"):
        """
        初始化环境配置，加载.env和YAML，递归替换环境变量，合并db_config。
        :param env_name: 环境名（如test/dev/prod）
        """
        if not cls._initialized:
            env_file = project_root / '.env'
            yaml_file = project_root / 'config' / 'env' / f'{env_name}.yaml'

            # 1. 加载.env环境变量
            if env_file.exists():
                load_dotenv(env_file, override=True)
                Loggers.info(f"已加载环境变量文件: {env_file}")
            else:
                Loggers.error(f"环境变量文件不存在: {env_file}")

            # 2. 加载YAML配置
            if yaml_file.exists():
                YamlUtil.init("config")
                config = YamlUtil.read_yaml(f"env/{env_name}.yaml")
                Loggers.info(f"已加载YAML配置文件: {yaml_file}")
                # 3. 递归替换环境变量
                cls._replace_env_vars(config)
            else:
                Loggers.warning(f"YAML配置文件不存在: {yaml_file}")
                config = {}

            # 4. 合并db_config（变量名需与YAML一致）
            db_config = {
                "host": os.environ.get(f"{env_name.upper()}_DB_HOST"),
                "port": int(os.environ.get(f"{env_name.upper()}_DB_PORT", 3306)),
                "user": os.environ.get(f"{env_name.upper()}_DB_USER"),
                "password": os.environ.get(f"{env_name.upper()}_DB_PASSWORD"),
                "database": os.environ.get(f"{env_name.upper()}_DB_NAME"),
                "charset": os.environ.get("DB_CHARSET", "utf8mb4")
            }
            config["database"][db_config_name] = db_config
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
    def get_base_data(cls, module='gen',db_config_name="erp_db"):
        """
        获取指定模块的基础数据，优先读缓存，否则自动初始化并写入缓存。
        :param module: 业务模块名（如gen/fin/prd等）
        :return: 结构化业务数据
        """
        cache_key = f'{module}_cache'
        data = CacheUtil.get(cache_key)
        if not data:
            yaml_path = Path(__file__).parent.parent / 'testdata' / 'init' / f'{module}_init.yaml'
            db_config = cls._env_config["database"][db_config_name]
            data = SQLInitializer.init_sql(yaml_path, db_config)
        return data

    @classmethod
    def init_sql_data(cls, config_path: Path, db_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        直接初始化指定SQL配置的数据（兼容老接口）。
        :param config_path: SQL配置YAML路径
        :param db_config: 数据库连接配置
        :return: 结构化业务数据
        """
        return SQLInitializer.init_sql(config_path, db_config)

    @staticmethod
    def process_init_data(init_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        结构化原始init_data，便于用例直接取用。
        :param init_data: 原始数据
        :return: 结构化数据
        """
        return {
            "user_info": {"user_info": init_data.get("base_info", {}).get("user_info", {})},
            "base_info": {
                "so_type_info": init_data.get("base_info", {}).get("so_type_info", {}),
                "sales_channel_info": init_data.get("base_info", {}).get("sales_channel_info", {}),
                "exchange_rate_type_info": init_data.get("base_info", {}).get("exchange_rate_type_info", {}),
                "currency_info": init_data.get("base_info", {}).get("currency_info", {})
            },
            "org_info": {
                "sls_org_info": init_data.get("org_info", {}).get("sls_org_info", {}),
                "pur_org_info": init_data.get("org_info", {}).get("pur_org_info", {}),
                "inv_org_info": init_data.get("org_info", {}).get("inv_org_info", {}),
                "com_org_info": init_data.get("org_info", {}).get("com_org_info", {})
            },
            "partner_info": {
                "cust_info": init_data.get("partner_info", {}).get("cust_info", {})
            },
            "material_info": {
                "inv_loc_info": init_data.get("material_info", {}).get("inv_loc_info", {})
            }
        }

    @staticmethod
    def extract_ids(structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从结构化数据中提取常用ID，便于用例参数化。
        :param structured_data: 结构化数据
        :return: ID映射字典
        """
        id_mappings = {
            'cust_id': ('partner_info', 'cust_info', 'id'),
            'so_type_id': ('base_info', 'so_type_info', 'id'),
            'sls_org_id': ('org_info', 'sls_org_info', 'id'),
            'pur_org_id': ('org_info', 'pur_org_info', 'id'),
            'inv_org_id': ('org_info', 'inv_org_info', 'id'),
            'com_org_id': ('org_info', 'com_org_info', 'id'),
            'sls_dc_id': ('base_info', 'sales_channel_info', 'id'),
            'inv_loc_id': ('material_info', 'inv_loc_info', 'id'),
            'exchange_rate_type_id': ('base_info', 'exchange_rate_type_info', 'exchange_rate_type_id'),
            'base_curr_id': ('base_info', 'currency_info', 'curr_id'),
            'sls_curr_id': ('base_info', 'currency_info', 'curr_id')
        }
        ids = {}
        for attr_name, path in id_mappings.items():
            value = structured_data
            # print(f"value: {value}")
            for key in path:
                # print(f"key: {key}")
                value = value.get(key, {})
            ids[attr_name] = value
        print(f"ids: {ids}")
        return ids

    @classmethod
    def clear_test_data(cls, data_type, **kwargs):
        """
        清理测试数据（预留接口，便于后续扩展）。
        :param data_type: 数据类型
        :param kwargs: 其他参数
        """
        # TODO: 实现数据清理逻辑
        pass

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
    # data = data.get_env_config()
    data = data.get_base_data()
    # data = data.extract_ids(data)
    print(data)
    
    