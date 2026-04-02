"""ERP_FIN 结算域仓储。"""

from __future__ import annotations

from typing import Any, Optional

from utils.mysql_util import DBManager


class FinSettRepository:
    """结算模块查询仓储。"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_latest_sett_type_id(self) -> Optional[Any]:
        sql = "SELECT id FROM fin_sett_type_cf WHERE deleted = 0 ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql)
        return rows[0].get("id") if rows else None

    def get_spg_id_by_code(self, spg_code: str) -> Optional[Any]:
        sql = "SELECT id FROM fin_sett_spg_type_cf WHERE spg_code = %s ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql, [spg_code])
        return rows[0].get("id") if rows else None

    def get_latest_sett_doc_type_id_like(self, code_like: str) -> Optional[Any]:
        sql = (
            "SELECT id FROM fin_sett_doc_type_cf "
            "WHERE sett_doc_type_code LIKE %s "
            "ORDER BY created_at DESC LIMIT 1"
        )
        rows = self.db.query(sql, [code_like])
        return rows[0].get("id") if rows else None

    def get_latest_curr_formula_type_id(self) -> Optional[Any]:
        sql = "SELECT id FROM gen_curr_formula_type_cf WHERE deleted = 0 ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql)
        return rows[0].get("id") if rows else None

    def get_latest_sett_sds_head_id(self) -> Optional[Any]:
        sql = "SELECT id FROM sett_sds_head_cf WHERE deleted = 0 ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql)
        return rows[0].get("id") if rows else None

    def get_latest_sdc_head_id(self) -> Optional[Any]:
        sql = "SELECT id FROM sett_sdc_head_cf WHERE deleted = 0 ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql)
        return rows[0].get("id") if rows else None

    def get_latest_sdc_head_id_by_sett_head_type(self, sett_head_type: Any) -> Optional[Any]:
        sql = (
            "SELECT id FROM sett_sdc_head_cf "
            "WHERE deleted = 0 AND sett_head_type = %s "
            "ORDER BY created_at DESC LIMIT 1"
        )
        rows = self.db.query(sql, [sett_head_type])
        return rows[0].get("id") if rows else None

    def get_latest_sett_item_id(self) -> Optional[Any]:
        sql = "SELECT id FROM sett_item_tr WHERE deleted = 0 ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql)
        return rows[0].get("id") if rows else None

    def get_latest_sett_item_id_by_status(self, status: str) -> Optional[Any]:
        sql = (
            "SELECT id FROM sett_item_tr "
            "WHERE deleted = 0 AND sett_item_status = %s "
            "ORDER BY created_at DESC LIMIT 1"
        )
        rows = self.db.query(sql, [status])
        return rows[0].get("id") if rows else None

    def get_sett_item_by_id(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        sql = "SELECT * FROM sett_item_tr WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, [sett_item_id])
        return rows[0] if rows else None

    def get_sett_item_status_row(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, sett_item_status, async_execution_status, sett_doc_id "
            "FROM sett_item_tr WHERE deleted = 0 AND id = %s LIMIT 1"
        )
        rows = self.db.query(sql, [sett_item_id])
        return rows[0] if rows else None

    def get_sett_items_by_sett_doc_id(self, sett_doc_id: Any) -> list[dict[str, Any]]:
        sql = "SELECT * FROM sett_item_tr WHERE sett_doc_id = %s"
        return self.db.query(sql, [sett_doc_id])

    def get_sett_item_codes_by_statuses(self, statuses: list[str], limit: int) -> list[dict[str, Any]]:
        placeholders = ",".join(["%s"] * len(statuses))
        sql = (
            "SELECT id, sett_item_code, sett_item_status "
            f"FROM sett_item_tr WHERE deleted = 0 AND sett_item_status IN ({placeholders}) "
            "ORDER BY created_at DESC LIMIT %s"
        )
        return self.db.query(sql, [*statuses, limit])

    def get_sett_doc_by_id(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        sql = "SELECT * FROM sett_doc_tr WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, [sett_doc_id])
        return rows[0] if rows else None

    def get_sett_doc_confirm_status(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT sett_doc_status, async_execution_status, trading_doc_id, "
            "trading_doc_status, trading_doc_code, client_side_confirm_status "
            "FROM sett_doc_tr WHERE deleted = 0 AND id = %s"
        )
        rows = self.db.query(sql, [sett_doc_id])
        return rows[0] if rows else None

    def get_sett_doc_deleted_flag(self, sett_doc_id: Any) -> Optional[Any]:
        sql = "SELECT deleted FROM sett_doc_tr WHERE id = %s"
        rows = self.db.query(sql, [sett_doc_id])
        return rows[0].get("deleted") if rows else None

    def get_sett_doc_type_by_doc_id(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT bt_class, sett_class FROM fin_sett_doc_type_cf "
            "WHERE deleted = 0 AND id = (SELECT sett_doc_type_id FROM sett_doc_tr WHERE id = %s)"
        )
        rows = self.db.query(sql, [sett_doc_id])
        return rows[0] if rows else None

    def get_sett_item_types(self, bt_class: str, sett_class: str) -> list[dict[str, Any]]:
        sql = (
            "SELECT * FROM fin_sett_item_type_cf "
            "WHERE deleted = 0 AND bt_class = %s AND sett_class = %s"
        )
        return self.db.query(sql, [bt_class, sett_class])

    def get_first_autotest_mat(self) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT * FROM gen_mat_md WHERE deleted = 0 "
            "AND mat_code LIKE %s LIMIT 1"
        )
        rows = self.db.query(sql, ["%AUTOTEST%"])
        return rows[0] if rows else None

    def get_tax_codes_by_taxcate(self, taxcate: str) -> list[dict[str, Any]]:
        sql = "SELECT id, tax_code, tax FROM gen_tax_type_cf WHERE deleted = 0 AND taxcate = %s"
        return self.db.query(sql, [taxcate])

    def get_inv_org_id_autotest(self) -> Optional[Any]:
        sql = (
            "SELECT id FROM org_struct_md WHERE deleted = 0 "
            "AND org_code LIKE %s LIMIT 1"
        )
        rows = self.db.query(sql, ["AUTOTEST_INV_ORG"])
        return rows[0].get("id") if rows else None

    def get_sett_doc_amt(self, sett_doc_id: Any) -> Optional[Any]:
        sql = "SELECT sett_doc_amt FROM sett_doc_tr WHERE id = %s"
        rows = self.db.query(sql, [sett_doc_id])
        return rows[0].get("sett_doc_amt") if rows else None

    def get_sett_items_by_codes(self, codes: list[str]) -> list[dict[str, Any]]:
        if not codes:
            return []
        placeholders = ",".join(["%s"] * len(codes))
        sql = f"SELECT * FROM sett_item_tr WHERE deleted = 0 AND sett_item_code IN ({placeholders})"
        return self.db.query(sql, codes)

    def get_sett_doc_status_by_sett_item_id(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT sett_doc_status, sett_doc_code, trading_doc_id "
            "FROM sett_doc_tr WHERE id IN (SELECT sett_doc_id FROM sett_item_tr WHERE id = %s)"
        )
        rows = self.db.query(sql, [sett_item_id])
        return rows[0] if rows else None

    def get_ar_head_by_id(self, trading_doc_id: Any) -> Optional[dict[str, Any]]:
        sql = "SELECT ar_head_code, ar_status FROM fin_arm_ar_head_tr WHERE id = %s AND deleted = 0"
        rows = self.db.query(sql, [trading_doc_id])
        return rows[0] if rows else None

    def get_latest_aggregate_record(self) -> Optional[dict[str, Any]]:
        sql = "SELECT id, task_code FROM sett_aggregate_record_tr WHERE deleted = 0 ORDER BY created_at DESC LIMIT 1"
        rows = self.db.query(sql)
        return rows[0] if rows else None

    def get_latest_aggregate_records(self, limit: int) -> list[dict[str, Any]]:
        sql = (
            "SELECT id, task_code, task_status, doc_type, oper_type "
            "FROM sett_aggregate_record_tr WHERE deleted = 0 "
            "ORDER BY created_at DESC LIMIT %s"
        )
        return self.db.query(sql, [limit])

