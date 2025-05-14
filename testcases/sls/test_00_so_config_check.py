"""销售订单配置检查测试用例"""

import pytest
from pathlib import Path
from loguru import logger
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil

class TestSalesOrderConfig(BaseTest):
    """销售订单配置检查测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.so_stnd_id = None
        cls.yaml_util = YamlUtil()
        cls._build_params()
    
    @classmethod
    def _replace_template(cls, data: dict, variables: dict) -> None:
        """递归替换字典中的模板变量"""
        for key, value in data.items():
            if isinstance(value, dict):
                cls._replace_template(value, variables)
            elif isinstance(value, str):
                data[key] = value.format(**variables)
    
    @classmethod
    def _build_params(cls):    
        # 加载配置文件
        api_path = Path(project_root) / "testdata" / "sls" / "so_api.yaml"
        config_path = Path(project_root) / "testdata" / "sls" / "so_config.yaml"
        
        cls.api_path = cls.yaml_util.read_yaml(api_path)["销售订单"]["销售配置"]
        cls.params = cls.yaml_util.read_yaml(config_path)
        
        # 替换所有模板变量
        variables = {
            "tmodule": cls.api_path["tmodule"],
            "modelKey": cls.api_path["modelKey"]
        }
        cls._replace_template(cls.params, variables)
        logger.info(f"Parameters after replacement: {cls.params}")
    
    @pytest.mark.order(1)
    def test_01_query_order_type(self):
        """查询订单类型配置"""
        try:
            response = self.http.post(
                url=self.api_path["查询订单类型配置"],
                params=self.params['sys_params'],
                json=self.params['page_data'],
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
            
        except Exception as e:
            self.logger.error(f"查询订单类型失败: {str(e)}")
            if hasattr(e, 'response'):
                self.logger.error(f"响应内容: {e.response.text}")
            raise
    
    @pytest.mark.order(2)
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        if not self.so_stnd_id:
            self.test_01_query_order_type()
            
        self.logger.info(f"使用订单类型ID: {self.so_stnd_id}")
        self.params['detail_data']['params']['request']['id'] = self.so_stnd_id
        
        try:
            response = self.http.post(
                url=self.api_path["查询订单类型详情"],
                params=self.params['sys_params'],
                json=self.params['detail_data'],
                description="查询订单类型详情"
            )
            
            self.assert_util.assert_response_success(response)
            
            # 验证响应数据
            response_data = response.get("data", {}).get("data", {})
            assert response_data.get("id") == self.so_stnd_id, "返回的ID与请求的ID不匹配"
            assert response_data.get("soTypeCode") == "STND", "订单类型代码不匹配"
            assert response_data.get("status") == "ENABLED", "订单类型状态不匹配"           
            return response
            
        except Exception as e:
            self.logger.error(f"查询订单类型详情失败: {str(e)}")
            if hasattr(e, 'response'):
                self.logger.error(f"响应内容: {e.response.text}")
            raise

if __name__ == "__main__":
    # test = TestSalesOrderConfig()
    # test.setup_class()
    # test.test_01_query_order_type()
    # test.test_02_query_order_type_detail()
    
    allure_dir = Path(project_root) / "reports" / "allure-results"
    pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])
