import os
import sys
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional, Union, Tuple
import allure
import pymysql
from pymysql.cursors import DictCursor
from pymysql.connections import Connection
from dbutils.pooled_db import PooledDB as Pool
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.yaml_util import YamlUtil
from utils.exception_util import safe_db_operation, TestException, DatabaseException
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
    """数据库管理器
    
    提供基本的数据库操作功能，包括：
    1. 查询数据
    2. 插入数据
    3. 更新数据
    4. 删除数据
    
    使用示例：
    ```python
    # 创建数据库连接
    db = DBManager({
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'test',
        'charset': 'utf8mb4'
    })
    
    # 查询数据
    results = db.query("SELECT * FROM users WHERE id = %s", [1])
    
    # 插入数据
    db.insert("users", {"name": "张三", "age": 18})
    
    # 更新数据
    db.update("users", {"age": 19}, "name = %s", ["张三"])
    
    # 删除数据
    db.delete("users", "name = %s", ["张三"])
    ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        """初始化数据库连接
        
        Args:
            config: 数据库配置，包含 host, port, user, password, database 等
        """
        self.config = config
        self.connection = None
        self.log = Loggers()
        self.connect()
    
    def connect(self) -> None:
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                **self.config,
                cursorclass=DictCursor
            )
            self.log.info(f"数据库连接成功 [host={self.config['host']}, port={self.config['port']}]")
        except Exception as e:
            self.log.error(f"数据库连接失败: {str(e)}")
            raise
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.log.info("数据库连接已关闭")
    
    def query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """执行查询SQL
        
        Args:
            sql: SQL语句
            params: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params or [])
                result = cursor.fetchall()
                self.log.debug(f"执行查询: {sql}")
                if params:
                    self.log.debug(f"查询参数: {params}")
                self.log.debug(f"查询结果: {json.dumps(result, ensure_ascii=False, cls=DecimalEncoder)}")
                return result
        except Exception as e:
            self.log.error(f"查询执行失败: {str(e)}")
            self.log.error(f"SQL: {sql}")
            if params:
                self.log.error(f"参数: {params}")
            raise
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入数据
        
        Args:
            table: 表名
            data: 要插入的数据
            
        Returns:
            int: 插入的ID
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = list(data.values())
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, values)
                self.connection.commit()
                inserted_id = cursor.lastrowid
                self.log.info(f"插入数据成功 [表={table}, ID={inserted_id}]")
                return inserted_id
        except Exception as e:
            self.connection.rollback()
            self.log.error(f"插入数据失败: {str(e)}")
            self.log.error(f"SQL: {sql}")
            self.log.error(f"数据: {data}")
            raise
    
    def update(self, table: str, data: Dict[str, Any], where: str, params: Optional[List[Any]] = None) -> int:
        """更新数据
        
        Args:
            table: 表名
            data: 要更新的数据
            where: WHERE条件
            params: 条件参数
            
        Returns:
            int: 受影响的行数
        """
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        values = list(data.values()) + (params or [])
        
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, values)
                self.connection.commit()
                self.log.info(f"更新数据成功 [表={table}, 影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            self.connection.rollback()
            self.log.error(f"更新数据失败: {str(e)}")
            self.log.error(f"SQL: {sql}")
            self.log.error(f"数据: {data}")
            raise
    
    def delete(self, table: str, where: str, params: Optional[List[Any]] = None) -> int:
        """删除数据
        
        Args:
            table: 表名
            where: WHERE条件
            params: 条件参数
            
        Returns:
            int: 受影响的行数
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or [])
                self.connection.commit()
                self.log.info(f"删除数据成功 [表={table}, 影响行数={affected_rows}]")
                return affected_rows
        except Exception as e:
            self.connection.rollback()
            self.log.error(f"删除数据失败: {str(e)}")
            self.log.error(f"SQL: {sql}")
            if params:
                self.log.error(f"参数: {params}")
            raise

if __name__ == "__main__":
    # 测试代码
    db = DBManager({
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'test',
        'charset': 'utf8mb4'
    })
    
    try:
        # 查询测试
        results = db.query("SELECT * FROM users WHERE id = %s", [1])
        print(json.dumps(results, ensure_ascii=False, indent=2, cls=DecimalEncoder))
    finally:
        db.close()