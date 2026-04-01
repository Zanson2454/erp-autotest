import pytest
import allure
from testcases.scm_sls import SlsBase
from utils.report_util import a, case_decorator
from utils.param_util import ParamUtil

@allure.epic("销售管理")
@allure.feature("销售订单-组织详情")
class TestSoOrgQuery(SlsBase):
    
    @classmethod
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
             
        # 初始化订单配置数据
        if cls.init_data:
            cls.curr_id = cls.init_data.get("currency_info",[])[0].get("curr_id")
            cls.coun_id = cls.init_data.get("country_info",[])[0].get("coun_id")
            cls.exchange_rate_type_id = cls.init_data.get("exchange_rate_type_info",[])[0].get("exchange_rate_type_id")
        # 初始化MD
        if cls.md_cache_data:
            cls.cust_id = cls.md_cache_data.get("partner_info",{}).get("cust_info",[])[0].get("cust_id")
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.sls_dc_id = cls.md_cache_data.get("org_info",{}).get("sls_dc_md",[])[0].get("id")
            cls.sls_org_id = cls.md_cache_data.get("org_info",{}).get("sls_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
            cls.inv_loc_id = cls.md_cache_data.get("org_info",{}).get("inv_loc_info",[])[0].get("id")
            
            
    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-按组织id查询组织详情服务",
        description="验证SO_ORG_QUERY_EVENT_SERVICE接口",
        severity="critical",
        order=200,
        tags=["销售订单", "组织详情", "SO_ORG_QUERY_EVENT_SERVICE"]
    )
    def test_so_org_query_event_service(self):
        """SLS-销售订单-按组织id查询组织详情服务"""
        try:
            api_path = self.get_api_path("SLS-销售订单-按组织id查询组织详情服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "params"], ["params"]
            )
            set_dict = {
                "id": self.sls_org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response = self.http.post(url, json=params)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
            # 可根据实际返回结构补充断言
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
