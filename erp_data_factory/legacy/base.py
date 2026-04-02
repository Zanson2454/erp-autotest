from pathlib import Path
from dotenv import load_dotenv
import hashlib
import sys
from typing import Dict, Any, List, Optional, Union
import os
from decimal import Decimal

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from utils.yaml_util import YamlUtil
from utils.cache_util import CacheUtil
from utils.mysql_util import DBManager
from utils.log_util import Loggers


class ConfigLoader:
    """
    专门负责配置加载和环境变量替换
    新增组件，职责单一化
    支持多项目配置：通过 project 参数指定项目名称
    """

    def __init__(self, env_name: str = "test", project: str = None):
        """
        初始化配置加载器
        
        :param env_name: 环境名称（如 test, dev, staging, prod）
        :param project: 项目名称（可选），如果指定则从 config/env/{project}/{env_name}.yaml 加载，
                       否则从 config/env/{env_name}.yaml 加载（向后兼容）
        """
        self.env_name = env_name
        self.project = project
        self._env_config: Optional[Dict[str, Any]] = None

    def load_env_config(self) -> Dict[str, Any]:
        """
        加载环境配置，包含环境变量替换
        :return: 处理后的配置字典
        """
        if self._env_config is not None:
            return self._env_config

        # 确定.env文件路径（支持多项目模式）
        # 优先级：项目特定的.env > config/env/.env > 根目录.env
        project_env_file = None
        if self.project:
            # 多项目模式：优先加载项目特定的.env文件
            project_env_file = project_root / 'config' / 'env' / self.project / '.env'
        
        # 默认环境变量文件：config/env/.env（推荐位置）
        default_env_file = project_root / 'config' / 'env' / '.env'
        
        # 根目录.env文件（向后兼容）
        global_env_file = project_root / '.env'
        
        # 加载.env环境变量（按优先级顺序）
        env_loaded = False
        
        # 1. 优先加载项目特定的.env文件
        if project_env_file and project_env_file.exists():
            load_dotenv(project_env_file, override=True)
            Loggers.info(f"已加载项目环境变量文件: {project_env_file} (项目: {self.project})")
            env_loaded = True
        
        # 2. 加载默认环境变量文件 config/env/.env
        if default_env_file.exists():
            # override=False：如果项目特定的.env已加载，不再覆盖；否则覆盖
            load_dotenv(default_env_file, override=not env_loaded)
            if not env_loaded:
                Loggers.info(f"已加载默认环境变量文件: {default_env_file}")
            else:
                Loggers.debug(f"已加载默认环境变量文件作为补充: {default_env_file}")
            env_loaded = True
        
        # 3. 加载根目录.env文件（向后兼容）
        if global_env_file.exists():
            # override=False：前面的.env已加载的话，不再覆盖
            load_dotenv(global_env_file, override=not env_loaded)
            if not env_loaded:
                Loggers.info(f"已加载根目录环境变量文件: {global_env_file} (向后兼容)")
            else:
                Loggers.debug(f"已加载根目录环境变量文件作为补充: {global_env_file}")
        else:
            if not env_loaded:
                Loggers.warning(f"未找到环境变量文件，尝试了以下路径:")
                if self.project:
                    Loggers.warning(f"  - {project_env_file} (项目特定)")
                Loggers.warning(f"  - {default_env_file} (默认)")
                Loggers.warning(f"  - {global_env_file} (根目录)")
        
        # 确定YAML配置文件路径（支持多项目模式）
        if self.project:
            # 多项目模式：从项目目录加载配置
            yaml_file = project_root / 'config' / 'env' / self.project / f'{self.env_name}.yaml'
            if not yaml_file.exists():
                Loggers.warning(f"项目配置文件不存在: {yaml_file}，尝试使用默认配置")
                # 如果项目配置不存在，尝试使用默认配置（向后兼容）
                yaml_file = project_root / 'config' / 'env' / f'{self.env_name}.yaml'
        else:
            # 默认模式：从根目录加载配置（向后兼容）
            yaml_file = project_root / 'config' / 'env' / f'{self.env_name}.yaml'

        # 加载YAML配置
        if yaml_file.exists():
            YamlUtil.init("config")
            if self.project:
                # 多项目模式：使用相对路径
                relative_path = f"env/{self.project}/{self.env_name}.yaml"
            else:
                relative_path = f"env/{self.env_name}.yaml"
            
            config = YamlUtil.read_yaml(relative_path)
            self._replace_env_vars(config)  # 递归替换
            Loggers.info(f"已加载YAML配置文件: {yaml_file}" + (f" (项目: {self.project})" if self.project else ""))
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
    支持上下文管理器，自动管理数据库连接资源
    """

    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self._db_manager: Optional[DBManager] = None

    def get_db_manager(self) -> DBManager:
        """获取数据库管理器实例（延迟初始化）"""
        if self._db_manager is None:
            self._db_manager = DBManager(**self.db_config)
        return self._db_manager

    def close(self) -> None:
        """关闭数据库连接"""
        if self._db_manager:
            try:
                self._db_manager.close()
                Loggers.debug("SQLExecutor数据库连接已关闭")
            except Exception as e:
                Loggers.warning(f"关闭数据库连接时出错: {str(e)}")
            finally:
                self._db_manager = None

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，确保资源释放"""
        self.close()
        return False  # 不抑制异常

    @staticmethod
    def _render_sql(sql: str) -> str:
        """
        处理SQL字符串中的环境变量替换，支持 ${VAR_NAME:-default_value} 语法
        """
        import re
        import os
        # 匹配 ${VAR} 或 ${VAR:-default}
        pattern = re.compile(r'\$\{([a-zA-Z0-9_]+)(?::-([^}]*))?\}')
        
        def replacer(match):
            var_name = match.group(1)
            default_val = match.group(2) if match.group(2) is not None else ""
            # 获取环境变量，如果没有且无默认值，则使用默认值
            return os.getenv(var_name, default_val)
            
        return pattern.sub(replacer, sql)

    def execute_sql_config(self, sql_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行SQL配置，返回结果字典
        :param sql_config: SQL配置字典
        :return: 执行结果
        """
        result = {}
        for key, value in sql_config.items():
            if isinstance(value, dict) and 'sql' in value:
                raw_sql = value['sql']
                sql = self._render_sql(raw_sql)
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
    @staticmethod
    def _get_default_expire_minutes() -> int:
        """
        获取默认缓存过期时间（分钟）
        
        :return: 过期时间（分钟），测试环境5分钟，生产环境1440分钟（24小时）
        """
        env = os.getenv("TEST_ENV", "test")
        return 5 if env in ["test", "dev", "uat"] else 1440

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
            expire_minutes = cls._get_default_expire_minutes()
        
        # 缓存检查（保持向后兼容，所有项目共享缓存）
        # 如果项目切换，缓存会在过期时间内自动失效，或用户手动清除
        if cache_key:
            CacheUtil.init(str(project_root / 'testdata' / 'cache'), expire_minutes=expire_minutes)
            cache_data = CacheUtil.get(cache_key)
            if cache_data:
                Loggers.info(f"从缓存获取数据成功 (过期时间: {expire_minutes}分钟)")
                return cache_data
            Loggers.info(f"缓存数据不存在或已过期（超过{expire_minutes}分钟），开始初始化数据")

        # 使用上下文管理器确保数据库连接正确关闭
        with SQLExecutor(db_config) as sql_executor:
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
    _last_project = None  # 记录上次使用的项目，用于检测项目切换


    @classmethod
    def __init__(cls, env_name="test", db_config_name="erp_db", project=None):
        """
        向后兼容的初始化方法
        内部使用新的ConfigLoader组件，但保持原有行为
        
        :param env_name: 环境名称
        :param db_config_name: 数据库配置名（保留参数，向后兼容）
        :param project: 项目名称（可选），如果指定则从 config/env/{project}/{env_name}.yaml 加载
        """
        if not cls._initialized:
            # 从环境变量获取项目名称（如果未通过参数传入）
            if project is None:
                project = os.getenv("TEST_PROJECT")
            
            # 使用新的ConfigLoader
            cls._config_loader = ConfigLoader(env_name, project)
            cls._env_config = cls._config_loader.load_env_config()
            
            # 记录当前项目，用于检测项目切换
            cls._last_project = project
            
            cls._initialized = True



    @classmethod
    def get_env_config(cls):
        """
        获取全局环境配置（含db_config），便于用例和工厂方法统一调用。
        :return: 环境配置字典
        """
        return cls._env_config
    
    @classmethod
    def _clear_cache_if_project_changed(cls, cache_key: str, cache_dir: str) -> None:
        """
        检查项目是否切换，如果切换则清除缓存
        :param cache_key: 缓存key
        :param cache_dir: 缓存目录
        """
        current_project = os.getenv("TEST_PROJECT")
        
        # 如果项目切换了，清除缓存
        if cls._last_project is not None and cls._last_project != current_project:
            from utils.cache_util import CacheUtil
            from pathlib import Path
            
            cache_file = Path(cache_dir) / f"{cache_key}.json"
            if cache_file.exists():
                try:
                    cache_file.unlink()
                    Loggers.info(f"检测到项目切换（{cls._last_project} -> {current_project}），已清除缓存: {cache_file}")
                except Exception as e:
                    Loggers.warning(f"清除缓存文件失败: {cache_file}, 错误: {str(e)}")
        
        # 更新记录的项目
        cls._last_project = current_project

    @classmethod
    def _invalidate_json_cache_if_sql_yaml_changed(
        cls,
        cache_key: str,
        sql_yaml_path: Path,
        cache_dir: Union[str, Path],
    ) -> None:
        """若 SQL YAML 文件内容变更，则删除对应 json 缓存，避免改配置后仍读旧缓存。"""
        cache_dir_path = Path(cache_dir)
        sql_path = Path(sql_yaml_path).resolve()
        if not sql_path.is_file():
            return
        new_hash = hashlib.sha256(sql_path.read_bytes()).hexdigest()
        hash_file = cache_dir_path / f".{cache_key}.source_hash"
        json_file = cache_dir_path / f"{cache_key}.json"
        if hash_file.exists():
            try:
                old_hash = hash_file.read_text(encoding="utf-8").strip()
            except OSError:
                old_hash = ""
            if old_hash != new_hash and json_file.exists():
                try:
                    json_file.unlink()
                    Loggers.info(
                        f"检测到 SQL 配置文件已变更，已丢弃缓存: {cache_key} ({sql_path.name})"
                    )
                except OSError as exc:
                    Loggers.warning(f"删除过期 SQL 缓存失败: {json_file}, {exc}")
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            hash_file.write_text(new_hash, encoding="utf-8")
        except OSError as exc:
            Loggers.warning(f"写入 SQL 源 hash 失败: {hash_file}, {exc}")

    @classmethod
    def get_base_data(cls, project="erp", db_config_name="erp_db", cache_key="init_cache", expire_minutes: int = None):
        """
        获取指定项目的基础数据，优先读缓存，否则自动初始化并写入缓存。
        :param project: 项目名（如erp/other_project），注意这里的project指的是SQL配置文件的项目目录（config/erp/），不是环境配置的项目
        :param db_config_name: 数据库配置名
        :param cache_key: 缓存key（所有项目共享，向后兼容）
        :param expire_minutes: 缓存过期时间（分钟），None时自动根据环境判断：
            - 测试环境：5分钟（考虑用例执行时间）
            - 生产环境：1440分钟（24小时）
        :return: 原始业务数据（未结构化）
        """
        # 如果未指定过期时间，根据环境自动判断
        if expire_minutes is None:
            expire_minutes = SQLInitializer._get_default_expire_minutes()
        sql_config_full = YamlUtil.get_project_config(project, "base_init_sql.yaml")
        sql_config = sql_config_full.get("base_info", {})  # 只取 base_info 层
        Loggers.info(f"加载SQL配置keys: {list(sql_config.keys())}")

        # 获取数据库配置
        if cls._env_config:
            db_config = cls._env_config["database"][db_config_name]
        else:
            db_config = {}

        # 检查项目是否切换，如果切换则清除缓存
        cache_dir = str(project_root / 'testdata' / 'cache')
        cls._clear_cache_if_project_changed(cache_key, cache_dir)

        base_yaml = project_root / "config" / project / "base_init_sql.yaml"
        cls._invalidate_json_cache_if_sql_yaml_changed(cache_key, base_yaml, cache_dir)
        
        # SQLInitializer内部已处理缓存逻辑（保持向后兼容，不传递项目参数）
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
        :param cache_key: 缓存key（所有项目共享，向后兼容）
        :param cache_dir: 缓存目录
        :param expire_minutes: 缓存过期时间（分钟），None时自动根据环境判断：
            - 测试环境：5分钟（考虑用例执行时间）
            - 生产环境：1440分钟（24小时）
        :return: 查询结果
        
        注意：所有项目共享缓存，如果切换项目，建议：
        1. 等待缓存过期（测试环境5分钟）
        2. 手动清除缓存文件：rm testdata/cache/{cache_key}.json
        3. 使用 refresh=True 参数强制刷新
        """
        # 如果未指定过期时间，根据环境自动判断
        if expire_minutes is None:
            expire_minutes = SQLInitializer._get_default_expire_minutes()
        
        # 检查项目是否切换，如果切换则清除缓存
        cls._clear_cache_if_project_changed(cache_key, cache_dir)

        sql_path = Path(sql_config_path).resolve()
        cls._invalidate_json_cache_if_sql_yaml_changed(cache_key, sql_path, cache_dir)
        
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
        # 4. 初始化SQL并缓存（保持向后兼容，不传递项目参数）
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
            expire_minutes = SQLInitializer._get_default_expire_minutes()
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
                    # 使用上下文管理器确保数据库连接正确关闭
                    with SQLExecutor(db_cfg) as sql_executor:
                        result_data = sql_executor.execute_sql_config(sql_cfg)
                    return result_data
                return refresh_callback
            
            refresh_callbacks[cache_key] = make_refresh_callback(sql_config, db_config)
        
        # 执行刷新
        return CacheUtil.refresh_expired_cache(refresh_callbacks)

if __name__ == "__main__":
    import os
    env = os.getenv("TEST_ENV", "test")
    project = os.getenv("TEST_PROJECT")
    DataFactory.__init__(env_name=env, project=project)
    print(DataFactory.get_base_data(project="erp"))
    
    