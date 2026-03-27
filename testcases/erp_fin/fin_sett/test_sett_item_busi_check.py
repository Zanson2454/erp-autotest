import pytest
import sys
import allure
from pathlib import Path
import time

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from testcases.erp_fin import FinBaseTest
from utils.log_util import Loggers
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettItemBusiCheck(FinBaseTest):
    """结算管理业务检查测试用例"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("结算管理业务检查测试类初始化完成")  
    
    
    def get_sett_item_id(self):
        """获取不同状态的结算项ID 已创建，已对账，已汇单 """
        #已创建结算项
        created_sett_item_id=self.create_settlement_item("E_SLS_GOODS")
        #已对账结算项
        reconciled_sett_item_id=self.create_settlement_item("E_SLS_GOODS")
        self.db.update("sett_item_tr", {"sett_item_status":"RECONCILED"}, f"id={reconciled_sett_item_id}")
        #已汇单结算项
        self.create_settlement_doc("E_SLS_GOODS")
        sql="""
        select id from sett_item_tr where deleted=0 and sett_item_status='SETT_DOC_CREATED' order by created_at desc limit 1;
        """
        sett_doc_created_sett_item_id=self.db.query(sql)[0]["id"]
        
        return [created_sett_item_id, sett_doc_created_sett_item_id,reconciled_sett_item_id]
    
    @case_decorator(
        story="结算项批量处理",
        title="结算项对账确认",
        description="验证结算项对账确认",
        severity="critical",
        order=1,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "结算项对账确认"]
    )
    def test_sett_item_record(self):
        """测试结算项对账确认"""
        try:
            # 获取结算项ID列表
            sett_item_ids = self.get_sett_item_id()
            
            # 遍历每个ID进行测试
            for index, sett_item_id in enumerate(sett_item_ids):
                api_path = self.get_api_path("SETT-ITEM-结算项确认及汇单-关联操作-异步服务")
                params, url = self.get_api_params(api_path)
                data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                data=ParamUtil.convert_param_type(data, ["params", "request"], "array")
                data["params"]["request"][0]["id"] = sett_item_id
                result, _ = self.standard_api_call(
                    api_key="SETT-ITEM-结算项确认及汇单-关联操作-异步服务",
                    set_dict=data.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                #等待异步任务执行完成，当状态为PROCESSING时一直等待，最长超时10秒
                start_time = time.time()
                timeout = 10
                while True:
                    sql = f"""
                        select id, sett_item_status, async_execution_status, sett_doc_id
                        from sett_item_tr where deleted=0
                        and id={sett_item_id} limit 1;
                    """
                    sql_result = self.db.query(sql)
                    if sql_result and sql_result[0].get("async_execution_status") != "PROCESSING":
                        break
                    if time.time() - start_time >= timeout:
                        raise TimeoutError(f"等待异步任务执行超时（{timeout}秒）")
                    time.sleep(0.5)
                
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
                a.json(data, f"请求数据 - ID: {sett_item_id}")
                a.json(result, f"响应数据 - ID: {sett_item_id}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="结算项批量处理",
        title="批量手工汇单",
        description="验证结算项手工汇单",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "结算项手工汇单"]
    )
    def test_sett_item_manual_remittance(self):
        """测试结算项手工汇单"""
        try:
            api_path = self.get_api_path("SETT-ITEM-结算项手工汇单-关联操作-异步服务")
            params, url = self.get_api_params(api_path)
            sett_item_ids = self.get_sett_item_id()
            for index, sett_item_id in enumerate(sett_item_ids):
                data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                data=ParamUtil.convert_param_type(data, ["params", "request"], "array")
                data["params"]["request"][0]["id"] = sett_item_id
                result, _ = self.standard_api_call(
                    api_key="SETT-ITEM-结算项手工汇单-关联操作-异步服务",
                    set_dict=data.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                #等待异步任务执行完成，当状态为PROCESSING时一直等待，最长超时10秒
                start_time = time.time()
                timeout = 10
                while True:
                    sql = f"""
                        select id, sett_item_status, async_execution_status, sett_doc_id
                        from sett_item_tr where deleted=0
                        and id={sett_item_id} limit 1;
                    """
                    sql_result = self.db.query(sql)
                    if sql_result and sql_result[0].get("async_execution_status") != "PROCESSING":
                        break
                    if time.time() - start_time >= timeout:
                        raise TimeoutError(f"等待异步任务执行超时（{timeout}秒）")
                    time.sleep(0.5)
                if index == 0 or index == 1:  # 第1.3个ID的断言 已创建、已汇单结算项不可以手工汇单
                    assert result.get("success",{}) == False
                    #assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                elif index == 2:  # 第2个ID的断言 已对账结算项可以手工汇单
                    self.assert_util.assert_response_success(result)
                    self.assert_util.assert_by_operator(sql_result[0]["sett_item_status"], "=", "SETT_DOC_CREATED")
                    self.assert_util.assert_by_operator(sql_result[0]["async_execution_status"], "=", "SUCCEEDED")
                    self.assert_util.assert_by_operator(sql_result[0]["sett_doc_id"], "not_empty")
                a.json(data, f"请求数据 - ID: {sett_item_id}")
                a.json(result, f"响应数据 - ID: {sett_item_id}")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
                
    def test_batch_task_record(self):
        """批量任务记录"""
        try:
            api_path = self.get_api_path("结算汇单记录-分页数据服务_PmHKWs1")
            params, url = self.get_api_params(api_path)
            filter_data = ParamUtil.filter_post_body_fields(params, ["pageNo","pageSize","conditionItems","sortOrders"],["params","request","pageable"])
            filter_data["params"]["request"]["pageable"]["pageNo"] = "1"
            filter_data["params"]["request"]["pageable"]["pageSize"] = "20"
            filter_data["params"]["request"]["pageable"]["conditionItems"] =None
            filter_data["params"]["request"]["pageable"]["sortOrders"] = None
            result, _ = self.standard_api_call(
                api_key="结算汇单记录-分页数据服务_PmHKWs1",
                set_dict=filter_data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            assert result.get("data",{}).get("data",{}).get("total",{}) >= 0
            a.json(filter_data, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    
    
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
        order=7,
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
            api_path = self.get_api_path("结算项-结算批量锁定服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(
                params, 
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
            
            result, _ = self.standard_api_call(
                api_key="结算项-结算批量锁定服务",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            
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
        order=8,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "SETT_BATCH_AGGREGATION_LOCK_EVENT_SERVICE"]
    )
    def test_import_batch_get_scope(self):
        """测试命中范围导入匹配"""
        try:
            sql="""
                select id,sett_item_code,sett_item_status from sett_item_tr
                where deleted=0
                and sett_item_status in ('RECONCILED','CREATED') order by created_at desc limit 3;
            """
            result=self.db.query(sql)
            sett_item_codes=[sett_item_code["sett_item_code"] for sett_item_code in result]
                     
            api_path = self.get_api_path("结算项-结算批量锁定服务")
            params, url = self.get_api_params(api_path)
            data=ParamUtil.filter_post_body_fields(
                params,
                ["docType","operType","settItemCodes"],
                ["params","request"])
            set_dict={
                "docType":"SETT_ITEM",
                "operType":"CONFIRM",
                "settItemCodes":sett_item_codes
            }
            ParamUtil.set_request_params(data, set_dict)
            result, _ = self.standard_api_call(
                api_key="结算项-结算批量锁定服务",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskCode",{}),"not_empty")
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("docType",{}),"=","SETT_ITEM")
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("operType",{}),"=",set_dict["operType"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("taskStatus",{}),"=","PENDING")
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("submitQty",{}),"=",len(set_dict["settItemCodes"]))
            a.json(data, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        
    @case_decorator(
        story="结算批量处理",
        title="根据ID查找数据服务",
        description="结算汇单记录-根据ID查找数据服务",
        severity="critical",
        order=9,
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
            api_path = self.get_api_path("结算汇单记录-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            data=ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params","request"])
            set_dict={"id":task_id}
            ParamUtil.set_request_params(data, set_dict)
            result, _ = self.standard_api_call(
                api_key="结算汇单记录-根据ID查找数据服务",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
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
        order=10,
        smoke=False,
        tags=["结算管理", "结算项批量任务处理", "SETT_BATCH_AGGREGATION_CANCEL_ASYNC_EVENT_SERVICE"]
    )
    def test_cancal_scope(self):
        """测试取消命中范围"""
        try:
            api_path = self.get_api_path("结算项-批量任务取消-异步服务")
            params_base, url = self.get_api_params(api_path)
            
            #获取最新的批量任务记录（2条）
            sql="""
                select id,task_code,task_status,doc_type,oper_type
                from sett_aggregate_record_tr where deleted=0 order by created_at desc limit 2;
            """
            task_list = self.db.query(sql)
            
            # 遍历每条数据执行测试
            for index, task_info in enumerate(task_list):
                data = ParamUtil.filter_post_body_fields(
                    params_base, 
                    ["docType","id","operType","taskCode","taskStatus"],
                    ["params", "request"]
                )
                
                task_code = task_info["task_code"]
                doc_type = task_info["doc_type"]
                oper_type = task_info["oper_type"]
                task_id = task_info["id"]
                task_status = task_info["task_status"]
                
                set_dict = {
                    "docType": doc_type,
                    "id": task_id,
                    "operType": oper_type,
                    "taskCode": task_code,
                    "taskStatus": task_status
                }
                ParamUtil.set_request_params(data, set_dict)
                result, _ = self.standard_api_call(
                    api_key="结算项-批量任务取消-异步服务",
                    set_dict=data.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                
                # 相同的断言逻辑
                self.assert_util.assert_response_success(result)
                a.json(data, f"请求数据 - 第{index+1}条")
                a.json(result, f"响应数据 - 第{index+1}条")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
     
         
if __name__ == "__main__":
    # 运行参数化测试的示例
    test = TestSettItemBusiCheck()
    test.setup_class()
    #test.test_batch_get_scope(test.BATCH_GET_SCOPE_TEST_CASES[0])

        
        
