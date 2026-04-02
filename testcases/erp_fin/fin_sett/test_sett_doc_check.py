import pytest
import allure

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettDocCheck(FinBaseTest):
    """结算单测试用例"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("结算单测试类初始化完成")  
        
    @case_decorator(
        story="结算单管理",
        title="测试查询结算单详情",
        description="测试查询结算单详情",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算单管理", "查询结算单详情","SETT_DOC_TR_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_search_detail(self):
        """测试查询结算单详情"""
        try:
            api_path = self.get_api_path("结算单表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            filtered_data = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
            filtered_data["params"]["request"]["id"] = self.create_settlement_doc("E_SLS_GOODS")
            result, _ = self.standard_api_call(
                api_key="结算单表-根据ID查找数据服务",
                set_dict=filtered_data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            a.json(filtered_data, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    @case_decorator(
        story="结算单条件查询",
        title="测试条件查询结算单分页数据",
        description="验证条件查询结算单分页数据功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["结算单管理", "条件查询", "SETT_ITEM_TR_PAGING_DATA_SERVICE"]
    )
    def test_sett_doc_paging_data(self):
        """测试条件查询结算单分页数据"""
        try:
            api_path = self.get_api_path("结算项表-分页数据服务")
            params, url = self.get_api_params(api_path)
            # TODO: 实现分页查询逻辑
            a.json(params, "请求数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        
        
if __name__ == "__main__":
    test = TestSettDocCheck()
    test.setup_class()
    test.test_search_detail()
