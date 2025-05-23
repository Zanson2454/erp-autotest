import os
import sys
import json
import pytest
import allure
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


# 添加项目根目录到 Python 路径
project_root =Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from testcases.sls.test_01_create import TestSalesOrderCreate
from utils.exception_util import safe_api_call


class TestOrderDelete(BaseTest):
    """销售订单删除测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        
        # 加载配置文件
        cls.base_api_path = Path(project_root) / "testdata" / "sls" / "sls_api_path.yaml"
        cls.base_config_path = Path(project_root) / "testdata" / "sls" / "so_api_params.yaml"
        
        # 当前用例集所需接口
        cls.so_path = cls.yaml_util.read_yaml(cls.base_api_path)["销售订单"]["订单管理"]
        
        # 当前用例集所需参数
        cls.so_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})
        
        
        cls.so_type_id = cls.ids.get("so_type_id")
        cls.user_id = cls.ids.get("user_id")
    
    
    @allure.title("删除销售订单")
    @allure.description("""
    测试步骤：
    1. 查询待删除的订单
    2. 如果订单不存在，创建新订单
    3. 准备删除请求
    4. 执行删除操作
    5. 验证删除结果
    6. 验证数据库中的删除状态
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="删除销售订单失败")
    def test_01_delete_order(self):
        """测试删除销售订单"""
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
        self.logger.info(f"执行查询: {sql}")
        result = self.db.query(sql, (self.so_type_id, self.user_id))
        self.logger.info(f"查询结果: {result}")
        self.assert_util.assert_not_empty(result, "订单列表")
        # 2. 如果订单不存在，创建新订单
        if not result or len(result) == 0:
            self.logger.info("未找到可删除的订单，创建新订单")
            try:
                test_create = TestSalesOrderCreate()
                test_create.setup_class()
                test_create.test_save_sales_order()
                self.logger.info("成功创建新订单")
                # 重新查询订单
                result = self.db.query(sql, (self.so_type_id, self.user_id))
                self.logger.info(f"创建新订单后查询结果: {result}")
                self.assert_util.assert_not_empty(result, "订单列表")
            except Exception as e:
                self.logger.error(f"创建新订单失败: {str(e)}")
                pytest.fail(f"创建新订单失败: {str(e)}")
        
        order = result[0]
        self.logger.info(f"查询结果: {order}")
        
        # 3. 准备删除请求
        url = self.so_path["删除订单"]
        data = self.so_params.get(url, {})
        data['params']['request']['id'] =  order["id"]
        
        # 4. 执行删除操作
        response = self.http.post(url, json=data, description="删除销售订单")
        
        # 5. 验证删除结果
        self.assert_util.assert_response_success(response)
        self.logger.info(f"成功删除订单: {order['id']}")
        
        # 6. 验证数据库中的删除状态
        verify_sql = """
            SELECT id, deleted
            FROM sls_so_head_tr
            WHERE id = %s
        """
        deleted_record = self.db.query(verify_sql, (order["id"],))
        self.assert_util.assert_not_eq(deleted_record[0]['deleted'], 0, f"订单 {order['id']} 在数据库中未标记为删除状态")
        self.logger.info(f"订单 {order['id']} 在数据库中已标记为删除状态")

    @allure.title("批量删除销售订单")
    @allure.description("""
    测试步骤：
    1. 查询待删除的订单
    2. 如果订单数量不足，创建新订单
    3. 准备批量删除请求
    4. 执行删除操作并验证结果
    5. 验证数据库中的删除状态
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(2)
    @safe_api_call(error_message="批量删除销售订单失败")
    def test_02_batch_delete_orders(self):
        """测试批量删除销售订单"""
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
        self.logger.info(f"执行查询: {sql}")
        result = self.db.query(sql, (self.so_type_id, self.user_id))
        
        # 2. 如果订单数量不足，创建新订单
        if len(result) < 2:
            self.logger.info(f"当前只有 {len(result)} 条订单，需要创建 {2 - len(result)} 条新订单")
            for i in range(2 - len(result)):
                try:
                    test_create = TestSalesOrderCreate()
                    test_create.setup_class()
                    test_create.test_save_sales_order()
                    self.logger.info(f"成功创建第 {i+1} 条新订单")
                except Exception as e:
                    self.logger.error(f"创建新订单失败: {str(e)}")
                    pytest.fail(f"创建新订单失败: {str(e)}")
            
            # 重新查询订单
            result = self.db.query(sql, (self.so_type_id, self.user_id))
            self.assert_util.assert_true(len(result) >= 2, f"创建订单后仍然不足2条，当前有 {len(result)} 条订单")
        
        # 3. 准备批量删除请求
        order_ids = [order['id'] for order in result]
        self.logger.info(f"准备删除的订单ID: {order_ids}")
        
        # 更新测试数据
        self.test_data["order_ids"] = order_ids
        self.test_data["order_codes"] = [order['so_code'] for order in result]
        self.logger.info(f"测试数据: {self.test_data}")
        
        delete_url = self.so_path["批量删除订单"]
        delete_data = self.so_params.get(delete_url, {})
        delete_data['params']['request']['ids'] = self.test_data['order_ids']
        self.logger.info(f"删除请求数据: {delete_data}")
        
        # 4. 执行删除操作
        self.logger.info(f"开始批量删除订单")
        response = self.http.post(delete_url, json=delete_data, description="批量删除销售订单")
        
        # 5. 验证删除结果
        self.assert_util.assert_response_success(response)
        self.logger.info(f"成功批量删除订单，订单ID: {self.test_data['order_ids']}")
        
        # 6. 验证数据库中的删除状态
        verify_sql = """
            SELECT id, deleted
            FROM sls_so_head_tr
            WHERE id IN %s
        """
        deleted_records = self.db.query(verify_sql, (tuple(self.test_data['order_ids']),))
        self.logger.info(f"删除记录: {deleted_records}")
        
        # 验证每个订单的删除状态
        for record in deleted_records:
            self.assert_util.assert_not_eq(record['deleted'], 0, f"订单 {record['id']} 在数据库中未标记为删除状态")
        
        self.logger.info("所有订单在数据库中已标记为删除状态")


if __name__ == "__main__":
    test = TestOrderDelete()
    test.setup_class()
    test.test_01_delete_order()
    # test.test_02_batch_delete_orders()
  
