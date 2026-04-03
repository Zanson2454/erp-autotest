import sys
from pathlib import Path

import allure

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售订单-组织详情")
class TestSoOrgQuery(SlsBase):
    
    @classmethod
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 初始化订单配置数据
        if cls.init_data:
            currency_info = cls.init_data.get("currency_info") or []
            if currency_info:
                cls.curr_id = currency_info[0].get("curr_id")
            else:
                # 默认货币ID（人民币 CNY）
                cls.curr_id = 2000001
            
            country_info = cls.init_data.get("country_info") or []
            if country_info:
                cls.coun_id = country_info[0].get("coun_id")
            else:
                cls.coun_id = None
            
            exchange_rate_type_info = cls.init_data.get("exchange_rate_type_info") or []
            if exchange_rate_type_info:
                cls.exchange_rate_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
            else:
                cls.exchange_rate_type_id = None
        else:
            # 当 init_data 为空时，设置默认值
            cls.curr_id = 2000001  # 默认货币ID（人民币 CNY）
            cls.coun_id = None
            cls.exchange_rate_type_id = None
        # 初始化MD
        if cls.md_cache_data:
            partner_info = cls.md_cache_data.get("partner_info") or {}
            cust_info = partner_info.get("cust_info") or []
            if cust_info:
                cls.cust_id = cust_info[0].get("cust_id") or cust_info[0].get("id")
            
            org_info = cls.md_cache_data.get("org_info") or {}
            gr_come_org_info = org_info.get("gr_come_org_info") or []
            if gr_come_org_info:
                cls.com_org_id = gr_come_org_info[0].get("id")
            
            sls_dc_md = org_info.get("sls_dc_md") or []
            if sls_dc_md:
                cls.sls_dc_id = sls_dc_md[0].get("id")
            
            sls_org_info = org_info.get("sls_org_info") or []
            if sls_org_info:
                cls.sls_org_id = sls_org_info[0].get("id")
            
            inv_org_info = org_info.get("inv_org_info") or []
            if inv_org_info:
                cls.inv_org_id = inv_org_info[0].get("id")
            
            inv_loc_info = org_info.get("inv_loc_info") or []
            if inv_loc_info:
                cls.inv_loc_id = inv_loc_info[0].get("id")
            
            
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
            response, _ = self.standard_api_call(
                api_key="SLS-销售订单-按组织id查询组织详情服务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
            # 可根据实际返回结构补充断言
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
