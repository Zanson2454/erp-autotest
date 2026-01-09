"""SCM_SLS 模块的 pytest 配置

提供 session 级别的统一数据清理功能
汇总所有测试类原有的清理逻辑，在所有 scm_sls 测试用例执行完后统一清理
只清理原本按 code/name 前缀删除的数据，保持原逻辑不变

注意：在并行执行（pytest-xdist）时，每个 worker 进程都有自己的 session scope，
清理逻辑会在每个 worker 的所有测试完成后执行。使用 pytest_sessionfinish hook
确保在所有 worker 都完成测试后才执行最终清理（仅在主进程中执行）。
"""

import pytest
from utils.log_util import Loggers
from utils.mysql_util import DBManager
from data_factory.base import DataFactory
import os
import time
from datetime import datetime
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).resolve().parent.parent.parent

# 存储 session 开始时间，用于在所有 worker 完成后统一清理
_session_start_time = None


def pytest_sessionstart(session):
    """pytest session 开始时记录时间戳（仅在主进程中执行一次）"""
    global _session_start_time
    if _session_start_time is None:
        _session_start_time = int(time.time() * 1000)
        Loggers.info(f"SCM_SLS 模块测试开始（主进程），记录时间戳: {_session_start_time}")


def pytest_sessionfinish(session, exitstatus):
    """pytest session 结束时执行清理（仅在主进程中执行，确保在所有 worker 完成后执行）"""
    global _session_start_time
    if _session_start_time is None:
        return
    
    # 测试完成后执行清理
    try:
        # 获取环境配置（使用 DataFactory 确保环境变量被正确替换）
        # 支持多项目：自动从环境变量 TEST_PROJECT 获取项目名称
        env = os.getenv("TEST_ENV", "test")
        project = os.getenv("TEST_PROJECT")
        data_factory = DataFactory(env_name=env, project=project)
        env_config = data_factory.get_env_config()
        
        if not env_config:
            Loggers.warning("未找到环境配置，跳过数据清理")
            return
        
        # 获取数据库配置
        db_config = env_config.get("database", {}).get("erp_db")
        if not db_config:
            Loggers.warning("未找到数据库配置，跳过数据清理")
            return
        
        # 创建数据库连接
        db = DBManager(**db_config)
        
        try:
            Loggers.info("开始清理 SCM_SLS 模块测试数据（所有 worker 测试完成后统一清理）...")
            
            # 调用清理逻辑
            _perform_cleanup(db, _session_start_time)
            
        finally:
            # 关闭数据库连接
            db.close()
            
    except Exception as e:
        Loggers.error(f"❌ SCM_SLS 模块测试数据清理失败: {str(e)}")


def _perform_cleanup(db, session_start_time):
    """执行清理逻辑的辅助函数"""
    # 将毫秒时间戳转换为 datetime 对象
    # session_start_time 是毫秒时间戳，需要除以 1000 转换为秒
    session_start_datetime = datetime.fromtimestamp(session_start_time / 1000.0)
    
    try:
        # ========== 清理子表数据（先删除，避免外键约束） ==========
        
        # 1. 按创建时间清理销售单、销售订单行、交货单、交货单行、报价单等单据数据
        # 清理所有在测试开始后创建的数据
        try:
            # 1.1 清理销售订单行和报价单行（子表，先删除）
            db.delete(
                table="sls_so_item_tr",
                where="created_at >= %s",
                params=[session_start_datetime]
            )
            Loggers.info(f"✅ 已清理表 sls_so_item_tr 中测试开始后创建的数据（包括销售订单行和报价单行，时间 >= {session_start_datetime}）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_item_tr 失败: {str(e)}")
        
        try:
            # 1.2 清理交货单行（子表，先删除）
            # 只清理销售相关的交货单（bt_class = 'SLS'）
            # 使用 JOIN 方式清理，避免子查询问题
            db.execute(
                sql="""
                    DELETE i FROM del_dn_item_tr i
                    INNER JOIN del_dn_head_tr h ON i.dn_id = h.id
                    WHERE h.bt_class = 'SLS' 
                      AND (i.created_at >= %s OR h.created_at >= %s)
                """,
                params=[session_start_datetime, session_start_datetime]
            )
            Loggers.info(f"✅ 已清理表 del_dn_item_tr 中测试开始后创建的销售交货单行数据（时间 >= {session_start_datetime}）")
        except Exception as e:
            Loggers.debug(f"清理表 del_dn_item_tr 失败: {str(e)}")
        
        try:
            # 1.3 清理销售单主表和报价单主表（主表，后删除）
            # 注意：报价单存储在 sls_so_head_tr 表中（通过 soTypeId 区分）
            # 清理 sls_so_head_tr，确保包含所有销售订单和报价单数据
            db.delete(
                table="sls_so_head_tr",
                where="created_at >= %s",
                params=[session_start_datetime]
            )
            Loggers.info(f"✅ 已清理表 sls_so_head_tr 中测试开始后创建的数据（包括销售订单和报价单，时间 >= {session_start_datetime}）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_head_tr 失败: {str(e)}")
        
        try:
            # 1.4 清理交货单主表（主表，后删除）
            # 只清理销售相关的交货单（bt_class = 'SLS'）
            db.delete(
                table="del_dn_head_tr",
                where="bt_class = 'SLS' AND created_at >= %s",
                params=[session_start_datetime]
            )
            Loggers.info(f"✅ 已清理表 del_dn_head_tr 中测试开始后创建的销售交货单数据（时间 >= {session_start_datetime}）")
        except Exception as e:
            Loggers.debug(f"清理表 del_dn_head_tr 失败: {str(e)}")
        
        # 2. 清理价格调整单数据（test_price_crud.py, test_so_price.py）
        # 原逻辑：按 price_adj_name 清理，保持原条件
        # 注意：只清理 price_adj_head_tr 表，gen_price_adj_head_tr 和 erp_price_adj_head_tr 表不存在
        try:
            db.delete(
                table="price_adj_head_tr",
                where="price_adj_name LIKE %s OR price_adj_name LIKE %s OR price_adj_name LIKE %s",
                params=["自动化测试价格调整_%", "hxy维护价格_%", "删除价格_%"]
            )
            Loggers.info("✅ 已清理表 price_adj_head_tr 中的测试数据（test_price_crud.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 price_adj_head_tr 失败: {str(e)}")
        
        # test_so_price.py 的价格调整单清理逻辑
        try:
            db.delete(
                table="price_adj_head_tr",
                where="price_adj_name LIKE %s OR price_adj_name LIKE %s",
                params=["订单价格维护_%", "订单价格校验创建价格_%"]
            )
            Loggers.info("✅ 已清理表 price_adj_head_tr 中的测试数据（test_so_price.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 price_adj_head_tr 失败: {str(e)}")
        
        # ========== 清理主表数据（后删除） ==========
        
        # 9. 清理销售渠道数据（test_sls_dc_management.py）
        # 原逻辑：code like 'AT_%'，保持原条件
        try:
            db.delete(
                table="sls_dc_md",
                where="code like %s",
                params=["AT_%"]
            )
            Loggers.info("✅ 已清理表 sls_dc_md 中的测试数据（test_sls_dc_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_dc_md 失败: {str(e)}")
        
        # 10. 清理寻仓规则配置数据（test_wh_find_rule_management.py）
        # 原逻辑：name like '自动化寻仓规则_%'，保持原条件
        try:
            db.delete(
                table="sls_wh_find_rule_cf",
                where="name like %s",
                params=["自动化寻仓规则_%"]
            )
            Loggers.info("✅ 已清理表 sls_wh_find_rule_cf 中的测试数据（test_wh_find_rule_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_wh_find_rule_cf 失败: {str(e)}")
        
        # 11. 清理订单类型定义数据（test_so_type_management.py）
        # 原逻辑：so_type_code like 'AT_%'，保持原条件
        try:
            db.delete(
                table="sls_so_type_cf",
                where="so_type_code like %s",
                params=["AT_%"]
            )
            Loggers.info("✅ 已清理表 sls_so_type_cf 中的测试数据（test_so_type_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_type_cf 失败: {str(e)}")
        
        # 12. 清理订单项目行分配数据（test_so_type_detm_management.py）
        # 原逻辑：remark like '自动化测试%'，保持原条件
        try:
            db.delete(
                table="sls_so_item_detm_cf",
                where="remark like %s",
                params=["自动化测试%"]
            )
            Loggers.info("✅ 已清理表 sls_so_item_detm_cf 中的测试数据（test_so_type_detm_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_item_detm_cf 失败: {str(e)}")
        
        # 13. 清理订单行项目类型定义数据（test_so_item_type_management.py）
        # 原逻辑：so_item_type_code like 'AT_%'，保持原条件
        try:
            db.delete(
                table="sls_so_item_type_cf",
                where="so_item_type_code like %s",
                params=["AT_%"]
            )
            Loggers.info("✅ 已清理表 sls_so_item_type_cf 中的测试数据（test_so_item_type_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_item_type_cf 失败: {str(e)}")
        
        # 14. 清理销售审单规则数据（test_so_approval_rule_management.py）
        # 原逻辑：name like '测试审单规则_%'，保持原条件
        try:
            db.delete(
                table="sls_so_approval_rule_cf",
                where="name like %s",
                params=["测试审单规则_%"]
            )
            Loggers.info("✅ 已清理表 sls_so_approval_rule_cf 中的测试数据（test_so_approval_rule_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_approval_rule_cf 失败: {str(e)}")
        
        # 15. 清理订单行项目类型组数据（test_sls_item_type_group_management.py）
        # 原逻辑：code like 'AT_%'，保持原条件
        try:
            db.delete(
                table="sls_so_item_type_group_cf",
                where="code like %s",
                params=["AT_%"]
            )
            Loggers.info("✅ 已清理表 sls_so_item_type_group_cf 中的测试数据（test_sls_item_type_group_management.py 原逻辑）")
        except Exception as e:
            Loggers.debug(f"清理表 sls_so_item_type_group_cf 失败: {str(e)}")
        
        Loggers.info("✅ SCM_SLS 模块测试数据清理完成")
        Loggers.info("⚠️  注意：原本按 id 删除的数据（如 sls_so_head_tr, sls_dn_head_tr, rebate_policy_head_tr）")
        Loggers.info("    和通过 API 查询后删除的数据（gen_match_record_md）无法在 session 级别清理，")
        Loggers.info("    这些数据需要在各自的测试类中保持原清理逻辑")
        
    except Exception as e:
        Loggers.error(f"❌ SCM_SLS 模块测试数据清理失败: {str(e)}")


# 注意：清理逻辑已移至 pytest_sessionfinish hook 函数中
# 这样可以确保在并行执行（pytest-xdist）时，清理逻辑在所有 worker 完成后才执行
