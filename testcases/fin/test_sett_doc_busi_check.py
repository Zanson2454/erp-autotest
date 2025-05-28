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
        Loggers.info(f"已创建结算单ID: {created_sett_doc_id}")
        
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
        
    # todo 
    def test_sett_doc_remark(self):
        """测试结算单修改备注操作"""
        url = self.fin_path["结算单表-根据ID查找无行信息数据服务"]["path"]
        data = self.fin_params.get(url, {})
        filtered_data = ParamUtil.filter_post_body_fields(data, ["id"], ["params", "request"])
        print(filtered_data)
        
    @allure.story("结算单确认")
    def test_sett_doc_confirm(self):
        """测试结算单确认"""
        url = self.fin_path["SETT-DOC-运营端结算单确认下推应收应付-异步服务"]["path"]
        data = self.fin_params.get(url, {})
        sett_doc_ids  = self.get_sett_doc_id()
        for index, sett_doc_id in enumerate(sett_doc_ids):
            data["params"]["request"]["id"][0] = sett_doc_id
            result = self.http.post(url, json=data, description=f"结算单确认 - ID: {sett_doc_id}")
            time.sleep(2)
            if index == 0:
                sql = f"""
                select sett_doc_status,async_execution_status,trading_doc_id,trading_doc_status,trading_doc_code,client_side_confirm_status
                from sett_doc_tr where deleted=0 and id={sett_doc_id}
                """
                sql_result = self.db.query(sql)
                self.assert_util.assert_response_success(result)
                self.assert_util.assert_eq(sql_result[0]["sett_doc_status"], "CONFIRMED")
                self.assert_util.assert_eq(sql_result[0]["async_execution_status"], "SUCCEEDED")
                self.assert_util.assert_not_empty(sql_result[0]["trading_doc_id"], "往来单号id为空")
                self.assert_util.assert_eq(sql_result[0]["trading_doc_status"], "CREATED")
                self.assert_util.assert_not_empty(sql_result[0]["trading_doc_code"], "往来单号code为空")
                self.assert_util.assert_eq(sql_result[0]["client_side_confirm_status"], "CONFIRMED")
            elif index == 1:
                assert result.get("success",{}) == False
                assert result.get("err",{}).get("msg",{}) == "结算单异步任务提交失败，请确认结算单异步执行状态！"
                
    def test_cancel_sett_doc(self):
        """测试结算单取消汇单"""
        url = self.fin_path["SETT-DOC-结算单取消服务"]["path"]
        data = self.fin_params.get(url, {})
        sett_doc_ids  = self.get_sett_doc_id()
        for index, sett_doc_id in enumerate(sett_doc_ids):
            
            # 获取已经汇单的结算单对应的结算项的id
            sett_item_sql=f"""
                select * from sett_item_tr where sett_doc_id={sett_doc_id}
                """
            sett_item_sql_result = self.db.query(sett_item_sql)
            
            # 取消汇单接口
            data["params"]["request"][0]["id"] = sett_doc_id
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
                self.assert_util.assert_not_eq(sql_result[0]["deleted"], 0)
                self.assert_util.assert_eq(sett_sql_result[0]["sett_item_status"], "RECONCILED")
                self.assert_util.assert_eq(sett_sql_result[0]["sett_doc_id"], None)
                self.assert_util.assert_eq(sett_sql_result[0]["is_sdc_cancel_relv"], 1)
            elif index == 1:
                assert result.get("success",{}) == False
                assert result.get("err",{}).get("msg",{}) == "存在已确认的结算单，请重新选择后再进行操作"
            
if __name__ == "__main__":
    test = TestSettDocBusiCheck()
    test.setup_class()
    test.test_sett_doc_remark()
            
            