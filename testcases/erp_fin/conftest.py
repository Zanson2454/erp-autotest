"""ERP_FIN 模块清理注册。"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_erp_fin() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_FIN 数据清理")
            return

        db = DBManager(**db_config)

        # fin_ap
        db.delete(table="fin_apm_ap_type_md", where="ap_type_code like %s", params=["AT_%"])

        # fin_iv - 这些表没有独立 code 字段，由业务表级联清理，跳过
        # db.delete(table="fin_iv_voucher_head_tr", ...)
        # db.delete(table="fin_iv_acc_detail_tr", ...)
        # db.delete(table="fin_iv_execute_record_tr", ...)
        # db.delete(table="fin_iv_acc_period_tr", ...)
        # 清理配置表（有 code 字段）
        db.delete(table="fin_iv_rule_cf", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_rule_detail_cf", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_route_cf", where="code like %s", params=["AT_%"])
        db.delete(
            table="fin_iv_mat_acc_cate_link_cf",
            where="acc_cate_id in (select id from fin_iv_acc_cate_type_cf where acc_cate_code like %s)",
            params=["AT_%"],
        )
        db.delete(table="fin_iv_acc_cate_type_cf", where="acc_cate_code like %s", params=["AT_%"])

        # fin_sett - 结算模块配置表和事务表
        # 先清事务表（子表）
        db.delete(table="sett_item_tr", where="sett_item_code like %s", params=["AUTOTEST%"])
        db.delete(table="sett_item_tr", where="sett_item_code like %s", params=["AUTO-TEST%"])
        db.delete(table="sett_doc_tr", where="sett_doc_code like %s", params=["AUTOTEST%"])
        db.delete(table="sett_doc_tr", where="sett_doc_code like %s", params=["AUTO-TEST%"])
        # 再清配置表（父表）
        db.delete(table="fin_sett_srs_link_cf", where="srs_code like %s", params=["AT_%"])
        db.delete(table="sett_sdc_head_cf", where="sdc_head_code like %s", params=["AT_%"])
        db.delete(table="sett_sds_head_cf", where="sds_head_code like %s", params=["AT_%"])
        db.delete(table="fin_sett_doc_type_cf", where="sett_doc_type_code like %s", params=["AUTO-TEST%"])
        db.delete(table="fin_sett_item_type_cf", where="sett_item_type_code like %s", params=["AUTO-TEST%"])
        db.delete(table="fin_sett_spg_type_cf", where="spg_code like %s", params=["AT_%"])
        db.delete(table="fin_sett_type_cf", where="code like %s", params=["AT_%"])
        db.delete(table="fin_sett_rule_cf", where="code like %s", params=["AT_%"])
        db.delete(table="fin_sett_price_group_cf", where="code like %s", params=["AT_%"])

        Loggers.info("✅ ERP_FIN 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"ERP_FIN 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_fin_cleanup", _cleanup_erp_fin, order=240)
