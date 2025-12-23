"""SCM_DEL 模块的 pytest 配置"""

import pytest
from utils.log_util import Loggers
from utils.mysql_util import DBManager


@pytest.fixture(scope="session", autouse=True)
def scm_del_module_cleanup():
    """SCM_DEL 模块的 session 级别清理 fixture"""
    yield
    # 测试完成后执行清理
    try:
        db = DBManager()
        
        # 清理交货单数据
        db.delete(table="del_dn_head_tr", where="remark like %s", params=["%执行自动化测试备注SQW%"])
        db.delete(table="del_dn_item_tr", where="remark like %s", params=["%执行自动化测试备注SQW%"])
        db.delete(table="sls_so_head_tr", where="remark like %s", params=["%执行自动化测试备注SQW%"])
        db.delete(table="del_dn_type_cf", where="dn_type_code like %s", params=["AT_%"])
        db.delete(table="del_dn_item_type_cf", where="dn_item_type_code like %s", params=["AT_%"])
        
        Loggers.info("✅ SCM_DEL 模块测试数据清理完成")
    except Exception as e:
        Loggers.error(f"❌ SCM_DEL 模块测试数据清理失败: {str(e)}")

