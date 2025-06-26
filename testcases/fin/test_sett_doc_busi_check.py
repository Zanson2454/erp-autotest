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
from data_factory.fin_sett_factory import FinSettlementFactory
from utils.log_util import Loggers
from utils.param_util import ParamUtil
@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettDocBusiCheck(BaseTest):
    """结算单业务测试用例"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "fin" / "fin_api_path.yaml"
        cls.base_api_params = Path(project_root) / "testdata" / "fin" / "fin_api_params.yaml"
        cls.yaml_util = YamlUtil()  
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})
    def get_sett_doc_id(self):
        """获取不同状态的结算单ID 已创建，已确认 """
        created_sett_doc = FinSettlementFactory.get_or_create_settlement_doc("CREATED")
        created_sett_doc_id = created_sett_doc.get("id")
        # Loggers.debug(f"已创建结算单ID: {created_sett_doc_id}")
        
        sql = """
        SELECT * FROM sett_doc_tr
        WHERE deleted = 0
        AND sett_doc_status = 'CONFIRMED'
        ORDER BY
        created_at DESC
        LIMIT 1 
        """
        result = self.db.query(sql)
        return [created_sett_doc_id,result[0]["id"]]
        

    def test_sett_doc_remark(self):
        """测试结算单修改备注操作"""
        url = self.fin_path["结算单表-根据ID查找无行信息数据服务"]["path"]
        data = self.fin_params.get(url, {})
        filtered_data = ParamUtil.filter_post_body_fields(data, ["id"], ["params", "request"])
        sett_doc_id  = self.get_sett_doc_id()[0]
        filtered_data["params"]["request"]["id"] = sett_doc_id
        result = self.http.post(url, json=filtered_data, description=f"结算单修改备注操作 - ID: {sett_doc_id}")
        # Loggers.debug(f"结算单修改备注操作结果: {result}")
        self.assert_util.assert_response_success(result)
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("id",{}),"=",sett_doc_id)
        
    def test_sett_doc_remark_save(self):
        """测试结算单修改备注保存操作"""
        url = self.fin_path["结算单表-保存数据服务"]["path"]
        data = self.fin_params.get(url, {})
        filtered_data = ParamUtil.filter_post_body_fields(data, ["id","baseCurrId","comOrgId",
                                                                 "docCurrId","partnerName","partnerType","purSlsOrgName",
                                                                 "remark","settBaseAmt","settDate","settDocAmt","settDocCode",
                                                                 "settDocStatus","settDocTypeId","tradingDocCode","tradingDocStatus"], ["params", "request"])
        
        sett_doc_id  = self.get_sett_doc_id()[0]
        sql = f"""
        select * from sett_doc_tr where id={sett_doc_id}
        """
        sql_result = self.db.query(sql)
        filtered_data["params"]["request"]["id"] = sql_result[0]["id"]
        filtered_data["params"]["request"]["baseCurrId"] = sql_result[0]["base_curr_id"]
        filtered_data["params"]["request"]["comOrgId"] = sql_result[0]["com_org_id"]
        filtered_data["params"]["request"]["docCurrId"] = sql_result[0]["doc_curr_id"]
        filtered_data["params"]["request"]["partnerName"] = sql_result[0]["partner_name"]
        filtered_data["params"]["request"]["partnerType"] = sql_result[0]["partner_type"]
        filtered_data["params"]["request"]["purSlsOrgName"] = sql_result[0]["pur_sls_org_name"]
        filtered_data["params"]["request"]["remark"] = "AUTOTEST-remark"
        filtered_data["params"]["request"]["settBaseAmt"] = float(sql_result[0]["sett_base_amt"])
        filtered_data["params"]["request"]["settDate"] = int(datetime.strptime(str(sql_result[0]["sett_date"]), "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
        filtered_data["params"]["request"]["settDocAmt"] = float(sql_result[0]["sett_doc_amt"])
        filtered_data["params"]["request"]["settDocCode"] = sql_result[0]["sett_doc_code"]
        filtered_data["params"]["request"]["settDocStatus"] = sql_result[0]["sett_doc_status"]
        filtered_data["params"]["request"]["settDocTypeId"] = sql_result[0]["sett_doc_type_id"]
        filtered_data["params"]["request"]["tradingDocCode"] = sql_result[0]["trading_doc_code"]
        filtered_data["params"]["request"]["tradingDocStatus"] = sql_result[0]["trading_doc_status"]
        # Loggers.debug(filtered_data["params"]["request"])
        result = self.http.post(url, json=filtered_data, description=f"结算单修改备注保存操作 - ID: {sett_doc_id}")
        # Loggers.debug(f"结算单修改备注保存操作结果: {result}")
        self.assert_util.assert_response_success(result)
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("id",{}),"=",sett_doc_id)
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("remark",{}),"=","AUTOTEST-remark")
        
        

    @allure.story("结算单确认")
    def test_sett_doc_confirm(self):
        """测试结算单确认"""
        url = self.fin_path["SETT-DOC-运营端结算单确认下推应收应付-异步服务"]["path"]
        data = ParamUtil.filter_post_body_fields(self.fin_params.get(url, {}), ["id"], ["params", "request"])
        data=ParamUtil.convert_param_type(data, ["params", "request","id"], "array")
        sett_doc_ids  = self.get_sett_doc_id()
        for index, sett_doc_id in enumerate(sett_doc_ids):
            data["params"]["request"]["id"][0] = sett_doc_id
            result = self.http.post(url, json=data, description=f"结算单确认 - ID: {sett_doc_id}")
            time.sleep(3)
            if index == 0:
                sql = f"""
                select sett_doc_status,async_execution_status,trading_doc_id,trading_doc_status,trading_doc_code,client_side_confirm_status
                from sett_doc_tr where deleted=0 and id={sett_doc_id}
                """
                sql_result = self.db.query(sql)
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_by_operator(sql_result[0]["sett_doc_status"], "=", "CONFIRMED")
                self.assert_util.assert_by_operator(sql_result[0]["async_execution_status"], "=", "SUCCEEDED")
                self.assert_util.assert_by_operator(sql_result[0]["trading_doc_id"], "not_empty")
                self.assert_util.assert_by_operator(sql_result[0]["trading_doc_status"], "=", "CREATED")
                self.assert_util.assert_by_operator(sql_result[0]["trading_doc_code"], "not_empty")
                self.assert_util.assert_by_operator(sql_result[0]["client_side_confirm_status"], "=", "CONFIRMED")
            elif index == 1:
                assert result.get("success",{}) == False
                assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                
    def test_cancel_sett_doc(self):
        """测试结算单取消汇单"""
        url = self.fin_path["SETT-DOC-结算单取消服务"]["path"]
        data = ParamUtil.filter_post_body_fields(self.fin_params.get(url, {}), [""], ["params", "request", 0])
        data=ParamUtil.convert_param_type(data, ["params", "request"], "array")
        sett_doc_ids  = self.get_sett_doc_id()
        for index, sett_doc_id in enumerate(sett_doc_ids):
            
            # 获取已经汇单的结算单对应的结算项的id
            sett_item_sql=f"""
                select * from sett_item_tr where sett_doc_id={sett_doc_id}
                """
            sett_item_sql_result = self.db.query(sett_item_sql)
            
            # 取消汇单接口
            data["params"]["request"][0] = {"id":sett_doc_id}
            result = self.http.post(url, json=data, description=f"结算单取消汇单 - ID: {sett_doc_id}")
            time.sleep(2)
            
            # 获取取消汇单后的结算项id
            sett_sql = f"""
            select * from sett_item_tr where id={sett_item_sql_result[0]["id"]}
            """
            sett_sql_result = self.db.query(sett_sql)

            #获取已经删除的结算单的逻辑删除字段
            sql = f"""
            select deleted
            from sett_doc_tr where  id={sett_doc_id}
            """
            sql_result = self.db.query(sql)
            
            if index == 0:
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_by_operator(sql_result[0]["deleted"], "!=", 0)  
                self.assert_util.assert_by_operator(sett_sql_result[0]["sett_item_status"], "=", "RECONCILED")
                self.assert_util.assert_by_operator(sett_sql_result[0]["sett_doc_id"], "empty")
                self.assert_util.assert_by_operator(sett_sql_result[0]["is_sdc_cancel_relv"], "=", 1)
            elif index == 1:
                assert result.get("success",{}) == False
                assert result.get("err",{}).get("msg",{}) == "存在已确认的结算单，请重新选择后再进行操作"
    
    @allure.title("结算单修改操作")
    @allure.description("测试步骤：点击修改结算单")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_sett_doc_modify(self):
        """测试修改结算单"""
        url = self.fin_path["结算单-详情视图查询服务"]["path"]
        data = self.fin_params.get(url, {})
        filtered_data = ParamUtil.filter_post_body_fields(data, ["id"], ["params", "request"])
        filtered_data["params"]["request"]["id"] = FinSettlementFactory.get_or_create_settlement_doc("CREATED").get("id")
        result = self.http.post(url, json=filtered_data, description=f"修改结算单")
        self.assert_util.assert_response_success(result)   
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("id",{}),"=",filtered_data["params"]["request"]["id"])
        
    @allure.title("结算单修改保存操作")
    @allure.description("测试步骤：1结算单修改保存")
    @allure.severity(allure.severity_level.CRITICAL)
    #检查修改后的结算单金额，检查修改后生成的结算项状态、关联单据id
    def test_sett_doc_save(self):
        """结算单修改保存"""
        url = self.fin_path["结算单-结算单保存调整结算项服务"]["path"]
        data = self.fin_params.get(url, {})
        #过滤请求参数
        filtered_data = ParamUtil.filter_post_body_fields(data, ["id","settItems"], ["params", "request"])
        sett_doc = FinSettlementFactory._insert_settlement_doc("CREATED")
        #获取已创建的结算单id
        filtered_data["params"]["request"]["id"] = sett_doc.get("id")
        
        #获取符合条件的结算行项目类型
        sql =f"""
        select bt_class,sett_class from sett_doc_type_cf where deleted=0 and  id=(select sett_doc_type_id
        from sett_doc_tr where id={filtered_data["params"]["request"]["id"]});
        """
        sql_result = self.db.query(sql)
        sett_class = sql_result[0]["sett_class"]
        bt_class = sql_result[0]["bt_class"]
        sql_sett_item_type = f"""
        select *
        from sett_item_type_cf where deleted=0 and bt_class='{bt_class}'and sett_class='{sett_class}'
        """
        sql_sett_item_type_result = self.db.query(sql_sett_item_type)
        
        
        
        #获取物料
        sql_mat = f"""
            select *
            from gen_mat_md 
            where deleted=0 
            and mat_code like 'AUTOTEST_MAT_RAWM'
        """
        sql_mat_result = self.db.query(sql_mat)
        
        #获取税码
        
        taxcate = 'X' if sett_class=='EXTERNAL' and bt_class=='PURCHASE' else 'J'
        
        sql_tax_code = f"""
            select id, tax_code,tax
            from gen_tax_type_cf
            where deleted=0 and taxcate='{taxcate}'
        """
        sql_tax_code_result = self.db.query(sql_tax_code)
        
        #获取库存组织
        sql="""
            select *
            from org_struct_md 
            where deleted=0 
            and org_code like 'AUTOTEST_INV_ORG'
        """
        invOrgId=self.db.query(sql)[0]["id"]
        
        # 初始化总金额和结算项代码列表
        total_sett_doc_amt = Decimal('0')
        all_sett_item_code = []
        
        # 初始化settItems列表
        item_count = random.randint(2,10)
        filtered_data["params"]["request"]["settItems"] = [{} for _ in range(item_count)]

        for i in range(item_count):
            filtered_data["params"]["request"]["settItems"][i]["basicUnitId"] = {'id': sql_mat_result[0]["base_uom_id"]}
            filtered_data["params"]["request"]["settItems"][i]["invOrgId"] = {'id': invOrgId}
            filtered_data["params"]["request"]["settItems"][i]["matId"] = {'id': sql_mat_result[0]["id"]}
            filtered_data["params"]["request"]["settItems"][i]["remark"] =  f"AUTOTEST-SETTI{int(time.time())}"
            filtered_data["params"]["request"]["settItems"][i]["settItemTypeId"] = {'id': sql_sett_item_type_result[0]["id"]}
            filtered_data["params"]["request"]["settItems"][i]["taxCodeId"] = {'id': sql_tax_code_result[0]["id"]}
            filtered_data["params"]["request"]["settItems"][i]["taxRate"] = sql_tax_code_result[0]["tax"]
            # 生成-1000到1000之间的随机整数
            sett_qty = random.randint(-1000, 1000)
            filtered_data["params"]["request"]["settItems"][i]["settQty"] = sett_qty
            filtered_data["params"]["request"]["settItems"][i]["settItemCode"] = f"AUTOTEST-SETTI{int(time.time())}"
            # 生成1到100之间的随机数，保留6位小数
            filtered_data["params"]["request"]["settItems"][i]["settDocPrice"] = Decimal(str(round(random.uniform(1, 100), 6)))
            filtered_data["params"]["request"]["settItems"][i]["settDocAmt"] = (Decimal(str(sett_qty)) * filtered_data["params"]["request"]["settItems"][i]["settDocPrice"]).quantize(Decimal('0.01'))
            filtered_data["params"]["request"]["settItems"][i]["netBaseAmt"] = (filtered_data["params"]["request"]["settItems"][i]["settDocAmt"]/(Decimal('1')+Decimal(str(sql_tax_code_result[0]["tax"]))*Decimal('0.01'))).quantize(Decimal('0.01'))
            filtered_data["params"]["request"]["settItems"][i]["netDocAmt"] = (filtered_data["params"]["request"]["settItems"][i]["settDocAmt"]/(Decimal('1')+Decimal(str(sql_tax_code_result[0]["tax"]))*Decimal('0.01'))).quantize(Decimal('0.01'))
            filtered_data["params"]["request"]["settItems"][i]["grossBaseAmt"] = (Decimal(str(sett_qty)) * filtered_data["params"]["request"]["settItems"][i]["settDocPrice"]).quantize(Decimal('0.01'))
            filtered_data["params"]["request"]["settItems"][i]["taxAmt"] = (filtered_data["params"]["request"]["settItems"][i]["settDocAmt"]-filtered_data["params"]["request"]["settItems"][i]["netDocAmt"]).quantize(Decimal('0.01'))
            
            total_sett_doc_amt += filtered_data["params"]["request"]["settItems"][i]["settDocAmt"]
            all_sett_item_code.append(filtered_data["params"]["request"]["settItems"][i]["settItemCode"])
        # Loggers.debug(f"total_sett_doc_amt: {total_sett_doc_amt}")
        # Loggers.debug(f"sett_doc.get('sett_doc_amt'): {sett_doc.get('sett_doc_amt')}")
        # Loggers.debug(sett_doc)
        # 转换Decimal为字符串
        def convert_decimal_to_str(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimal_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimal_to_str(item) for item in obj]
            return obj
        
        # 转换请求数据中的Decimal为字符串
        filtered_data = convert_decimal_to_str(filtered_data)
        
        result = self.http.post(url, json=filtered_data, description=f"结算单修改保存")
        
        self.assert_util.assert_response_success(result)
        
        expected_amount = (total_sett_doc_amt.quantize(Decimal('0.01')) + Decimal(str(sett_doc.get("sett_doc_amt")))).quantize(Decimal('0.01'))
        actual_amount = Decimal(str(result.get("data",{}).get("data",{}).get("settDocAmt",{}))).quantize(Decimal('0.01'))
        self.assert_util.assert_eq(actual_amount, expected_amount)
        
        
        sql_sett_item_code = f"""
            select * from sett_item_tr where deleted=0 and sett_item_code in ('{"','".join(all_sett_item_code)}')
        """
        sql_sett_item_code_result = self.db.query(sql_sett_item_code)
        # 断言所有结算项的状态都是SETT_DOC_CREATED
        for item in sql_sett_item_code_result:
            self.assert_util.assert_by_operator(item["sett_item_status"], "=", "SETT_DOC_CREATED")
            self.assert_util.assert_by_operator(item["sett_doc_id"], "=", filtered_data["params"]["request"]["id"])
        
        
        
               
if __name__ == "__main__":
    test = TestSettDocBusiCheck()
    test.setup_class()
    test.test_sett_doc_confirm()
    #FinSettlementFactory._insert_settlement_doc("CREATED")
            
            