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
            
            # 2. 调用报价转订单API
            api_path = self.get_api_path("SLS-销售报价-转订单服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 构造转订单参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], 
                ["params", "request"]
            )
            
            set_dict = {
                "id": self.quote_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 获取转订单后的数据
            response_data = response.get("data", {}).get("data", {})
            a.json(response_data, "报价单转订单响应数据")
            
            # 6. 调用保存服务真正保存订单到数据库
            save_api_path = self.get_api_path("销售订单保存服务")
            save_params, save_url = self.get_api_params(save_api_path)
            
            # 构造保存参数 - 传递完整的订单数据
            save_filtered_params = ParamUtil.filter_post_body_fields(
                save_params, ["id", "soCode", "soDesc", "soDocDate", "baseCurrId", "slsCurrId", 
                             "exchRate", "grossBaseAmt", "netBaseAmt", "totalAmt", "taxAmt", 
                             "soCreateSource", "slsOrgId", "slsComId", "slsDcId", "soTypeId", 
                             "custId", "soStatus", "soBusinessStatus", "btClass", "soItems"], 
                ["params", "request"]
            )
            
            # 使用转订单返回的完整数据
            save_set_dict = {
                "id": response_data.get("id"),
                "soCode": response_data.get("soCode"),
                "soDesc": response_data.get("soDesc"),
                "soDocDate": response_data.get("soDocDate"),
                "baseCurrId": response_data.get("baseCurrId"),
                "slsCurrId": response_data.get("slsCurrId"),
                "exchRate": response_data.get("exchRate"),
                "grossBaseAmt": response_data.get("grossBaseAmt"),
                "netBaseAmt": response_data.get("netBaseAmt"),
                "totalAmt": response_data.get("totalAmt"),
                "taxAmt": response_data.get("taxAmt"),
                "soCreateSource": response_data.get("soCreateSource"),
                "slsOrgId": response_data.get("slsOrgId"),
                "slsComId": response_data.get("slsComId"),
                "slsDcId": response_data.get("slsDcId"),
                "soTypeId": response_data.get("soTypeId"),
                "custId": response_data.get("custId"),
                "soStatus": response_data.get("soStatus"),
                "soBusinessStatus": response_data.get("soBusinessStatus"),
                "btClass": response_data.get("btClass"),
                "soItems": response_data.get("soItems", [])
            }
            ParamUtil.set_request_params(save_filtered_params, save_set_dict)
            
            # 发送保存请求
            save_response = self.http.post(save_url, json=save_filtered_params)
            self.assert_util.assert_response_data(save_response)
            
            # 7. 保存订单ID - 使用保存订单后返回的ID
            save_response_data = save_response.get("data", {}).get("data", {})
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
