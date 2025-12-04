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
from utils.report_util import a, case_decorator
class TestPiSbBusiCheck(BaseTest):
    """发票管理业务测试用例"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "erp_fin" / "fin_api_path.yaml"
        cls.base_api_params = Path(project_root) / "testdata" / "erp_fin" / "fin_api_params.yaml"
        cls.yaml_util = YamlUtil()  
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})
    
    @case_decorator(
        story="发票管理",
        title="测试基于应付单创建发票操作",
        description="测试基于应付单创建发票操作",
        severity="critical",
        order=0,
        smoke=False,
        tags=["发票管理", "创建发票","FIN_APM_AP_ITEM_TR_PAGING_DATA_SERVICE_PmHKWs1"]
    )
    def test_create_pi_by_api(self):
        url=self.fin_path["应付单行-分页数据服务_PmHKWs1"]["path"]
        data=self.fin_params.get(url, {})
        data=ParamUtil.filter_post_body_fields(
            data, 
            ["pageNo","pageSize"],
            ["params","request","pageable"])
        set_dict = {
            "pageNo":"1",
            "pageSize":"20"
        }
        ParamUtil.set_request_params(data, set_dict)
        result=self.http.post(url, json=data, description="基于应付单创建发票操作")
        self.assert_util.assert_response_success(result)
        assert result.get("data",{}).get("data",{}).get("total",{}) >= 0
        
if __name__ == "__main__":
    test = TestPiSbBusiCheck()
    test.setup_class()
    test.test_create_pi_by_api()
        
        
        
        