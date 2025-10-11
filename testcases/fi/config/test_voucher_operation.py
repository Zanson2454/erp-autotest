
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
        
    def create_voucher_with_amounts(self, debit_amt, credit_amt, remark):
        """创建指定借贷金额的凭证"""
        url = self.get_api_path("总账-凭证-凭证暂存服务")
        params, url = self.get_api_params(url)
        calendarItemId, vouchNumber, ab_type_id, vt_type, ve_date, as_org_id, coa_type = self.get_ve_base_info()
    
        # 获取货币和汇率类型
        sql = "select id from gen_curr_type_cf where deleted=0 and curr_code='CNY'"
        curr_id = self.db.query(sql)[0]["id"]
    
        sql = "select id from gen_curr_exchange_rate_type_cf where deleted=0 and type_code='HR' order by created_at desc limit 1;"
        rt_type_id = self.db.query(sql)[0]["id"]
    
        # 获取科目
        sql = f"select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf where coa_type={coa_type} and leaf=1;"
        aa_head_ids = self.db.query(sql)
        aa_head_ids = [aa_head_id["id"] for aa_head_id in aa_head_ids]
    
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            ["abType","asOrgId","bizDate","calendarItemId","createType","veItems","voEntryDate","vouchNumber","vtTypeId","whetherAdPeriodVe"],
            ["params","request"]
        )
    
        set_dict = {
            "abType": {"id": ab_type_id},
            "asOrgId": {"id": as_org_id},
            "remark": remark,
            "bizDate": ve_date // 1000 * 1000,
            "calendarItemId": calendarItemId,
            "createType": "MANUAL",
            "voEntryDate": ve_date,
            "vouchNumber": vouchNumber,
            "vtTypeId": {"id": vt_type},
            "whetherAdPeriodVe": False,
            "veItems": [
                {
                    "aaHeadId": {"id": aa_head_ids[0]},
                    "currId": {"id": curr_id},
                    "debitAmt": debit_amt,
                    "exRate": 1,
                    "origCurrAmt": debit_amt,
                    "veItemDescr": "摘要",
                    "rtType": {"id": rt_type_id}
                },
                {
                    "aaHeadId": {"id": aa_head_ids[1]},
                    "currId": {"id": curr_id},
                    "creditAmt": credit_amt,
                    "exRate": 1,
                    "origCurrAmt": credit_amt,
                    "veItemDescr": "摘要",
                    "rtType": {"id": rt_type_id}
                }
            ]
        }
    
        ParamUtil.set_request_params(filtered_params, set_dict)
        response = self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, f"创建凭证请求数据-{remark}")
        a.json(response, f"创建凭证响应数据-{remark}")   
    
    @case_decorator(
        story="总账凭证操作",
        title="新增总账凭证",
        description="测试新增总账凭证",
        severity="critical",
        order=1,
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
                "remark":"测试正常业务流程",
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
        
    @case_decorator(
        story="总账凭证操作",
        title="提交凭证",
        description="测试总账凭证提交操作",
        severity="critical",
        order=2,
        smoke=False,
        tags=["凭证录入","提交","FIN_GLM_VE_SUBMIT_BY_ID_EVENT_SERVICE"]
    )
    @pytest.mark.parametrize("test_data", [
        {
            "name": "正常借贷平衡",
            "debit_amt": 123.45,
            "credit_amt": 123.45,
            "remark": "测试正常业务流程",
            "expected_status": "APPROVING"
        },
        {
            "name": "借贷金额不平衡",
            "debit_amt": 100.00,
            "credit_amt": 200.00,
            "remark": "测试借贷不平衡业务流程",
            "expected_status": "DRAFT"  # 预期提交失败，保持草稿状态
        }
    ])
    def test_submit_voucher(self, test_data):
        """测试总账凭证提交操作"""
        # 首先创建凭证
        self.create_voucher_with_amounts(
            test_data["debit_amt"], 
            test_data["credit_amt"], 
            test_data["remark"]
        )
        url=self.get_api_path("总账-凭证-凭证列表提交服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        
        sql=f"""
        select id from fin_glm_ve_head_tr where remark='{test_data["remark"]}' and ve_status='DRAFT' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        
        if test_data["name"] == "正常借贷平衡":
            # 正常情况应该成功
            self.assert_util.assert_response_success(response)
            self.assert_util.assert_by_operator(
                response["data"]["data"]["veStatus"], 
                "=", 
                "APPROVING", 
                "凭证状态不是待审批"
            )
        else:
            # 借贷不平衡情况应该失败
            assert response["success"] is False
            self.assert_util.assert_by_operator(
                response["err"]["code"], 
                "=", 
                "glm.ve.credit.debit.not.equal", 
                "错误代码不是凭证借贷不相等"
            )
            self.assert_util.assert_by_operator(
                response["err"]["msg"], 
                "=", 
                "凭证借贷不相等", 
                "错误信息不是凭证借贷不相等"
            )


    @case_decorator(
        story="总账凭证操作",
        title="凭证审批同意",
        description="测试总账凭证审批同意操作",
        severity="critical",
        order=3,
        smoke=False,
        tags=["凭证录入","审批同意","FIN_GLM_VE_APPROVAL_EVENT_SERVICE"]
    )
    def test_approve_voucher(self):
        """测试总账凭证审批同意操作"""
        url=self.get_api_path("总账-凭证-凭证审核服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='APPROVING' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    @case_decorator(
        story="总账凭证操作",
        title="凭证复核同意操作",
        description="测试总账凭证复核同意操作",
        severity="critical",
        order=4,
        smoke=False,
        tags=["凭证录入","复核同意","FIN_GLM_VE_CHECK_EVENT_SERVICE"]
    )
    def test_check_voucher(self):
        """测试总账凭证复核同意操作"""
        url=self.get_api_path("总账-凭证-凭证复核服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='CHECKING' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    
    @case_decorator(
        story="总账凭证操作",
        title="凭证记账操作",
        description="测试总账凭证记账操作",
        severity="critical",
        order=5,
        smoke=False,
        tags=["凭证录入","记账","FIN_GLM_VE_ACCOUNTING_EVENT_SERVICE"]
    )
    def test_account_voucher(self):
        """测试总账凭证记账操作"""
        url=self.get_api_path("总账-凭证-凭证记账服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='WAIT_ACCOUNT' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    @case_decorator(
        story="总账凭证操作",
        title="凭证反记账操作",
        description="测试总账凭证反记账操作",
        severity="critical",
        order=6,
        smoke=False,
        tags=["凭证录入","反记账","FIN_GLM_VE_ACCOUNT_REVERSE_EVENT_SERVICE"]
    )
    def test_account_reverse_voucher(self):
        """测试总账凭证反记账操作"""
        url=self.get_api_path("总账-凭证-反过账Event服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='ACCOUNTED' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    @case_decorator(
        story="总账凭证操作",
        title="凭证作废操作",
        description="测试总账凭证作废操作",
        severity="critical",
        order=7,
        smoke=False,
        tags=["凭证录入","作废","FIN_GLM_VE_INVALID_ACTION_SERVICE"]
    )
    def test_invalid_voucher(self):
        """测试总账凭证作废操作"""
        url=self.get_api_path("总账-凭证-凭证作废服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='WAIT_ACCOUNT' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    @case_decorator(
        story="总账凭证操作",
        title="凭证取消作废操作",
        description="测试总账凭证取消作废操作",
        severity="critical",
        order=8,
        smoke=False,
        tags=["凭证录入","作废","FIN_GLM_VE_CANCEL_INVALID_ACTION_SERVICE"]
    ) 
    def test_cancel_invalid_voucher(self):
        """测试总账凭证取消作废操作"""
        url=self.get_api_path("总账-凭证-凭证取消作废服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='CANCELED' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")
        
    @case_decorator(
        story="总账凭证操作",
        title="凭证删除操作",
        description="测试总账凭证删除操作",
        severity="critical",
        order=9,
        smoke=False,
        tags=["凭证录入","删除","FIN_GLM_VE_DELETE_EVENT_SERVICE"]
    )
    def test_delete_voucher(self):
        """测试总账凭证删除操作"""
        url=self.get_api_path("总账-凭证-凭证删除服务")
        params,url=self.get_api_params(url)
        filtered_params=ParamUtil.filter_post_body_fields(
            params, ["id"], ["params", "request"])
        sql="""
        select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='DRAFT' order by created_at desc limit 1;
        """
        voucher_id=self.db.query(sql)[0]["id"]
        set_dict={
            "id":voucher_id
        }
        ParamUtil.set_request_params(filtered_params, set_dict)
        response=self.http.post(url, json=filtered_params)
        self.assert_util.assert_response_success(response)
        a.json(filtered_params, "请求数据")
        a.json(response, "响应数据")

    
        
        
if __name__ == "__main__":
    test=TestVoucherOperation()
    test.setup_class()
    test.test_account_voucher()