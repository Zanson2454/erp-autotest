"""
应付单查询服务测试用例
包含查询应付单详情的测试场景
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from utils.yaml_util import YamlUtil
from pathlib import Path

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApDocumentQuery(BaseTest):
    ap_query_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 初始化API配置
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        base_api_path = project_root / "testdata" / "fin" / "fin_api_path.yaml"
        base_api_params = project_root / "testdata" / "fin" / "fin_api_params.yaml"
        yaml_util = YamlUtil()
        cls.apis = yaml_util.read_yaml(base_api_path).get("apis", {})
        cls.api_params = yaml_util.read_yaml(base_api_params).get("api_params", {})

    @ParamUtil.case_decorator(
        story="应付单查询",
        title="查询草稿态应付单详情",
        description="测试步骤：查询草稿态应付单详情",
        severity="critical",
        order=1,
        smoke=False,
        tags=["ap", "query", "draft"]
    )
    def test_query_draft_ap_doc_detail(self):
        try:
            with a.step("查询草稿态应付单详情"):
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {"id": 9405597})
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                TestApDocumentQuery.ap_query_info["draft_id"] = 9405597
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_query_info, "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单查询",
        title="查询已确认应付单详情",
        description="测试步骤：查询已提交应付单详情",
        severity="critical",
        order=2,
        smoke=False,
        tags=["ap", "query", "confirmed"]
    )
    def test_query_confirmed_ap_doc_detail(self):
        try:
            with a.step("查询已确认应付单详情"):
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {"id": 9406132})
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                TestApDocumentQuery.ap_query_info["confirmed_id"] = 9406132
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_query_info, "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单查询",
        title="查询已完成应付单详情",
        description="测试步骤：查询已完成应付单详情",
        severity="critical",
        order=3,
        smoke=False,
        tags=["ap", "query", "done"]
    )
    def test_query_done_ap_doc_detail(self):
        try:
            with a.step("查询已完成应付单详情"):
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {"id": 9439273})
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                TestApDocumentQuery.ap_query_info["done_id"] = 9439273
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_query_info, "断言结果")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise