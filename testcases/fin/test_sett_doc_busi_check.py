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
        sql = """
        (
            SELECT * FROM sett_doc_tr
            WHERE deleted = 0 AND sett_doc_status = 'CREATED'
            ORDER BY created_at DESC
            LIMIT 1
        )
            UNION ALL
        (
            SELECT * FROM sett_doc_tr
            WHERE deleted = 0 AND sett_doc_status = 'CONFIRMED'
            ORDER BY created_at DESC
            LIMIT 1
        )
        ORDER BY created_at,sett_doc_status DESC 
        """
        result = self.db.query(sql)
        return [result[0]["id"],result[1]["id"]]
        
    # todo 
    def test_sett_doc_remark(self):
        """测试结算单修改备注"""

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
if __name__ == "__main__":
    test = TestSettDocBusiCheck()
    test.setup_class()
    test.test_sett_doc_confirm()
            
            