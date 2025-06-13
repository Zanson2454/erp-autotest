import os
import sys
import json
import pytest
import allure
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
# 添加项目根目录到 Python 路径


project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))



from utils.yaml_util import YamlUtil
from utils.exception_util import  safe_api_call, handle_class_method_exception
from testcases.comm.base_test import BaseTest
from utils.response_util import ResponseUtil
from testcases.sls.test_01_create import TestSalesOrderCreate
from testcases.sls import SlsBase
class TestSalesOrderOperator(BaseTest,SlsBase):
    """销售订单操作测试类"""
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls):
        """测试类初始化，获取必要的ID和配置信息"""
        super().setup_class()
        
        # 初始化测试数据
        cls.order_id = None
        cls.so_data = None
        cls.user_id = cls.init_data["user_info"]["user_info"]["id"]
        cls.so_type_id = cls.init_data["base_info"]["so_type_info"]["id"]
        cls.logger.info("测试类初始化完成")
        cls.response_util = ResponseUtil()
        cls.test_create = TestSalesOrderCreate()
        cls.test_create.setup_class()
        
    def setup_method(self, method):
        """每个测试方法执行前的准备工作"""
        self.logger.info(f"开始执行测试方法: {method.__name__}")
        # 确保每个测试方法都有独立的订单数据
        self.order_id = None
        self.so_data = None

    def teardown_method(self, method):
        """每个测试方法执行后的清理工作"""
        self.logger.info(f"测试方法 {method.__name__} 执行完成")

    def _query_draft_orders_from_db(self) -> Dict[str, Any]:
        """从数据库查询草稿态订单
        
        Returns:
            Dict[str, Any]: 订单数据，包含id、so_code和so_status
        """
        sql = """
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE created_by = %s
                AND so_status = 'DRAFT'
                AND deleted = 0 
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        self.logger.info(f"执行查询草稿态订单: {sql}")
        result = self.db.query(sql, (self.user_info['id'],))
        
        if not result or len(result) == 0:
            self.logger.error("未找到草稿态订单")
            return {}
        
        order = result[0]
        self.test_data = {
            "so_id": str(order["id"]),
            "so_code": order["so_code"],
            "so_status": order["so_status"]
        }
        
        self.logger.info(f"查询到的草稿态订单数据: {json.dumps(self.test_data, ensure_ascii=False, indent=2)}")
        return self.test_data

    def _query_effective_orders_from_db(self) -> Dict[str, Any]:
        """从数据库查询生效态订单
        
        Returns:
            Dict[str, Any]: 订单数据，包含id、so_code和so_status
        """
        sql = """
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE created_by = %s
                AND so_status = 'EFFECT'
                AND deleted = 0 
            ORDER BY created_at DESC
            LIMIT 1
        """
        
        self.logger.info(f"执行查询生效态订单: {sql}")
        result = self.db.query(sql, (self.user_info['id'],))
        
        if not result or len(result) == 0:
            self.logger.error("未找到生效态订单")
            return {}
        
        order = result[0]
        self.test_data = {
            "so_id": str(order["id"]),
            "so_code": order["so_code"],
            "so_status": order["so_status"]
        }
        
        self.logger.info(f"查询到的生效态订单数据: {json.dumps(self.test_data, ensure_ascii=False, indent=2)}")
        return self.test_data

    @allure.title("查询销售订单详情")
    @allure.description("测试查询销售订单详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询销售订单详情失败")
    def test_01_query_order_detail(self):
        """测试查询销售订单详情"""
        # 查询草稿态订单
        draft_order = self._query_draft_orders_from_db()
        if not draft_order:
            raise ValueError("未找到草稿态订单")
            
        self.order_id = draft_order["so_id"]
        
        # 构建请求URL
        url = self.sls_api_paths["订单管理"]["查询订单详情"]
        data = self.sls_api_params[url]
        data["params"]["request"]["id"] = self.order_id
        
        # 发送请求
        self.logger.info(f"查询订单详情请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        result = self.http.post(url, json=data, description="订单详情查询")
        self.logger.info(json.dumps(result, ensure_ascii=False, indent=2))
        
        # 保存订单详情数据
        self.so_data = result
        assert self.so_data is not None, "获取订单详情失败"
        assert "data" in self.so_data, "订单详情数据格式错误"

    @allure.title("销售订单编辑")
    @allure.description("测试销售订单编辑")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(2)
    @safe_api_call(error_message="销售订单编辑失败")
    def test_02_sales_order_edit(self):
        """测试编辑销售订单"""
        # 查询草稿态订单
        draft_order = self._query_draft_orders_from_db()
        if not draft_order:
            raise ValueError("未找到草稿态订单")
            
        self.order_id = draft_order["so_id"]
        original_so_code = draft_order["so_code"]
        
        # 构造请求数据
        request_data = {
            "sceneKey": "ERP_SCM$sls_so_730",
            "viewKey": "ERP_SCM$sls_so_730:edit",
            "appId": 0,
            "teamId": 22,
            "serviceKey": "ERP_SCM$query_sls_order_bom_detail",
            "params": {
                "id": str(self.order_id)    
            }
        }
        
        # 编辑订单
        url = self.sls_api_paths["订单管理"]["编辑订单"]
        data = self.sls_api_params[url]
        data.update(request_data)
        
        result = self.http.post(url, json=data, description="编辑订单")
        assert result is not None, "编辑销售订单失败"
        assert result.get('success', False), f"编辑销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单
        new_so_code = result['data']['data']['soCode']
        self.so_data = result['data']['data']
        assert new_so_code is not None, "响应中未找到新订单号"
        
    @allure.title("销售订单编辑提交")
    @allure.description("测试销售订单编辑提交")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(2)
    @safe_api_call(error_message="销售订单编辑提交失败")
    def test_03_submit_sales_order_edit(self):
        """测试销售订单编辑提交"""
        # 编辑订单
        self.test_02_sales_order_edit()

       # 构造请求数据
        request_data = {
            "params": {
                "request": {
                    **self.so_data,
                    "syncSubmit": True
                }
            }
        }
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["编辑页提交"]
        data = self.sls_api_params[url]
        data["params"]["request"] = request_data["params"]["request"]
        
        result = self.http.post(url, json=data, description="提交复制订单")
        assert result is not None, "提交复制的销售订单失败"
        assert result.get('success', False), f"提交复制的销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单状态
        new_so_code = result['data']['data']['soCode']
        assert new_so_code == self.so_data['soCode'], f"订单号不匹配: 期望={self.so_data['soCode']}, 实际={new_so_code}"
        
        so_status = self.db.query(f"select id,so_code,so_status from sls_so_head_tr where so_code='{new_so_code}'")
        assert so_status[0]['so_status'] == 'EFFECT', "复制订单提交失败"

    @allure.title("销售订单列表提交")
    @allure.description("测试销售订单列表提交")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(3)
    @safe_api_call(error_message="销售订单列表提交失败")
    def test_04_manual_submit_sales_order(self):
        """测试销售订单列表提交"""
        # 查询草稿态订单
        draft_order = self._query_draft_orders_from_db()
        if not draft_order:
            raise ValueError("未找到草稿态订单")
            
        self.order_id = draft_order["so_id"]
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["提交订单"]
        data = self.sls_api_params[url]
        data["params"]["request"] = {"id": self.order_id}
        
        result = self.http.post(url, json=data, description="销售订单手动提交")
        assert result is not None, "销售订单列表提交失败"
        assert result.get('success', False), f"销售订单列表提交失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单状态
        so_status = self.db.query(f"select id,so_code,so_status from sls_so_head_tr where id={self.order_id}")
        assert so_status[0]['so_status'] == 'EFFECT', "销售订单提交失败"

    @allure.title("取消提交销售订单")
    @allure.description("测试取消提交销售订单")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(4)
    @safe_api_call(error_message="取消提交销售订单失败")
    def test_05_cancel_submit_sales_order(self):
        """测试取消提交销售订单"""
        # 查询生效态订单
        effective_order = self._query_effective_orders_from_db()
        if not effective_order:
            raise ValueError("未找到生效态订单")
            
        self.order_id = effective_order["so_id"]
        
        # 构造请求数据
        request_data = {
            "params": {
                "request": {
                    "id": self.order_id
                }
            }
        }
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["取消提交"]
        data = self.sls_api_params[url]
        data["params"]["request"] = request_data["params"]["request"]
        
        result = self.http.post(url, json=data, description="取消提交")
        assert result is not None, "取消提交销售订单失败"
        assert result.get('success', False), f"取消提交销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单状态
        so_status = self.db.query(f"select id,so_code,so_status from sls_so_head_tr where id={self.order_id}")
        assert so_status[0]['so_status'] == 'DRAFT', "销售订单取消提交失败"

    @allure.title("作废销售订单")
    @allure.description("测试作废销售订单")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(5)
    @safe_api_call(error_message="作废销售订单失败")
    def test_06_repeal_sales_order(self):
        """测试作废销售订单"""
        # 查询生效态订单
        effective_order = self._query_effective_orders_from_db()
        if not effective_order:
            raise ValueError("未找到生效态订单")
            
        self.order_id = effective_order["so_id"]
        
        # 构造请求数据
        request_data = {
            "params": {
                "request": {
                    "id": self.order_id
                }
            }
        }
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["作废订单"]
        data = self.sls_api_params[url]
        data["params"]["request"] = request_data["params"]["request"]
        
        result = self.http.post(url, json=data, description="作废订单")
        assert result is not None, "作废销售订单失败"
        assert result.get('success', False), f"作废销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单状态
        so_status = self.db.query(f"select id,so_code,so_status from sls_so_head_tr where id={self.order_id}")
        assert so_status[0]['so_status'] == 'CANCELLED', "销售订单作废失败"

    @allure.title("冻结销售订单")
    @allure.description("测试冻结销售订单")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(6)
    @safe_api_call(error_message="冻结销售订单失败")
    def test_07_freeze_sales_order(self):
        """测试冻结销售订单"""
        # 查询生效态订单
        effective_order = self._query_effective_orders_from_db()
        if not effective_order:
            raise ValueError("未找到生效态订单")
            
        self.order_id = effective_order["so_id"]
        
        # 构造请求数据
        request_data = {
            "params": {
                "request": {
                    "id": self.order_id
                }
            }
        }
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["冻结订单"]
        data = self.sls_api_params[url]
        data["params"]["request"] = request_data["params"]["request"]
        
        result = self.http.post(url, json=data, description="冻结订单")
        assert result is not None, "冻结销售订单失败"
        assert result.get('success', False), f"冻结销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单状态
        so_status = self.db.query(f"select id,so_code,so_status,freeze_type from sls_so_head_tr where id={self.order_id}")
        assert so_status[0]['so_status'] == 'EFFECT', "销售订单状态不正确"
        assert so_status[0]['freeze_type'] == 'ALL_FREEZE', "销售订单冻结失败"

    @allure.title("复制销售订单")
    @allure.description("测试复制销售订单")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(7)
    @safe_api_call(error_message="复制销售订单失败")
    def test_08_copy_sales_order(self):
        """测试复制销售订单"""
        # 查询生效态订单
        effective_order = self._query_effective_orders_from_db()
        if not effective_order:
            raise ValueError("未找到生效态订单")
            
        self.order_id = effective_order["so_id"]
        original_so_code = effective_order["so_code"]
        
        # 构造请求数据
        request_data = {
            "params": {
                "request": {
                    "id": str(self.order_id)
                }
            }
        }
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["复制订单"]
        data = self.sls_api_params[url]
        data["params"]["request"] = request_data["params"]["request"]
        
        result = self.http.post(url, json=data, description="复制订单")
        assert result is not None, "复制销售订单失败"
        assert result.get('success', False), f"复制销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证新订单
        new_so_code = result['data']['data']['soCode']
        self.so_data = result['data']['data']
        assert new_so_code is not None, "响应中未找到新订单号"
        assert new_so_code != original_so_code, f"新订单号与原订单号相同: {new_so_code}"

    @allure.title("提交复制的销售订单")
    @allure.description("测试提交复制的销售订单")
    @allure.severity(allure.severity_level.CRITICAL)    
    @pytest.mark.order(8)
    @safe_api_call(error_message="提交复制的销售订单失败")
    def test_09_submit_copied_sales_order(self):
        """测试提交复制的销售订单"""
        # 复制订单
        self.test_08_copy_sales_order()
        
        # 构造请求数据
        request_data = {
            "params": {
                "request": {
                    **self.so_data,
                    "syncSubmit": True
                }
            }
        }
        
        # 发送请求
        url = self.sls_api_paths["订单管理"]["编辑页提交"]
        data = self.sls_api_params[url]
        data["params"]["request"] = request_data["params"]["request"]
        
        result = self.http.post(url, json=data, description="提交复制订单")
        assert result is not None, "提交复制的销售订单失败"
        assert result.get('success', False), f"提交复制的销售订单失败: {result.get('err', {}).get('msg', '未知错误')}"
        
        # 验证订单状态
        new_so_code = result['data']['data']['soCode']
        assert new_so_code == self.so_data['soCode'], f"订单号不匹配: 期望={self.so_data['soCode']}, 实际={new_so_code}"
        
        so_status = self.db.query(f"select id,so_code,so_status from sls_so_head_tr where so_code='{new_so_code}'")
        assert so_status[0]['so_status'] == 'EFFECT', "复制订单提交失败"

if __name__ == "__main__":
    test = TestSalesOrderOperator()
    test.setup_class()  
    test.test_01_query_order_detail()
    test.test_02_sales_order_edit()
    test.test_03_submit_sales_order_edit()
    test.test_04_manual_submit_sales_order()   
    test.test_05_cancel_submit_sales_order()
    test.test_06_repeal_sales_order()
    test.test_07_freeze_sales_order()
    test.test_08_copy_sales_order()
    test.test_09_submit_copied_sales_order()
    #allure_dir = Path(project_root) / "reports" / "allure-results"
    #pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])    
