import pytest
import os
import sys
import allure
from pathlib import Path
from datetime import datetime

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("ERP通业财模块")
@allure.feature("结算管理")
class TestSettConfig(BaseTest):
    """结算配置测试用例"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.base_api_path = Path(project_root) / "testdata" / "erp_fin" / "fin_api_path.yaml"
        cls.base_api_params = Path(project_root) / "testdata" / "erp_fin" / "fin_api_params.yaml"
        cls.yaml_util = YamlUtil()
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})

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
        url=self.fin_path["结算价格组-保存主数据服务"]["path"]
        data=self.fin_params.get(url,{})
        data=ParamUtil.filter_post_body_fields(
            data,
            ["spgCode","spgName"],
            ["params","request"])
        now_str = datetime.now().strftime("%Y%m%d%H%M%S")
        set_dict={
            "spgCode":f"AUTO-TEST-CODE-{now_str}",
            "spgName":f"AUTO-TEST-NAME-{now_str}"
        }
        ParamUtil.set_request_params(data,set_dict)
        result=self.http.post(url,json=data,description=f"新增结算价格组")
        self.assert_util.assert_response_success(result)
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("spgCode",{}),"=",set_dict["spgCode"])
        self.assert_util.assert_by_operator(result.get("data",{}).get("data",{}).get("spgName",{}),"=",set_dict["spgName"])
        a.json(data, "请求数据")
        a.json(result, "响应数据")
        
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
        url=self.fin_path["结算类型-保存主数据服务"]["path"]
        data=self.fin_params.get(url,{})
        pass


if __name__ == "__main__":
    test = TestSettConfig()
    test.setup_class()
    test.test_add_sett_price_group()
