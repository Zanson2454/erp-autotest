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
    _connection = None
    _initialized = False
    _logger = Loggers

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

    @classmethod
    def close(cls):
        if cls._connection:
            cls._connection.close()
            cls._connection = None
            cls._logger.info("数据库连接已关闭")

    @classmethod
    def query(cls, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        cls.connect()
        try:
            with cls._connection.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
                cls._logger.debug(f"执行查询: {sql}")
                if params:
                    cls._logger.debug(f"查询参数: {params}")
                cls._logger.debug(f"查询结果: {json.dumps(result, ensure_ascii=False, cls=DecimalEncoder)}")
                return result
        except Exception as e:
            cls._logger.error(f"查询执行失败: {str(e)}")
            cls._logger.error(f"SQL: {sql}")
            if params:
                cls._logger.error(f"参数: {params}")
            raise

    @classmethod
    def insert(cls, table: str, data: Dict[str, Any]) -> int:
        cls.connect()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        try:
            with cls._connection.cursor() as cursor:
                cursor.execute(sql, values)
                cls._connection.commit()
                inserted_id = cursor.lastrowid
                cls._logger.info(f"插入数据成功 [表={table}, ID={inserted_id}]")
                return inserted_id
        except Exception as e:
            cls._connection.rollback()
            cls._logger.error(f"插入数据失败: {str(e)}")
            cls._logger.error(f"SQL: {sql}")
            cls._logger.error(f"数据: {data}")
            raise

    @classmethod
    def update(cls, table: str, data: Dict[str, Any], where: str, params: Optional[List[Any]] = None) -> int:
        cls.connect()
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        values = list(data.values()) + (params or [])
        try:
            with cls._connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, values)
                cls._connection.commit()
                cls._logger.info(f"更新数据成功 [表={table}, 影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            cls._connection.rollback()
            cls._logger.error(f"更新数据失败: {str(e)}")
            cls._logger.error(f"SQL: {sql}")
            cls._logger.error(f"数据: {data}")
            raise

    @classmethod
    def delete(cls, table: str, where: str, params: Optional[List[Any]] = None) -> int:
        cls.connect()
        sql = f"DELETE FROM {table} WHERE {where}"
        try:
            with cls._connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or [])
                cls._connection.commit()
                cls._logger.info(f"删除数据成功 [表={table}, 影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            cls._connection.rollback()
            cls._logger.error(f"删除数据失败: {str(e)}")
            cls._logger.error(f"SQL: {sql}")
            if params:
                cls._logger.error(f"参数: {params}")
            raise

if __name__ == "__main__":
    # 测试代码
      # 数据库配置
    db_config ={}
    db = DBManager()
    db.init(db_config)
    print(db.query("SELECT * FROM users WHERE id = %s", [1]))

    try:
        # 查询测试
        results = db.query("SELECT * FROM users WHERE id = %s", [1])
        print(json.dumps(results, ensure_ascii=False, indent=2, cls=DecimalEncoder))
    finally:
        db.close()