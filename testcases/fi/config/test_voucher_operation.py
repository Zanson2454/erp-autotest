
import allure
import pytest
from typing import Any
import pytest
import os
import sys
import allure
from pathlib import Path

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
from testcases.fi import FiBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("基础财务")
@allure.feature("总账凭证操作")
class TestVoucherOperation(FiBaseTest):
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
     
    def get_ve_base_info(self):
        """获取新增凭证的基础信息部分"""
        try:
            #获取预制的自动化测试的核算账簿、核酸组织,默认凭证类型
            sql="""
                select id,as_org,vt_type,coa_type from fin_glm_ab_type_cf where deleted=0 and ab_type_code like '%AUTO-TEST%' order by created_at desc limit 1;
            """
            ab_type_id,as_org_id,vt_type,coa_type=self.db.query(sql)[0]["id"],self.db.query(sql)[0]["as_org"],self.db.query(sql)[0]["vt_type"],self.db.query(sql)[0]["coa_type"]
            ve_date=self.mock_util.get_timestamp(timestamp=True)
            #获取新增凭证的凭证号、会计期间id
            url=self.get_api_path("总账-凭证-获取凭证号服务")
            params,url=self.get_api_params(url)
            filtered_params=ParamUtil.filter_post_body_fields(
                params,
                ["abType","voEntryDate","vtTypeId"],
                ["params","request"]
            )
            set_dict={
                "abType":{
                    "id":ab_type_id
                },
                "voEntryDate":ve_date,
                "vtTypeId":{
                    "id":vt_type
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response=self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            calendarItemId=response["data"]["data"]["calendarItemId"]
            vouchNumber=response["data"]["data"]["vouchNumber"]
            return calendarItemId,vouchNumber,ab_type_id,vt_type,ve_date,as_org_id,coa_type
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="总账凭证操作",
        title="新增总账凭证",
        description="测试新增总账凭证",
        severity="critical",
        order=0,
        smoke=False,
        tags=["凭证录入","保存","FIN_GLM_VE_SAVE_EVENT_SERVICE"]
    )
    def test_add_voucher(self):
        """新增总账保存凭证用例"""
        try:
            url=self.get_api_path("总账-凭证-凭证暂存服务")
            params,url=self.get_api_params(url)
            calendarItemId,vouchNumber,ab_type_id,vt_type,ve_date,as_org_id,coa_type=self.get_ve_base_info()
            sql="""
            select id from gen_curr_type_cf where deleted=0 and curr_code='CNY'
            """
            curr_id=self.db.query(sql)[0]["id"]
            sql="""
            select id from gen_curr_exchange_rate_type_cf where deleted=0 and type_code='HR' order by created_at desc limit 1;
            """
            rt_type_id=self.db.query(sql)[0]["id"]
            
            sql=f"""
            select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf where coa_type={coa_type} and leaf=1;
            """
            aa_head_ids=self.db.query(sql)
            aa_head_ids=[aa_head_id["id"] for aa_head_id in aa_head_ids]
            
            filtered_params=ParamUtil.filter_post_body_fields(
                params,
                ["abType","asOrgId","bizDate","calendarItemId","createType","veItems","voEntryDate","vouchNumber","vtTypeId","whetherAdPeriodVe"],
                ["params","request"]
            )
            set_dict={
                "abType":{
                    "id":ab_type_id
                },
                "asOrgId":{
                    "id":as_org_id
                },
                "bizDate":ve_date // 1000 * 1000,
                "calendarItemId":calendarItemId,
                "createType":"MANUAL",
                "voEntryDate":ve_date,
                "vouchNumber":vouchNumber,
                "vtTypeId":{
                    "id":vt_type
                },
                "whetherAdPeriodVe":False,
                "veItems":[
                    {
                        "aaHeadId":{
                            "id":aa_head_ids[0]
                        },
                        "currId":{
                            "id":curr_id
                        },
                        "debitAmt":123.45,
                        "exRate":1,
                        "origCurrAmt":123.45,
                        "veItemDescr":"摘要",
                        "rtType":{
                            "id":rt_type_id
                        }
                    },
                    {
                        "aaHeadId":{
                            "id":aa_head_ids[1]
                        },
                        "currId":{
                            "id":curr_id
                        },
                        "creditAmt":123.45,
                        "exRate":1,
                        "origCurrAmt":123.45,
                        "veItemDescr":"摘要",
                        "rtType":{
                            "id":rt_type_id
                        }
                    }
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            response=self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test=TestVoucherOperation()
    test.setup_class()
    test.test_add_voucher()