"""ERP_FIN 初始化配置仓储。"""

from __future__ import annotations

from typing import Any, Optional

from utils.mysql_util import DBManager


class FinApInitConfigRepository:
    """应付初始化配置查询仓储。"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_existing_config(self, gr_com_org_id: Any, module_code: str) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, com_org, module_code, initialization_type, start_type "
            "FROM fin_gen_im_head_tr "
            "WHERE com_org = %s AND module_code = %s "
            "LIMIT 1"
        )
        rows = self.db.query(sql, [gr_com_org_id, module_code])
        return rows[0] if rows else None


class FinIvInitConfigRepository:
    """存货核算初始化配置查询仓储。"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_existing_config(self, com_org_id: Any, iv_type: str) -> Optional[dict[str, Any]]:
        sql = (
            "SELECT id, com_org_id, iv_type, init_status, async_execution_status, "
            "enable_status, begin_status "
            "FROM fin_iv_init_cf "
            "WHERE com_org_id = %s AND iv_type = %s "
            "LIMIT 1"
        )
        rows = self.db.query(sql, [com_org_id, iv_type])
        return rows[0] if rows else None

