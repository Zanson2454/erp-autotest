"""销售订单配置检查测试用例"""

import json
import pytest
from typing import Dict, Any, Optional, List
from pathlib import Path
from loguru import logger
import sys
import os

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))  # 确保转换为字符串
logger.info(f"project_root: {project_root}")

from testcases.comm.base_test import BaseTest
from utils.exception_util import safe_api_call

class TestSalesOrderConfig(BaseTest):
    """销售订单配置检查测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.so_stnd_id = None
    
    @pytest.mark.order(1)
    def test_01_query_order_type(self):
        """查询订单类型配置"""
        # URL和查询参数
        url = "/api/trantor/service/engine/execute/ERP_SCM$SYS_PagingDataService"
        params = {
            "tmodule": "ERP_SCM",
            "modelKey": "ERP_SCM$sls_so_type_cf"
        }
        
        # 构建请求参数
        data = {
            "sceneKey": "ERP_SCM$so_type_cf",
            "viewKey": "ERP_SCM$so_type_cf:list",
            "containerKey": "ERP_SCM$so_type_cf-list-ERP_SCM$sls_so_type_cf",
            "serviceKey": "ERP_SCM$SYS_PagingDataService",
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
        
        # 构建请求头
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'terminus-request-id': self._generate_request_id()
        }
        
        # 发送请求
        try:
            response = self.http.post(
                url=url,
                params=params,
                json=data,
                headers=headers,
                description="查询订单类型"
            )
            
            # 验证响应
            self.assert_util.assert_response_success(response)
            
            # 获取标准订单类型ID
            response_data = response.get("data", {}).get("data", {}).get("data", [])
            stnd_record = next(
                (record for record in response_data if record.get("soTypeCode") == "STND"),
                None
            )
            if stnd_record:
                self.so_stnd_id = stnd_record["id"]
                self.logger.info(f"找到STND记录, ID: {self.so_stnd_id}")
            else:
                self.logger.error("未找到标准订单类型(STND)")
                
            return response
        except Exception as e:
            self.logger.error(f"查询订单类型失败: {str(e)}")
            if hasattr(e, 'response'):
                self.logger.error(f"响应内容: {e.response.text}")
            raise
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        import uuid
        return str(uuid.uuid4())
    
    @pytest.mark.order(2)
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        # 检查并获取标准订单类型ID
        if not self.so_stnd_id:
            self.test_01_query_order_type()
        self.logger.info(f"使用订单类型ID: {self.so_stnd_id}")
        
        # 准备请求参数
        url = "/api/trantor/service/engine/execute/ERP_SCM$SYS_FindDataByIdService"
        params = {
            "tmodule": "ERP_SCM",
            "modelKey": "ERP_SCM$sls_so_type_cf"
        }
        
        data = {
            "sceneKey": "ERP_SCM$so_type_cf",
            "viewKey": "ERP_SCM$so_type_cf:list",
            "containerKey": "ERP_SCM$so_type_cf-detailView-ERP_SCM$sls_so_type_cf-detail",
            "serviceKey": "ERP_SCM$SYS_FindDataByIdService",
            "params": {
                "request": {
                    "id": self.so_stnd_id
                },
                "modelKey": "ERP_SCM$sls_so_type_cf"
            }
        }
        # 发送请求
        try:
            response = self.http.post(
                url=url,
                params=params,
                json=data,
                description="查询订单类型详情"
            )
            self.logger.info(f"响应数据: {response}")
            
            # 验证响应
            self.assert_util.assert_response_success(response)
            
            # 验证详细数据
            response_data = response.get("data", {}).get("data", {})
            assert response_data.get("id") == self.so_stnd_id, "返回的ID与请求的ID不匹配"
            assert response_data.get("soTypeCode") == "STND", "订单类型代码不匹配"
            assert response_data.get("status") == "ENABLED", "订单类型状态不匹配"
            
            # 检查必要字段
            required_fields = ["soTypeCode", "soTypeName", "id", "status"]
            for field in required_fields:
                assert field in response_data, f"缺少必要字段: {field}"
            
            return response
        except Exception as e:
            self.logger.error(f"查询订单类型详情失败: {str(e)}")
            if hasattr(e, 'response'):
                self.logger.error(f"响应内容: {e.response.text}")
            raise

if __name__ == "__main__":
    test = TestSalesOrderConfig()
    test.setup_class()
    test.test_01_query_order_type()
    test.test_02_query_order_type_detail()
