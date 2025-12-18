import allure
import pytest
import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_sls import SlsBase
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("销售订单报价")
class TestQuotePrimary(SlsBase):
    """销售订单报价测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.quote_id = None
        cls.order_id = None
        cls.delivery_id = None
        cls.logger.info("销售订单报价测试类初始化完成")
    
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
            if cls.quote_id:
                cls.db.delete(
                    table="sls_quote_head_tr",
                    where="id = %s",
                    params=[cls.quote_id]
                )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="销售订单报价流程",
        title="创建草稿态报价单",
        description="测试创建草稿态报价单，验证报价单创建成功",
        severity="critical",
        order=1,
        smoke=True,
        tags=["销售订单", "报价", "创建"]
    )
    def test_01_create_draft_quote(self):
        """测试创建草稿态报价单"""
        try:
            # 使用公共方法创建草稿态报价单
            self.quote_id = self.create_quote(submit=False)
            
            a.text(f"草稿报价单创建成功，报价单ID: {self.quote_id}", "报价单ID")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单报价流程",
        title="提交草稿态报价单",
        description="测试提交草稿态报价单，验证报价单提交成功",
        severity="critical",
        order=2,
        smoke=True,
        tags=["销售订单", "报价", "提交"]
    )
    def test_02_submit_draft_quote(self):
        """测试提交草稿态报价单"""
        try:
            # 1. 确保有报价数据
            if not self.quote_id:
                self.test_01_create_draft_quote()
            
            # 2. 使用不同的提交API
            submit_params = {
                "sceneKey": "SCM_SLS$sls_so_price",
                "viewKey": "SCM_SLS$sls_so_price:list",
                "viewTitle": "list",
                "buttonKey": "SCM_SLS$sls_so_price-RdEaeGYQWColCWLGgyCot",
                "buttonName": "提交",
                "appId": 0,
                "teamId": 22,
                "serviceKey": "SCM_SLS$SLS_SO_MANUAL_SUBMIT",
                "params": {
                    "request": {
                        "id": self.quote_id
                    }
                }
            }
            
            # 3. 发送提交请求
            response = self.http.post(
                "https://t-erp-huoshan-portal-test.app.duandian.com/api/trantor/service/engine/execute/SCM_SLS$SLS_SO_MANUAL_SUBMIT?tmodule=SCM_SLS",
                json=submit_params
            )
            self.assert_util.assert_response_data(response)
            
            # 4. 保存提交后的报价单ID
            response_data = response.get("data", {}).get("data", {})
            self.quote_id = response_data.get("id")
            
            a.text(f"报价单提交成功，报价单ID: {self.quote_id}", "报价单ID")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单报价流程",
        title="报价单生成订单",
        description="测试报价单生成订单，验证订单创建成功",
        severity="critical",
        order=3,
        smoke=True,
        tags=["销售订单", "报价", "生成订单"]
    )
    def test_03_quote_to_order(self):
        """测试报价单生成订单"""
        try:
            # 1. 确保有已提交的报价数据
            if not self.quote_id:
                self.test_02_submit_draft_quote()
            
            # 2. 使用销售订单复制服务复制报价单
            copy_api_path = self.get_api_path("销售订单复制服务")
            copy_params, copy_url = self.get_api_params(copy_api_path)
            
            copy_filtered_params = ParamUtil.filter_post_body_fields(
                copy_params, ["id"], 
                ["params", "request"]
            )
            ParamUtil.set_request_params(copy_filtered_params, {"id": self.quote_id})
            
            copy_response = self.http.post(copy_url, json=copy_filtered_params)
            self.assert_util.assert_response_data(copy_response)
            copied_data = copy_response.get("data", {}).get("data", {})
            
            # 3. 使用复制后的数据保存为订单（使用保存服务）
            save_api_path = self.get_api_path("SLS-销售订单-保存服务")
            save_params, save_url = self.get_api_params(save_api_path)
            
            # 构造保存参数 - 使用复制后的数据，但修改订单编码和描述
            save_filtered_params = ParamUtil.filter_post_body_fields(
                save_params, ["soCode", "soDesc", "custId", "slsOrgId", "slsComId", "slsDcId", 
                             "soTypeId", "baseCurrId", "slsCurrId", "soItems"], 
                ["params", "request"]
            )
            
            # 使用复制后的数据，但生成新的订单编码
            order_code = self.mock_util.generate_unique_code(tag="SO")
            save_set_dict = {
                "soCode": order_code,
                "soDesc": f"从报价单{copied_data.get('soCode', '')}创建的订单",
                "custId": copied_data.get("custId", {}),
                "slsOrgId": copied_data.get("slsOrgId", {}),
                "slsComId": copied_data.get("slsComId", {}),
                "slsDcId": copied_data.get("slsDcId", {}),
                "soTypeId": copied_data.get("soTypeId", {}),
                "baseCurrId": copied_data.get("baseCurrId", {}),
                "slsCurrId": copied_data.get("slsCurrId", {}),
                "soItems": copied_data.get("soItems", [])
            }
            ParamUtil.set_request_params(save_filtered_params, save_set_dict)
            
            # 4. 发送保存请求和断言
            save_response = self.http.post(save_url, json=save_filtered_params)
            self.assert_util.assert_response_data(save_response)
            
            # 5. 获取保存后的订单数据
            save_response_data = save_response.get("data", {}).get("data", {})
            a.json(save_response_data, "报价单转订单响应数据")
            
            # 6. 保存订单ID
            self.order_id = save_response_data.get("id")
            if not self.order_id:
                raise ValueError("保存订单后无法获取订单ID")
                
            a.text(f"报价单转订单成功，订单ID: {self.order_id}", "订单ID")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售订单报价流程",
        title="订单发货创建交货单",
        description="测试订单发货创建交货单，验证交货单创建成功",
        severity="critical",
        order=4,
        smoke=True,
        tags=["销售订单", "报价", "交货单"]
    )
    def test_04_create_delivery_from_order(self):
        """测试订单发货创建交货单"""
        try:
            # 1. 确保有订单数据
            if not self.order_id:
                self.test_03_quote_to_order()
            
            # 2. 调用创建交货单的公共方法
            self.delivery_id = self.create_delivery_order(self.order_id)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
