import os
import sys
import json
import pytest
import allure
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from testcases.SCM.base_test import BaseTest, DecimalEncoder
from utils.ExceptionUtil import safe_api_call

@allure.epic("SCM")
@allure.feature("SO")
@allure.story("订单类型配置")
class TestOrderTypeConfig(BaseTest):
    """订单类型配置测试类"""
    
    def setup_class(self):
        """测试类初始化"""
        super().setup_class()
        self.so_stnd_id = None
    
    @pytest.mark.order(1)
    @allure.title("查询订单类型")
    def test_01_query_order_type(self):
        """测试查询订单类型"""
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_PagingDataService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_type_cf"
        data = {
            "params": {
                "request": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "conditionItems": None
                    }
                },
                "modelKey": "ERP_SCM$sls_so_type_cf"
            }
        }
        
        response = self._make_request(url, data, "查询订单类型",extract_nested_data=True)
    
        
        # 检查响应结构并提取数据
        for record in response:
            if record.get("soTypeCode") == "STND":
                self.so_stnd_id = record['id']
                logger.info(f"找到STND记录, ID: {self.so_stnd_id}")
                break
        assert self.so_stnd_id is not None, "未找到STND记录"
    
    @pytest.mark.order(2)
    @allure.title("查询订单类型详情")
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        logger.info(f"self.so_stnd_id: {self.so_stnd_id}")
        if not self.so_stnd_id:
           self.test_01_query_order_type()
            
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_FindDataByIdService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_type_cf"
        data = {
            "params": {
                "request": {
                    "id": self.so_stnd_id
                },
                "modelKey": "ERP_SCM$sls_so_type_cf"
            }
        }
        
        response = self._make_request(url, data, "查询订单类型详情",extract_nested_data=True)
        logger.info(f"response: {response}")
    
        assert response is not None, "响应数据为空"
        assert response["id"] == self.so_stnd_id, "返回的ID与请求的ID不匹配"
        assert response["soTypeCode"] == "STND", "订单类型代码不匹配"
        assert response["status"] == "ENABLED", "订单类型状态不匹配"
    
if __name__ == "__main__":
    pytest.main(["-v", __file__])
    # test = TestOrderTypeConfig()
    # test.setup_class()
    # test.test_01_query_order_type()
    # test.test_02_query_order_type_detail()
