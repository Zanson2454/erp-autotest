"""ERP_FI 模块清理注册。"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_erp_fi() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_FI 数据清理")
            return

        db = DBManager(**db_config)

        # --- Voucher: 凭证行（子表先） ---
        db.delete(
            table="fin_glm_ve_item_tr",
            where="ve_head_id in (select id from fin_glm_ve_head_tr where remark in (%s, %s))",
            params=["测试正常业务流程", "测试正常批量业务流程"],
        )

        # --- Voucher: 凭证头 ---
        db.delete(
            table="fin_glm_ve_head_tr", where="remark in (%s, %s)", params=["测试正常业务流程", "测试正常批量业务流程"]
        )

        # --- Config: 会计政策类型 ---
        db.delete(table="fin_glm_ap_type_cf", where="ap_type_code like %s", params=["AUTO-AP-CODE-%"])

        # --- Config: 会计要素行（子表先） ---
        db.delete(table="fin_glm_ae_item_cf", where="ae_item_code like %s", params=["AUTO-AE-ITEM%-CODE-%"])

        # --- Config: 会计要素头 ---
        db.delete(table="fin_glm_ae_head_cf", where="ae_head_code like %s", params=["AUTO-AE-CODE-%"])

        Loggers.info("✅ ERP_FI 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"ERP_FI 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_fi_cleanup", _cleanup_erp_fi, order=245)
