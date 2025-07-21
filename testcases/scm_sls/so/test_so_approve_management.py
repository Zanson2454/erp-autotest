import pytest
import allure
from testcases.sls import SlsBase
from utils.report_util import a, case_decorator

@allure.epic("销售管理")
@allure.feature("销售订单审批管理")
class TestSoApproveManagement(SlsBase):
    """销售订单审批相关接口专项测试类"""

    @case_decorator(
        story="销售订单审批",
        title="创建销售订单提交审批任务",
        description="验证SLS_CRATE_SUBMIT_APPROVAL_SERVICE接口",
        severity="critical",
        order=1,
        tags=["销售订单", "审批", "SLS_CRATE_SUBMIT_APPROVAL_SERVICE"]
    )
    def test_crate_submit_approval_service(self):
        """创建销售订单提交审批任务"""
        try:
            api_path = self.get_api_path("创建销售订单提交审批任务")
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
        story="销售订单审批",
        title="SLS-销售订单-审批拒绝服务",
        description="验证SLS_SO_APPROVAL_REFUSE_ACTION_SERVICE接口",
        severity="critical",
        order=2,
        tags=["销售订单", "审批拒绝", "SLS_SO_APPROVAL_REFUSE_ACTION_SERVICE"]
    )
    def test_so_approval_refuse_action_service(self):
        """SLS-销售订单-审批拒绝服务"""
        try:
            api_path = self.get_api_path("SLS-销售订单-审批拒绝服务")
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
        story="销售订单审批",
        title="SLS-销售订单-审批同意服务",
        description="验证SLS_SO_APPROVAL_AGREE_ACTION_SERVICE接口",
        severity="critical",
        order=3,
        tags=["销售订单", "审批同意", "SLS_SO_APPROVAL_AGREE_ACTION_SERVICE"]
    )
    def test_so_approval_agree_action_service(self):
        """SLS-销售订单-审批同意服务"""
        try:
            api_path = self.get_api_path("SLS-销售订单-审批同意服务")
            params, url = self.get_api_params(api_path)
            # TODO: 构造请求参数
            response = self.http.post(url, json=params)
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            self.assert_util.assert_response_success(response)
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
