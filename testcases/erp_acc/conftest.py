"""ERP_ACC 模块清理注册（低优先级，主要为只读测试）。"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_erp_acc() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_ACC 数据清理")
            return

        db = DBManager(**db_config)

        # 导出/导入任务记录（如有）
        db.delete(table="gei_task_export", where="task_name like %s", params=["%自动化测试%"])
        db.delete(table="gei_task_import", where="task_name like %s", params=["%自动化测试%"])

        Loggers.info("✅ ERP_ACC 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"ERP_ACC 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_acc_cleanup", _cleanup_erp_acc, order=220)
