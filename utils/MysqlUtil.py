import os
import sys
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
import allure
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

import pymysql
from loguru import logger
import json
from datetime import datetime
from decimal import Decimal

# 动态获取项目根目录（兼容不同调用方式）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from config.config import Config

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

class DBManager:
    """数据库管理器"""
    
    def __init__(self, is_runtime: bool = False):
        """
        初始化数据库管理器
        
        参数:
            is_runtime: 是否连接运行时数据库
        """
        self.is_runtime = is_runtime
        self.engine: Engine = create_engine(Config.get_connection_url(is_runtime))
        self.Session = sessionmaker(bind=self.engine)
        self.connection = None
        logger.info(f"数据库管理器初始化完成，运行时模式: {is_runtime}")
        
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
        
    def connect(self):
        """建立数据库连接"""
        if not self.connection:
            db_config = Config.get_db_config()
            self.connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                charset='utf8mb4'
            )
            logger.info(f"数据库连接成功: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已关闭")
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        创建数据库会话的上下文管理器
        
        用法:
            with db_manager.session() as session:
                session.execute(...)
        """
        session = self.Session()
        try:
            yield session
            session.commit()
            logger.debug("数据库会话已提交")
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话回滚: {str(e)}")
            raise e
        finally:
            session.close()
            logger.debug("数据库会话已关闭")
    
    def execute_query(self, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行查询语句
        
        参数:
            sql: SQL查询语句
            params: 查询参数
        
        返回:
            查询结果列表
        """
        with allure.step(f"执行SQL查询: {sql}"):
            try:
                self.connect()
                with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    # 如果提供了参数，使用参数化查询
                    if params:
                        cursor.execute(sql, params)
                    else:
                        # 否则直接执行SQL语句
                        cursor.execute(sql)
                    results = cursor.fetchall()
                    logger.info(f"\n{'='*50}\n执行SQL查询:\n{sql}\n参数: {params}\n结果:\n{json.dumps(results, ensure_ascii=False, indent=2, cls=DecimalEncoder)}\n{'='*50}")
                    return results
            except Exception as e:
                logger.error(f"执行SQL查询失败: {str(e)}")
                raise
            finally:
                self.disconnect()
    
    def execute_update(self, sql: str, params: Dict[str, Any] = None) -> int:
        """
        执行更新语句
        
        参数:
            sql: SQL更新语句
            params: 更新参数
        
        返回:
            受影响的行数
        """
        with allure.step(f"执行SQL更新: {sql}"):
            with self.session() as session:
                result = session.execute(text(sql), params or {})
                affected_rows = result.rowcount
                logger.info(f"\n{'='*50}\n执行SQL更新:\n{sql}\n参数: {params}\n影响行数: {affected_rows}\n{'='*50}")
                return affected_rows
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        插入数据
        
        参数:
            table: 表名
            data: 要插入的数据
        
        返回:
            插入的ID
        """
        columns = ", ".join(data.keys())
        values = ", ".join([f":{k}" for k in data.keys()])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        
        with allure.step(f"插入数据到表 {table}"):
            with self.session() as session:
                result = session.execute(text(sql), data)
                inserted_id = result.lastrowid
                logger.info(f"\n{'='*50}\n插入数据:\n表名: {table}\n数据: {json.dumps(data, ensure_ascii=False, indent=2)}\n插入ID: {inserted_id}\n{'='*50}")
                return inserted_id
    
    def delete(self, table: str, where: str, params: Dict[str, Any] = None) -> int:
        """
        删除数据
        
        参数:
            table: 表名
            where: WHERE条件
            params: 条件参数
        
        返回:
            删除的行数
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        
        with allure.step(f"从表 {table} 删除数据"):
            affected_rows = self.execute_update(sql, params)
            logger.info(f"\n{'='*50}\n删除数据:\n表名: {table}\n条件: {where}\n参数: {params}\n影响行数: {affected_rows}\n{'='*50}")
            return affected_rows
    
    def cleanup(self, cleanup_data: List[Dict[str, Any]]):
        """
        清理测试数据
        
        参数:
            cleanup_data: 清理数据列表，每个元素包含：
                - table: 表名
                - where: WHERE条件
                - params: 条件参数
        """
        with allure.step("清理测试数据"):
            for data in cleanup_data:
                self.delete(
                    table=data["table"],
                    where=data["where"],
                    params=data.get("params")
                )
            logger.info(f"\n{'='*50}\n清理测试数据完成:\n{json.dumps(cleanup_data, ensure_ascii=False, indent=2)}\n{'='*50}")
    
    def get_table_schema(self, table: str) -> List[Dict[str, Any]]:
        """
        获取表结构
        
        参数:
            table: 表名
        
        返回:
            表结构信息列表
        """
        sql = f"""
        SELECT 
            COLUMN_NAME, 
            DATA_TYPE, 
            IS_NULLABLE, 
            COLUMN_KEY, 
            EXTRA
        FROM 
            INFORMATION_SCHEMA.COLUMNS 
        WHERE 
            TABLE_SCHEMA = :database 
            AND TABLE_NAME = :table
        ORDER BY 
            ORDINAL_POSITION
        """
        
        config = Config.get_db_config(self.is_runtime)
        results = self.execute_query(sql, {
            "database": config["database"],
            "table": table
        })
        logger.info(f"\n{'='*50}\n获取表结构:\n表名: {table}\n结构:\n{json.dumps(results, ensure_ascii=False, indent=2)}\n{'='*50}")
        return results
    
    def table_exists(self, table: str) -> bool:
        """
        检查表是否存在
        
        参数:
            table: 表名
        
        返回:
            表是否存在
        """
        sql = """
        SELECT 
            COUNT(*) as count
        FROM 
            INFORMATION_SCHEMA.TABLES 
        WHERE 
            TABLE_SCHEMA = :database 
            AND TABLE_NAME = :table
        """
        
        config = Config.get_db_config(self.is_runtime)
        result = self.execute_query(sql, {
            "database": config["database"],
            "table": table
        })
        
        exists = result[0]["count"] > 0
        logger.info(f"\n{'='*50}\n检查表是否存在:\n表名: {table}\n结果: {exists}\n{'='*50}")
        return exists

    def execute(self, sql: str, params: tuple = None) -> int:
        """
        执行SQL语句
        
        参数:
            sql: SQL语句
            params: SQL参数
            
        返回:
            影响的行数
        """
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(sql, params)
                self.connection.commit()
                logger.info(f"\n{'='*50}\n执行SQL:\n{sql}\n参数: {params}\n影响行数: {affected_rows}\n{'='*50}")
                return affected_rows
        finally:
            self.disconnect()
    
    def _format_result(self, result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        格式化查询结果
        
        参数:
            result: 查询结果
            
        返回:
            格式化后的结果
        """
        if not result:
            return None
            
        formatted = {}
        for key, value in result.items():
            if isinstance(value, datetime):
                formatted[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted[key] = value
        return formatted
    
    def query_one(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        
        参数:
            sql: SQL查询语句
            params: 查询参数
            
        返回:
            查询结果
        """
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchone()
                if result:
                    result = dict(zip([col[0] for col in cursor.description], result))
                    result = self._format_result(result)
                    logger.info(f"\n{'='*50}\n查询单条记录:\nSQL: {sql}\n参数: {params}\n结果:\n{json.dumps(result, ensure_ascii=False, indent=2)}\n{'='*50}")
                return result
        finally:
            self.disconnect()
    
    def query_all(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        执行查询并返回多条记录
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict]: 查询结果列表
        """
        try:
            self.connect()
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # 如果提供了参数，使用参数化查询
                if params:
                    cursor.execute(sql, params)
                else:
                    # 否则直接执行SQL语句，不使用格式化
                    cursor.execute(sql)
                results = cursor.fetchall()
                logger.info(f"\n{'='*50}\n查询多条记录:\nSQL: {sql}\n参数: {params}\n结果:\n{json.dumps(results, ensure_ascii=False, indent=2, cls=DecimalEncoder)}\n{'='*50}")
                return results
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise
        finally:
            self.disconnect()
    
    def update(self, table: str, data: Dict[str, Any], 
               where: str, params: tuple = None) -> int:
        """
        更新数据
        
        参数:
            table: 表名
            data: 要更新的数据
            where: WHERE条件
            params: 条件参数
            
        返回:
            影响的行数
        """
        set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                # 合并数据值和条件参数
                all_params = tuple(data.values()) + (params or ())
                affected_rows = cursor.execute(sql, all_params)
                self.connection.commit()
                logger.info(f"\n{'='*50}\n更新数据:\n表名: {table}\n数据: {json.dumps(data, ensure_ascii=False, indent=2)}\n条件: {where}\n参数: {params}\n影响行数: {affected_rows}\n{'='*50}")
                return affected_rows
        finally:
            self.disconnect()
    
    def execute_sql(self, sql: str) -> None:
        """
        执行SQL语句
        
        参数:
            sql: SQL语句
        """
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                self.connection.commit()
                logger.info(f"\n{'='*50}\n执行SQL:\n{sql}\n{'='*50}")
        finally:
            self.disconnect()
    
    def execute_sql_file(self, file_path: str) -> None:
        """
        执行SQL文件
        
        参数:
            file_path: SQL文件路径
        """
        try:
            self.connect()
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                logger.info(f"\n{'='*50}\n执行SQL文件:\n{file_path}\n内容:\n{sql_content}\n{'='*50}")
                
                with self.connection.cursor() as cursor:
                    for statement in sql_content.split(';'):
                        statement = statement.strip()
                        if statement and not statement.startswith('--'):
                            cursor.execute(statement)
                    self.connection.commit()
                    logger.info("SQL文件执行完成")
        finally:
            self.disconnect()

if __name__ == "__main__":
    from loguru import logger
    
    db = DBManager()
    # 查询客户信息
    sql = "SELECT * FROM gen_cust_info_md WHERE cust_name = %s"
    params = ("北京智创科技有限公司",)
    result = db.query_one(sql, params)