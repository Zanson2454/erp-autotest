"""清理辅助工具 — 供各模块 conftest 复用。

提供安全删除、表存在性检测、列名探测等能力，
避免每个模块 conftest 重复定义相同的内嵌函数。
"""

from typing import List, Optional, Set

from utils.log_util import Loggers
from utils.mysql_util import DBManager


def safe_delete(db: DBManager, table: str, where: str, params=None) -> None:
    """执行 DELETE，失败仅警告不抛出。"""
    try:
        db.delete(table=table, where=where, params=params)
    except Exception as exc:
        Loggers.warning(f"跳过清理 {table}: where={where}, params={params}, error={exc}")


def table_exists(db: DBManager, table: str) -> bool:
    """检查当前库中表是否存在。"""
    try:
        rows = db.query(
            "SELECT 1 FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s LIMIT 1",
            [table],
        )
        return bool(rows)
    except Exception as exc:
        Loggers.warning(f"读取表信息失败 {table}: {exc}")
        return False


def table_columns(db: DBManager, table: str) -> Set[str]:
    """返回表的列名集合。"""
    try:
        rows = db.query(
            "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
            [table],
        )
        return {row.get("COLUMN_NAME") for row in rows if row.get("COLUMN_NAME")}
    except Exception as exc:
        Loggers.warning(f"读取表结构失败 {table}: {exc}")
        return set()


def pick_cleanup_column(db: DBManager, table: str, candidates: List[str]) -> Optional[str]:
    """从候选列名中选出第一个在表中实际存在的列。"""
    cols = table_columns(db, table)
    for col in candidates:
        if col in cols:
            return col
    return None


def safe_delete_like(
    db: DBManager, table: str, candidates: List[str], pattern: str
) -> None:
    """探测列名后执行 LIKE 删除，表或列不存在时仅记录日志。"""
    if not table_exists(db, table):
        Loggers.info(f"跳过清理 {table}: 表不存在")
        return
    col = pick_cleanup_column(db, table, candidates)
    if not col:
        Loggers.info(f"跳过清理 {table}: 未找到候选列 {candidates}")
        return
    safe_delete(db, table=table, where=f"{col} like %s", params=[pattern])
