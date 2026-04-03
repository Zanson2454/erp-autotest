"""ERP_COND 模块清理注册。

注意：各测试类的 teardown_class 中使用了 AT_% 前缀清理，
但实际生成的 code 使用 AF/MS/MSQ/UG 等标签前缀，此处统一修正。
"""

from testcases.comm.cleanup_registry import get_module_db_config, register_cleanup
from utils.log_util import Loggers
from utils.mysql_util import DBManager


def _cleanup_erp_cond() -> None:
    db = None
    try:
        db_config = get_module_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 ERP_COND 数据清理")
            return

        db = DBManager(**db_config)

        # --- 允许字段 ---
        db.delete(table="allow_field_item_md", where="code like %s", params=["AF%"])

        # --- 匹配记录 ---
        db.delete(table="match_record_head_md", where="code like %s", params=["AT_%"])

        # --- 匹配方案 ---
        db.delete(table="match_scheme_md", where="code like %s", params=["MS%"])

        # --- 匹配序列 ---
        db.delete(table="match_seq_head_md", where="code like %s", params=["MSQ%"])

        # --- 用量组 ---
        db.delete(table="usage_group_md", where="code like %s", params=["UG%"])

        Loggers.info("✅ ERP_COND 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.warning(f"ERP_COND 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("erp_cond_cleanup", _cleanup_erp_cond, order=225)
