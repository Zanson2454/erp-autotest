import pytest
import allure
import sys
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
        cls.order_id = None
        cls.delivery_id = None
        cls.logger.info("标准销售订单流程测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.delivery_id:
                cls.db.delete(
                    table="sls_dn_head_tr",
                    where="id = %s",
                    params=[cls.delivery_id]
                )
            if cls.order_id:
                cls.db.delete(
                    table="sls_so_head_tr",
                    where="id = %s",
                    params=[cls.order_id]
                )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
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
            
            # 验证订单状态为已生效
            order_info = self.db.query(f"SELECT id, so_code, so_status FROM sls_so_head_tr WHERE id={self.order_id}")
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
        title="订单发货创建交货单",
        description="测试基于已生效销售订单创建交货单",
        severity="critical",
        order=3,
        smoke=True,
        tags=["销售订单", "交货单", "标准流程"]
    )
    def test_02_create_delivery_from_order(self):
        """测试基于已生效销售订单创建交货单"""
        try:
            # 确保有已生效的订单
            if not self.order_id:
                self.test_01_create_effective_standard_order()
            
            # 使用继承的create_delivery_order方法创建交货单
            self.delivery_id = self.create_delivery_order(self.order_id)
            
            # 记录创建结果
            a.text(f"交货单创建成功 - 销售订单ID: {self.order_id}, 交货单ID: {self.delivery_id}", "创建结果")
            self.logger.info(f"交货单创建成功 - 销售订单ID: {self.order_id}, 交货单ID: {self.delivery_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise