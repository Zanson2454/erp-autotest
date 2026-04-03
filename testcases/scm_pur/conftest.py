"""SCM_PUR 模块清理注册。"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_scm_pur() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 SCM_PUR 数据清理")
            return

        db = DBManager(**db_config)

        # --- Config: 采购申请头类型 ---
        db.delete(table="pur_pr_head_type_cf", where="pr_type_code like %s", params=["AUTOTEST_PR_%"])

        # --- Config: 采购申请行类型 ---
        db.delete(table="pur_pr_item_type_cf", where="pr_item_type_code like %s", params=["AUTOTEST_PRI_%"])

        # --- Config: 采购订单类型 ---
        db.delete(table="pur_po_type_cf", where="po_type like %s", params=["AUTOTEST_PO_%"])

        # --- Config: 采购订单行类型 ---
        db.delete(table="pur_po_item_type_cf", where="po_item_type like %s", params=["AUTOTEST_ITEM%"])

        # --- Transaction: 采购申请（软删除，子表先） ---
        db.delete(
            table="pur_pr_item_tr",
            where="pur_pr_head_tr_id in (select id from pur_pr_head_tr where pr_name like %s)",
            params=["AT_PR_%"],
        )
        db.delete(table="pur_pr_head_tr", where="pr_name like %s", params=["AT_PR_%"])

        # --- Transaction: 采购订单（软删除，按备注标识） ---
        db.delete(
            table="pur_po_schl_tr",
            where="po_head_id in (select id from pur_po_head_tr where pur_remark = %s)",
            params=["执行自动化测试备注"],
        )
        db.delete(
            table="pur_po_item_tr",
            where="po_head_id in (select id from pur_po_head_tr where pur_remark = %s)",
            params=["执行自动化测试备注"],
        )
        db.delete(table="pur_po_head_tr", where="pur_remark = %s", params=["执行自动化测试备注"])

        Loggers.info("✅ SCM_PUR 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"SCM_PUR 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("scm_pur_cleanup", _cleanup_scm_pur, order=230)
