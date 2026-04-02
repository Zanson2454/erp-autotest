import pytest
import allure
import time

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettDocAssoc(FinBaseTest):
    """结算单关联配置测试用例"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("结算管理业务检查测试类初始化完成")
        cls.db.update("sett_doc_assoc_doc_type_cf", 
                       {"accounting_mode": "INVOICE_BASED","auto_confirm":True,"auto_post":True}, 
                       f"company_organization='{cls.com_org_id_2}' and settlement_type='{cls.sett_doc_type_info}' and deleted=0")
    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        cls.db.update("sett_doc_assoc_doc_type_cf", 
                       {"accounting_mode": "RECEIVABLE_BASED","auto_confirm":False,"auto_post":False}, 
                       f"company_organization='{cls.com_org_id_2}' and settlement_type='{cls.sett_doc_type_info}' and deleted=0")
    @case_decorator(
        story="结算项管理",
        title="测试结算项汇单（发票立账）",
        description="测试发票立账和结算项的汇单功能",
        severity="critical",
        order=1,
        smoke=False,
        tags=["结算项管理", "结算项汇单","SETT_ITEM_CONFIRM_AND_REMAINTTANCE_ASSOCIATE_ASYNC_EVENT_SERVICE"]
    )
    def test_sett_item_remittance(self):
        """测试结算项汇单（发票立账）"""
        try:
            sett_item_id = self.create_settlement_item("E_SLS_GOODS",org=2)
            api_path = self.get_api_path("SETT-ITEM-结算项确认及汇单-关联操作-异步服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
            data = ParamUtil.convert_param_type(data, ["params", "request"], "array")
            data["params"]["request"][0]["id"] = sett_item_id
            result, _ = self.standard_api_call(
                api_key="SETT-ITEM-结算项确认及汇单-关联操作-异步服务",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_by_operator(result.get("success", {}), "=", False)
            self.assert_util.assert_by_operator(result.get("err", {}).get("code", {}), "=", "sett.item.tr.batch.account.mode.has.invoice")
            self.assert_util.assert_by_operator(result.get("err", {}).get("msg", {}), "=", "该批量操作不允许有发票立账模式的结算项")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="结算项管理",
        title="测试结算项汇单（应收立账）",
        description="测试结算单自动确认和自动过账功能",
        severity="critical",
        order=3,
        smoke=False,
        tags=["结算项管理", "结算项汇单","SETT_ITEM_CONFIRM_AND_REMAINTTANCE_ASSOCIATE_ASYNC_EVENT_SERVICE"]
    )
    def test_sett_auto_confirm_and_post(self):
        """测试结算单自动确认和自动过账"""
        try:
            self.db.update("sett_doc_assoc_doc_type_cf", 
                       {"accounting_mode": "RECEIVABLE_BASED"}, 
                       f"company_organization='{self.com_org_id_2}' and settlement_type='{self.sett_doc_type_info}' and deleted=0")
            sett_item_id = self.create_settlement_item("E_SLS_GOODS",org=2)
            api_path = self.get_api_path("SETT-ITEM-结算项确认及汇单-关联操作-异步服务")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
            data = ParamUtil.convert_param_type(data, ["params", "request"], "array")
            data["params"]["request"][0]["id"] = sett_item_id
            result, _ = self.standard_api_call(
                api_key="SETT-ITEM-结算项确认及汇单-关联操作-异步服务",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            time.sleep(15)
            #查询生成的结算单是否自动生成了应收应付
            sett_doc_row = self.query_service.get_sett_doc_status_by_sett_item_id(sett_item_id)
            if not sett_doc_row:
                raise ValueError(f"结算单自动确认和自动过账失败: 未找到结算单ID {sett_item_id}")
            self.assert_util.assert_by_operator(sett_doc_row["sett_doc_status"], "=", "CONFIRMED")
            self.assert_util.assert_by_operator(sett_doc_row["trading_doc_id"], "!=", None)
            trading_doc_id = sett_doc_row["trading_doc_id"]
            #查询应收单是否自动过账完成
            ar_row = self.query_service.get_ar_head_by_id(trading_doc_id)
            if not ar_row:
                raise ValueError(f"结算单自动确认和自动过账失败: 未找到应收单ID {trading_doc_id}")
            self.assert_util.assert_by_operator(ar_row["ar_status"], "=", "DONE")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    @case_decorator(
        story="结算项管理",
        title="测试结算项开票功能",
        description="测试结算项开票功能",
        severity="critical",
        order=2,
        smoke=False,
        tags=["结算项管理", "结算项开票",""]
    )
    def test_sett_item_billing(self):
        """测试结算项开票功能"""
        try:
            sett_item_id = self.create_settlement_item("E_SLS_GOODS",org=2)
            #执行结算项-批量转换销售发票校验服务
            api_path = self.get_api_path("结算项-批量转换销售发票校验")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["ids"], ["params", "request"])
            data["params"]["request"]["ids"] = [sett_item_id]
            result, _ = self.standard_api_call(
                api_key="结算项-批量转换销售发票校验",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            #执行结算项-批量转换销售发票服务
            api_path = self.get_api_path("结算项批量转化销售发票")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["ids"], ["params", "request"])
            data["params"]["request"]["ids"] = [sett_item_id]
            result, _ = self.standard_api_call(
                api_key="结算项批量转化销售发票",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            #执行销售发票-保存业务单据记录服务
            api_path = self.get_api_path("销售发票-结算创建保存并更新来源")
            params, url = self.get_api_params(api_path)
            data = ParamUtil.filter_post_body_fields(params, ["request"], ["params"])
            # 将转换销售发票服务的结果作为保存的参数
            convert_result_data = result.get("data", {}).get("data", {})
            if not convert_result_data:
                raise ValueError("转换销售发票服务返回数据为空")
            data["params"]["request"] = convert_result_data
            data["params"]["request"]["docTypeId"] = {"id": self.sb_type_info}
            data["params"]["request"]["posNeg"] = "BLUE"
            data["params"]["request"]["bilCode"] = f"SB_{self.mock_util.get_timestamp(timestamp=True)}"
            
            save_result, _ = self.standard_api_call(
                api_key="销售发票-结算创建保存并更新来源",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(save_result)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
if __name__ == "__main__":
    test = TestSettDocAssoc()
    test.setup_class()
    test.test_sett_item_billing()
    test.teardown_class()
