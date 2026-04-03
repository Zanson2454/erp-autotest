import allure
import pytest

from testcases.scm_sls import SlsBase
from utils.report_util import a, case_decorator


@allure.epic("销售管理")
@allure.feature("外部订单相关接口")
class TestSlsExternal(SlsBase):
    """外部订单相关接口测试类"""

    @pytest.mark.skip(reason="业务未引用")
    @case_decorator(
        story="外部订单",
        title="根据外部订单行号批量作废",
        description="验证根据外部订单行号批量作废接口",
        severity="normal",
        order=1,
        tags=["外部订单", "批量作废", "batch_cancel_line_by_external_line"]
    )
    def test_batch_cancel_line_by_external_line(self):
        """根据外部订单行号批量作废"""
        try:
            api_path = self.get_api_path("根据外部订单行号批量作废")
            params, url = self.get_api_params(api_path)
            # 这里应构造请求参数
            response, _ = self.standard_api_call(
                api_key="根据外部订单行号批量作废",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            a.json(params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="业务未引用")
    @case_decorator(
        story="外部订单",
        title="OMS渠道创建订单服务",
        description="验证OMS渠道创建订单服务接口",
        severity="normal",
        order=2,
        tags=["外部订单", "OMS", "oms_channel_create_order_service"]
    )
    def test_oms_channel_create_order_service(self):
        """OMS渠道创建订单服务"""
        try:
            api_path = self.get_api_path("OMS渠道创建订单服务")
            params, url = self.get_api_params(api_path)
            response, _ = self.standard_api_call(
                api_key="OMS渠道创建订单服务",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            a.json(params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="业务未引用")
    @case_decorator(
        story="外部订单",
        title="外部销售订单创建",
        description="验证外部销售订单创建接口",
        severity="normal",
        order=3,
        tags=["外部订单", "创建", "external_sales_order_creation"]
    )
    def test_external_sales_order_creation(self):
        """外部销售订单创建"""
        try:
            api_path = self.get_api_path("外部销售订单创建")
            params, url = self.get_api_params(api_path)
            response, _ = self.standard_api_call(
                api_key="外部销售订单创建",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            a.json(params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="业务未引用")
    @case_decorator(
        story="外部订单",
        title="外部价格主数据接口",
        description="验证外部价格主数据接口",
        severity="normal",
        order=4,
        tags=["外部订单", "价格主数据", "external_price_master_data"]
    )
    def test_external_price_master_data(self):
        """外部价格主数据接口"""
        try:
            api_path = self.get_api_path("外部价格主数据接口")
            params, url = self.get_api_params(api_path)
            response, _ = self.standard_api_call(
                api_key="外部价格主数据接口",
                set_dict=(params.get("params", {}) if isinstance(params, dict) else params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            a.json(params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
