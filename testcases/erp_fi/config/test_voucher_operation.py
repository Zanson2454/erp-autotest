
import sys
from datetime import datetime
from pathlib import Path

import allure
import pytest

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from testcases.erp_fi import FiBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("基础财务")
@allure.feature("总账凭证操作")
class TestVoucherOperation(FiBaseTest):
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
     
    def get_ve_base_info(self):
        """获取新增凭证的基础信息部分"""
        try:
            #获取预制的自动化测试的核算账簿、核酸组织,默认凭证类型
            sql="""
                select id,as_org,vt_type,coa_type from fin_glm_ab_type_cf where deleted=0 and ab_type_code like '%AUTO-TEST%' order by created_at desc limit 1;
            """
            ab_type_id,as_org_id,vt_type,coa_type=self.query_service.query(sql)[0]["id"],self.query_service.query(sql)[0]["as_org"],self.query_service.query(sql)[0]["vt_type"],self.query_service.query(sql)[0]["coa_type"]
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
            response, _ = self.standard_api_call(
                api_key="总账-凭证-获取凭证号服务",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            calendarItemId=response["data"]["data"]["calendarItemId"]
            vouchNumber=response["data"]["data"]["vouchNumber"]
            return calendarItemId,vouchNumber,ab_type_id,vt_type,ve_date,as_org_id,coa_type
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    def create_voucher_with_amounts(self, debit_amt, credit_amt, remark, use_cash_account=False, use_ad_account=False):
        """创建指定借贷金额的凭证
        
        Args:
            debit_amt: 借方金额
            credit_amt: 贷方金额  
            remark: 凭证备注
            use_cash_account: 是否使用现金类科目，默认False
            use_ad_account: 是否使用辅助维度科目，默认False
        """
        url = self.get_api_path("总账-凭证-凭证暂存服务")
        params, url = self.get_api_params(url)
        calendarItemId, vouchNumber, ab_type_id, vt_type, ve_date, as_org_id, coa_type = self.get_ve_base_info()
    
         # 从init_data中获取货币ID
        currency_info = self.init_data.get("currency_info") or []
        if currency_info:
            curr_id = currency_info[0].get("curr_id")
        else:
            raise ValueError("未找到货币信息，请检查init_data配置")
    
        # 从init_data中获取汇率类型ID
        exchange_rate_type_info = self.init_data.get("exchange_rate_type_info") or []
        if exchange_rate_type_info:
            rt_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
        else:
            raise ValueError("未找到汇率类型信息，请检查init_data配置")
    
        # 根据参数选择科目类型
        if use_cash_account:
            # 获取现金类科目
            sql = f"""
            select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf 
            where coa_type={coa_type} and leaf=1 and aa_head_name like '%现金%' and deleted=0 
            order by created_at desc limit 1;
            """
        elif use_ad_account:
            # 获取有辅助维度的科目
            sql = f"""
            select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf 
            where coa_type={coa_type} and leaf=1 and aa_head_name like '%辅助维度%' 
            order by created_at desc limit 1;
            """
        else:
            # 获取普通科目
            sql = f"select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf where coa_type={coa_type} and leaf=1;"
        
        aa_head_ids = self.query_service.query(sql)
        aa_head_ids = [aa_head_id["id"] for aa_head_id in aa_head_ids]
        
        # 如果现金类科目不足2个，则补充普通科目
        if len(aa_head_ids) < 2:
            sql = f"select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf where coa_type={coa_type} and leaf=1;"
            additional_accounts = self.query_service.query(sql)
            for account in additional_accounts:
                if account["id"] not in aa_head_ids:
                    aa_head_ids.append(account["id"])
                    if len(aa_head_ids) >= 2:
                        break
    
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
        response, _ = self.standard_api_call(
            api_key="总账-凭证-凭证暂存服务",
            set_dict=filtered_params.get("params", {}),
            store_id_as=None,
            use_param_util=False,
            param_path=["params"]
        )
        #self.assert_util.assert_response_success(response)
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
            # 从init_data中获取货币ID
            currency_info = self.init_data.get("currency_info") or []
            if currency_info:
                curr_id = currency_info[0].get("curr_id")
            else:
                raise ValueError("未找到货币信息，请检查init_data配置")
            
            # 从init_data中获取汇率类型ID
            exchange_rate_type_info = self.init_data.get("exchange_rate_type_info") or []
            if exchange_rate_type_info:
                rt_type_id = exchange_rate_type_info[0].get("exchange_rate_type_id")
            else:
                raise ValueError("未找到汇率类型信息，请检查init_data配置")
            
            sql=f"""
            select id,aa_head_code,aa_head_name from fin_glm_aa_head_cf where coa_type={coa_type} and leaf=1;
            """
            aa_head_ids=self.query_service.query(sql)
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
            response, _ = self.standard_api_call(
                api_key="总账-凭证-凭证暂存服务",
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
            "expected_status": "APPROVING",
            "use_cash_account": False,
            "expected_success": True,
            "expected_error_code": None,
            "expected_error_msg": None
        },
        {
            "name": "借贷金额不平衡",
            "debit_amt": 100.00,
            "credit_amt": 200.00,
            "remark": "测试借贷不平衡业务流程",
            "expected_status": "DRAFT",
            "use_cash_account": False,
            "expected_success": False,
            "expected_error_code": "glm.ve.credit.debit.not.equal",
            "expected_error_msg": "凭证借贷不相等"
        },
        {
            "name": "现金类科目不指定现金流量",
            "debit_amt": 500.00,
            "credit_amt": 500.00,
            "remark": "测试现金类科目不指定现金流量业务流程",
            "expected_status": "DRAFT",
            "use_cash_account": True,
            "expected_success": False,
            "expected_error_code": "glm.ve.amt.of.cai.and.cas.item.check.not.equal",
            "expected_error_msg": "凭证流量检查不通过，现金科目金额与凭证行现金类科目金额不相等"
        },
        {
            "name":"辅助维度科目不指定辅助维度值",
            "debit_amt": 4.12,
            "credit_amt": 4.12,
            "remark": "测试辅助维度科目不指定辅助维度值业务流程",
            "expected_status": "DRAFT",
            "use_cash_account": False,
            "use_ad_account": True,  # 使用辅助维度科目
            "expected_success": False,
            "expected_error_code": "glm.ve.ads.required.ad.miss",
            "expected_error_msg": "必填维度缺失"
        }
    ])
    def test_submit_voucher(self, test_data):
        """测试总账凭证提交操作"""
        try:
                # 首先创建凭证
                self.create_voucher_with_amounts(
                    test_data["debit_amt"], 
                    test_data["credit_amt"], 
                    test_data["remark"],
                    test_data.get("use_cash_account", False),
                    test_data.get("use_ad_account", False)
                )
                url=self.get_api_path("总账-凭证-凭证列表提交服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])

                sql=f"""
                select id from fin_glm_ve_head_tr where remark='{test_data["remark"]}' and ve_status='DRAFT' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证列表提交服务",
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )

                # 统一断言逻辑
                if test_data["expected_success"]:
                    # 成功情况断言
                    self.assert_util.assert_response_success(response)
                    self.assert_util.assert_by_operator(
                        response["data"]["data"]["veStatus"], 
                        "=", 
                        test_data["expected_status"], 
                        f"凭证状态不是{test_data['expected_status']}"
                    )
                else:
                    # 失败情况断言
                    assert response["success"] is False
                    self.assert_util.assert_by_operator(
                        response["err"]["code"], 
                        "=", 
                        test_data["expected_error_code"], 
                        f"错误代码不是{test_data['expected_error_code']}"
                    )
                    self.assert_util.assert_by_operator(
                        response["err"]["msg"], 
                        "=", 
                        test_data["expected_error_msg"], 
                        f"错误信息不是{test_data['expected_error_msg']}"
                    )


        except Exception as e:
            a.text(str(e), "失败原因")
            raise

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
        try:
                url=self.get_api_path("总账-凭证-凭证审核服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='APPROVING' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证审核服务",
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
        try:
                url=self.get_api_path("总账-凭证-凭证复核服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='CHECKING' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证复核服务",
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
        try:
                url=self.get_api_path("总账-凭证-凭证记账服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id ,biz_date ,ab_type from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='WAIT_ACCOUNT' and deleted=0 order by created_at desc limit 1;
                """
                voucher_id,biz_date,ab_type=self.query_service.query(sql)[0]["id"],self.query_service.query(sql)[0]["biz_date"],self.query_service.query(sql)[0]["ab_type"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证记账服务",
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                sql=f"""
                select start_time,end_time from fin_common_calendar_item_cf where id=(select period_of_current  from fin_glm_ab_type_cf where id={ab_type})
                """
                start_time,end_time=self.query_service.query(sql)[0]["start_time"],self.query_service.query(sql)[0]["end_time"]
                if biz_date < start_time or biz_date > end_time:
                    self.assert_util.assert_by_operator(response["err"]["code"], "=", "glm.ve.account.datetime.error")
                    self.assert_util.assert_by_operator(response["err"]["msg"], "=", "凭证日期不在账簿当前期间")
                else:
                    self.assert_util.assert_response_success(response)
                a.json(filtered_params, "请求数据")
                a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

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
        try:
                url=self.get_api_path("总账-凭证-反过账Event服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='ACCOUNTED' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-反过账Event服务",
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
        try:
                url=self.get_api_path("总账-凭证-凭证作废服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='WAIT_ACCOUNT' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证作废服务",
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
        try:
                url=self.get_api_path("总账-凭证-凭证取消作废服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='CANCELED' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证取消作废服务",
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
        try:
                url=self.get_api_path("总账-凭证-凭证删除服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常业务流程' and ve_status='DRAFT' order by created_at desc limit 1;
                """
                voucher_id=self.query_service.query(sql)[0]["id"]
                set_dict={
                    "id":voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证删除服务",
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
        story="总账凭证批量操作",
        title="凭证批量提交操作",
        description="测试总账凭证批量提交操作",
        severity="critical",
        order=1,
        smoke=False,
        tags=["凭证录入","批量提交","FIN_GLM_VE_SUBMIT_BY_ID_BATCH_EVENT_SERVICE"]
    )
    def test_batch_submit_voucher(self):
        """测试总账凭证批量提交操作"""
        try:
                url=self.get_api_path("总账-凭证-凭证列表批量提交服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["request"], ["params"])

                # 执行3次创建凭证
                for _ in range(3):
                    self.create_voucher_with_amounts(
                        1.23,
                        1.23,
                        "测试正常批量业务流程",
                        False,
                        False
                    )

                # 获取凭证ID列表
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常批量业务流程' and ve_status='DRAFT' order by created_at desc limit 3;
                """
                voucher_ids=self.query_service.query(sql)

                # 直接设置request参数为列表
                filtered_params['params']['request'] = voucher_ids
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证列表批量提交服务",
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
        story="总账凭证批量操作",
        title="批量审批",
        description="测试总账凭证批量审批",
        severity="critical",
        order=2,
        smoke=False,
        tags=["凭证录入","批量审批","FIN_GLM_VE_APPROVAL_EVENT_SERVICE"]
    )
    def test_batch_approve_voucher(self):
        """测试总账凭证批量审批"""
        try:
                url=self.get_api_path("总账-凭证-凭证审核服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常批量业务流程' and ve_status='APPROVING' and deleted=0 order by created_at desc limit 3;
                """
                voucher_ids=self.query_service.query(sql)
                filtered_params['params']['request']['id'] = [voucher_id["id"] for voucher_id in voucher_ids]
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证审核服务",
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
        story="总账凭证批量操作",
        title="批量复核",
        description="测试总账凭证批量复核",
        severity="critical",
        order=3,
        smoke=False,
        tags=["凭证录入","批量复核","FIN_GLM_VE_CHECK_EVENT_SERVICE"]
    )
    def test_batch_check_voucher(self):
        """测试总账凭证批量复核"""
        try:
                url=self.get_api_path("总账-凭证-凭证复核服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["id"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常批量业务流程' and ve_status='CHECKING' and deleted=0 order by created_at desc limit 3;
                """
                voucher_ids=self.query_service.query(sql)
                filtered_params['params']['request']['id'] = [voucher_id["id"] for voucher_id in voucher_ids]
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证复核服务",
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
        story="总账凭证批量操作",
        title="批量记账",
        description="测试总账凭证批量记账",
        severity="critical",
        order=4,
        smoke=False,
        tags=["凭证录入","批量记账","FIN_GLM_VE_ACCOUNTING_BATCH_EVENT_SERVICE"]
    )
    def test_batch_account_voucher(self):
        """测试总账凭证批量记账"""
        try:
                url=self.get_api_path("总账-凭证-凭证批量记账服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["request"], ["params"])
                sql="""
                select id from fin_glm_ve_head_tr where remark='测试正常批量业务流程' and ve_status='WAIT_ACCOUNT' and deleted=0 order by created_at desc limit 3;
                """
                voucher_ids=self.query_service.query(sql)
                 # 验证是否有数据
                if not voucher_ids:
                    raise ValueError("未找到待记账的凭证数据，请检查数据")

                filtered_params['params']['request']=voucher_ids
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证批量记账服务",
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
        story="总账凭证批量操作",
        title="批量打印",
        description="测试总账凭证批量打印",
        severity="critical",
        order=5,
        smoke=False,
        tags=["凭证录入","批量反记账","FIN_GLM_VE_PRINT_STATUS_BY_ID_BATCH_SERVICE"]
    )
    def test_batch_print_voucher(self):
        """测试总账凭证批量打印"""
        try:
                url=self.get_api_path("FIN_GLM_VE_PRINT_STATUS_BY_ID_BATCH_SERVICE")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["ids"], ["params", "request"])
                sql="""
                select id from fin_glm_ve_head_tr order by created_at desc  limit 3;
                """
                voucher_ids=self.query_service.query(sql)
                filtered_params['params']['request']['ids'] = [voucher_id["id"] for voucher_id in voucher_ids]
                response, _ = self.standard_api_call(
                    api_key="FIN_GLM_VE_PRINT_STATUS_BY_ID_BATCH_SERVICE",
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_success(response)
                sql=f"""
                select print_status from fin_glm_ve_head_tr where id in ({','.join([str(voucher_id["id"]) for voucher_id in voucher_ids])})
                """
                print_status=self.query_service.query(sql)
                if print_status:
                    for print_statue in print_status:
                        self.assert_util.assert_by_operator(print_statue["print_status"], "=", "PRINTED")
                else:
                    raise ValueError("未找到打印状态数据，请检查数据")
                a.json(filtered_params, "请求数据")
                a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="总账凭证操作",
        title="凭证冲销-蓝冲",
        description="测试总账凭证冲销-蓝冲",
        severity="critical",
        order=6,
        smoke=False,
        tags=["凭证录入","冲销-蓝冲","FIN_GLM_VE_OFFSET_EVENT_SERVICE"]
    )
    def test_offset_voucher(self):
        """测试总账凭证冲销-蓝冲"""
        try:
                url=self.get_api_path("总账-凭证-凭证冲销服务")
                params,url=self.get_api_params(url)
                filtered_params=ParamUtil.filter_post_body_fields(
                    params, ["offsetType","sourceVeHeadId"], ["params", "request"])
                #获取凭证头
                sql="""
                select id,vouch_number,vo_entry_date,biz_date,debit_total_amt,credit_total_amt from fin_glm_ve_head_tr where remark in ('测试正常业务流程','测试正常批量业务流程')and ve_status='ACCOUNTED' and deleted=0  and offset_status='UNOFFSET' order by created_at limit 1;
                """
                voucher_id,vouch_number,vo_entry_date,_biz_date,debit_total_amt,credit_total_amt=self.query_service.query(sql)[0]["id"],self.query_service.query(sql)[0]["vouch_number"],self.query_service.query(sql)[0]["vo_entry_date"],self.query_service.query(sql)[0]["biz_date"],self.query_service.query(sql)[0]["debit_total_amt"],self.query_service.query(sql)[0]["credit_total_amt"]
                #获取凭证行
                sql=f"""
                select ve_item_descr,debit_amt,credit_amt from fin_glm_ve_item_tr where ve_head_id={voucher_id}
                """
                voucher_items=self.query_service.query(sql)
                set_dict={
                    "offsetType": "BLUE",
                    "sourceVeHeadId": voucher_id
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                response, _ = self.standard_api_call(
                    api_key="总账-凭证-凭证冲销服务",
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )

                self.assert_util.assert_response_success(response)
                #凭证头信息断言
                self.assert_util.assert_by_operator(response["data"]["data"]['voEntryDate'], "=",int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000) )
                self.assert_util.assert_by_operator(response["data"]["data"]['debitTotalAmt'], "=", float(debit_total_amt))
                self.assert_util.assert_by_operator(response["data"]["data"]['creditTotalAmt'], "=", float(credit_total_amt))
                self.assert_util.assert_by_operator(response["data"]["data"]['veStatus'], "=", "WAIT_ACCOUNT")
                self.assert_util.assert_by_operator(response["data"]["data"]['offsetStatus'], "=", "UNOFFSET")
                self.assert_util.assert_by_operator(response["data"]["data"]['whetherOffset'], "=", True)
                #凭证行信息断言
                ve_items=response["data"]["data"].get("veItems",[])
                assert len(ve_items) == len(voucher_items), "凭证行数量不一致"
                for voucher_item, ve_item in zip(voucher_items, ve_items):
                    self.assert_util.assert_by_operator(ve_item["veItemDescr"], 
                                                        "=", 
                                                        f'冲-{vo_entry_date.strftime("%Y%m%d")}-{vouch_number}-{voucher_item["ve_item_descr"]}')
                    if ve_item.get("debitAmt"):
                        self.assert_util.assert_by_operator(voucher_item["debit_amt"], "=",None)
                    if ve_item.get("creditAmt"):
                        self.assert_util.assert_by_operator(voucher_item["credit_amt"], "=",None)
                    if not ve_item.get("debitAmt"):
                        self.assert_util.assert_by_operator(float(voucher_item["debit_amt"]), "=",ve_item["creditAmt"])
                    if not ve_item.get("creditAmt"):
                        self.assert_util.assert_by_operator(float(voucher_item["credit_amt"]), "=",ve_item["debitAmt"])




                a.json(filtered_params, "请求数据")
                a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
if __name__ == "__main__":
    test=TestVoucherOperation()
    test.setup_class()
    test.test_offset_voucher()
