import pytest
import sys
import allure
from pathlib import Path
from datetime import datetime

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettConfig(FinBaseTest):
    """结算配置测试用例"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("结算配置测试类初始化完成")

    @case_decorator(
        story="结算配置",
        title="测试新增结算价格组",
        description="验证新增结算价格组功能",
        severity="critical",
        order=0,
        smoke=False,
        tags=["结算配置", "新增结算价格组","SETT_SPG_TYPE_MD_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_add_sett_price_group(self):
        try:
            api_path = self.get_api_path("结算价格组-保存主数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["spgCode","spgName"],
                ["params","request"])
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            set_dict={
                "spgCode":f"AUTO-TEST-CODE-{now_str}",
                "spgName":f"AUTO-TEST-NAME-{now_str}"
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增结算价格组")
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("spgCode",{}),"=",set_dict["spgCode"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("spgName",{}),"=",set_dict["spgName"])
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="结算配置",
        title="测试新增结算方式",
        description="验证新增结算方式功能",
        severity="critical",
        order=1,
        smoke=False,
        tags=["结算配置", "新增结算方式","FIN_SETT_TYPE_CF_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_add_sett_type(self):
        try:
            api_path = self.get_api_path("结算类型-保存主数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["code","name","type",],
                ["params","request"])
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            set_dict={
                "code":f"AUTO-TEST-CODE-{now_str}",
                "name":f"AUTO-TEST-NAME-{now_str}",
                "type":"CASH"
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增结算方式")
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("code",{}),"=",set_dict["code"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("name",{}),"=",set_dict["name"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("type",{}),"=",set_dict["type"])
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="结算配置",
        title="测试启用结算方式",
        description="验证启用结算方式功能",
        severity="critical",
        order=2,
        smoke=False,
        tags=["结算配置", "启用结算方式","FIN_SETT_TYPE_CF_MASTER_DATA_ENABLE_DATA_SERVICE"]
    )
    def test_enable_sett_type(self):
        try:
            api_path = self.get_api_path("结算类型-启用主数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params","request"])
            sql="""
            select id,code,name,status from fin_sett_type_cf where deleted=0 order by created_at desc  limit 1;
            """
            id=self.db.query(sql)[0]["id"]
            set_dict={
                "id":id
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"启用结算方式")
            self.assert_util.assert_response_success(result)
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="结算配置",
        title="测试新增结算单据类型",
        description="验证新增结算单据类型功能",
        severity="critical",
        order=3,
        smoke=False,
        tags=["结算配置", "新增结算单据类型","SETT_DOC_TYPE_CF_SAVE_DATA_SERVICE"]
    )
    def test_add_sett_doc_type(self):
        try:
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            api_path = self.get_api_path("结算单类型定义表-保存数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["btClass","collaborativeConfirmationMethod","settClass","settDocTypeCode","settDocTypeName"],
                ["params","request"])
            set_dict={
                "btClass":"PURCHASE",
                "collaborativeConfirmationMethod":"NO_PRIORITY",
                "settClass":"EXTERNAL",
                "settDocTypeCode":f"AUTO-TEST-CODE-{now_str}",
                "settDocTypeName":f"AUTO-TEST-NAME-{now_str}"
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增结算单据类型")
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("settDocTypeCode",{}),"=",set_dict["settDocTypeCode"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("settDocTypeName",{}),"=",set_dict["settDocTypeName"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("btClass",{}),"=",set_dict["btClass"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("collaborativeConfirmationMethod",{}),"=",set_dict["collaborativeConfirmationMethod"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("settClass",{}),"=",set_dict["settClass"])
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
      
    @case_decorator(
        story="结算配置",
        title="测试新增结算行项目类型",
        description="验证新增结算行项目类型功能",
        severity="critical",
        order=4,
        smoke=False,
        tags=["结算配置", "新增结算项目类型","SETT_ITEM_TYPE_CF_SAVE_DATA_SERVICE"]
    )
    def test_add_sett_item_type(self):
        try:
            api_path = self.get_api_path("结算行项类型定义表-保存数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["priceGroupId","settClass","settDocTypeCode","settItemTypeCode","settItemTypeName","btClass","exchangeRateType","priceGroupClass"],
                ["params","request"])
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            sql="""
            select id,spg_code,spg_name from fin_sett_spg_type_cf where spg_code ='GOODS' order by created_at desc limit 1;
            """
            spg_id=self.db.query(sql)[0]["id"]
            sql="""
            select id,sett_doc_type_code,sett_doc_type_name from fin_sett_doc_type_cf where sett_doc_type_code like '%AUTO-TEST%' order by created_at desc limit 1;
            """
            sett_doc_type_id=self.db.query(sql)[0]["id"]
            sql="""
            select * from gen_curr_formula_type_cf where deleted=0 order by created_at desc limit 1
            """
            sett_item_type_id=self.db.query(sql)[0]["id"]
            set_dict={
                "priceGroupId":{
                    "id":spg_id
                },
                "settClass":"EXTERNAL",
                "settDocTypeCode":{
                    "id":sett_doc_type_id
                },
                "settItemTypeCode":f"AUTO-TEST-CODE-{now_str}",
                "settItemTypeName":f"AUTO-TEST-NAME-{now_str}",
                "btClass":"PURCHASE",
                "exchangeRateType":{
                    "id":sett_item_type_id
                },
                "priceGroupClass":"COST"
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增结算行项目类型")
            if result.get("err"):
                self.assert_util.assert_by_operator(result.get("err",{}).get("masg",{}),"=","结算行项类型定义表 数据已存在")
            if not result.get("err"):
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("settItemTypeCode",{}),"=",set_dict["settItemTypeCode"])
                self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("settItemTypeName",{}),"=",set_dict["settItemTypeName"])
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
     
     
     
    def get_sett_sds_head_invoke_code(self):
        api_path = self.get_api_path("结算单汇单策略头表-调用取号规则服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            [],
            ["params","request"])
        result=self.http.post(url,json=filtered_params,description=f"获取汇单策略调用取号规则")
        return result.get("data",{}).get("data",{})
        
    @case_decorator(
        story="结算配置",
        title="测试新增汇单策略",
        description="验证新增结算汇单策略功能",
        severity="critical",
        order=5,
        smoke=False,
        tags=["结算配置", "新增结算策略","SETT_SDS_SAVE_EVENT_SERVICE"]
    )
    def test_add_sett_strategy(self):
        try:
            api_path = self.get_api_path("SETT-SDS-汇单策略保存服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["reamrk","sdsHeadCode","sdsHeadName","strategyType"],
                ["params","request"])
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            set_dict={
                "remark":f"AUTO-TEST-REMARK-{now_str}",
                "sdsHeadCode":self.get_sett_sds_head_invoke_code(),
                "sdsHeadName":f"AUTO-TEST-NAME-{now_str}",
                "strategyType":'CONFIRM'
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增汇单策略")
            self.assert_util.assert_response_success(result)
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("sdsHeadCode",{}),"=",set_dict["sdsHeadCode"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("sdsHeadName",{}),"=",set_dict["sdsHeadName"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("strategyType",{}),"=",set_dict["strategyType"])
            self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("remark",{}),"=",set_dict["remark"])
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    
    def get_sett_rule_link_item_code(self):
        api_path = self.get_api_path("结算单汇单维度配置行表-调用取号规则服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            [],
            ["params","request"])
        result=self.http.post(url,json=filtered_params,description=f"获取汇单维度配置行表调用取号规则")
        return result.get("data",{}).get("data",{})
    
    def get_sett_rule_scope_item_code(self):
        api_path = self.get_api_path("结算单汇单范围配置行表-调用取号规则服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            [],
            ["params","request"])
        result=self.http.post(url,json=filtered_params,description=f"获取汇单范围配置行表调用取号规则")
        return result.get("data",{}).get("data",{})
    
    
    def get_sett_rule_invoke_code(self):
        """获取汇单规则调用取号规则"""
        api_path = self.get_api_path("结算单汇单配置头表-调用取号规则服务")
        params, url = self.get_api_params(api_path)
        filtered_params = ParamUtil.filter_post_body_fields(
            params,
            [],
            ["params","request"])
        result=self.http.post(url,json=filtered_params,description=f"获取汇单规则调用取号规则")
        return result.get("data",{}).get("data",{})
    
    @case_decorator(
        story="结算配置",
        title="测试新增汇单规则",
        description="验证新增结算汇单规则功能",
        severity="critical",
        order=6,
        smoke=False,
        tags=["结算配置", "新增结算规则","SETT_SDC_SAVE_SERVICE"]
    )
    def test_add_sett_rule(self):
        try:
            api_path = self.get_api_path("结算单-汇单规则保存服务")
            params, url = self.get_api_params(api_path)
            sql="""
            select id from fin_sett_doc_type_cf where sett_doc_type_code like '%AUTO-TEST%' order by created_at desc limit 1;
            """
            sett_doc_type_id=self.db.query(sql)[0]["id"]
            sql="""
            select * from sett_sds_head_cf where deleted=0 order by created_at desc limit 1;
            """
            sett_sds_head_id=self.db.query(sql)[0]["id"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["enabledStatus","sdcDescription","sdcHeadCode","settHeadType","settSdcLinkCfId","settSdcTypeCfId","settSdsHeadCfId"],
                ["params","request"])
            now_str = datetime.now().strftime("%Y%m%d%H%M%S")
            sdcHeadCode=self.get_sett_rule_invoke_code()
            set_dict={
                "enabledStatus":'INACTIVE',
                "sdcDescription":f"AUTO-TEST-DESCRIPTION-{now_str}",
                "sdcHeadCode":sdcHeadCode,
                "settHeadType":{
                    "id":sett_doc_type_id
                },
                "settSdsHeadCfId":{
                    "id":sett_sds_head_id
                },
                "settSdcLinkCfId":[{
                    "sdcHeadCode":sdcHeadCode,
                    "sdcLinkCode":self.get_sett_rule_link_item_code(),
                    "settItemFieldCode":"settItemTypeId"
                    
                }],
                "settSdcTypeCfId":[{
                    "sdcHeadCode":sdcHeadCode,
                    "sdcTypeCode":self.get_sett_rule_scope_item_code(),
                    "matchValueType":"enumeration",
                    "matchValue":"RECONCILED",
                    "controlFieldType":"enumeration",
                    "controlFieldCode":"sett_item_status",
                    "comparisonOperatorCode":"EQUAL"
                }]
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增汇单规则")
            self.assert_util.assert_response_success(result)
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        
    @case_decorator(
        story="结算配置",
        title="测试启用汇单规则",
        description="验证启用结算汇单规则功能",
        severity="critical",
        order=7,
        smoke=False,
        tags=["结算配置", "启用结算汇单规则","SETT_SDC_ENABLE_SERVICE"]
    )
    def test_enable_sett_rule(self):
        try:
            api_path = self.get_api_path("SETT-SDC-结算汇单规则启用服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params","request"])
            sql="""
            select id,sdc_head_code from sett_sdc_head_cf where deleted=0  order by created_at desc limit 1;
            """
            id=self.db.query(sql)[0]["id"]
            set_dict={
                "id":id
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"启用汇单规则")
            self.assert_util.assert_response_success(result)
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
    @case_decorator(
        story="结算配置",
        title="测试新增结算行项目类型关联汇单规则",
        description="验证新增结算行项目类型关联汇单规则功能",
        severity="critical",
        order=8,
        smoke=False,
        tags=["结算配置", "新增结算行项目类型关联汇单规则","SETT_SRS_LINK_CF_SAVE_DATA_SERVICE"]
    )
    def test_add_sett_item_type_link_rule(self):
        try:
            api_path = self.get_api_path("结算行项目类型关联汇单规则-保存数据服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["comOrgId","sdcHeadCode","settDocTypeCode","settItemTypeCode"],
                ["params","request"])
            sql="""
            select id,org_code,org_name from org_struct_md where deleted=0 and org_code like '%AUTOTEST_GR_ORG%';
            """
            com_org_id=self.db.query(sql)[0]["id"]
            sql="""
            select id,sett_doc_type_code,sett_item_type_name
            from  fin_sett_item_type_cf where deleted=0 and sett_item_type_code ='E_SLS_GOODS' order by created_at desc limit 1;
            """
            sett_item_type_id=self.db.query(sql)[0]["id"]
            sett_doc_type_id=self.db.query(sql)[0]["sett_doc_type_code"]
            sql=f"""
            select id,sdc_head_code,sdc_description
            from sett_sdc_head_cf where deleted=0 and sett_head_type={sett_doc_type_id} order by created_at desc limit 1;
            """
            sdc_head_id=self.db.query(sql)[0]["id"]
            set_dict={
                "comOrgId":{
                    "id":com_org_id
                },
                "sdcHeadCode":{
                    "id":sdc_head_id
                },
                "settDocTypeCode":{
                    "id":sett_doc_type_id
                },
                "settItemTypeCode":{
                    "id":sett_item_type_id
                }
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增结算行项目类型关联汇单规则")
            self.assert_util.assert_response_success(result)
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        
        
    @case_decorator(
        story="结算配置",
        title="测试新增结算单据类型关联往来单据",
        description="验证新增结算单据类型关联往来单据功能",
        severity="critical",
        order=9,
        smoke=False,
        tags=["结算配置", "新增结算单据类型关联往来单据","SETT_DOC_ASSOC_TYPE_CREATE_EVENT_SERVICE"]
    )
    def test_add_sett_doc_type_link_apar_type(self):
        try:
            api_path = self.get_api_path("结算单关联往来单据类型配置-保存服务")
            params, url = self.get_api_params(api_path)
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["companyOrganization","settlementType","apType"],
                ["params","request"])
            
            sql="""
            select id,org_code,org_name from org_struct_md where deleted=0 and org_code like '%AUTOTEST_GR_ORG%';
            """
            com_org_id=self.db.query(sql)[0]["id"]
            sql="""
            select id,sett_doc_type_code,sett_doc_type_name from fin_sett_doc_type_cf where deleted=0 and sett_doc_type_code like '%AUTO%' order by created_at desc limit 1;
            """
            sett_doc_type_id=self.db.query(sql)[0]["id"]
            sql="""
            select id,ap_type_code,name from fin_apm_ap_type_md where deleted=0 order by created_at desc limit 1;
            """
            ap_type_id=self.db.query(sql)[0]["id"]
            set_dict={
                "companyOrganization":{
                    "id":com_org_id
                },
                "settlementType":{
                    "id":sett_doc_type_id
                },
                "apType":{
                    "id":ap_type_id
                }
            }
            ParamUtil.set_request_params(filtered_params,set_dict)
            result=self.http.post(url,json=filtered_params,description=f"新增结算单据类型关联往来单据")
            self.assert_util.assert_response_success(result)
            a.json(filtered_params, "请求数据")
            a.json(result, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        

if __name__ == "__main__":
    test = TestSettConfig()
    test.setup_class()
    test.test_add_sett_doc_type_link_apar_type()
