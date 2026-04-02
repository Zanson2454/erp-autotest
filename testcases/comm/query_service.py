"""统一查询服务层。

目标：
1. 将测试用例中的 SQL 查询集中管理，避免散落在测试方法里。
2. 强制参数化查询，降低 SQL 注入与维护风险。
"""

from __future__ import annotations

from typing import Any, Optional

from repository.erp_fin import (
    FinApInitConfigRepository,
    FinIvInitConfigRepository,
    FinIvRepository,
    FinSbRepository,
    FinSettRepository,
    SettlementRepository,
)
from utils.mysql_util import DBManager


class QueryService:
    """测试查询服务。

    目前先覆盖 gen_md 已使用的查询场景，后续按模块逐步扩展。
    """

    def __init__(self, db: DBManager):
        self.db = db
        self.fin_ap_init_repo = FinApInitConfigRepository(db)
        self.fin_iv_init_repo = FinIvInitConfigRepository(db)
        self.fin_iv_repo = FinIvRepository(db)
        self.fin_sb_repo = FinSbRepository(db)
        self.fin_sett_repo = FinSettRepository(db)
        self.settlement_repo = SettlementRepository(db)

    def query(self, sql: str, params: Optional[list[Any]] = None) -> list[dict[str, Any]]:
        """通用查询入口。"""
        return self.db.query(sql, params)

    def query_one(self, sql: str, params: Optional[list[Any]] = None) -> Optional[dict[str, Any]]:
        """查询单行记录。"""
        rows = self.db.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: Optional[list[Any]] = None) -> int:
        """通用执行入口（INSERT/UPDATE/DELETE）。"""
        return self.db.execute(sql, params)

    def get_sett_item_status_row(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        return self.settlement_repo.get_sett_item_status_row(sett_item_id)

    def get_sett_doc_status_row(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        return self.settlement_repo.get_sett_doc_status_row(sett_doc_id)

    def get_ap_existing_init_config(self, gr_com_org_id: Any, module_code: str) -> Optional[dict[str, Any]]:
        return self.fin_ap_init_repo.get_existing_config(gr_com_org_id, module_code)

    def get_iv_existing_init_config(self, com_org_id: Any, iv_type: str) -> Optional[dict[str, Any]]:
        return self.fin_iv_init_repo.get_existing_config(com_org_id, iv_type)

    def get_enabled_inv_mvn_type(self) -> Optional[dict[str, Any]]:
        return self.fin_iv_repo.get_enabled_inv_mvn_type()

    def get_latest_iv_execute_record_id(self, com_org_id: int) -> Optional[int]:
        return self.fin_iv_repo.get_latest_execute_record_id(com_org_id)

    def get_latest_sett_type_id(self) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sett_type_id()

    def get_spg_id_by_code(self, spg_code: str) -> Optional[Any]:
        return self.fin_sett_repo.get_spg_id_by_code(spg_code)

    def get_latest_sett_doc_type_id_like(self, code_like: str) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sett_doc_type_id_like(code_like)

    def get_latest_curr_formula_type_id(self) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_curr_formula_type_id()

    def get_latest_sett_sds_head_id(self) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sett_sds_head_id()

    def get_latest_sdc_head_id(self) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sdc_head_id()

    def get_latest_sdc_head_id_by_sett_head_type(self, sett_head_type: Any) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sdc_head_id_by_sett_head_type(sett_head_type)

    def get_latest_sett_item_id(self) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sett_item_id()

    def get_latest_sett_item_id_by_status(self, status: str) -> Optional[Any]:
        return self.fin_sett_repo.get_latest_sett_item_id_by_status(status)

    def get_sett_item_by_id(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_item_by_id(sett_item_id)

    def get_sett_items_by_sett_doc_id(self, sett_doc_id: Any) -> list[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_items_by_sett_doc_id(sett_doc_id)

    def get_sett_item_codes_by_statuses(self, statuses: list[str], limit: int) -> list[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_item_codes_by_statuses(statuses, limit)

    def get_sett_doc_by_id(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_doc_by_id(sett_doc_id)

    def get_sett_doc_confirm_status(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_doc_confirm_status(sett_doc_id)

    def get_sett_doc_deleted_flag(self, sett_doc_id: Any) -> Optional[Any]:
        return self.fin_sett_repo.get_sett_doc_deleted_flag(sett_doc_id)

    def get_sett_doc_type_by_doc_id(self, sett_doc_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_doc_type_by_doc_id(sett_doc_id)

    def get_sett_item_types(self, bt_class: str, sett_class: str) -> list[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_item_types(bt_class, sett_class)

    def get_first_autotest_mat(self) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_first_autotest_mat()

    def get_tax_codes_by_taxcate(self, taxcate: str) -> list[dict[str, Any]]:
        return self.fin_sett_repo.get_tax_codes_by_taxcate(taxcate)

    def get_inv_org_id_autotest(self) -> Optional[Any]:
        return self.fin_sett_repo.get_inv_org_id_autotest()

    def get_sett_doc_amt(self, sett_doc_id: Any) -> Optional[Any]:
        return self.fin_sett_repo.get_sett_doc_amt(sett_doc_id)

    def get_sett_items_by_codes(self, codes: list[str]) -> list[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_items_by_codes(codes)

    def get_sett_doc_status_by_sett_item_id(self, sett_item_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_sett_doc_status_by_sett_item_id(sett_item_id)

    def get_ar_head_by_id(self, trading_doc_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_ar_head_by_id(trading_doc_id)

    def get_latest_aggregate_record(self) -> Optional[dict[str, Any]]:
        return self.fin_sett_repo.get_latest_aggregate_record()

    def get_latest_aggregate_records(self, limit: int) -> list[dict[str, Any]]:
        return self.fin_sett_repo.get_latest_aggregate_records(limit)

    def get_ar_item_ids_by_head_id(self, ar_head_id: Any) -> list[Any]:
        return self.fin_sb_repo.get_ar_item_ids_by_head_id(ar_head_id)

    def get_ar_head_async_status_row(self, ar_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_ar_head_async_status_row(ar_head_id)

    def get_sb_item_by_rel_doc_head_id(self, rel_doc_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_sb_item_by_rel_doc_head_id(rel_doc_head_id)

    def get_sb_head_by_id(self, sb_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_sb_head_by_id(sb_head_id)

    def get_sb_items_by_head_id(self, sb_head_id: Any) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_sb_items_by_head_id(sb_head_id)

    def get_ar_head_full_by_id(self, ar_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_ar_head_by_id(ar_head_id)

    def get_ar_items_by_head_id(self, ar_head_id: Any) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_ar_items_by_head_id(ar_head_id)

    def get_ibc_items_by_rel_doc_heads(self, rel_doc_head_ids: list[Any]) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_ibc_items_by_rel_doc_heads(rel_doc_head_ids)

    def get_latest_cleared_sb_head(self) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_latest_cleared_sb_head()

    def get_ar_head_ids_by_sb_head_id(self, sb_head_id: Any) -> list[Any]:
        return self.fin_sb_repo.get_ar_head_ids_by_sb_head_id(sb_head_id)

    def get_ar_head_amount_row(self, ar_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_ar_head_amount_row(ar_head_id)

    def get_ar_item_amount_rows(self, ar_head_id: Any) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_ar_item_amount_rows(ar_head_id)

    def get_clearing_head_ids_by_rel_doc_head_id(self, rel_doc_head_id: Any) -> list[Any]:
        return self.fin_sb_repo.get_clearing_head_ids_by_rel_doc_head_id(rel_doc_head_id)

    def get_clearing_items_by_head_ids(self, clearing_head_ids: list[Any]) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_clearing_items_by_head_ids(clearing_head_ids)

    def get_clearing_heads_deleted_rows(self, clearing_head_ids: list[Any]) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_clearing_heads_deleted_rows(clearing_head_ids)

    def get_clearing_items_deleted_rows(self, clearing_item_ids: list[Any]) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_clearing_items_deleted_rows(clearing_item_ids)

    def get_latest_sb_head_by_statuses(self, statuses: list[str]) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_latest_sb_head_by_statuses(statuses)

    def get_latest_sb_head_by_status(self, status: str) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_latest_sb_head_by_status(status)

    def get_sb_deleted_status_row(self, sb_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_sb_deleted_status_row(sb_head_id)

    def get_sb_deleted_flag(self, sb_head_id: Any) -> Optional[Any]:
        return self.fin_sb_repo.get_sb_deleted_flag(sb_head_id)

    def get_active_sb_item_count(self, sb_head_id: Any) -> int:
        return self.fin_sb_repo.get_active_sb_item_count(sb_head_id)

    def get_sb_item_amount_rows(self, sb_head_id: Any) -> list[dict[str, Any]]:
        return self.fin_sb_repo.get_sb_item_amount_rows(sb_head_id)

    def get_sb_reversal_verify_row(self, sb_head_id: Any) -> Optional[dict[str, Any]]:
        return self.fin_sb_repo.get_sb_reversal_verify_row(sb_head_id)

    def get_survey_mission_item_id(self, mission_id: Any) -> Optional[Any]:
        sql = "SELECT id FROM gen_survey_mission_item_md WHERE gen_survey_mission_md_id = %s LIMIT 1"
        rows = self.db.query(sql, (mission_id,))
        if not rows:
            return None
        return rows[0].get("id")

    def get_survey_mission_state(self, mission_id: Any) -> Optional[str]:
        sql = "SELECT state FROM gen_survey_mission_md WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (mission_id,))
        if not rows:
            return None
        return rows[0].get("state")

    def get_survey_detail_id(self, mission_id: Any) -> Optional[Any]:
        sql = "SELECT id FROM gen_survey_detail_md WHERE survey_mission = %s LIMIT 1"
        rows = self.db.query(sql, (mission_id,))
        if not rows:
            return None
        return rows[0].get("id")

    def get_org_relation_by_dimensions(
        self,
        org_head_dimension_id: Any,
        org_head_unit_id: Any,
        org_relation_dimension_id: Any,
        org_relation_unit_id: Any,
    ) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, org_relation_status FROM org_relation_cf "
            "WHERE org_head_dimension_id = %s AND org_head_unit_id = %s "
            "AND org_relation_dimension_id = %s AND org_relation_unit_id = %s "
            "LIMIT 1"
        )
        rows = self.db.query(
            sql,
            (
                org_head_dimension_id,
                org_head_unit_id,
                org_relation_dimension_id,
                org_relation_unit_id,
            ),
        )
        if not rows:
            return None
        return rows[0]

    def get_org_relation_status_by_id(self, relation_id: Any) -> Optional[str]:
        sql = "SELECT org_relation_status FROM org_relation_cf WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (relation_id,))
        if not rows:
            return None
        return rows[0].get("org_relation_status")

    def get_org_switch_model_id_by_model_key(self, model_key: str) -> Optional[Any]:
        sql = "SELECT id FROM org_switch_model_cf WHERE model_key = %s LIMIT 1"
        rows = self.db.query(sql, (model_key,))
        if not rows:
            return None
        return rows[0].get("id")

    def get_latest_org_switch_by_org_id(self, switch_org_id: Any) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, switch_name FROM org_switch_list_cf "
            "WHERE switch_org_id = %s ORDER BY id DESC LIMIT 1"
        )
        rows = self.db.query(sql, (switch_org_id,))
        if not rows:
            return None
        return rows[0]

    def get_org_switch_id_by_name(self, switch_name: str) -> Optional[Any]:
        sql = "SELECT id FROM org_switch_list_cf WHERE switch_name = %s LIMIT 1"
        rows = self.db.query(sql, (switch_name,))
        if not rows:
            return None
        return rows[0].get("id")

    def get_org_business_type_status(self, org_type_id: Any) -> Optional[str]:
        sql = "SELECT status FROM org_business_type_cf WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (org_type_id,))
        if not rows:
            return None
        return rows[0].get("status")

    def get_org_business_type_deleted(self, org_type_id: Any) -> Optional[Any]:
        sql = "SELECT deleted FROM org_business_type_cf WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (org_type_id,))
        if not rows:
            return None
        return rows[0].get("deleted")

    def get_org_dimension_status(self, org_dimension_id: Any) -> Optional[str]:
        sql = "SELECT status FROM org_dimension_cf WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (org_dimension_id,))
        if not rows:
            return None
        return rows[0].get("status")

    def get_org_dimension_deleted(self, org_dimension_id: Any) -> Optional[Any]:
        sql = "SELECT deleted FROM org_dimension_cf WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (org_dimension_id,))
        if not rows:
            return None
        return rows[0].get("deleted")

    def get_first_adm_org_draft_id(self) -> Optional[Any]:
        sql = (
            "SELECT id FROM org_struct_md "
            "WHERE org_status = %s AND org_dimension_code = %s "
            "AND org_code LIKE %s AND deleted = 0 "
            "LIMIT 1"
        )
        rows = self.db.query(sql, ("DRAFT", "ADM_ORG_GRP", "AT_%"))
        if not rows:
            return None
        return rows[0].get("id")

    def get_employee_org_link_id(
        self,
        employee_id: Any,
        identity_id: Any,
        org_unit_id: Any,
    ) -> Optional[Any]:
        sql = (
            "SELECT id FROM org_employee_org_link_cf "
            "WHERE employee_id = %s AND identity_id = %s AND org_unit_id = %s "
            "LIMIT 1"
        )
        rows = self.db.query(sql, (employee_id, identity_id, org_unit_id))
        if not rows:
            return None
        return rows[0].get("id")

    def get_first_org_struct_id(
        self,
        org_dimension_code: str,
        org_code_like: str = "AT_%",
        deleted: int = 0,
        org_status: Optional[str] = None,
    ) -> Optional[Any]:
        if org_status is None:
            sql = (
                "SELECT id FROM org_struct_md "
                "WHERE deleted = %s AND org_dimension_code = %s AND org_code LIKE %s "
                "LIMIT 1"
            )
            params = (deleted, org_dimension_code, org_code_like)
        else:
            sql = (
                "SELECT id FROM org_struct_md "
                "WHERE deleted = %s AND org_dimension_code = %s "
                "AND org_status = %s AND org_code LIKE %s "
                "LIMIT 1"
            )
            params = (deleted, org_dimension_code, org_status, org_code_like)
        rows = self.db.query(sql, params)
        if not rows:
            return None
        return rows[0].get("id")

    def get_org_struct_status(self, org_id: Any) -> Optional[str]:
        sql = "SELECT org_status FROM org_struct_md WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (org_id,))
        if not rows:
            return None
        return rows[0].get("org_status")

    def get_org_struct_deleted(self, org_id: Any) -> Optional[Any]:
        sql = "SELECT deleted FROM org_struct_md WHERE id = %s LIMIT 1"
        rows = self.db.query(sql, (org_id,))
        if not rows:
            return None
        return rows[0].get("deleted")

    def get_inv_org_mat_type_link_id(
        self,
        mat_type_id: Any,
        inv_org_id: Any,
        deleted: Optional[int] = None,
    ) -> Optional[Any]:
        if deleted is None:
            sql = (
                "SELECT id FROM gen_inv_org_mat_type_link_cf "
                "WHERE mat_type_id = %s AND inv_org_id = %s "
                "LIMIT 1"
            )
            params = (mat_type_id, inv_org_id)
        else:
            sql = (
                "SELECT id FROM gen_inv_org_mat_type_link_cf "
                "WHERE mat_type_id = %s AND inv_org_id = %s AND deleted = %s "
                "LIMIT 1"
            )
            params = (mat_type_id, inv_org_id, deleted)
        rows = self.db.query(sql, params)
        if not rows:
            return None
        return rows[0].get("id")
