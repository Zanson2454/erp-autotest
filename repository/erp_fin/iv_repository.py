"""ERP_FIN 存货核算域仓储。"""

from __future__ import annotations

from typing import Optional

from utils.mysql_util import DBManager


class FinIvRepository:
    """存货核算相关查询仓储。"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_enabled_inv_mvn_type(self) -> Optional[dict]:
        sql = (
            "SELECT code, name "
            "FROM inv_mvn_type_cf "
            "WHERE deleted = 0 AND enable_status = %s "
            "LIMIT 1"
        )
        rows = self.db.query(sql, ["ENABLE"])
        return rows[0] if rows else None

    def get_latest_execute_record_id(self, com_org_id: int) -> Optional[int]:
        sql = (
            "SELECT id "
            "FROM fin_iv_execute_record_tr "
            "WHERE deleted = 0 AND com_org_id = %s "
            "ORDER BY created_at DESC "
            "LIMIT 1"
        )
        rows = self.db.query(sql, [com_org_id])
        if not rows:
            return None
        return rows[0].get("id")

