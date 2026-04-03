"""ERP_PRD 模块清理注册。"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_erp_prd() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_PRD 数据清理")
            return

        db = DBManager(**db_config)

        # --- Master: 工作中心 ---
        db.delete(
            table="prd_work_centor_activity_item_md",
            where="prd_work_centor_header_id in (select id from prd_work_centor_header_md where wc_code like %s)",
            params=["AUTO_%"],
        )
        db.delete(table="prd_work_centor_header_md", where="wc_code like %s", params=["AUTO_%"])

        # --- Master: 工艺路线 ---
        db.delete(
            table="prd_routings_item_md",
            where="routings_header_id in (select id from prd_routings_header_md where vrs_code like %s)",
            params=["test_%"],
        )
        db.delete(table="prd_routings_header_md", where="vrs_code like %s", params=["test_%"])

        # --- Master: 生产版本 ---
        db.delete(table="prd_prd_version_md", where="prd_vrs_code like %s", params=["test_%"])

        # --- Order: 生产订单（软删除） ---
        db.delete(
            table="prd_order_confirm_header_tr",
            where="wo_id in (select id from prd_order_header_tr where wo_code like %s)",
            params=["AUTO_%"],
        )
        db.delete(
            table="prd_order_routings_item_tr",
            where="prd_order_header_tr_id in (select id from prd_order_header_tr where wo_code like %s)",
            params=["AUTO_%"],
        )
        db.delete(table="prd_order_header_tr", where="wo_code like %s", params=["AUTO_%"])

        # --- Order: 领料单（软删除） ---
        db.delete(
            table="prd_issue_item_tr",
            where="prd_issue_head_tr_id in (select id from prd_issue_head_tr where issue_code like %s)",
            params=["AUTO_%"],
        )
        db.delete(table="prd_issue_head_tr", where="issue_code like %s", params=["AUTO_%"])

        # --- Order: 交货单（生产确认/领料/退料关联，软删除） ---
        db.delete(
            table="del_dn_item_tr",
            where="dn_code in (select dn_code from del_dn_head_tr where bt_class in ('PRD_ISSUE','PRD_ISSUE_RETURN','PRD_CONFIRM') and dn_code like %s)",
            params=["AUTO_%"],
        )
        db.delete(
            table="del_dn_head_tr",
            where="bt_class in ('PRD_ISSUE','PRD_ISSUE_RETURN','PRD_CONFIRM') and dn_code like %s",
            params=["AUTO_%"],
        )

        Loggers.info("✅ ERP_PRD 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"ERP_PRD 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_prd_cleanup", _cleanup_erp_prd, order=250)
