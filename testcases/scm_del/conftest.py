"""SCM_DEL 模块的 pytest 配置"""

import os
from utils.log_util import Loggers
from utils.mysql_util import DBManager
from data_factory.base import DataFactory
from testcases.comm.cleanup_registry import register_cleanup


def _cleanup_scm_del() -> None:
    """统一清理入口：由 cleanup_registry 在 session 末尾调用。"""
    db = None
    try:
        env = os.getenv("TEST_ENV", "test")
        project = os.getenv("TEST_PROJECT")
        data_factory = DataFactory(env_name=env, project=project)
        env_config = data_factory.get_env_config()
        db_config = (env_config or {}).get("database", {}).get("erp_db")
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 SCM_DEL 数据清理")
            return

        db = DBManager(**db_config)
        # 清理交货单数据
        db.delete(table="del_dn_head_tr", where="remark like %s", params=["%执行自动化测试备注SQW%"])
        db.delete(table="del_dn_item_tr", where="remark like %s", params=["%执行自动化测试备注SQW%"])
        db.delete(table="sls_so_head_tr", where="remark like %s", params=["%执行自动化测试备注SQW%"])
        db.delete(table="del_dn_type_cf", where="dn_type_code like %s", params=["AT_%"])
        db.delete(table="del_dn_item_type_cf", where="dn_item_type_code like %s", params=["AT_%"])
        Loggers.info("✅ SCM_DEL 模块测试数据清理完成")
    except Exception as e:
        Loggers.error(f"❌ SCM_DEL 模块测试数据清理失败: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("scm_del_cleanup", _cleanup_scm_del, order=220)
