
import allure

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettItemCheck(FinBaseTest):
    """结算项测试用例"""
    sett_item_code_result = None
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("结算项测试类初始化完成")  

    @case_decorator(
        story="结算项管理",
        title="测试查询结算项详情",
        description="测试查询结算项详情",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算项管理", "查询结算项详情","SETT_ITEM_TR_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_search_detail(self):
        """测试查询结算项详情"""
        try:
            request_id = self.query_service.get_latest_sett_item_id()
            if not request_id:
                self.create_settlement_item("E_SLS_GOODS")
                request_id = self.query_service.get_latest_sett_item_id()
            
            api_path = self.get_api_path("结算项表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            params["params"]["request"]["id"] = request_id
            self.logger.debug(f"查询结算项详情请求参数: {params}")

            result, _ = self.standard_api_call(
                api_key="结算项表-根据ID查找数据服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            
            assert result.get("data").get("data").get("id") == request_id
            self.assert_util.assert_response_success(result)
            a.json(params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="结算项管理",
        title="测试获取结算项编码",
        description="测试获取结算项编码",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算项管理", "获取结算项编码","SETT_ITEM_TR_CODE_SERVICE"]
    )
    def test_get_sett_item_code(self):
        """测试获取结算项编码"""
        try:
            api_path = self.get_api_path("结算项表-调用取号规则服务")
            params, url = self.get_api_params(api_path)
            params["params"]["request"]["ruleKey"] = "ERP_FIN$sett_item_tr_code"
            params["params"]["modelKey"] = "ERP_FIN$sett_item_tr"
            self.logger.debug(f"获取结算项编码请求参数: {params}")
            
            result, _ = self.standard_api_call(
                api_key="结算项表-调用取号规则服务",
                set_dict=params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            assert result.get("data").get("data")
            assert "SETTI" in result.get("data").get("data")
            self.logger.debug(f"获取结算项编码响应数据: {result}")
            self.sett_item_code_result = result.get("data").get("data")
            a.json(params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="结算项管理",
        title="测试新增结算项",
        description="测试新增结算项",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算项管理", "新增结算项","SETT-ITEM-手动创建服务"]
    )
    def test_add_sett_item(self):
        """测试新增结算项"""
        try:
            self.create_settlement_item("E_SLS_GOODS")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
   
    @case_decorator(
        story="结算项管理",
        title="测试删除结算项",
        description="测试删除结算项",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算项管理", "删除结算项","SETT-ITEM-删除服务"]
    )
    def test_delete_sett_item(self):
        """测试删除结算项"""
        try:
            api_path = self.get_api_path("结算项-删除服务")
            params, url = self.get_api_params(api_path)
            
            request_id = self.query_service.get_latest_sett_item_id_by_status("CREATED")
            if not request_id:
                self.create_settlement_item("E_SLS_GOODS")
                request_id = self.query_service.get_latest_sett_item_id_by_status("CREATED")
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params","request"])
            set_dict = {"id": request_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            result, _ = self.standard_api_call(
                api_key="结算项-删除服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            after_item = self.query_service.get_sett_item_by_id(request_id)
            assert (not after_item) or after_item.get("deleted") != 0
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="结算项管理",
        title="测试查询结算项分页数据",
        description="测试查询结算项分页数据",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算项管理", "查询结算项分页数据","SETT_ITEM_TR_PAGING_DATA_SERVICE"]
    )
    def test_sett_item_paging_data(self):
        """测试结算项分页数据"""
        try:
            api_path = self.get_api_path("结算项表-分页数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params","request","pageable"])
            filtered_params["params"]["request"]["pageable"]["pageNo"] = 1
            filtered_params["params"]["request"]["pageable"]["pageSize"] = 200
            
            result, _ = self.standard_api_call(
                api_key="结算项表-分页数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(result)
            assert result.get("data").get("data").get("total") >= 0
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        

if __name__ == "__main__":
    test = TestSettItemCheck()
    test.setup_class()
    test.test_add_sett_item()
