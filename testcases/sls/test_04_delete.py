import os
import sys
import json
import pytest
import allure
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.yaml_util import YamlUtil
from testcases.comm.base_test import BaseTest, DecimalEncoder
from utils.exception_util import safe_api_call
from testcases.sls.test_01_create import TestSalesOrderCreate
from utils.assert_util import AssertHelper
from utils.http_util import HttpUtil

class TestOrderDelete(BaseTest):
    """销售订单删除测试类"""
    
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
        self.http_util = HttpUtil()
        # 初始化测试数据，但保留已有的数据
        if not hasattr(self, 'test_data') or not self.test_data:
            # 如果类属性中有测试数据，使用类属性中的数据
            if hasattr(TestOrderDelete, 'test_data') and TestOrderDelete.test_data:
                self.test_data = TestOrderDelete.test_data
                self.log.info("使用类属性中的测试数据")
            else:
                self.test_data = {
                    "so_id": None,
                    "so_code": None
                }
                self.log.info("初始化新的测试数据")
        
        # 如果提供了 method 参数，记录方法名
        if method and hasattr(method, '__name__'):
            self.log.info(f"开始执行测试方法: {method.__name__}")
        else:
            self.log.info("开始执行测试方法")
            
        self.log.info("初始化测试数据完成")
    
    def _build_delete_order_data(self, order_id: str) -> Dict[str, Any]:
        """构建删除销售订单的请求数据
        
        Args:
            order_id: 要删除的订单ID
            
        Returns:
            Dict[str, Any]: 删除订单的请求数据
        """
        return {
            "params": {
                "request": {
                    "id": order_id
                },
                "modelKey": "ERP_SCM$sls_so_head_tr"
            }
        }

    @allure.title("删除销售订单")
    @allure.description("""
    测试步骤：
    1. 删除销售订单
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="删除销售订单失败")
    def test_01_delete_order(self):
        """测试删除销售订单
        
        Steps:
        1. 查询待删除的订单
        2. 如果订单不存在，创建新订单
        3. 准备删除请求
        4. 执行删除操作
        5. 验证删除结果
        6. 验证数据库中的删除状态
        """
        # 1. 查询待删除的订单
        sql = """
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE so_status = 'DRAFT' 
                AND so_type_id = %s
                AND created_by = %s
                AND deleted = 0 
            ORDER BY created_at DESC
            LIMIT 1
        """
        self.log.info(f"执行查询: {sql}")
        result = self.db.execute_query(sql, (self.so_type_id, self.user_id))
        
        # 2. 如果订单不存在，创建新订单
        if not result or len(result) == 0:
            self.log.info("未找到可删除的订单，创建新订单")
            try:
                test_create = TestSalesOrderCreate()
                test_create.setup_class()
                test_create.test_08_save_sales_order()
                self.log.info("成功创建新订单")
                # 重新查询订单
                result = self.db.execute_query(sql, (self.so_type_id, self.user_id))
                self.assert_util.assert_list_not_empty(result, "订单列表")
            except Exception as e:
                self.log.error(f"创建新订单失败: {str(e)}")
                pytest.fail(f"创建新订单失败: {str(e)}")
        
        order = result[0]
        self.order_id = order["id"]
        self.so_code = order["so_code"]
        # 添加URL参数
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_DeleteDataByIdService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_head_tr"
        
        # 构建删除订单的请求数据
        data = self._build_delete_order_data(self.order_id)
        
        # 4. 执行删除操作
        self.log.info(f"准备删除订单: ID = {self.order_id}, 编号 = {self.so_code}")
        response = self.http.post(url, json=data, description="删除销售订单")
        
        # 5. 验证删除结果
        self.log.info(f"成功删除订单: {self.order_id}")
        
        # 6. 验证数据库中的删除状态
        verify_sql = """
            SELECT id, deleted
            FROM sls_so_head_tr
            WHERE id = %s
        """
        deleted_record = self.db.execute_query(verify_sql, (self.order_id,))
        self.log.info(f"删除记录: {deleted_record}")
        if deleted_record[0]['deleted'] !=0:
            self.log.info(f"订单 {self.order_id} 在数据库中已标记为删除状态")
        else:
            self.log.error(f"订单 {self.order_id} 在数据库中未标记为删除状态")
            pytest.fail(f"订单 {self.order_id} 在数据库中未标记为删除状态")

    @allure.title("批量删除销售订单")
    @allure.description("""
    测试步骤：
    1. 批量删除销售订单
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(2)
    @safe_api_call(error_message="批量删除销售订单失败")
    def test_02_batch_delete_orders(self):
        """测试批量删除销售订单
        
        Steps:
        1. 查询待删除的订单
        2. 如果订单数量不足，创建新订单
        3. 准备批量删除请求
        4. 执行删除操作并验证结果
        
        Returns:
            None
        """
        # 1. 查询待删除的订单
        sql = """
            SELECT id, so_code, so_status, deleted
            FROM sls_so_head_tr 
            WHERE so_status = 'DRAFT' 
                AND so_type_id = %s
                AND created_by = %s
                AND deleted = 0 
            ORDER BY created_at DESC
            LIMIT 2
        """
        self.log.info(f"执行查询: {sql}")
        result = self.db.execute_query(sql, (self.so_type_id, self.user_id))
        
        # 2. 如果订单数量不足，创建新订单
        if len(result) < 2:
            self.log.info(f"当前只有 {len(result)} 条订单，需要创建 {2 - len(result)} 条新订单")
            for i in range(2 - len(result)):
                try:
                    test_create = TestSalesOrderCreate()
                    test_create.setup_class()
                    test_create.test_save_sales_order()
                    self.log.info(f"成功创建第 {i+1} 条新订单")
                except Exception as e:
                    self.log.error(f"创建新订单失败: {str(e)}")
                    pytest.fail(f"创建新订单失败: {str(e)}")
            
            # 重新查询订单
            result = self.db.execute_query(sql, (self.so_type_id, self.user_id))
            if len(result) < 2:
                pytest.fail(f"创建订单后仍然不足2条，当前有 {len(result)} 条订单")
        
        # 3. 准备批量删除请求
        order_ids = [order['id'] for order in result]
        self.log.info(f"准备删除的订单ID: {order_ids}")
        
        delete_url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$sales_order_batch_delete_service"
        delete_data = {
            "params": {
                "request": {
                    "ids": order_ids
                }
            }
        }
        
        # 4. 执行删除操作
        self.log.info(f"开始批量删除订单")
        response = self.http.post(delete_url, json=delete_data, description="批量删除销售订单")
        
        # 5. 验证删除结果
        assert response.get("success", False), "批量删除订单失败"
        self.log.info(f"成功批量删除订单，订单ID: {order_ids}")
        
        # 6. 验证数据库中的删除状态
        verify_sql = """
            SELECT id, deleted
            FROM sls_so_head_tr
            WHERE id IN %s
        """
        deleted_records = self.db.execute_query(verify_sql, (tuple(order_ids),))
        assert all(record['deleted'] != 0 for record in deleted_records), "部分订单未成功删除"
        self.log.info("所有订单在数据库中已标记为删除状态")


if __name__ == "__main__":
    test = TestOrderDelete()
    test.setup_class()
    test.test_01_delete_order()
    test.test_02_batch_delete_orders()
  
