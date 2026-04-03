"""ERP_PLN 模块清理注册。"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_erp_pln() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_PLN 数据清理")
            return

        db = DBManager(**db_config)

        # --- 计划工序（自引用表，先清关联） ---
        db.delete(table="pln_process_tr", where="code like %s", params=["PLN_%"])

        Loggers.info("✅ ERP_PLN 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"ERP_PLN 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_pln_cleanup", _cleanup_erp_pln, order=235)
