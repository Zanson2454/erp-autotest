"""SCM_INV 模块清理注册。"""

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


def _cleanup_scm_inv() -> None:
    db = None
    try:
        db_config = _get_erp_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 SCM_INV 数据清理")
            return

        db = DBManager(**db_config)

        # 关联子查询清理翻译表（需在主表删除前执行）
        try:
            db.execute(
                """
                DELETE FROM inv_inv_type_trans_cf
                WHERE created_by IN (
                    SELECT DISTINCT created_by FROM inv_inv_type_cf WHERE code LIKE %s
                )
                """,
                ["AT_%"],
            )
        except Exception as exc:
            Loggers.warning(f"跳过清理 inv_inv_type_trans_cf: {exc}")

        db.delete(table="inv_inv_type_cf", where="code like %s", params=["AT_%"])
        db.delete(table="inv_mvm_type_cf", where="remark = %s", params=["AUTOMATION_TEST"])
        db.delete(table="inv_spc_stk_type_cf", where="code like %s", params=["AT_%"])
        db.delete(table="inv_fb_type_cf", where="code like %s", params=["AT_%"])
        db.delete(table="inv_mvm_ext_type_cf", where="code like %s", params=["AT_%"])
        db.delete(table="inv_bs_type_cf", where="name like %s", params=["%AT%"])
        db.delete(table="inv_atp_rule_cf", where="code like %s", params=["AUTOTEST_%"])
        db.delete(table="inv_atp_group_md", where="code like %s", params=["AUTOTEST_ATP_%"])
        db.delete(table="inv_move_doc_head", where="doc_code like %s", params=["AUTOTEST_%"])
        db.delete(table="inv_move_doc_item", where="note like %s", params=["%AUTOTEST%"])

        Loggers.info("✅ SCM_INV 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.error(f"❌ SCM_INV 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("scm_inv_cleanup", _cleanup_scm_inv, order=220)
