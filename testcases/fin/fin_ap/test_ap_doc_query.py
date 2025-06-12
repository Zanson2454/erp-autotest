"""
应付单详情查询自动化用例
覆盖草稿、已确认、已完成三种状态，动态获取ID，符合testcaserole规范
"""
import allure
from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil
from utils.allure_simple import a
from data_factory.fin_ap_factory import FinApFactory
from pathlib import Path

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApDocumentQuery(BaseTest):
    ap_query_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ap_factory = FinApFactory()
        # 初始化财务API配置
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        apis = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_path.yaml").get("apis", {})
        api_params = cls.yaml_util.read_yaml(project_root / "testdata/fin/fin_api_params.yaml").get("api_params", {})
        cls.apis = apis
        cls.api_params = api_params

    @ParamUtil.case_decorator(
        story="应付单详情查询",
        title="查询草稿态应付单详情",
        description="动态获取草稿态应付单ID，查询详情并断言成功",
        severity="critical",
        order=1,
        smoke=False,
        tags=["ap", "query", "draft"]
    )
    def test_query_draft_ap_doc_detail(self):
        try:
            with a.step("准备草稿态应付单ID"):
                draft_id = self.ap_factory.get_latest_ap_doc_id_by_status('DRAFT')
                assert draft_id, "未找到草稿态应付单ID"
                a.text(str(draft_id), "草稿态应付单ID")
                
            with a.step("查询草稿态应付单详情"):
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {"id": draft_id})
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                TestApDocumentQuery.ap_query_info.update({"draft_id": draft_id})
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_query_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单详情查询",
        title="查询已确认应付单详情",
        description="动态获取已确认应付单ID，查询详情并断言成功",
        severity="critical",
        order=2,
        smoke=False,
        tags=["ap", "query", "confirmed"]
    )
    def test_query_confirmed_ap_doc_detail(self):
        try:
            with a.step("准备已确认应付单ID"):
                confirmed_id = self.ap_factory.get_latest_ap_doc_id_by_status('CONFIRM')
                assert confirmed_id, "未找到已确认应付单ID"
                a.text(str(confirmed_id), "已确认应付单ID")
                
            with a.step("查询已确认应付单详情"):
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {"id": confirmed_id})
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                TestApDocumentQuery.ap_query_info.update({"confirmed_id": confirmed_id})
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_query_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @ParamUtil.case_decorator(
        story="应付单详情查询",
        title="查询已完成应付单详情",
        description="动态获取已完成应付单ID，查询详情并断言成功",
        severity="critical",
        order=3,
        smoke=False,
        tags=["ap", "query", "done"]
    )
    def test_query_done_ap_doc_detail(self):
        try:
            with a.step("准备已完成应付单ID"):
                done_id = self.ap_factory.get_latest_ap_doc_id_by_status('DONE')
                assert done_id, "未找到已完成应付单ID"
                a.text(str(done_id), "已完成应付单ID")
                
            with a.step("查询已完成应付单详情"):
                api_path = ParamUtil.get_api_path(self.apis, "应付单头表-根据ID查找数据服务")
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params", "request"])
                ParamUtil.set_request_params(filtered_params, {"id": done_id})
                
                result = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_success(result)
                
                TestApDocumentQuery.ap_query_info.update({"done_id": done_id})
                
                a.json(filtered_params, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_query_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApDocumentQuery()
    test.setup_class()