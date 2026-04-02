"""ERP_FIN 销售发票域仓储。"""

from __future__ import annotations

from typing import Any, Optional

from utils.mysql_util import DBManager


class FinSbRepository:
    """销售发票相关查询仓储。"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_ar_item_ids_by_head_id(self, ar_head_id: Any) -> list[Any]:
        sql = "SELECT id FROM fin_arm_ar_item_tr WHERE arm_ar_head_tr_id = %s AND deleted = 0"
        rows = self.db.query(sql, [ar_head_id])
        return [row.get("id") for row in rows if row.get("id") is not None]

    def get_ar_head_async_status_row(self, ar_head_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, ar_head_code, async_execution_status, async_execution_failure_reason, "
            "billed_doc_amt, billing_doc_amt, unbilled_doc_amt "
            "FROM fin_arm_ar_head_tr WHERE id = %s LIMIT 1"
        )
        rows = self.db.query(sql, [ar_head_id])
        return rows[0] if rows else None

    def get_sb_item_by_rel_doc_head_id(self, rel_doc_head_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT sb_head_code, tm_sb_head_tr_id FROM fin_tm_sb_item_tr "
            "WHERE rel_doc_head_id = %s AND deleted = 0 LIMIT 1"
        )
        rows = self.db.query(sql, [rel_doc_head_id])
        return rows[0] if rows else None

    def get_sb_head_by_id(self, sb_head_id: Any) -> Optional[dict[str, Any]]:
        sql = "SELECT * FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, [sb_head_id])
        return rows[0] if rows else None

    def get_sb_items_by_head_id(self, sb_head_id: Any) -> list[dict[str, Any]]:
        sql = "SELECT * FROM fin_tm_sb_item_tr WHERE tm_sb_head_tr_id = %s"
        return self.db.query(sql, [sb_head_id])

    def get_ar_head_by_id(self, ar_head_id: Any) -> Optional[dict[str, Any]]:
        sql = "SELECT * FROM fin_arm_ar_head_tr WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, [ar_head_id])
        return rows[0] if rows else None

    def get_ar_items_by_head_id(self, ar_head_id: Any) -> list[dict[str, Any]]:
        sql = "SELECT * FROM fin_arm_ar_item_tr WHERE arm_ar_head_tr_id = %s"
        return self.db.query(sql, [ar_head_id])

    def get_ibc_items_by_rel_doc_heads(self, rel_doc_head_ids: list[Any]) -> list[dict[str, Any]]:
        if not rel_doc_head_ids:
            return []
        placeholders = ",".join(["%s"] * len(rel_doc_head_ids))
        sql = (
            "SELECT * FROM fin_brm_ibc_item_tr "
            "LEFT JOIN fin_brm_ibc_head_tr ON brm_ibc_head_tr_id = fin_brm_ibc_head_tr.id "
            f"WHERE rel_doc_head_id IN ({placeholders})"
        )
        return self.db.query(sql, rel_doc_head_ids)

    def get_latest_cleared_sb_head(self) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, sb_head_code, cleared_doc_amt FROM fin_tm_sb_head_tr "
            "WHERE deleted = 0 AND clearing_status = %s "
            "ORDER BY created_at DESC LIMIT 1"
        )
        rows = self.db.query(sql, ["CLEARED"])
        return rows[0] if rows else None

    def get_ar_head_ids_by_sb_head_id(self, sb_head_id: Any) -> list[Any]:
        sql = (
            "SELECT rel_doc_head_id AS ar_head_id FROM fin_tm_sb_item_tr "
            "WHERE tm_sb_head_tr_id = %s AND deleted = 0 AND rel_doc_head_id IS NOT NULL "
            "ORDER BY created_at DESC"
        )
        rows = self.db.query(sql, [sb_head_id])
        return [row.get("ar_head_id") for row in rows if row.get("ar_head_id")]

    def get_ar_head_amount_row(self, ar_head_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, billing_doc_amt, unbilled_doc_amt, billed_doc_amt "
            "FROM fin_arm_ar_head_tr WHERE id = %s AND deleted = 0 LIMIT 1"
        )
        rows = self.db.query(sql, [ar_head_id])
        return rows[0] if rows else None

    def get_ar_item_amount_rows(self, ar_head_id: Any) -> list[dict[str, Any]]:
        sql = (
            "SELECT id, clearing_doc_amt, uncleared_doc_amt, cleared_doc_amt "
            "FROM fin_arm_ar_item_tr WHERE arm_ar_head_tr_id = %s AND deleted = 0 ORDER BY id"
        )
        return self.db.query(sql, [ar_head_id])

    def get_clearing_head_ids_by_rel_doc_head_id(self, rel_doc_head_id: Any) -> list[Any]:
        sql = (
            "SELECT DISTINCT brm_ibc_head_tr_id AS clearing_head_id FROM fin_brm_ibc_item_tr "
            "WHERE rel_doc_head_id = %s AND deleted = 0"
        )
        rows = self.db.query(sql, [rel_doc_head_id])
        return [row.get("clearing_head_id") for row in rows if row.get("clearing_head_id")]

    def get_clearing_items_by_head_ids(self, clearing_head_ids: list[Any]) -> list[dict[str, Any]]:
        if not clearing_head_ids:
            return []
        placeholders = ",".join(["%s"] * len(clearing_head_ids))
        sql = (
            "SELECT id, brm_ibc_head_tr_id, rel_doc_head_id FROM fin_brm_ibc_item_tr "
            f"WHERE brm_ibc_head_tr_id IN ({placeholders}) AND deleted = 0"
        )
        return self.db.query(sql, clearing_head_ids)

    def get_clearing_heads_deleted_rows(self, clearing_head_ids: list[Any]) -> list[dict[str, Any]]:
        if not clearing_head_ids:
            return []
        placeholders = ",".join(["%s"] * len(clearing_head_ids))
        sql = f"SELECT id, deleted FROM fin_brm_ibc_head_tr WHERE id IN ({placeholders})"
        return self.db.query(sql, clearing_head_ids)

    def get_clearing_items_deleted_rows(self, clearing_item_ids: list[Any]) -> list[dict[str, Any]]:
        if not clearing_item_ids:
            return []
        placeholders = ",".join(["%s"] * len(clearing_item_ids))
        sql = f"SELECT id, deleted FROM fin_brm_ibc_item_tr WHERE id IN ({placeholders})"
        return self.db.query(sql, clearing_item_ids)

    def get_latest_sb_head_by_statuses(self, statuses: list[str]) -> Optional[dict[str, Any]]:
        if not statuses:
            return None
        placeholders = ",".join(["%s"] * len(statuses))
        sql = (
            "SELECT id, sb_head_code, sb_status FROM fin_tm_sb_head_tr "
            f"WHERE deleted = 0 AND sb_status IN ({placeholders}) AND sb_head_code IS NOT NULL "
            "ORDER BY CASE WHEN sb_status = 'DRAFT' THEN 0 ELSE 1 END, "
            "CASE WHEN sb_head_code LIKE 'SB%' THEN 0 ELSE 1 END, created_at DESC LIMIT 1"
        )
        rows = self.db.query(sql, statuses)
        return rows[0] if rows else None

    def get_latest_sb_head_by_status(self, status: str) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, sb_head_code, sb_status FROM fin_tm_sb_head_tr "
            "WHERE deleted = 0 AND sb_status = %s AND sb_head_code IS NOT NULL "
            "ORDER BY CASE WHEN sb_head_code LIKE 'SB%' THEN 0 ELSE 1 END, created_at DESC LIMIT 1"
        )
        rows = self.db.query(sql, [status])
        return rows[0] if rows else None

    def get_sb_deleted_status_row(self, sb_head_id: Any) -> Optional[dict[str, Any]]:
        sql = "SELECT deleted, sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, [sb_head_id])
        return rows[0] if rows else None

    def get_sb_deleted_flag(self, sb_head_id: Any) -> Optional[Any]:
        sql = "SELECT deleted FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, [sb_head_id])
        return rows[0].get("deleted") if rows else None

    def get_active_sb_item_count(self, sb_head_id: Any) -> int:
        sql = (
            "SELECT COUNT(*) AS item_count FROM fin_tm_sb_item_tr "
            "WHERE tm_sb_head_tr_id = %s AND deleted = 0"
        )
        rows = self.db.query(sql, [sb_head_id])
        return int(rows[0].get("item_count") or 0) if rows else 0

    def get_sb_item_amount_rows(self, sb_head_id: Any) -> list[dict[str, Any]]:
        sql = (
            "SELECT id, cleared_doc_amt, clearing_doc_amt, uncleared_doc_amt "
            "FROM fin_tm_sb_item_tr WHERE tm_sb_head_tr_id = %s AND deleted = 0 ORDER BY id"
        )
        return self.db.query(sql, [sb_head_id])

    def get_sb_reversal_verify_row(self, sb_head_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, sb_status, pst_date, billed_doc_amt, billing_doc_amt, uncleared_doc_amt, "
            "cleared_doc_amt, clearing_doc_amt, uncleared_doc_amt "
            "FROM fin_tm_sb_head_tr WHERE id = %s AND deleted = 0 LIMIT 1"
        )
        rows = self.db.query(sql, [sb_head_id])
        return rows[0] if rows else None
