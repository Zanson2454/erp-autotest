"""ERP_FIN 模块清理注册。"""

import os

from data_factory.base import DataFactory
from testcases.comm.cleanup_registry import register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _get_erp_db_config():
    env = os.getenv("TEST_ENV", "test")
    project = os.getenv("TEST_PROJECT")
    data_factory = DataFactory(env_name=env, project=project)
    env_config = data_factory.get_env_config() or {}
    return env_config.get("database", {}).get("erp_db")


def _cleanup_erp_fin() -> None:
    db = None
    try:
        db_config = _get_erp_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_FIN 数据清理")
            return

        db = DBManager(**db_config)

        # fin_ap
        db.delete(table="fin_apm_ap_type_md", where="ap_type_code like %s", params=["AT_%"])

        # fin_iv
        db.delete(table="fin_iv_voucher_item_tr", where="code like %s", params=["AT_%"])
        db.delete(table="iv_doc_tr", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_acc_detail_tr", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_execute_record_tr", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_acc_period_tr", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_rule_cf", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_rule_detail_cf", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_voucher_head_tr", where="code like %s", params=["AT_%"])
        db.delete(table="fin_iv_route_cf", where="code like %s", params=["AT_%"])
        db.delete(
            table="fin_iv_mat_acc_cate_link_cf",
            where="acc_cate_id in (select id from fin_iv_acc_cate_type_cf where acc_cate_code like %s)",
            params=["AT_%"],
        )
        db.delete(table="fin_iv_acc_cate_type_cf", where="acc_cate_code like %s", params=["AT_%"])

        Loggers.info("✅ ERP_FIN 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.error(f"❌ ERP_FIN 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_fin_cleanup", _cleanup_erp_fin, order=240)
