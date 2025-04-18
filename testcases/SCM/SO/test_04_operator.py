import os
import sys
import json
import pytest
from decimal import Decimal
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from common.login_manager import LoginManager
from config.config import Config
from testcases.SCM.scm_init import InitSQL
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers
from utils.MysqlUtil import DBManager
from utils.YamlUtil import YamlReader
from utils.HttpUtil import HttpUtil
from utils.ExceptionUtil import handle_exception, safe_api_call, handle_class_method_exception
from testcases.SCM.base_test import BaseTest, DecimalEncoder
from utils.MockUtil import MockData

class TestSalesOrderOperator(BaseTest):
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
        # 初始化请求头
        cls.headers = {
            'Content-Type': 'application/json',
            'Referer': f"{cls.base_url}/TERP_PORTAL-TERP",
            'User-Agent': MockData().get_mock_user_agent()
        }
        
        cls.logger.info("测试类初始化完成")
        
    

    def _query_draft_orders_from_db(self) -> Dict[str, Any]:
        """从数据库查询草稿态订单"""
        # SQL查询语句
        sql = f"""
         select id,so_code,so_status 
        from sls_so_head_tr 
        where created_by = {self.user_id}
        and so_status = 'DRAFT'
        and deleted=0 order by created_at desc
        limit 1
        """
        
        # 执行查询
        self.logger.info(f"执行查询: {sql}")
        result = self.db.execute_query(sql)
        
        # 处理查询结果
        if result and len(result) > 0:
            order = result[0]
            self.test_data = {
                "so_id": str(order["id"]),  # 确保ID是字符串类型
                "so_code": order["so_code"],
                "so_status": order["so_status"]
            }
            
            # 输出查询结果
            self.logger.info(f"\n查询到的草稿态订单数据: {json.dumps(self.test_data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
            return self.test_data
        else:
            self.logger.warning("未查询到草稿状态的订单数据")
            return {}

    @pytest.mark.order(1)
    @safe_api_call(error_message="查询销售订单详情失败")
    def test_01_query_order_detail(self):
        """测试查询销售订单详情"""
        # 如果没有订单ID，尝试获取
        if not self.order_id:
            logger.info("未找到订单ID，尝试从数据库查询")
            draft_order = self._query_draft_orders_from_db()
            if not draft_order:
                raise ValueError("未找到草稿态订单")
            self.order_id = draft_order["so_id"]
            logger.info(f"从数据库获取到订单ID: {self.order_id}")
        else:
            logger.info(f"使用已有订单ID: {self.order_id}")
            
        # 构建请求URL
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SO_QUERY_DETAIL_EVENT_SERVICE?tmodule=ERP_SCM"
        
        # 构建请求数据
        data = {
            "params": {
                "request": {
                    "id": self.order_id
                }
            }
        }
        
        # 发送请求
        logger.info(f"查询订单详情请求数据: {json.dumps(data, cls=DecimalEncoder, ensure_ascii=False, indent=2)}")
        try:
            result = super()._make_request(url, data, "订单详情查询", extract_nested_data=True, headers=self.headers)
            logger.info(json.dumps(result, cls=DecimalEncoder, ensure_ascii=False, indent=2))
            
            # 保存订单详情数据
            self.so_data =result
            logger.info(json.dumps(self.so_data, cls=DecimalEncoder, ensure_ascii=False, indent=2))
        except Exception as e:
            raise e

    @pytest.mark.order(2)
    @safe_api_call(error_message="销售订单编辑提交失败")
    def test_02_submit_sales_order_edit(self):
        """测试销售订单编辑提交"""
        if not hasattr(self, 'so_data') or self.so_data is None:
            self.test_01_query_order_detail()
            
        if not hasattr(self, 'order_id') or self.order_id is None:
            self._query_draft_orders_from_db()
       # 发送请求
        self.so_data['syncSubmit'] = True # 直接设 置 id 字段
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SALES_MANUAL_SAVE_EVENT?tmodule=ERP_SCM" 
      
        data = {
            "params": {
                "request": {
                    **self.so_data
                }
            }
        }
       
        result = self._make_request(url, data, "销售订单编辑提交", extract_nested_data=True)
        logger.info(json.dumps(result, cls=DecimalEncoder, ensure_ascii=False, indent=2))
        
        so_status = self.db.execute_query(f"select id,so_code,so_status from sls_so_head_tr where id={self.order_id}")
        assert so_status[0]['so_status'] == 'EFFECT', "销售订单编辑提交失败"
        assert result is not None, "销售订单编辑提交失败"
        logger.info("销售订单编辑提交成功")


    @pytest.mark.order(3)
    @safe_api_call(error_message="销售订单列表提交失败")
    def test_03_manual_submit_sales_order(self):
        """测试销售订单列表提交"""
        sql = f"""
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE so_status = 'EFFECT' 
                and so_type_id = {self.so_type_id}
                AND deleted = 0 order by created_at desc
                LIMIT 1
            """
        logger.info(f"执行查询: {sql}")
        result = self.db.execute_query(sql)
        if not result or len(result) == 0:
            pytest.fail("未找到可提交的订单")
        order = result[0]
        self.order_id = order["id"]
        logger.info(f"找到可提交订单: ID={self.order_id}, 订单号={order['so_code']}")
        # 发送请求
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SO_MANUAL_SUBMIT?tmodule=ERP_SCM"
        data = {
            "params": {
                "request": {
                    "id": self.order_id
                }
            }
        }
        logger.debug(f"销售订单手动提交请求数据: {json.dumps(data, cls=DecimalEncoder, indent=2)}")
        result = super()._make_request(url, data, "销售订单手动提交", extract_nested_data=True)
        logger.debug(f"销售订单手动提交响应数据: {json.dumps(result, cls=DecimalEncoder, indent=2)}")
        # 验证响应
        assert result is not None, "销售订单列表提交失败"
        logger.info("销售订单列表提交成功")

    @pytest.mark.order(4)
    @safe_api_call(error_message="取消提交销售订单失败")
    def test_04_cancel_submit_sales_order(self):
        """取消提交销售订单"""
        try:
            # 1. 从数据库查询已提交的订单
            sql = f"""
               SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE so_status = 'EFFECT' 
            and so_type_id = {self.so_type_id}
            and  id not in (select doc_id from del_dn_item_tr  where deleted=0 and doc_id is not null)
            AND deleted = 0 order by created_at desc
            LIMIT 1
        
            """
            logger.info(f"执行查询: {sql}")
            result = self.db.execute_query(sql)
            
            if not result or len(result) == 0:
                self.test_03_manual_submit_sales_order()
                
            order = result[0]
            order_id = order["id"]
            logger.info(f"找到已提交订单: ID={order_id}, 订单号={order['so_code']}")
           
            # 2. 构造请求数据
            request_data = {
                "params": {
                    "request": {
                        "id": order_id
                }
                }
            }
            
            # 3. 发送请求
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SO_CANNEL_COMMIT_EVENT_SERVICE?tmodule=ERP_SCM"


            
            response = self.session.post(url, json=request_data, headers=self.headers)
            response_data = response.json()
            
            logger.info(f"取消提交订单响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 4. 验证响应
            assert response.status_code == 200, f"取消提交订单失败: {response.text}"
            assert response_data.get("success"), f"取消提交订单失败: {response_data.get('message')}"
            
            # 5. 验证订单状态
            so_status = self.db.execute_query(f"select id,so_code,so_status from sls_so_head_tr where id={order_id}")
            assert so_status[0]['so_status'] == 'DRAFT', "销售订单取消提交失败"
            
            logger.info(f"订单 {self.order_id} 取消提交成功")
            
        except Exception as e:
            logger.error(f"取消提交订单失败: {str(e)}")
            raise

    @pytest.mark.order(5)
    @safe_api_call(error_message="作废销售订单失败")
    def test_05_repeal_sales_order(self):
        """作废销售订单"""
        try:
            # 1. 从数据库查询已提交的订单
            sql = f"""
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE so_status = 'EFFECT' 
            and so_type_id = {self.so_type_id}
            AND deleted = 0 order by created_at desc
            LIMIT 1
            """
            logger.info(f"执行查询: {sql}")
            result = self.db.execute_query(sql)
            
            if not result or len(result) == 0:
                self.test_03_manual_submit_sales_order()
                
            order = result[0]
            order_id = order["id"]
            logger.info(f"找到已提交订单: ID={order_id}, 订单号={order['so_code']}")
            
            # 2. 构造请求数据
            request_data = {
                "params": {
                    "request": {
                        "id": order_id
                    }
                }
            }
            
            # 3. 发送请求
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_REPEAL_EVENT_SERVICE?tmodule=ERP_SCM"
            logger.info(f"作废订单请求URL: {url}")
            logger.info(f"作废订单请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(url, json=request_data, headers=self.headers)
            response_data = response.json()
            
            logger.info(f"作废订单响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 4. 验证响应
            assert response.status_code == 200, f"作废订单失败: {response.text}"
            assert response_data.get("success"), f"作废订单失败: {response_data.get('message')}"
            
            # 5. 验证订单状态
            verify_sql = f"""
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE id = {order_id}
            """
            verify_result = self.db.execute_query(verify_sql)
            assert verify_result[0]["so_status"] == "CANCELLED", f"订单状态未更新为已作废: {verify_result[0]['so_status']}"
            
            logger.info(f"订单 {order_id} 作废成功")
            
        except Exception as e:
            logger.error(f"作废订单失败: {str(e)}")
            raise

    @pytest.mark.order(6)
    @safe_api_call(error_message="冻结销售订单失败")
    def test_06_freeze_sales_order(self):
        """冻结销售订单"""
        try:
            # 1. 从数据库查询已提交且未冻结的订单
            sql = f"""
            SELECT id, so_code, so_status, freeze_type 
            FROM sls_so_head_tr 
            WHERE so_status = 'EFFECT' 
            and so_type_id = {self.so_type_id}
            AND freeze_type = 'NU_FREEZE'
            AND deleted = 0 order by created_at desc
            LIMIT 1
            """
            logger.info(f"执行查询: {sql}")
            result = self.db.execute_query(sql)
            
            if not result or len(result) == 0:
                self.test_03_manual_submit_sales_order()
                result = self.db.execute_query(sql)
                if not result or len(result) == 0:
                    pytest.fail("未找到可冻结的订单")
                
            order = result[0]
            order_id = order["id"]
            logger.info(f"找到可冻结订单: ID={order_id}, 订单号={order['so_code']}")
            
            # 2. 构造请求数据
            request_data = {
                "params": {
                    "request": {
                        "id": order_id
                    }
                }
            }
            
            # 3. 发送请求
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SO_HEAD_FREEZE_EVENT_SERVICE?tmodule=ERP_SCM"
            
            logger.info(f"冻结订单请求URL: {url}")
            logger.info(f"冻结订单请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(url, json=request_data, headers=self.headers)
            response_data = response.json()
            
            logger.info(f"冻结订单响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 4. 验证响应
            assert response.status_code == 200, f"冻结订单失败: {response.text}"
            assert response_data.get("success"), f"冻结订单失败: {response_data.get('message')}"
            
            # 5. 验证订单状态
            verify_sql = f"""
            SELECT id, so_code, so_status, freeze_type 
            FROM sls_so_head_tr 
            WHERE id = {order_id}
            """
            verify_result = self.db.execute_query(verify_sql)
            assert verify_result[0]["so_status"] == "EFFECT", f"订单状态不正确: {verify_result[0]['so_status']}"
            assert verify_result[0]["freeze_type"] == "ALL_FREEZE", f"冻结状态未更新为已冻结: {verify_result[0]['freeze_type']}"
            
            logger.info(f"订单 {order_id} 冻结成功")
            
        except Exception as e:
            logger.error(f"冻结订单失败: {str(e)}")
            raise

    @pytest.mark.order(7)
    @safe_api_call(error_message="复制销售订单失败")
    def test_07_copy_sales_order(self):
        """复制销售订单"""
        try:
            # 1. 从数据库查询已提交的订单
            sql = f"""
            SELECT id, so_code, so_status 
            FROM sls_so_head_tr 
            WHERE so_status = 'EFFECT' 
            and so_type_id = {self.so_type_id}
            AND deleted = 0 order by created_at desc
            LIMIT 1
            """
            logger.info(f"执行查询: {sql}")
            result = self.db.execute_query(sql)
            
            if not result or len(result) == 0:
                self.test_03_manual_submit_sales_order()
                result = self.db.execute_query(sql)
                if not result or len(result) == 0:
                    pytest.fail("未找到可复制的订单")
                
            order = result[0]
            order_id = order["id"]
            original_so_code = order["so_code"]
            logger.info(f"找到可复制订单: ID={order_id}, 订单号={original_so_code}")
            
            # 2. 构造请求数据
            request_data = {
                "params": {
                    "request": {
                        "id": str(order_id)
                    }
                }
            }
            
            # 3. 发送请求
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SO_DATA_COPY_EVENT_SERVICE?tmodule=ERP_SCM"
            
            logger.info(f"复制订单请求URL: {url}")
            logger.info(f"复制订单请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(url, json=request_data, headers=self.headers)
            response_data = response.json()
            
            logger.info(f"复制订单响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 4. 验证响应
            assert response.status_code == 200, f"复制订单失败: {response.text}"
            assert response_data.get("success"), f"复制订单失败: {response_data.get('message')}"
            
            # 5. 验证新订单号
            new_so_code = response_data['data']['data']['soCode']
            self.so_data = response_data['data']['data']
            assert new_so_code is not None, "响应中未找到新订单号"
            assert new_so_code != original_so_code, f"新订单号与原订单号相同: {new_so_code}"
            
            logger.info(f"订单复制成功，原订单号: {original_so_code}, 新订单号: {new_so_code}")
            
        except Exception as e:
            logger.error(f"复制订单失败: {str(e)}")
            raise

    @pytest.mark.order(8)
    @safe_api_call(error_message="提交复制的销售订单失败")
    def test_08_submit_copied_sales_order(self):
        """提交复制的销售订单"""
        try:
            # 1. 确保有复制的订单数据
            if not hasattr(self, 'so_data') or self.so_data is None:
                self.test_07_copy_sales_order()
            
            # 2. 构造请求数据
            request_data = {
                "params": {
                    "request": {
                        **self.so_data,
                        "syncSubmit": True
                    }
                }
            }
            
            # 3. 发送请求
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SLS_SALES_MANUAL_SAVE_EVENT?tmodule=ERP_SCM"
            
            logger.info(f"提交复制订单请求URL: {url}")
            logger.info(f"提交复制订单请求数据: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            response = self.session.post(url, json=request_data, headers=self.headers)
            response_data = response.json()
            
            logger.info(f"提交复制订单响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            # 4. 验证响应
            assert response.status_code == 200, f"提交复制订单失败: {response.text}"
            # assert response_data.get("success"), f"提交复制订单失败: {response_data.get('message')}"
            
            # 5. 验证订单号
            new_so_code = response_data['data']['data']['soCode']
            assert new_so_code == self.so_data['soCode'], f"订单号不匹配: 期望={self.so_data['soCode']}, 实际={new_so_code}"
            
            logger.info(f"复制订单提交成功，订单号: {new_so_code}")
            
        except Exception as e:
            logger.error(f"提交复制订单失败: {str(e)}")
            raise

if __name__ == "__main__":
    # test = TestSalesOrderOperator()
    # test.setup_class()
    # test.test_01_query_order_detail()
    # test.test_02_submit_sales_order_edit()
    # test.test_03_manual_submit_sales_order()    
    # test.test_04_cancel_submit_sales_order()
    # test.test_05_repeal_sales_order()
    # test.test_06_freeze_sales_order()
    # test.test_07_copy_sales_order()
    # test.test_08_submit_copied_sales_order()
    
    pytest.main(["-v", __file__])