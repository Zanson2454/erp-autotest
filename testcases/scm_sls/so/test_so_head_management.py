import pytest
import allure
from testcases.sls import SlsBase
from utils.report_util import a, case_decorator

@allure.epic("销售管理")
@allure.feature("销售订单主表管理")
class TestSoHeadManagement(SlsBase):
    """销售订单主表（so_head）增删改查及接口专项测试类"""

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-提交服务",
        description="验证SLS_SO_SUBMIT_ACTION_SERVICE接口",
        severity="critical",
        order=100,
        tags=["销售订单", "提交", "SLS_SO_SUBMIT_ACTION_SERVICE"]
    )
    def test_submit_action_service(self):
        """SLS-销售订单-提交服务"""
        try:
            api_path = self.get_api_path("SLS-销售订单-提交服务")
            params, url = self.get_api_params(api_path)
            # TODO: 构造请求参数
            response = self.http.post(url, json=params)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="物料选择后重新渲染",
        description="验证SLS_AFTER_MAT_SELECT_RENDER_SERVICE接口",
        severity="critical",
        order=101,
        tags=["销售订单", "渲染", "SLS_AFTER_MAT_SELECT_RENDER_SERVICE"]
    )
    def test_after_mat_select_render(self):
        """物料选择后重新渲染"""
        try:
            api_path = self.get_api_path("物料选择后重新渲染")
            params, url = self.get_api_params(api_path)
            # TODO: 构造请求参数
            response = self.http.post(url, json=params)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-保存服务",
        description="验证SLS_SO_SAVE_ACTION_SERVICE接口",
        severity="critical",
        order=102,
        tags=["销售订单", "保存", "SLS_SO_SAVE_ACTION_SERVICE"]
    )
    def test_save_action_service(self):
        """SLS-销售订单-保存服务"""
        try:
            api_path = self.get_api_path("SLS-销售订单-保存服务")
            params, url = self.get_api_params(api_path)
            # TODO: 构造请求参数
            response = self.http.post(url, json=params)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="销售订单",
        title="SLS-销售订单-触发行项目类型变更",
        description="验证sls_so_item_change_render_service接口",
        severity="critical",
        order=103,
        tags=["销售订单", "项目类型变更", "sls_so_item_change_render_service"]
    )
    def test_so_item_change_render_service(self):
        """SLS-销售订单-触发行项目类型变更"""
        try:
            api_path = self.get_api_path("SLS-销售订单-触发行项目类型变更")
            params, url = self.get_api_params(api_path)
            # TODO: 构造请求参数
            response = self.http.post(url, json=params)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
