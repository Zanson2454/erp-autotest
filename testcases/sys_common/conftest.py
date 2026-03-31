"""SYS_COMMON 模块清理注册。

注意：依赖运行时 user_id（created_by）的清理（org_employee_org_link_cf、
org_struct_business_type_link、org_dimension_business_link）需在各测试类
teardown_class 中保留，无法在无状态 conftest 内执行。
"""

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


def _cleanup_sys_common() -> None:
    db = None
    try:
        db_config = _get_erp_db_config()
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过 SYS_COMMON 数据清理")
            return

        db = DBManager(**db_config)

        # org
        db.delete(table="org_identity_cf",    where="code like %s",          params=["AT_%"])
        db.delete(table="org_employee_md",    where="emp_code like %s",       params=["AT_%"])
        db.delete(table="org_struct_md",      where="org_code like %s",       params=["AT_%"])
        db.delete(table="org_dimension_cf",   where="dimension_code like %s", params=["AT_%"])
        db.delete(table="org_business_type_cf", where="biz_type_code like %s", params=["AT_%"])

        # print
        db.delete(table="print_scene",       where="scene_code like %s", params=["AT_%"])
        db.delete(table="print_scene_view",  where="view_key like %s",   params=["AT_%"])

        # async task
        db.delete(table="async_task_instance",  where="task_code like %s",       params=["AT_%"])
        db.delete(table="async_task_definition", where="definition_code like %s", params=["AT_%"])

        # api config
        db.delete(table="api_config", where="config_key like %s", params=["AT_%"])

        # gei
        db.delete(table="gei_task",     where="task_name like %s",     params=["AT_%"])
        db.delete(table="gei_template", where="template_name like %s", params=["AT_%"])

        Loggers.info("✅ SYS_COMMON 模块测试数据统一清理完成")
    except Exception as e:
        Loggers.error(f"❌ SYS_COMMON 模块测试数据清理失败: {e}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


register_cleanup("sys_common_cleanup", _cleanup_sys_common, order=210)
