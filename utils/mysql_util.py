import sys
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional, Union, Tuple
import pymysql
from pymysql.cursors import DictCursor
from pymysql.connections import Connection
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from dbutils.pooled_db import PooledDB

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.log_util import Loggers



log = Loggers()

class DecimalEncoder(json.JSONEncoder):
    """处理 Decimal 类型的 JSON 编码器"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

class DBManager:
    """数据库管理器（全类属性+类方法风格）"""
    _config: Dict[str, Any] = {}
    _connection: Optional[Connection] = None
    _initialized = False
    _logger = Loggers
    _pool: Optional[PooledDB] = None  # 连接池实例

    # 连接池默认配置
    _default_pool_config = {
        'mincached': 2,    # 最小空闲连接数
        'maxcached': 10,   # 最大空闲连接数
        'maxconnections': 20,  # 最大连接数
        'blocking': True,   # 连接不足时是否等待
        'maxusage': 500,   # 单连接最大使用次数
    }

    def __init__(self, **kwargs):
        """新增：支持实例化构造，每个实例独立连接"""
        if kwargs:
            # 提取连接池配置参数
            pool_config = kwargs.pop('pool_config', None)
            
            # 实例模式：独立配置和连接
            self._instance_config = self._validate_config(kwargs)
            self._instance_connection: Optional[Connection] = None
            self._is_instance_mode = True
            self._is_pool_mode = kwargs.get('use_pool', True)  # 默认启用连接池
            self._instance_pool: Optional[PooledDB] = None
            
            # 合并连接池配置（参数传入 > 默认配置）
            self._pool_config = {**self._default_pool_config, **(pool_config or {})}
            
            if self._is_pool_mode:
                self._connect_pool()
            else:
                self._connect_instance()
        else:
            # 兼容模式：使用类级别连接
            self._is_instance_mode = False
            self._is_pool_mode = False
            self._pool_config = self._default_pool_config
            
    def execute(self, sql: str, params: Optional[List[Any]] = None) -> int:
        """执行SQL语句（INSERT/UPDATE/DELETE等）"""
        import os
        if sql.strip().upper().startswith("DELETE"):
            if os.getenv("ENABLE_PHYSICAL_DELETE", "true").lower() != "true":
                self._logger.warning(f"由于 ENABLE_PHYSICAL_DELETE=false，已拦截 DELETE 语句: {sql}")
                return 0

        connection = self._get_connection()
            
        try:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or [])
                connection.commit()
                self._logger.info(f"SQL执行成功 [影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            connection.rollback()
            self._logger.error(f"SQL执行失败: {str(e)}")
            self._logger.error(f"SQL: {sql}")
            if params:
                self._logger.error(f"参数: {params}")
            raise

    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证并标准化配置"""
        # 自动类型转换，保证port为int
        if "port" in config:
            try:
                config["port"] = int(config["port"])
            except Exception:
                config["port"] = 3306
        if not config.get("charset"):
            config["charset"] = "utf8mb4"
        # 验证必需字段
        required_fields = ["database", "host", "password", "user"]
        for field in required_fields:
            if not config.get(field):
                raise ValueError(f"数据库配置缺少 {field} 字段")
        return config

    def _connect_instance(self):
        """实例连接方法"""
        if self._instance_connection is None:
            try:
                self._instance_connection = pymysql.connect(
                    **self._instance_config,
                    cursorclass=DictCursor
                )
                self._logger.info(f"数据库实例连接成功 [database={self._instance_config['database']}]")
            except Exception as e:
                self._logger.error(f"数据库实例连接失败: {str(e)}")
                raise

    def _connect_pool(self):
        """连接池连接方法"""
        if self._instance_pool is None:
            try:
                self._instance_pool = PooledDB(
                    pymysql,
                    **self._pool_config,
                    **self._instance_config,
                    cursorclass=DictCursor
                )
                self._logger.info(f"数据库连接池创建成功 [database={self._instance_config['database']}, "
                               f"mincached={self._pool_config['mincached']}, "
                               f"maxcached={self._pool_config['maxcached']}]")
            except Exception as e:
                self._logger.error(f"数据库连接池创建失败: {str(e)}")
                raise

    @classmethod
    def init(cls, config: Dict[str, Any]):
        # 自动类型转换，保证port为int
        if "port" in config:
            try:
                config["port"] = int(config["port"])
            except Exception:
                config["port"] = 3306
        if not config.get("charset"):
            config["charset"] = "utf8mb4"
        if not config.get("database"):
            raise ValueError("数据库配置缺少 database 字段")
        if not config.get("host"):
            raise ValueError("数据库配置缺少 host 字段")
        if not config.get('password'):
            raise ValueError("数据库配置缺少 password 字段")
        if not config.get('user'):
            raise ValueError("数据库配置缺少 user 字段")
        if not cls._initialized or cls._config != config:
            cls._config = config
            cls._connection = None
            cls._initialized = True
            cls.connect()

    @classmethod
    def connect(cls):
        if cls._connection is None:
            try:
                cls._connection = pymysql.connect(
                    **cls._config,
                    cursorclass=DictCursor
                )
                cls._logger.info(f"数据库连接成功 [host={cls._config['host']}, port={cls._config['port']}]")
            except Exception as e:
                cls._logger.error(f"数据库连接失败: {str(e)}")
                raise

    def _get_connection(self):
        """获取连接（支持连接池和普通连接）"""
        # 实例模式
        if hasattr(self, '_is_instance_mode') and self._is_instance_mode:
            if self._is_pool_mode and self._instance_pool:
                return self._instance_pool.connection()
            elif self._instance_connection:
                return self._instance_connection
            else:
                raise RuntimeError("实例数据库连接未建立")
        # 类模式（向后兼容）
        else:
            self.__class__.connect()
            if self.__class__._connection is None:
                raise RuntimeError("数据库连接未建立")
            return self.__class__._connection

    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """查询方法 - 支持实例和类调用"""
        connection = self._get_connection()
            
        try:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
                self._logger.debug(f"执行查询: {sql}")
                if params:
                    self._logger.debug(f"查询参数: {params}")
                self._logger.debug(f"查询结果: {json.dumps(list(result), ensure_ascii=False, cls=DecimalEncoder)}")
                return list(result)
        except Exception as e:
            self._logger.error(f"查询执行失败: {str(e)}")
            self._logger.error(f"SQL: {sql}")
            if params:
                self._logger.error(f"参数: {params}")
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入方法 - 支持实例和类调用"""
        connection = self._get_connection()
            
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, values)
                connection.commit()
                inserted_id = cursor.lastrowid
                self._logger.info(f"插入数据成功 [表={table}, ID={inserted_id}]")
                return inserted_id
        except Exception as e:
            connection.rollback()
            self._logger.error(f"插入数据失败: {str(e)}")
            self._logger.error(f"SQL: {sql}")
            self._logger.error(f"数据: {data}")
            raise

    def update(self, table: str, data: Dict[str, Any], where: str, params: Optional[List[Any]] = None) -> int:
        """更新方法 - 支持实例和类调用"""
        connection = self._get_connection()
            
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        values = list(data.values()) + (params or [])
        try:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, values)
                connection.commit()
                self._logger.info(f"更新数据成功 [表={table}, 影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            connection.rollback()
            self._logger.error(f"更新数据失败: {str(e)}")
            self._logger.error(f"SQL: {sql}")
            self._logger.error(f"数据: {data}")
            raise

    def delete(self, table: str, where: str, params: Optional[List[Any]] = None) -> int:
        """删除方法 - 支持实例和类调用"""
        import os
        if os.getenv("ENABLE_PHYSICAL_DELETE", "true").lower() != "true":
            self._logger.warning(f"由于 ENABLE_PHYSICAL_DELETE=false，已拦截对表 {table} 的物理删除操作")
            return 0

        connection = self._get_connection()
            
        sql = f"DELETE FROM {table} WHERE {where}"
        try:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or [])
                connection.commit()
                self._logger.info(f"删除数据成功 [表={table}, 影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            connection.rollback()
            self._logger.error(f"删除数据失败: {str(e)}")
            self._logger.error(f"SQL: {sql}")
            if params:
                self._logger.error(f"参数: {params}")
            raise
        


    def close(self):
        """关闭连接"""
        if hasattr(self, '_instance_connection') and self._instance_connection:
            # 实例模式：关闭实例连接
            self._instance_connection.close()
            self._instance_connection = None
            self._logger.info("实例数据库连接已关闭")
        else:
            # 类模式：关闭类连接
            if self.__class__._connection:
                self.__class__._connection.close()
                self.__class__._connection = None
                self._logger.info("类数据库连接已关闭")



if __name__ == "__main__":
    # 测试代码
    print("测试DBManager类...")
    
    # 测试1: 无参数构造（兼容模式）
    db = DBManager()
    print("✓ 无参数构造成功")
    
    # 测试2: 有参数构造（实例模式）
    test_config = {
        "host": "localhost",
        "port": 3306,
        "user": "test",
        "password": "test",
        "database": "test",
        "charset": "utf8mb4"
    }
    
    try:
        db_instance = DBManager(**test_config)
        print("✓ 有参数构造成功")
        print(f"✓ 实例配置: {db_instance._instance_config['database']}")
    except Exception as e:
        print(f"○ 有参数构造测试（预期可能失败，因为没有真实数据库）: {e}")
    
    print("✓ DBManager测试完成")