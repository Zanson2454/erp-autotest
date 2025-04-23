import os
import sys
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
import allure
import pymysql
from loguru import logger
import json
from datetime import datetime
from decimal import Decimal

# 动态获取项目根目录（兼容不同调用方式）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from common.config_manager import ConfigManager

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
            db_config = ConfigManager().get_db_config()
            self.connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['name'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"数据库连接成功: {db_config['host']}:{db_config['port']}/{db_config['name']}")
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("数据库连接已关闭")
    
    @contextmanager
    def cursor(self):
        """
        创建数据库游标的上下文管理器
        
        用法:
            with db_manager.cursor() as cursor:
                cursor.execute(...)
        """
        self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
            logger.debug("数据库事务已提交")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"数据库事务回滚: {str(e)}")
            raise e
        finally:
            cursor.close()
            self.disconnect()
            logger.debug("数据库游标已关闭")
    
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
            with self.cursor() as cursor:
                cursor.execute(sql, params or {})
                results = cursor.fetchall()
                logger.info(f"\n{'='*50}\n执行SQL查询:\n{sql}\n参数: {params}\n结果:\n{json.dumps(results, ensure_ascii=False, indent=2, cls=DecimalEncoder)}\n{'='*50}")
                return results
    
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
            with self.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or {})
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
        placeholders = ", ".join(["%s" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())
        
        with allure.step(f"插入数据到表 {table}"):
            with self.cursor() as cursor:
                cursor.execute(sql, values)
                inserted_id = cursor.lastrowid
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
            TABLE_SCHEMA = %(database)s 
            AND TABLE_NAME = %(table)s
        """
        
        config = Config.get_db_config(self.is_runtime)
        result = self.execute_query(sql, {
            "database": config["database"],
            "table": table
        })[0]
        exists = result["count"] > 0
        logger.info(f"\n{'='*50}\n检查表是否存在:\n表名: {table}\n结果: {exists}\n{'='*50}")
        return exists

if __name__ == "__main__":
    from loguru import logger
    
    db = DBManager()
    # 查询客户信息
    sql = "SELECT * FROM gen_cust_info_md WHERE cust_name = %s"
    params = ("北京智创科技有限公司",)
    result = db.execute_query(sql, params)