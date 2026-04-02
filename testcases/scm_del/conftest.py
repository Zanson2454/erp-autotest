"""SCM_DEL 模块的 pytest 配置"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_scm_del() -> None:
    """统一清理入口：由 cleanup_registry 在 session 末尾调用。"""
    db = None
    try:
        db_config = get_module_db_config()
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
        Loggers.warning(f"SCM_DEL 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("scm_del_cleanup", _cleanup_scm_del, order=220)
