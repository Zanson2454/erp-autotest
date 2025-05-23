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
        
    def test_sett_item_record(self):
        """测试结算项对账确认"""
        # 调用 test_add_sett_item 方法 新建一条结算项使用新建结算项进行对账确认
        sett_item = TestSettlementItem()
        sett_item.setup_class()
        sett_item_id = sett_item.test_add_sett_item()
        
        url = self.fin_path["SETT-ITEM-结算项确认及汇单-关联操作-异步服务"]["path"]
        data = self.fin_params.get(url, {})
        data["params"]["request"][0]["id"] = sett_item_id
        result=self.http.post(url, json=data, description="结算项对账确认")
        
        #等待异步任务执行
        time.sleep(3)  # 等待3秒
        
        sql=f"""
            select id, sett_item_status, async_execution_status, sett_doc_id
            from sett_item_tr where deleted=0
            and id={sett_item_id};
        """
        sql_result=self.db.query(sql)
        self.assert_util.assert_response_success(result)
        self.assert_util.assert_eq(sql_result[0]["sett_item_status"], "SETT_DOC_CREATED")
        self.assert_util.assert_eq(sql_result[0]["async_execution_status"], "SUCCEEDED")
        self.assert_util.assert_not_empty(sql_result[0]["sett_doc_id"], "结算单号为空")
        
if __name__ == "__main__":
    test = TestSettBusiCheck()
    test.setup_class()
    test.test_sett_item_record()

        
        