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
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.param_util import ParamUtil
from data_factory.fin_sett_factory import FinSettlementFactory
from utils.log_util import Loggers
@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettDocCheck(BaseTest):
    """结算单测试用例"""
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "erp_fin" / "fin_api_path.yaml"
        
        cls.base_api_params = Path(project_root) / "testdata" / "erp_fin" / "fin_api_params.yaml"
        
        cls.yaml_util = YamlUtil()
        
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})

        
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})  
        
    @allure.title("查询结算单详情")
    @allure.description("测试步骤：查询结算单详情")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_detail(self):
        """测试查询结算单详情"""
        url = self.fin_path["结算单表-根据ID查找数据服务"]["path"]
        data = self.fin_params.get(url, {})
        filtered_data = ParamUtil.filter_post_body_fields(data, ["id"], ["params", "request"])
        filtered_data["params"]["request"]["id"] = FinSettlementFactory.get_or_create_settlement_doc("CREATED").get("id")
        result = self.http.post(url, json=filtered_data, description=f"查询结算单详情")
        self.assert_util.assert_response_success(result)
        #self.assert_util.assert_eq(result.get("data",{}).get("data",{}).get("id",{}),filtered_data["params"]["request"]["id"])
        #self.assert_util.assert_not_empty(result.get("data",{}).get("data",{}).get("settItems",{}),"结算单明细为空")
    
        
        
if __name__ == "__main__":
    test = TestSettDocCheck()
    test.setup_class()
    test.test_search_detail()