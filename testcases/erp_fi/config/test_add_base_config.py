
import sys
from pathlib import Path

import allure

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from testcases.erp_fi import FiBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("基础财务")
@allure.feature("添加基础财务配置")
class TestAddBaseConfig(FiBaseTest):
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
    
    
    @case_decorator(
        story="基础财务配置",
        title="添加会计要素",
        description="测试添加会计要素配置",
        severity="critical",
        order=0,
        smoke=False,
        tags=["会计要素", "新增","FIN_GLM_AE_SUBMIT_EVENT_SERVICE"]
    )
    def test_add_accounting_elements(self):
        """新增会计要素用例"""
        try:
            url=self.get_api_path("会计要素表-提交服务")
            params,url=self.get_api_params(url)
            filtered_params=ParamUtil.filter_post_body_fields(
                params,
                ["accCodeStr","aeHeadCode","aeHeadName","finGlmAeItem",],
                ["params","request"]
            )
            set_dict={
                "aeHeadCode": f"AUTO-AE-CODE-{self.mock_util.get_timestamp(timestamp=True)}",
                "aeHeadName": f"AUTO-AE-NAME-{self.mock_util.get_timestamp(timestamp=True)}",
                "accCodeStr": "4-2-2-2",
                "finGlmAeItem": [
                    {
                        "accTypes":"损益",
                        "aeItemCode":f"AUTO-AE-ITEM1-CODE-{self.mock_util.get_timestamp(timestamp=True)}",
                        "balDirec":"DEBIT",
                        "eqFormDirection":"LEFT",
                        "isIncome":True,
                    },
                    {
                        "accTypes":"资产",
                        "aeItemCode":f"AUTO-AE-ITEM2-CODE-{self.mock_util.get_timestamp(timestamp=True)}",
                        "balDirec":"DEBIT",
                        "eqFormDirection":"LEFT",
                        "isIncome":False,
                    },
                    {
                        "accTypes":"负债",
                        "aeItemCode":f"AUTO-AE-ITEM3-CODE-{self.mock_util.get_timestamp(timestamp=True)}",
                        "balDirec":"CREDIT",
                        "eqFormDirection":"RIGHT",
                        "isIncome":False,
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response, _ = self.standard_api_call(
                api_key="会计要素表-提交服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="基础财务配置",
        title="启用会计要素",
        description="测试启用会计要素配置",
        severity="critical",
        order=1,
        smoke=False,
        tags=["会计要素", "启用","FIN_GLM_AE_HEAD_ENABLE_EVENT_SERVICE"]
    )
    def test_enable_accounting_elements(self):
        """启用会计要素用例"""
        try:
            url=self.get_api_path("会计要素头表-启用服务")
            params,url=self.get_api_params(url)
            filtered_params=ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params","request"]
            )
            sql="""
            select id from fin_glm_ae_head_cf where deleted=0 order by created_at desc limit 1;
            """
            id=self.query_service.query(sql)[0]["id"]
            set_dict={
                "id":id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response, _ = self.standard_api_call(
                api_key="会计要素头表-启用服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="基础财务配置",
        title="添加会计政策",
        description="测试添加会计政策配置",
        severity="critical",
        order=2,
        smoke=False,
        tags=["会计政策", "新增","FIN_GLM_AP_TYPE_CF_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_add_accounting_policy(self):
        """新增会计政策用例"""
        try:
            url=self.get_api_path("会计政策-保存主数据服务")
            params,url=self.get_api_params(url)
            filtered_params=ParamUtil.filter_post_body_fields(
                params,
                ["apTypeCode","apTypeName","currId","genCalendarHeadId","genCurrRateTypeId","aeHead"],
                ["params","request"]
            )
            sql="""
            select id from gen_curr_type_cf where curr_code='CNY' and deleted=0;
            """
            curr_id=self.query_service.query(sql)[0]["id"]
            
            sql="""
            select id from fin_common_calendar_head_cf where calendar_name='勿删勿改-标准会计期间';
            """
            gen_calendar_head_id=self.query_service.query(sql)[0]["id"]
            
            sql="""
            select id from gen_curr_exchange_rate_type_cf where type_code='HR';
            """
            gen_curr_rate_type_id=self.query_service.query(sql)[0]["id"]
            
            sql="""
            select id from fin_glm_ae_head_cf where deleted=0 order by created_at desc limit 1;
            """
            ae_head_id=self.query_service.query(sql)[0]["id"]
            
            set_dict={
                "apTypeCode":f"AUTO-AP-CODE-{self.mock_util.get_timestamp(timestamp=True)}",
                "apTypeName":f"AUTO-AP-NAME-{self.mock_util.get_timestamp(timestamp=True)}",
                "currId":{
                    "id":curr_id
                },
                "genCalendarHeadId":{
                    "id":gen_calendar_head_id
                },
                "genCurrRateTypeId":{
                    "id":gen_curr_rate_type_id
                },
                "aeHead":{
                    "id":ae_head_id
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response, _ = self.standard_api_call(
                api_key="会计政策-保存主数据服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise



    @case_decorator(
        story="基础财务配置",
        title="启用会计政策",
        description="测试启用会计政策配置",
        severity="critical",
        order=3,
        smoke=False,
        tags=["会计政策", "启用","FIN_GLM_AP_TYPE_CF_ENABLE_EVENT_SERVICE"]
    )
    def test_enable_accounting_policy(self):
        """启用会计政策用例"""
        try:
            url=self.get_api_path("FIN-会计政策-启用服务")
            params,url=self.get_api_params(url)
            filtered_params=ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params","request"]
            )
            sql="""
            select id from fin_glm_ap_type_cf where deleted=0 order by created_at desc limit 1;
            """
            id=self.query_service.query(sql)[0]["id"]
            set_dict={
                "id":id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response, _ = self.standard_api_call(
                api_key="FIN-会计政策-启用服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
if __name__ == "__main__":
    test = TestAddBaseConfig()
    test.setup_class()
    test.test_add_accounting_elements()
    test.test_enable_accounting_elements()
    test.test_add_accounting_policy()
    test.test_enable_accounting_policy()
