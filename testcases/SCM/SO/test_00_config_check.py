import os
import sys
import json
import pytest
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from testcases.SCM.base_test import BaseTest, DecimalEncoder
from utils.ExceptionUtil import safe_api_call

class TestOrderTypeConfig(BaseTest):
    """订单类型配置测试类"""
    
    def setup_method(self, method=None):
        """每个测试方法执行前的准备工作
        
        Args:
            method: 当前执行的测试方法，可选参数
        """
        # 确保 base_url 已初始化
        if not hasattr(self, 'base_url') or not self.base_url:
            self.setup_class()
            
        # 调用父类的 setup_method
        super().setup_method(method)
        
        # 如果提供了 method 参数，记录方法名
        if method and hasattr(method, '__name__'):
            logger.info(f"开始执行测试方法: {method.__name__}")
        else:
            logger.info("开始执行测试方法")
    
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询订单类型配置失败")
    def test_01_query_order_type(self):
        """测试查询订单类型配置"""
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
        
        # 执行测试
        logger.info(f"\n请求URL: {url}")
        logger.info(f"请求数据: {json.dumps(data, cls=DecimalEncoder, ensure_ascii=False)}")
        
        response = self._make_request(url, data, "查询订单类型配置", extract_nested_data=True)
        
        # 检查响应状态
        if hasattr(response, 'status_code'):
            logger.info(f"响应状态码: {response.status_code}")
            if response.status_code != 200:
                logger.error(f"响应头: {json.dumps(dict(response.headers), ensure_ascii=False)}")
                logger.error(f"响应内容: {json.dumps(response, cls=DecimalEncoder, ensure_ascii=False)}")
                raise AssertionError(f"请求失败，状态码: {response.status_code}")
        
        # 遍历列表查找STND记录
        stnd_record = None
        for item in response:
            if item.get("soTypeCode") == "STND":
                stnd_record = item
                logger.info(f"找到STND记录: {json.dumps(item, cls=DecimalEncoder, ensure_ascii=False)}")
                break
        
        # 断言找到STND记录
        assert stnd_record is not None, "未找到soTypeCode=STND的记录"
        
        # 保存STND记录的ID供后续测试使用
        self.stnd_id = stnd_record['id']
        assert self.stnd_id is not None, "STND记录缺少id字段"
    
    @pytest.mark.order(2)
    @safe_api_call(error_message="查询订单类型详情失败")
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        # 确保第一个测试已经执行并获取了ID
        if not hasattr(self, 'stnd_id'):
            error_msg = "未获取到STND记录的ID，无法执行详情查询测试"
            logger.error(error_msg)

        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_FindDataByIdService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_type_cf"
        
        data = {
            "params": {
                "request": {
                    "id": self.stnd_id
                },
                "modelKey": "ERP_SCM$sls_so_type_cf"
            }
        }

        # 执行测试
        logger.info(f"\n请求URL: {url}")
        logger.info(f"请求数据: {json.dumps(data, cls=DecimalEncoder, ensure_ascii=False)}")
        
        response = self._make_request(url, data, "查询订单类型详情", extract_nested_data=True)
        logger.info(f"响应数据: {json.dumps(response, cls=DecimalEncoder, ensure_ascii=False)}")
        
        # 进行断言
        assert response.get("status") == "ENABLED", f"状态不是ENABLED，实际值：{response.get('status')}"
        assert response.get("btClass") == "SALES", f"业务类型不是SALES，实际值：{response.get('btClass')}"
        assert response.get("isModifyApproval") is False, f"isModifyApproval不是false，实际值：{response.get('isModifyApproval')}"
        assert response.get("isSubmitApproval") is False, f"isSubmitApproval不是false，实际值：{response.get('isSubmitApproval')}"


if __name__ == "__main__":
    # pytest.main(["-v", __file__])
    test = TestOrderTypeConfig()
    test.setup_class()
    test.test_01_query_order_type()
    test.test_02_query_order_type_detail()
    