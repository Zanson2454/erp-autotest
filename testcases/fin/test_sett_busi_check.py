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
from testcases.fin.test_sett_check import TestSettlementItem
from data_factory.fin_sett_factory import FinSettlementFactory
from utils.log_util import Loggers
@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettBusiCheck(BaseTest):
    """结算管理业务检查测试用例"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "fin" / "fin_api_path.yaml"
        cls.base_api_params = Path(project_root) / "testdata" / "fin" / "fin_api_params.yaml"
        cls.yaml_util = YamlUtil()  
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})  
    
    
    def get_sett_item_id(self):
        """获取不同状态的结算项ID 已创建，已对账，已汇单 """
        created_sett_item = FinSettlementFactory.get_or_create_settlement_item("CREATED")
        created_sett_item_id = created_sett_item.get("id")
        Loggers.info(f"已创建结算项ID: {created_sett_item_id}")
        
        sett_doc_created_sql="""
            select id
            from sett_item_tr where deleted=0
            and sett_item_status='SETT_DOC_CREATED'
            order by created_at desc;
        """
        
        doc_created_sett_item_id=self.db.query(sett_doc_created_sql)[0]["id"]
        
        return [created_sett_item_id, doc_created_sett_item_id]
    
    @allure.title("结算项对账确认")
    @allure.description("1、新建结算项\n2、对账确认\n3、检查结算单是否生成")
    def test_sett_item_record(self):
        """测试结算项对账确认"""
        # 获取结算项ID列表
        sett_item_ids = self.get_sett_item_id()
        
        # 遍历每个ID进行测试
        for index, sett_item_id in enumerate(sett_item_ids):
            url = self.fin_path["SETT-ITEM-结算项确认及汇单-关联操作-异步服务"]["path"]
            data = self.fin_params.get(url, {})
            data["params"]["request"][0]["id"] = sett_item_id
            result = self.http.post(url, json=data, description=f"结算项对账确认 - ID: {sett_item_id}")
            
            #等待异步任务执行
            time.sleep(3)  # 等待3秒
            
            sql = f"""
                select id, sett_item_status, async_execution_status, sett_doc_id
                from sett_item_tr where deleted=0
                and id={sett_item_id};
            """
            sql_result = self.db.query(sql)
            
            if index == 0:  # 第一个ID的断言
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_eq(sql_result[0]["sett_item_status"], "SETT_DOC_CREATED")
                self.assert_util.assert_eq(sql_result[0]["async_execution_status"], "SUCCEEDED")
                self.assert_util.assert_not_empty(sql_result[0]["sett_doc_id"], "结算单号为空")
            elif index == 1:  # 第二个ID的断言
                assert result.get("success",{}) == False
                assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                self.assert_util.assert_eq(sql_result[0]["sett_item_status"], "SETT_DOC_CREATED")
                self.assert_util.assert_eq(sql_result[0]["async_execution_status"], "SUCCEEDED")
                self.assert_util.assert_not_empty(sql_result[0]["sett_doc_id"], "结算单号为空")
    
    #缺少已对账情况，待补充            
    def test_sett_item_manual_remittance(self):
        """测试结算项手工汇单"""
        url = self.fin_path["SETT-ITEM-结算项手工汇单-关联操作-异步服务"]["path"]
        sett_item_ids = self.get_sett_item_id()
        for index, sett_item_id in enumerate(sett_item_ids):
            data = self.fin_params.get(url, {})
            data["params"]["request"][0]["id"] = sett_item_id
            result = self.http.post(url, json=data, description=f"结算项手工汇单 - ID: {sett_item_id}")
            time.sleep(3)  # 等待3秒
            
            sql = f"""
                select id, sett_item_status, async_execution_status, sett_doc_id
                from sett_item_tr where deleted=0
                and id={sett_item_id};
            """
            sql_result = self.db.query(sql)
            if index == 0 or index == 1:  # 第1.2个ID的断言
                assert result.get("success",{}) == False
                assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
if __name__ == "__main__":
    test = TestSettBusiCheck()
    test.setup_class()
    test.test_sett_item_record()
    #test.test_sett_item_manual_remittance()

        
        