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
    
    提供数据库连接池、事务管理和查询执行功能。
    支持自动重连、连接池管理和事务控制。
    
    使用示例：
    ```python
    # 使用上下文管理器
    with DBManager() as db:
        results = db.execute_query("SELECT * FROM users WHERE id = %s", {"id": 1})
    
    # 使用连接池
    db = DBManager(pool_size=5)
    try:
        results = db.execute_query("SELECT * FROM users")
    finally:
        db.close()
    ```
    """
    
    _instance = None
    _pool: Optional[Pool] = None
    
    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        pool_size: int = 5,
        pool_name: str = "default",
        is_runtime: bool = False
    ):
        """初始化数据库管理器
        
        Args:
            pool_size: 连接池大小
            pool_name: 连接池名称
            is_runtime: 是否连接运行时数据库
        """
        self.pool_size = pool_size
        self.pool_name = pool_name
        self.is_runtime = is_runtime
        self.connection: Optional[Connection] = None
        self.log = log  # 先初始化logger
        self._init_pool()  # 再初始化连接池
        self.log.info(f"数据库管理器初始化完成 [pool={pool_name}, size={pool_size}, runtime={is_runtime}]")
    
    def _init_pool(self) -> None:
        """初始化数据库连接池"""
        if DBManager._pool is None:
            db_config = YamlUtil().get_db_config()
            DBManager._pool = Pool(
                creator=pymysql,
                maxconnections=self.pool_size,
                mincached=2,
                maxcached=5,
                blocking=True,
                maxusage=None,
                setsession=[],
                ping=0,
                **{
                    'host': db_config['host'],
                    'port': int(db_config['port']),
                    'user': db_config['user'],
                    'password': db_config['password'],
                    'database': db_config['name'],
                    'charset': 'utf8mb4',
                    'cursorclass': DictCursor
                }
            )
            self.log.info(f"数据库连接池初始化完成 [host={db_config['host']}, port={db_config['port']}]")
    
    def __enter__(self) -> 'DBManager':
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.disconnect()
    
    @safe_db_operation(error_message="数据库连接失败")
    def connect(self) -> None:
        """建立数据库连接"""
        if not self.connection:
            self.connection = DBManager._pool.connection()
            self.log.debug(f"获取数据库连接 [id={id(self.connection)}]")
    
    def disconnect(self) -> None:
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.log.debug("数据库连接已关闭")
    
    def close(self) -> None:
        """关闭连接池"""
        if DBManager._pool:
            DBManager._pool.close()
            DBManager._pool = None
            self.log.info("数据库连接池已关闭")
    
    @contextmanager
    def cursor(self) -> Generator[DictCursor, None, None]:
        """创建数据库游标的上下文管理器
        
        Yields:
            DictCursor: 数据库游标
            
        Raises:
            DatabaseException: 数据库操作异常
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
            self.log.debug("数据库事务已提交")
        except Exception as e:
            self.connection.rollback()
            self.log.error(f"数据库事务回滚: {str(e)}")
            raise DatabaseException(f"数据库操作失败: {str(e)}")
        finally:
            cursor.close()
            self.disconnect()
            self.log.debug("数据库游标已关闭")
    
    @safe_db_operation(error_message="SQL查询执行失败")
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """执行查询SQL
        
        Args:
            sql: SQL语句
            params: 查询参数，支持命名参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
            
        Raises:
            Exception: 查询执行失败时抛出
        """
        try:
            # 处理LIKE语句中的%通配符
            if 'LIKE' in sql.upper():
                # 先保存参数占位符
                placeholders = []
                for i in range(sql.count('%s')):
                    placeholders.append(f'__PLACEHOLDER_{i}__')
                
                # 替换参数占位符
                for i, placeholder in enumerate(placeholders):
                    sql = sql.replace('%s', placeholder, 1)
                
                # 转义LIKE中的%
                sql = sql.replace('%', '%%')
                
                # 恢复参数占位符
                for placeholder in placeholders:
                    sql = sql.replace(placeholder, '%s')
                
            self.log.debug(f"执行查询SQL: {sql}")
            if params:
                self.log.debug(f"查询参数: {params}")
                
            with self.cursor() as cursor:
                if params:
                    # 将命名参数转换为位置参数
                    if isinstance(params, dict):
                        # 将 %(name)s 格式的占位符替换为 %s
                        for key in params:
                            sql = sql.replace(f'%({key})s', '%s')
                        # 按顺序提取参数值
                        param_values = [params[key] for key in params]
                        cursor.execute(sql, param_values)
                    else:
                        cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                result = cursor.fetchall()
                self.log.debug(f"查询结果: {result}")
                return result
                    
        except Exception as e:
            self.log.error(f"执行查询失败: {str(e)}")
            self.log.error(f"SQL: {sql}")
            if params:
                self.log.error(f"参数: {params}")
            raise
    
    @safe_db_operation(error_message="SQL更新执行失败")
    def execute_update(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """执行更新语句
        
        Args:
            sql: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
            
        Raises:
            DatabaseException: 数据库操作异常
        """
        with allure.step(f"执行SQL更新: {sql}"):
            with self.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or {})
                self.log.info(
                    f"\n{'='*50}\n"
                    f"执行SQL更新:\n{sql}\n"
                    f"参数: {params}\n"
                    f"影响行数: {affected_rows}\n"
                    f"{'='*50}"
                )
                return affected_rows
    
    @safe_db_operation(error_message="数据插入失败")
    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> int:
        """插入数据
        
        Args:
            table: 表名
            data: 要插入的数据
            
        Returns:
            int: 插入的ID
            
        Raises:
            DatabaseException: 数据库操作异常
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())
        
        with allure.step(f"插入数据到表 {table}"):
            with self.cursor() as cursor:
                cursor.execute(sql, values)
                inserted_id = cursor.lastrowid
                self.log.info(
                    f"\n{'='*50}\n"
                    f"插入数据:\n"
                    f"表名: {table}\n"
                    f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}\n"
                    f"插入ID: {inserted_id}\n"
                    f"{'='*50}"
                )
                return inserted_id
    
    @safe_db_operation(error_message="数据删除失败")
    def delete(
        self,
        table: str,
        where: str,
        params: Optional[Dict[str, Any]] = None
    ) -> int:
        """删除数据
        
        Args:
            table: 表名
            where: WHERE条件
            params: 条件参数
            
        Returns:
            int: 删除的行数
            
        Raises:
            DatabaseException: 数据库操作异常
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        
        with allure.step(f"从表 {table} 删除数据"):
            affected_rows = self.execute_update(sql, params)
            self.log.info(
                f"\n{'='*50}\n"
                f"删除数据:\n"
                f"表名: {table}\n"
                f"条件: {where}\n"
                f"参数: {params}\n"
                f"影响行数: {affected_rows}\n"
                f"{'='*50}"
            )
            return affected_rows
    
    @safe_db_operation(error_message="测试数据清理失败")
    def cleanup(self, cleanup_data: List[Dict[str, Any]]) -> None:
        """清理测试数据
        
        Args:
            cleanup_data: 清理数据列表，每个元素包含：
                - table: 表名
                - where: WHERE条件
                - params: 条件参数
                
        Raises:
            DatabaseException: 数据库操作异常
        """
        with allure.step("清理测试数据"):
            for data in cleanup_data:
                self.delete(
                    table=data["table"],
                    where=data["where"],
                    params=data.get("params")
                )
            self.log.info(
                f"\n{'='*50}\n"
                f"清理测试数据完成:\n"
                f"{json.dumps(cleanup_data, ensure_ascii=False, indent=2)}\n"
                f"{'='*50}"
            )
    
    @safe_db_operation(error_message="获取表结构失败")
    def get_table_schema(self, table: str) -> List[Dict[str, Any]]:
        """获取表结构
        
        Args:
            table: 表名
            
        Returns:
            List[Dict[str, Any]]: 表结构信息列表
            
        Raises:
            DatabaseException: 数据库操作异常
        """
        sql = """
        SELECT 
            COLUMN_NAME, 
            DATA_TYPE, 
            IS_NULLABLE, 
            COLUMN_KEY, 
            EXTRA
        FROM 
            INFORMATION_SCHEMA.COLUMNS 
        WHERE 
            TABLE_SCHEMA = %(database)s 
            AND TABLE_NAME = %(table)s
        ORDER BY 
            ORDINAL_POSITION
        """
        
        config = YamlUtil().get_db_config()
        results = self.execute_query(sql, {
            "database": config["database"],
            "table": table
        })
        self.log.info(
            f"\n{'='*50}\n"
            f"获取表结构:\n"
            f"表名: {table}\n"
            f"结构:\n{json.dumps(results, ensure_ascii=False, indent=2)}\n"
            f"{'='*50}"
        )
        return results
    
    @safe_db_operation(error_message="检查表是否存在失败")
    def table_exists(self, table: str) -> bool:
        """检查表是否存在
        
        Args:
            table: 表名
            
        Returns:
            bool: 表是否存在
            
        Raises:
            DatabaseException: 数据库操作异常
        """
        sql = """
        SELECT 
            COUNT(*) as count
        FROM 
            INFORMATION_SCHEMA.TABLES 
        WHERE 
            TABLE_SCHEMA = %(database)s 
            AND TABLE_NAME = %(table)s
        """
        
        config = YamlUtil().get_db_config()
        result = self.execute_query(sql, {
            "database": config["database"],
            "table": table
        })[0]
        exists = result["count"] > 0
        self.log.info(
            f"\n{'='*50}\n"
            f"检查表是否存在:\n"
            f"表名: {table}\n"
            f"结果: {exists}\n"
            f"{'='*50}"
        )
        return exists


if __name__ == "__main__":
    # 测试代码
    with DBManager() as db:
        # 查询客户信息
        sql = "SELECT * FROM gen_cust_info_md WHERE cust_name = %s"
        params = {"cust_name": "北京智创科技有限公司"}
        result = db.execute_query(sql, params)
        print(json.dumps(result, ensure_ascii=False, indent=2, cls=DecimalEncoder))