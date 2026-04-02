"""ERP_FIN 结算域仓储。"""

from __future__ import annotations

from typing import Any, Optional

from utils.mysql_util import DBManager


class SettlementRepository:
    """结算相关查询仓储。"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_sett_item_status_row(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, sett_item_status, async_execution_status, sett_doc_id "
            "FROM sett_item_tr WHERE deleted = 0 AND id = %s LIMIT 1"
        )
        rows = self.db.query(sql, [sett_item_id])
        return rows[0] if rows else None

    def get_sett_doc_status_row(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, sett_doc_status, trading_doc_id "
            "FROM sett_doc_tr WHERE deleted = 0 AND id = %s LIMIT 1"
        )
        rows = self.db.query(sql, [sett_doc_id])
        return rows[0] if rows else None

