"""销售订单配置检查测试用例"""

import pytest
from pathlib import Path
from loguru import logger
import sys
import allure

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.exception_util import safe_api_call

class TestSalesOrderConfig(BaseTest):
    """销售订单配置检查测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.so_stnd_id = None
        cls.yaml_util = YamlUtil()
        # 加载配置文件
        cls.base_api_path = project_root / "testdata" / "sls" / "sls_api_path.yaml"
        cls.base_config_path = project_root / "testdata" / "sls" / "so_api_params.yaml"
        
        # 当前 case 要覆盖的接口
        cls.so_path = cls.yaml_util.read_yaml(cls.base_api_path)["销售订单"]["销售配置"]
        cls.so_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})

    @allure.title("查询订单类型配置")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型配置请求
    2. 验证响应状态
    3. 获取标准订单类型ID
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询订单类型配置失败")
    def test_01_query_order_type(self):
        """查询订单类型配置"""
        url = self.so_path["查询订单类型配置"]
        data = self.so_params.get(url, {})
        response = self.http.post(
            url=url,
            json=data,
            description="查询订单类型"
        )
        
        self.assert_util.assert_response_success(response)
        
        # 获取标准订单类型ID
        response_data = response.get("data", {}).get("data", {}).get("data", [])
        stnd_record = next(
            (record for record in response_data if record.get("soTypeCode") == "STND"),
            None
        )
        
        if stnd_record:
            self.so_stnd_id = stnd_record["id"]
            self.logger.info(f"标准订单类型ID: {self.so_stnd_id}")
        else:
            self.logger.error("未找到标准订单类型(STND)")
        
        return response

    @allure.title("查询订单类型详情")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型详情请求
    2. 验证响应状态
    3. 验证订单类型详情数据
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(2)
    @safe_api_call(error_message="查询订单类型详情失败")
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        if not self.so_stnd_id:
            self.test_01_query_order_type()
            
        self.logger.info(f"使用订单类型ID: {self.so_stnd_id}")
        url = self.so_path["查询订单类型详情"]
        data = self.so_params.get(url, {})
        data['params']['request']['id'] = self.so_stnd_id
        response = self.http.post(
            url=url,
            json=data,
            description="查询订单类型详情"
        )
        
        self.assert_util.assert_response_success(response)
        
        # 验证响应数据
        response_data = response.get("data", {}).get("data", {})
        assert response_data.get("id") == self.so_stnd_id, "返回的ID与请求的ID不匹配"
        assert response_data.get("soTypeCode") == "STND", "订单类型代码不匹配"
        assert response_data.get("status") == "ENABLED", "订单类型状态不匹配"           
        return response

if __name__ == "__main__":
    # test = TestSalesOrderConfig()
    # test.setup_class()
    # test.test_01_query_order_type()
    # test.test_02_query_order_type_detail()
    
    allure_dir = Path(project_root) / "reports" / "allure-results"
    pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])
