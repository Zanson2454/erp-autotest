"""
结算管理业务检查自动化用例
覆盖结算项对账确认、手工汇单、批量任务记录等场景
"""
import sys
import os
from pathlib import Path
import allure
import pytest
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from data_factory.fin_sett_factory import FinSettlementFactory
from utils.yaml_util import YamlUtil
from utils.log_util import logger
import time

# 添加项目路径到sys.path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettItemBusiCheck(BaseTest):
    """结算项业务检查测试用例集"""
    sett_item_info = {}

    @classmethod
    def setup_class(cls):
        """初始化测试环境和配置"""
        super().setup_class()
        logger.info("开始初始化结算项业务检查测试环境")
        
        # 初始化YAML工具
        cls.yaml_util = YamlUtil()
        
        # 获取项目根路径
        project_root = Path(__file__).resolve().parent.parent.parent
        
        # 加载API配置文件
        try:
            fin_api_path_file = project_root / "testdata" / "fin" / "fin_api_path.yaml"
            fin_api_params_file = project_root / "testdata" / "fin" / "fin_api_params.yaml"
            
            if fin_api_path_file.exists():
                apis_config = cls.yaml_util.read_yaml(fin_api_path_file)
                cls.apis = apis_config.get("apis", {}) if apis_config else {}
                logger.info(f"成功加载API路径配置，共{len(cls.apis)}个接口")
            else:
                logger.warning(f"API路径配置文件不存在: {fin_api_path_file}")
                cls.apis = {}
                
            if fin_api_params_file.exists():
                params_config = cls.yaml_util.read_yaml(fin_api_params_file)
                cls.api_params = params_config.get("api_params", {}) if params_config else {}
                logger.info(f"成功加载API参数配置，共{len(cls.api_params)}个参数模板")
            else:
                logger.warning(f"API参数配置文件不存在: {fin_api_params_file}")
                cls.api_params = {}
                
        except Exception as e:
            logger.error(f"加载API配置文件失败: {str(e)}")
            cls.apis = {}
            cls.api_params = {}
        
        # 初始化结算工厂
        try:
            cls.sett_factory = FinSettlementFactory()
            logger.info("结算工厂初始化成功")
        except Exception as e:
            logger.error(f"结算工厂初始化失败: {str(e)}")
            
        logger.info("结算项业务检查测试环境初始化完成")

    def _get_sett_item_ids(self):
        """获取不同状态的结算项ID"""
        # 已创建结算项
        created_sett_item = FinSettlementFactory.get_or_create_settlement_item("CREATED")
        # 已对账结算项
        reconciled_sett_item = FinSettlementFactory.get_or_create_settlement_item("RECONCILED")
        # 已创建结算单（同时获得已汇单结算项）
        settlement_doc = FinSettlementFactory.get_or_create_settlement_doc("CREATED")
        
        created_sett_item_id = created_sett_item.get("id")
        reconciled_sett_item_id = reconciled_sett_item.get("id")
        
        # 查询已汇单结算项
        sett_doc_created_sql = """
            SELECT id FROM sett_item_tr 
            WHERE deleted = 0 AND sett_item_status = 'SETT_DOC_CREATED'
            ORDER BY created_at DESC
            LIMIT 1
        """
        doc_created_result = self.db.query(sett_doc_created_sql)
        doc_created_sett_item_id = doc_created_result[0]["id"] if doc_created_result else None
        
        return [created_sett_item_id, doc_created_sett_item_id, reconciled_sett_item_id]

    @ParamUtil.case_decorator(
        story="结算项对账确认",
        title="结算项对账确认",
        description="新建结算项，对账确认，检查结算单是否生成",
        severity="critical",
        order=1,
        smoke=False,
        tags=["settlement", "confirm"]
    )
    def test_sett_item_record(self):
        """结算项对账确认测试用例"""
        try:
            with a.step("获取不同状态的结算项ID"):
                sett_item_ids = self._get_sett_item_ids()
                a.json(sett_item_ids, "结算项ID列表")
                
            with a.step("执行结算项对账确认"):
                api_path = ParamUtil.get_api_path(self.apis, "SETT-ITEM-结算项确认及汇单-关联操作-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                for index, sett_item_id in enumerate(sett_item_ids):
                    filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                    filtered_params = ParamUtil.convert_param_type(filtered_params, ["params", "request"], "array")
                    ParamUtil.set_request_params(filtered_params, [{"id": sett_item_id}])
                    
                    result = self.http.post(url, json=filtered_params)
                    
                    # 等待异步任务执行
                    time.sleep(3)
                    
                    # 查询结果验证
                    sql = f"""
                        SELECT id, sett_item_status, async_execution_status, sett_doc_id
                        FROM sett_item_tr 
                        WHERE deleted = 0 AND id = {sett_item_id}
                    """
                    sql_result = self.db.query(sql)
                    
                    # 已创建、已对账结算项可以汇单
                    if index == 0 or index == 2:
                        self.assert_util.assert_response_success(result)
                        if sql_result:
                            self.assert_util.assert_eq(sql_result[0]["sett_item_status"], "SETT_DOC_CREATED")
                            self.assert_util.assert_eq(sql_result[0]["async_execution_status"], "SUCCEEDED")
                            self.assert_util.assert_not_empty(sql_result[0]["sett_doc_id"], "结算单号为空")
                    elif index == 1:
                        # 已汇单结算项不能重复汇单
                        assert result.get("success") == False
                        assert result.get("err", {}).get("msg") == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                        if sql_result:
                            self.assert_util.assert_eq(sql_result[0]["sett_item_status"], "SETT_DOC_CREATED")
                            self.assert_util.assert_not_empty(sql_result[0]["sett_doc_id"], "结算单号为空")
                    
                    a.json(filtered_params, f"请求数据-ID{sett_item_id}")
                    a.json(result, f"响应结果-ID{sett_item_id}")
                    
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="结算项手工汇单",
        title="结算项手工汇单",
        description="测试结算项手工汇单功能",
        severity="critical",
        order=2,
        smoke=False,
        tags=["settlement", "manual_remittance"]
    )
    def test_sett_item_manual_remittance(self):
        """结算项手工汇单测试用例"""
        try:
            with a.step("获取不同状态的结算项ID"):
                sett_item_ids = self._get_sett_item_ids()
                a.json(sett_item_ids, "结算项ID列表")
                
            with a.step("执行结算项手工汇单"):
                api_path = ParamUtil.get_api_path(self.apis, "SETT-ITEM-结算项手工汇单-关联操作-异步服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                for index, sett_item_id in enumerate(sett_item_ids):
                    filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                    filtered_params = ParamUtil.convert_param_type(filtered_params, ["params", "request"], "array")
                    ParamUtil.set_request_params(filtered_params, [{"id": sett_item_id}])
                    
                    result = self.http.post(url, json=filtered_params)
                    
                    # 等待异步任务执行
                    time.sleep(3)
                    
                    # 查询结果验证
                    sql = f"""
                        SELECT id, sett_item_status, async_execution_status, sett_doc_id
                        FROM sett_item_tr 
                        WHERE deleted = 0 AND id = {sett_item_id}
                    """
                    sql_result = self.db.query(sql)
                    
                    # 已创建、已汇单结算项不可以手工汇单
                    if index == 0 or index == 1:
                        assert result.get("success") == False
                        assert result.get("err", {}).get("msg") == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                    elif index == 2:  # 已对账结算项可以手工汇单
                        self.assert_util.assert_response_success(result)
                        if sql_result:
                            self.assert_util.assert_eq(sql_result[0]["sett_item_status"], "SETT_DOC_CREATED")
                            self.assert_util.assert_eq(sql_result[0]["async_execution_status"], "SUCCEEDED")
                            self.assert_util.assert_not_empty(sql_result[0]["sett_doc_id"], "结算单号为空")
                    
                    a.json(filtered_params, f"请求数据-ID{sett_item_id}")
                    a.json(result, f"响应结果-ID{sett_item_id}")
                    
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="批量任务记录",
        title="批量任务记录查询",
        description="查询结算汇单记录分页数据",
        severity="normal",
        order=3,
        smoke=False,
        tags=["settlement", "batch_task"]
    )
    def test_batch_task_record(self):
        """批量任务记录查询测试用例"""
        try:
            with a.step("查询批量任务记录"):
                api_path = ParamUtil.get_api_path(self.apis, "结算汇单记录-分页数据服务_PmHKWs1")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, 
                    ["pageNo", "pageSize", "conditionItems", "sortOrders"], 
                    ["params", "request", "pageable"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "pageable": {
                        "pageNo": "1",
                        "pageSize": "20",
                        "conditionItems": None,
                        "sortOrders": None
                    }
                })
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                total = result.get("data", {}).get("data", {}).get("total", 0)
                assert total >= 0, "总记录数应该大于等于0"
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """模块独立运行入口"""
    test = TestSettItemBusiCheck()
    test.setup_class()
    
    # 可以在这里添加单独的测试方法调用
    # test.test_sett_item_record()
    # test.test_sett_item_manual_remittance()
    # test.test_batch_task_record()

        
        