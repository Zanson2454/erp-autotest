import pytest
import os
import sys
import allure
from pathlib import Path
import time
from datetime import datetime, timedelta
import random
from decimal import Decimal

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.param_util import ParamUtil
@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettItemCheck(BaseTest):
    """结算项测试用例"""
    sett_item_code_result = None
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "fin" / "fin_api_path.yaml"
        
        cls.base_api_params = Path(project_root) / "testdata" / "fin" / "fin_api_params.yaml"
        
        cls.yaml_util = YamlUtil()
        
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path)

        
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})  

    @allure.title("查询结算项详情")
    @allure.description("测试步骤：查询结算项详情")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_detail(self):
        """测试查询结算项详情"""
        
        #查询最新一条结算项
        sql="""
            SELECT id
            FROM sett_item_tr
            WHERE deleted = 0
            ORDER BY created_at DESC
            LIMIT 1
        """

        try:
            result = self.db.query(sql)
            if not result:
                self.logger.error("数据库查询结果为空，请新增结算项")
                return
            request_id = result[0]["id"]
        except Exception as e:
            self.logger.error(f"查询结算项失败: {str(e)}")
            return
          
        url = self.fin_path["apis"]["结算项表-根据ID查找数据服务"]["path"]
        self.logger.debug(f"查询结算项详情接口URL: {url}")
        
        data= self.fin_params.get(url, {})
        data["params"]["request"]["id"] = request_id
        self.logger.debug(f"查询结算项详情请求参数: {data}")
        

        result = self.http.post(url, json=data, description="查询结算项详情")
        
        assert result.get("data").get("data").get("id") == request_id
        self.assert_util.assert_response_success(result)


    @allure.title("获取结算项编码")
    @allure.description("测试步骤：获取结算项编码")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_sett_item_code(self):
        """测试获取结算项编码"""
        url = self.fin_path["apis"]["结算项表-调用取号规则服务"]["path"]
        self.logger.debug(f"获取结算项编码接口URL: {url}")
        
        data= self.fin_params.get(url, {})
        data["params"]["request"]["ruleKey"] = "ERP_FIN$sett_item_tr_code"
        data["params"]["modelKey"] = "ERP_FIN$sett_item_tr"
        self.logger.debug(f"获取结算项编码请求参数: {data}")
        
        result = self.http.post(url, json=data, description="获取结算项编码")
        self.assert_util.assert_response_success(result)
        assert result.get("data").get("data")
        assert "SETTI" in result.get("data").get("data")
        self.logger.debug(f"获取结算项编码响应数据: {result}")
        self.sett_item_code_result = result.get("data").get("data")
        # return result.get("data").get("data")
        
    @allure.title("新增结算项")
    @allure.description("测试步骤：新增结算项")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_sett_item(self):
        """测试新增结算项"""
        url = self.fin_path["apis"]["SETT-ITEM-手动创建服务"]["path"]
        self.logger.debug(f"新增结算项接口URL: {url}")
        
        data= ParamUtil.filter_post_body_fields(self.fin_params.get(url, {}), ["settItemCode","settItemStatus","settItemTypeId","settDate",
                                                                               "partnerType","ptHeadId","remark","comOrgId","purSlsOrgType",
                                                                               "invOrgId","matId","taxRate","basicUnitId","genMatTypeCfId",
                                                                               "settQty","settDocPrice","settDocAmt","netDocAmt","taxAmt",
                                                                               "docCurrId","baseCurrId","exchRate","grossBaseAmt","netBaseAmt",
                                                                               "settDocTypeId","settDocId","dnCode","dnItemCode","poSoCode",
                                                                               "poSoItemCode","asyncExecutionStatus","partnerId","taxCodeId",
                                                                               "purSlsOrgId"],["params","request"])
        
        #获取结算行项目类型
        sql="""
            select *
            from sett_item_type_cf
            where deleted=0
            and sett_item_type_code='E_SLS_GODS'
        """
        settItemTypeId=self.db.query(sql)[0]["id"]
        #获取公司组织
        sql="""
            select *
            from org_struct_md 
            where deleted=0 
            and org_code like 'AUTOTEST_COM_ORG'
        """
        comOrgId=self.db.query(sql)[0]["id"]
        
        #获取库存组织
        sql="""
            select *
            from org_struct_md 
            where deleted=0 
            and org_code like 'AUTOTEST_INV_ORG'
        """
        invOrgId=self.db.query(sql)[0]["id"]
        
        #获取物料
        sql="""
            select *
            from gen_mat_md 
            where deleted=0 
            and mat_code like 'AUTOTEST_MAT_RAWM'
        """
        matId=self.db.query(sql)[0]["id"]
        base_uom_id=self.db.query(sql)[0]["base_uom_id"]
        gen_mat_type_cf_id=self.db.query(sql)[0]["gen_mat_type_cf_id"]
        
        #获取币种
        sql="""
            select * from gen_curr_type_cf where deleted=0 and curr_name="人民币"
        """
        currId=self.db.query(sql)[0]["id"]
        
        #获取关联结算单类型
        sql="""
            select *
            from gen_sett_item_type_cf 
            where deleted=0 
            and sett_item_type_code='E_SLS_GODS'
        """
        settDocTypeId=self.db.query(sql)[0]["id"]
        
        #获取税码
        sql="""
            select id, tax_code,taxcate,tax ,associated_tax_code
            from gen_tax_type_cf
            where deleted=0
        """
        taxCodeId=self.db.query(sql)[0]["id"]
        tax=self.db.query(sql)[0]["tax"]
        
        #获取销售组织
        sql="""
            select *
            from org_struct_md 
            where deleted=0 
            and org_code like 'AUTOTEST_SLS_ORG'
        """
        purSlsOrgId=self.db.query(sql)[0]["id"]
        
        #获取汇率
        sql=f"""
           select unit_id,tar_curr_id,exch_rate from gen_curr_formula_type_cf where deleted=0 and unit_id={currId} and tar_curr_id={currId}
        """
        exchRate=self.db.query(sql)[0]["exch_rate"]
        
        #结算对象id，客户 供应商
        sql="""
            select * from gen_cust_info_md where deleted=0 and cust_code like 'AUTOTEST_CUST'
        """
        custId=self.db.query(sql)[0]["id"]
        
        settItemcode=self.test_get_sett_item_code()
        settItemcode=self.sett_item_code_result
        
        # 给参数附值
        data["params"]["request"]["id"] = None
        data["params"]["request"]["createdBy"] = None
        data["params"]["request"]["updatedBy"] = None
        data["params"]["request"]["createdAt"] = None
        data["params"]["request"]["updatedAt"] = None
        data["params"]["request"]["settItemCode"] = settItemcode
        data["params"]["request"]["settItemStatus"] = "CREATED"
        data["params"]["request"]["settItemTypeId"] = {"id":settItemTypeId}
        data["params"]["request"]["settDate"] = int((datetime.now() + timedelta(hours=8)).timestamp() * 1000)
        data["params"]["request"]["partnerType"] = "CUSTOMER"
        data["params"]["request"]["ptHeadId"] = None
        data["params"]["request"]["remark"] = "自动化测试新增结算项"
        data["params"]["request"]["comOrgId"] = {"id":comOrgId}
        data["params"]["request"]["purSlsOrgType"] = "SLS"
        data["params"]["request"]["invOrgId"] = {"id":invOrgId}
        data["params"]["request"]["matId"] = {"id":matId}
        data["params"]["request"]["taxRate"] = float(tax)
        data["params"]["request"]["basicUnitId"] = {"id":base_uom_id}
        data["params"]["request"]["genMatTypeCfId"] = {"id":gen_mat_type_cf_id}
        data["params"]["request"]["settQty"] = float(random.randint(1, 1000))
        data["params"]["request"]["settDocPrice"] = float(round(random.uniform(0.000001, 1000), 6))
        data["params"]["request"]["settDocAmt"] = float(data["params"]["request"]["settDocPrice"] * data["params"]["request"]["settQty"])
        data["params"]["request"]["netDocAmt"] = float(round(data["params"]["request"]["settDocAmt"] / float(1 + tax/100), 2))
        data["params"]["request"]["taxAmt"] = float(round(data["params"]["request"]["settDocAmt"] - data["params"]["request"]["netDocAmt"], 2))
        data["params"]["request"]["docCurrId"] = {"id":currId}
        data["params"]["request"]["baseCurrId"] = {"id":currId}
        data["params"]["request"]["exchRate"] = float(exchRate)
        data["params"]["request"]["grossBaseAmt"] = float(data["params"]["request"]["settDocPrice"] * data["params"]["request"]["settQty"])
        data["params"]["request"]["netBaseAmt"] = float(round(data["params"]["request"]["settDocAmt"] / float(1 + tax/100), 2))
        data["params"]["request"]["settDocTypeId"] = {"id":settDocTypeId}
        data["params"]["request"]["settDocId"] = None
        data["params"]["request"]["dnCode"] = None
        data["params"]["request"]["dnItemCode"] = None
        data["params"]["request"]["poSoCode"] = None
        data["params"]["request"]["poSoItemCode"] = None
        data["params"]["request"]["asyncExecutionStatus"] = "CREATED"
        data["params"]["request"]["partnerId"] =custId
        data["params"]["request"]["taxCodeId"] = {"id":taxCodeId}
        data["params"]["request"]["purSlsOrgId"] = {"id":purSlsOrgId}
        
        self.logger.debug(f"新增结算项请求参数: {data}")
        
        result = self.http.post(url, json=data, description="新增结算项")
        self.assert_util.assert_response_success(result)
        self.logger.debug(f"新增结算项响应数据: {result}")
        
            
        assert result.get("data").get("data")[0].get("settItemCode") == settItemcode
        assert result.get("data").get("data")[0].get("settItemStatus") == "CREATED"
        assert result.get("data").get("data")[0].get("asyncExecutionStatus") == 'CREATED'
        
        #提供其它测试用例使用
        #return result.get("data").get("data")[0].get("id")
        
    @allure.title("删除结算项")
    @allure.description("测试步骤：删除结算项")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_sett_item(self):
        """测试删除结算项"""
        url = self.fin_path["apis"]["结算项-删除服务"]["path"]
        self.logger.debug(f"删除结算项接口URL: {url}")
        
        #查询最新一条结算项
        sql="""
            select *
            from sett_item_tr where deleted=0
            and sett_item_status='CREATED'
            order by created_at desc;
        """
        request_id=self.db.query(sql)[0]["id"]
        
        data= self.fin_params.get(url, {})
        data["params"]["request"]["id"] = request_id
        
        result = self.http.post(url, json=data, description="删除结算项")
        self.assert_util.assert_response_success(result)
        after_sql=f"""
            select *
            from sett_item_tr where deleted=0
            and sett_item_status='CREATED'
            and id={request_id};
        """
        after_result=self.db.query(after_sql)
        assert not after_result

    @allure.title("查询结算项分页数据")
    @allure.description("测试步骤：查询结算项分页数据")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sett_item_paging_data(self):
        """测试结算项分页数据"""
        url = self.fin_path["apis"]["结算项表-分页数据服务"]["path"]
        self.logger.debug(f"结算项分页数据接口URL: {url}")
        
        data= ParamUtil.filter_post_body_fields(self.fin_params.get(url, {}), ["pageable"],["params","request","pageable"])
        data["params"]["request"]["pageable"]["pageNo"] = 1
        data["params"]["request"]["pageable"]["pageSize"] = 200
        
        result = self.http.post(url, json=data, description="结算项分页数据")
        self.assert_util.assert_response_success(result)
        assert result.get("data").get("data").get("total") >= 0


if __name__ == "__main__":
    test = TestSettItemCheck()
    test.setup_class()
    test.test_add_sett_item()