import pytest
import os
import sys
import allure
from pathlib import Path
import time
from datetime import datetime, timedelta
import random
from decimal import Decimal

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from data_factory.fin_sett_factory import FinSettlementFactory
from utils.log_util import Loggers
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettItemBusiCheck(BaseTest):
    """结算管理业务检查测试用例"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "erp_fin" / "fin_api_path.yaml"
        cls.base_api_params = Path(project_root) / "testdata" / "erp_fin" / "fin_api_params.yaml"
        cls.yaml_util = YamlUtil()  
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})  
    
    
    def get_sett_item_id(self):
        """获取不同状态的结算项ID 已创建，已对账，已汇单 """
        #已创建结算项
        created_sett_item = FinSettlementFactory.get_or_create_settlement_item("CREATED")
        #已对账结算项
        reconciled_sett_item = FinSettlementFactory.get_or_create_settlement_item("RECONCILED")
        #已创建结算单（同时获得已汇单结算项）
        FinSettlementFactory.get_or_create_settlement_doc("CREATED")
        created_sett_item_id = created_sett_item.get("id")
        reconciled_sett_item_id = reconciled_sett_item.get("id")
        Loggers.debug(f"已创建结算项ID: {created_sett_item_id}")
        Loggers.debug(f"已对账结算项ID: {reconciled_sett_item_id}")
        
        sett_doc_created_sql="""
            select id
            from sett_item_tr where deleted=0
            and sett_item_status='SETT_DOC_CREATED'
            order by created_at desc limit 1;
        """
        
        doc_created_sett_item_id=self.db.query(sett_doc_created_sql)[0]["id"]
        
        return [created_sett_item_id, doc_created_sett_item_id,reconciled_sett_item_id]
    
    @allure.title("结算项对账确认")
    @allure.description("1、新建结算项\n2、对账确认\n3、检查结算单是否生成")
    def test_sett_item_record(self):
        """测试结算项对账确认"""
        # 获取结算项ID列表
        sett_item_ids = self.get_sett_item_id()
        
        # 遍历每个ID进行测试
        for index, sett_item_id in enumerate(sett_item_ids):
            url = self.fin_path["SETT-ITEM-结算项确认及汇单-关联操作-异步服务"]["path"]
            data = ParamUtil.filter_post_body_fields(self.fin_params.get(url, {}), ["id"], ["params", "request"])
            data=ParamUtil.convert_param_type(data, ["params", "request"], "array")
            data["params"]["request"][0]["id"] = sett_item_id
            result = self.http.post(url, json=data, description=f"结算项对账确认 - ID: {sett_item_id}")
            
            #等待异步任务执行
            time.sleep(3)  # 等待3秒
            
            sql = f"""
                select id, sett_item_status, async_execution_status, sett_doc_id
                from sett_item_tr where deleted=0
                and id={sett_item_id} limit 1;
            """
            sql_result = self.db.query(sql)
            
            #已创建、已对账结算项可以汇单
            if index == 0 or index == 2:  # 第一个ID的断言
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_by_operator(sql_result[0]["sett_item_status"], "=", "SETT_DOC_CREATED")
                self.assert_util.assert_by_operator(sql_result[0]["async_execution_status"], "=", "SUCCEEDED")
                self.assert_util.assert_by_operator(sql_result[0]["sett_doc_id"], "not_empty")
            elif index == 1:  # 第二个ID的断言
                assert result.get("success",{}) == False
                #assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                self.assert_util.assert_by_operator(sql_result[0]["sett_item_status"], "=", "SETT_DOC_CREATED")
                self.assert_util.assert_by_operator(sql_result[0]["sett_doc_id"], "not_empty")
                
    def test_sett_item_manual_remittance(self):
        """测试结算项手工汇单"""
        url = self.fin_path["SETT-ITEM-结算项手工汇单-关联操作-异步服务"]["path"]
        sett_item_ids = self.get_sett_item_id()
        for index, sett_item_id in enumerate(sett_item_ids):
            data = ParamUtil.filter_post_body_fields(self.fin_params.get(url, {}), ["id"], ["params", "request"])
            data=ParamUtil.convert_param_type(data, ["params", "request"], "array")
            data["params"]["request"][0]["id"] = sett_item_id
            result = self.http.post(url, json=data, description=f"结算项手工汇单 - ID: {sett_item_id}")
            time.sleep(3)  # 等待3秒
            
            sql = f"""
                select id, sett_item_status, async_execution_status, sett_doc_id
                from sett_item_tr where deleted=0
                and id={sett_item_id} limit 1;
            """
            sql_result = self.db.query(sql)
            if index == 0 or index == 1:  # 第1.2个ID的断言 已创建、已汇单结算项不可以手工汇单
                assert result.get("success",{}) == False
                #assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
            elif index == 2:  # 第3个ID的断言 已对账结算项可以手工汇单
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_by_operator(sql_result[0]["sett_item_status"], "=", "SETT_DOC_CREATED")
                self.assert_util.assert_by_operator(sql_result[0]["async_execution_status"], "=", "SUCCEEDED")
                self.assert_util.assert_by_operator(sql_result[0]["sett_doc_id"], "not_empty")
                
    def test_batch_task_record(self):
        """批量任务记录"""
        url = self.fin_path["结算汇单记录-分页数据服务_PmHKWs1"]["path"]
        data = self.fin_params.get(url, {})
        filter_data = ParamUtil.filter_post_body_fields(data, ["pageNo","pageSize","conditionItems","sortOrders"],["params","request","pageable"])
        filter_data["params"]["request"]["pageable"]["pageNo"] = "1"
        filter_data["params"]["request"]["pageable"]["pageSize"] = "20"
        filter_data["params"]["request"]["pageable"]["conditionItems"] =None
        filter_data["params"]["request"]["pageable"]["sortOrders"] = None
        result = self.http.post(url, json=filter_data, description=f"批量任务记录")
        self.assert_util.assert_response_success(result)
        assert result.get("data",{}).get("data",{}).get("total",{}) >= 0
        
    
    
    BATCH_GET_SCOPE_TEST_CASES = [
        {
            "docType": "SETT_ITEM",
            "filterMethod": "CONDITION",
            "operType": "CONFIRM",
            "settItemStatus": "CREATED",
            "isCancelTrasferNote": False,
            "description": "操作类型：对账确认",
            "expected_status": "PENDING"
        },
        {
            "docType": "SETT_ITEM",
            "filterMethod": "CONDITION",
            "operType": "MANUAL",
            "settItemStatus": "RECONCILED",
            "isCancelTrasferNote": False,
            "description": "操作类型：手工汇单",
            "expected_status": "PENDING"
        },
    ]
    @case_decorator(
        story="结算项批量处理",
        title="批量任务处理获取命中范围",
        description="验证SETT_BATCH_AGGREGATION_LOCK_EVENT_SERVICE",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "SETT_BATCH_AGGREGATION_LOCK_EVENT_SERVICE"]
    )
    @pytest.mark.parametrize("test_params", BATCH_GET_SCOPE_TEST_CASES)
    def test_batch_get_scope(self, test_params):
        """测试批量任务处理获取命中范围 - 参数化测试
        
        Args:
            test_params: 包含测试参数的字典，包括：
                - docType: 文档类型
                - filterMethod: 筛选方法
                - operType: 操作类型
                - settItemStatus: 结算项状态
                - isCancelTrasferNote: 是否取消转单
                - description: 测试场景描述
                - expected_status: 期望的任务状态
        """
        try:
            url = self.fin_path["结算项-结算批量锁定服务"]["path"]
            data = self.fin_params.get(url, {})
            data = ParamUtil.filter_post_body_fields(
                data, 
                ["docType","filterMethod","operType","settItemStatus","isCancelTrasferNote"], 
                ["params", "request"]
            )
            
            # 设置请求参数
            set_dict = {
                "docType": test_params["docType"],
                "filterMethod": test_params["filterMethod"],
                "operType": test_params["operType"], 
                "settItemStatus": test_params["settItemStatus"],
                "isCancelTrasferNote": test_params["isCancelTrasferNote"]
            }
            ParamUtil.set_request_params(data, set_dict)
            
            self.logger.info(f"测试场景: {test_params['description']}")
            self.logger.info(f"请求参数: {data}")
            
            result = self.http.post(url, json=data, description=f"批量任务处理获取命中范围 - {test_params['description']}")
            
            # 通用断言逻辑 - 所有参数组合都使用相同的断言
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskCode",{}),"not_empty")
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("docType",{}),"=", test_params["docType"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("operType",{}),"=", test_params["operType"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskStatus",{}),"=", test_params["expected_status"])
            
            # 记录测试数据
            a.json(data, f"请求数据 - {test_params['description']}")
            a.json(result, f"响应数据 - {test_params['description']}")
            
        except Exception as e:
            a.text(f"测试场景 '{test_params['description']}' 失败: {str(e)}", "失败原因")
            raise
    
    
    @case_decorator(
        story="结算项批量处理",
        title="命中范围导入匹配",
        description="SETT_BATCH_AGGREGATION_LOCK_EVENT_SERVICE",
        severity="critical",
        order=1,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "SETT_BATCH_AGGREGATION_LOCK_EVENT_SERVICE"]
    )
    def test_import_batch_get_scope(self):
        """测试命中范围导入匹配"""
        
        sql="""
            select id,sett_item_code,sett_item_status from sett_item_tr
            where deleted=0
            and sett_item_status in ('RECONCILED','CREATED') order by created_at desc limit 3;
        """
        result=self.db.query(sql)
        sett_item_codes=[sett_item_code["sett_item_code"] for sett_item_code in result]
                 
        url=self.fin_path["结算项-结算批量锁定服务"]["path"]
        data=self.fin_params.get(url,{})
        data=ParamUtil.filter_post_body_fields(
            data,
            ["docType","operType","settItemCodes"],
            ["params","request"])
        set_dict={
            "docType":"SETT_ITEM",
            "operType":"CONFIRM",
            "settItemCodes":sett_item_codes
        }
        ParamUtil.set_request_params(data, set_dict)
        result=self.http.post(url, json=data, description=f"命中范围导入匹配")
        self.assert_util.assert_response_success(result)
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskCode",{}),"not_empty")
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("docType",{}),"=","SETT_ITEM")
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("operType",{}),"=",set_dict["operType"])
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskStatus",{}),"=","PENDING")
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("submitQty",{}),"=",len(set_dict["settItemCodes"]))
        a.json(data, "请求数据")
        a.json(result, "响应数据")
        
        
    @case_decorator(
        story="结算批量处理",
        title="根据ID查找数据服务",
        description="结算汇单记录-根据ID查找数据服务",
        severity="critical",
        order=2,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "SETT_AGGREGATE_RECORD_TR_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_sett_doc_by_id(self):
        """测试结算汇单记录-根据ID查找数据服务"""
        try:
            sql="""
                select id,task_code from sett_aggregate_record_tr where deleted=0 order by created_at desc limit 1;
            """
            task_id=self.db.query(sql)[0]["id"]
            task_code=self.db.query(sql)[0]["task_code"]
            url=self.fin_path["结算汇单记录-根据ID查找数据服务"]["path"]
            data=self.fin_params.get(url,{})
            data=ParamUtil.filter_post_body_fields(
                data,
                ["id"],
                ["params","request"])
            set_dict={"id":task_id}
            ParamUtil.set_request_params(data, set_dict)
            result=self.http.post(url, json=data, description=f"根据ID查找数据服务")
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskCode",{}),"=",task_code)
            a.json(data, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    
    @case_decorator(
        story="结算项批量处理",
        title="命中范围取消取消",
        description="验证SETT_BATCH_AGGREGATION_CANCEL_ASYNC_EVENT_SERVICE",
        severity="critical",
        order=1,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "SETT_BATCH_AGGREGATION_CANCEL_ASYNC_EVENT_SERVICE"]
    )
    def test_cancal_scope(self):
        """测试取消命中范围"""
        try:
            url = self.fin_path["结算项-批量任务取消-异步服务"]["path"]
            data = self.fin_params.get(url, {})
            data=ParamUtil.filter_post_body_fields(
                data, 
                ["docType","id","operType","taskCode","taskStatus"],
                ["params", "request"]
            )
        
            #获取最新的批量任务记录
            sql="""
                select id,task_code,task_status,doc_type,oper_type
                from sett_aggregate_record_tr where deleted=0 order by created_at desc limit 1;
            """
            task_info=self.db.query(sql)[0]
            task_code=task_info["task_code"]
            doc_type=task_info["doc_type"]
            oper_type=task_info["oper_type"]
            id=task_info["id"]
            task_status=task_info["task_status"]
            set_dict={
                "docType":doc_type,
                "id":id,
                "operType":oper_type,
                "taskCode":task_code,
                "taskStatus":task_status
            }
            ParamUtil.set_request_params(data, set_dict)
            result = self.http.post(url, json=data, description=f"取消命中范围")
            self.assert_util.assert_response_success(result)
            a.json(data, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
         
if __name__ == "__main__":
    # 运行参数化测试的示例
    test = TestSettItemBusiCheck()
    test.setup_class()
    test.test_find_sett_doc_by_id()
    #test.test_batch_get_scope(test.BATCH_GET_SCOPE_TEST_CASES[0])

        
        