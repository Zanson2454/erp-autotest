import copy
import pytest
import allure
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.report_util import a, case_decorator
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil


@allure.epic("销售管理")
@allure.feature("标准销售订单流程")
class TestStandardSalesOrder(SlsBase):
    """标准销售订单完整流程测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.order_id = None
        cls.delivery_id = None
        cls.so_item_id = None
        cls.order_code = None
        cls.logger.info("标准销售订单流程测试类初始化完成")
    
    
    
    @case_decorator(
        story="标准销售订单流程",
        title="创建已生效标准销售订单",
        description="测试创建已生效的标准销售订单",
        severity="critical",
        order=1,
        smoke=True,
        tags=["销售订单", "标准流程"]
    )
    def test_01_create_effective_standard_order(self):
        """测试创建已生效标准销售订单"""
        try:
            # 使用继承的create_sales_order方法创建已生效订单
            self.order_id = self.create_sales_order(order_type="STND", submit=True)
            
            # 验证订单创建成功
            assert self.order_id is not None, "创建订单失败，未返回订单ID"
            
            # 等待订单状态更新
            time.sleep(2)
            
            # 验证订单状态为已生效（添加重试机制）
            order_info = None
            for attempt in range(5):
                order_info = self.db.query(f"SELECT id, so_code, so_status FROM sls_so_head_tr WHERE id={self.order_id}")
                if order_info and order_info[0]['so_status'] in ['EFFECT', 'APPROVING']:
                    break
                
                # 如果状态不是预期状态，等待后重试
                if attempt < 4:
                    time.sleep(2)
                    self.logger.info(f"订单状态查询，等待2秒后重试 (第{attempt + 1}次)")
            
            assert order_info, "未找到创建的订单"
            assert order_info[0]['so_status'] in ['EFFECT', 'APPROVING'], f"订单状态不正确，期望：EFFECT或APPROVING，实际：{order_info[0]['so_status']}"
            
            # 保存订单信息供后续测试使用
            self.effective_order_code = order_info[0]['so_code']
            
            # 记录测试结果
            a.text(f"已生效销售订单创建成功，订单ID: {self.order_id}, 订单号: {self.effective_order_code}", "创建结果")
            self.logger.info(f"已生效销售订单创建成功，订单ID: {self.order_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售订单流程",
        title="完成销售订单行",
        description="测试完成销售订单行，并检查订单行和订单的业务状态为已完成",
        severity="critical",
        order=2,
        smoke=True,
        tags=["销售订单", "订单行", "完成", "标准流程"]
    )
    def test_02_complete_order_item(self):
        """测试完成销售订单行"""
        try:
            # 1. 确保有已生效的订单
            if not self.order_id:
                self.test_01_create_effective_standard_order()
            
            # 获取订单编号
            if not self.order_code:
                order_info = self.db.query(f"SELECT so_code FROM sls_so_head_tr WHERE id={self.order_id}")
                if not order_info:
                    raise ValueError(f"未找到订单，订单ID: {self.order_id}")
                self.order_code = order_info[0]['so_code']
            
            # 2. 从数据库查询订单行数据，并构造完成订单行所需的数据对象
            order_item_info = None
            for _ in range(5):
                order_item_info = self.db.query(
                    """SELECT id, so_id, so_item_code, so_item_status, so_item_business_status, 
                       version, mat_id, so_item_sls_qty, so_item_price, uom_sls_id, 
                       inv_org_id, inv_loc_id, so_item_type_id
                       FROM sls_so_item_tr WHERE so_id = %s LIMIT 1""",
                    (self.order_id,)
                )
                if order_item_info:
                    break
                time.sleep(1)
            
            if not order_item_info:
                raise ValueError(f"未找到订单对应的订单行，订单ID: {self.order_id}, 订单编号: {self.order_code}")
            
            item_data = order_item_info[0]
            self.so_item_id = item_data['id']
            
            # 3. 构造订单行数据对象（用于完成订单行操作）
            order_item = {
                "id": item_data['id'],
                "soId": item_data['so_id'],
                "soItemCode": item_data['so_item_code'],
                "soItemStatus": item_data['so_item_status'],
                "soItemBusinessStatus": item_data['so_item_business_status'],
                "version": item_data.get('version', 0),
                "matId": {"id": item_data['mat_id']} if item_data.get('mat_id') else None,
                "soItemSlsQty": float(item_data['so_item_sls_qty']) if item_data.get('so_item_sls_qty') else 0,
                "soItemPrice": float(item_data['so_item_price']) if item_data.get('so_item_price') else 0,
                "uomSlsId": {"id": item_data['uom_sls_id']} if item_data.get('uom_sls_id') else None,
                "invOrgId": {"id": item_data['inv_org_id']} if item_data.get('inv_org_id') else None,
                "invLocId": {"id": item_data['inv_loc_id']} if item_data.get('inv_loc_id') else None,
                "soItemTypeId": {"id": item_data['so_item_type_id']} if item_data.get('so_item_type_id') else None
            }
            
            a.text(f"从数据库查询到订单行，订单行ID: {self.so_item_id}, 订单编号: {self.order_code}", "订单行查询结果")
            
            # 6. 完成订单行
            complete_api_path = self.get_api_path("订单项目行手动完成服务")
            complete_params, complete_url = self.get_api_params(complete_api_path)
            
            # 7. 参数处理：使用查询到的订单行完整数据
            # 直接构造完成订单行的参数，使用查询到的完整订单行数据
            filtered_complete_params = {
                "sceneKey": "SCM_SLS$sls_so_item",
                "viewKey": "SCM_SLS$sls_so_item:list",
                "viewTitle": "list",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_SLS$SO_ITEM_MANUAL_COMPLETED_EVENT_SERVICE",
                "params": {
                    "request": order_item  # 使用查询到的完整订单行数据
                }
            }
            
            # 8. 发送完成订单行请求
            complete_response, _ = self.standard_api_call(
                api_key="订单项目行手动完成服务",
                set_dict=(filtered_complete_params.get("params", {}) if isinstance(filtered_complete_params, dict) else filtered_complete_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(complete_response)
            
            a.json(filtered_complete_params, "完成订单行-请求数据")
            a.json(complete_response, "完成订单行-响应数据")
            
            # 9. 验证订单行业务状态为已完成
            # 等待一下，确保状态更新完成
            time.sleep(1)
            
            order_item_info = self.db.query(f"""
                SELECT so_item_business_status, so_item_status 
                FROM sls_so_item_tr 
                WHERE id={self.so_item_id}
            """)
            
            if not order_item_info:
                raise ValueError(f"未找到订单行数据，订单行ID: {self.so_item_id}")
            
            so_item_business_status = order_item_info[0].get('so_item_business_status')
            a.text(f"订单行业务状态: {so_item_business_status}", "状态验证")
            self.assert_util.assert_by_operator(
                so_item_business_status, "=", "COMPLETED",
                message=f"订单行业务状态应为COMPLETED，实际: {so_item_business_status}"
            )
            
            # 10. 验证订单业务状态为已完成
            order_info = self.db.query(f"""
                SELECT so_business_status 
                FROM sls_so_head_tr 
                WHERE id={self.order_id}
            """)
            
            if not order_info:
                raise ValueError(f"未找到订单数据，订单ID: {self.order_id}")
            
            so_business_status = order_info[0].get('so_business_status')
            a.text(f"订单业务状态: {so_business_status}", "状态验证")
            self.assert_util.assert_by_operator(
                so_business_status, "=", "COMPLETED",
                message=f"订单业务状态应为COMPLETED，实际: {so_business_status}"
            )
            
            a.text(f"订单行完成成功，订单行ID: {self.so_item_id}, 订单ID: {self.order_id}", "完成结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售订单流程",
        title="取消完成销售订单行",
        description="测试取消完成销售订单行，并检查订单行和订单的业务状态恢复",
        severity="critical",
        order=3,
        smoke=True,
        tags=["销售订单", "订单行", "取消完成", "标准流程"]
    )
    def test_03_cancel_complete_order_item(self):
        """测试取消完成销售订单行"""
        try:
            # 1. 确保订单行已完成
            if not self.so_item_id:
                self.test_02_complete_order_item()
            
            # 2. 从数据库查询订单行数据，并构造取消完成订单行所需的数据对象
            order_item_info = None
            for _ in range(5):
                order_item_info = self.db.query(
                    """SELECT id, so_id, so_item_code, so_item_status, so_item_business_status, 
                       version, mat_id, so_item_sls_qty, so_item_price, uom_sls_id, 
                       inv_org_id, inv_loc_id, so_item_type_id
                       FROM sls_so_item_tr WHERE id = %s LIMIT 1""",
                    (self.so_item_id,)
                )
                if order_item_info:
                    break
                time.sleep(1)
            
            if not order_item_info:
                raise ValueError(f"未找到订单行，订单行ID: {self.so_item_id}")
            
            item_data = order_item_info[0]
            
            # 验证订单行当前状态为已完成
            if item_data.get('so_item_business_status') != "COMPLETED":
                raise ValueError(f"订单行状态不是COMPLETED，无法取消完成。当前状态: {item_data.get('so_item_business_status')}")
            
            # 获取订单编码
            if not self.order_code:
                order_info = self.db.query("SELECT so_code FROM sls_so_head_tr WHERE id = %s LIMIT 1", (self.order_id,))
                if order_info:
                    self.order_code = order_info[0]['so_code']
            
            # 构造订单行数据对象（用于取消完成订单行操作）
            order_item = {
                "id": item_data['id'],
                "soId": item_data['so_id'],
                "soCode": self.order_code,
                "soItemCode": item_data['so_item_code'],
                "soItemStatus": item_data['so_item_status'],
                "soItemBusinessStatus": item_data['so_item_business_status'],
                "version": item_data.get('version', 0),
                "matId": {"id": item_data['mat_id']} if item_data.get('mat_id') else None,
                "soItemSlsQty": float(item_data['so_item_sls_qty']) if item_data.get('so_item_sls_qty') else 0,
                "soItemPrice": float(item_data['so_item_price']) if item_data.get('so_item_price') else 0,
                "uomSlsId": {"id": item_data['uom_sls_id']} if item_data.get('uom_sls_id') else None,
                "invOrgId": {"id": item_data['inv_org_id']} if item_data.get('inv_org_id') else None,
                "invLocId": {"id": item_data['inv_loc_id']} if item_data.get('inv_loc_id') else None,
                "soItemTypeId": {"id": item_data['so_item_type_id']} if item_data.get('so_item_type_id') else None
            }
            
            a.text(f"从数据库查询到已完成的订单行，订单行ID: {self.so_item_id}", "订单行查询结果")

            # 3. 取消完成订单行
            cancel_complete_api_path = self.get_api_path("订单项目行手动取消完成服务")
            cancel_complete_params, cancel_complete_url = self.get_api_params(cancel_complete_api_path)
            
            # 构造取消完成订单行的参数，使用查询到的完整订单行数据
            filtered_cancel_complete_params = {
                "sceneKey": "SCM_SLS$sls_so_item",
                "viewKey": "SCM_SLS$sls_so_item:list",
                "viewTitle": "list",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_SLS$SO_ITEM_MANUAL_CANCEL_COMPLETED_EVENT_SERVICE",
                "params": {
                    "request": order_item  # 使用查询到的完整订单行数据
                }
            }
            
            # 4. 发送取消完成订单行请求
            cancel_complete_response, _ = self.standard_api_call(
                api_key="订单项目行手动取消完成服务",
                set_dict=(filtered_cancel_complete_params.get("params", {}) if isinstance(filtered_cancel_complete_params, dict) else filtered_cancel_complete_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(cancel_complete_response)
            
            a.json(filtered_cancel_complete_params, "取消完成订单行-请求数据")
            a.json(cancel_complete_response, "取消完成订单行-响应数据")
            
            # 5. 验证订单行业务状态已恢复（不再是COMPLETED）
            # 等待一下，确保状态更新完成
            time.sleep(1)
            
            order_item_info = self.db.query(f"""
                SELECT so_item_business_status, so_item_status 
                FROM sls_so_item_tr 
                WHERE id={self.so_item_id}
            """)
            
            if not order_item_info:
                raise ValueError(f"未找到订单行数据，订单行ID: {self.so_item_id}")
            
            so_item_business_status = order_item_info[0].get('so_item_business_status')
            a.text(f"取消完成后的订单行业务状态: {so_item_business_status}", "状态验证")
            self.assert_util.assert_by_operator(
                so_item_business_status, "!=", "COMPLETED",
                message=f"订单行业务状态不应为COMPLETED，实际: {so_item_business_status}"
            )
            
            # 6. 验证订单业务状态已恢复（不再是COMPLETED）
            order_info = self.db.query(f"""
                SELECT so_business_status 
                FROM sls_so_head_tr 
                WHERE id={self.order_id}
            """)
            
            if not order_info:
                raise ValueError(f"未找到订单数据，订单ID: {self.order_id}")
            
            so_business_status = order_info[0].get('so_business_status')
            a.text(f"取消完成后的订单业务状态: {so_business_status}", "状态验证")
            self.assert_util.assert_by_operator(
                so_business_status, "!=", "COMPLETED",
                message=f"订单业务状态不应为COMPLETED，实际: {so_business_status}"
            )
            
            a.text(f"订单行取消完成成功，订单行ID: {self.so_item_id}, 订单ID: {self.order_id}", "取消完成结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准销售订单流程",
        title="订单发货创建交货单",
        description="测试基于已生效销售订单创建交货单",
        severity="critical",
        order=4,
        smoke=True,
        tags=["销售订单", "交货单", "标准流程"]
    )
    def test_04_create_delivery_from_order(self):
        """测试基于已生效销售订单创建交货单"""
        try:
            # 确保有已生效的订单
            if not self.order_id:
                self.test_01_create_effective_standard_order()
            
            # 检查订单状态，确保订单已生效
            order_info = self.db.query(f"SELECT so_status FROM sls_so_head_tr WHERE id={self.order_id}")
            if not order_info:
                raise ValueError(f"未找到订单，订单ID: {self.order_id}")
            
            order_status = order_info[0]['so_status']
            if order_status != "EFFECT":
                self.logger.warning(f"订单状态不是已生效，当前状态: {order_status}。订单ID: {self.order_id}")
                a.text(f"订单状态不是已生效，当前状态: {order_status}。订单ID: {self.order_id}", "状态警告")
            
            # 使用继承的create_delivery_order方法创建交货单
            self.delivery_id = self.create_delivery_order(self.order_id)
            
            # 记录创建结果
            a.text(f"交货单创建成功 - 销售订单ID: {self.order_id}, 交货单ID: {self.delivery_id}", "创建结果")
            self.logger.info(f"交货单创建成功 - 销售订单ID: {self.order_id}, 交货单ID: {self.delivery_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
