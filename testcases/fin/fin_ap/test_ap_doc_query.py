"""
应付单详情查询自动化用例
覆盖草稿、已确认、已完成三种状态，动态获取ID，符合testcaserole规范
"""
import allure
from testcases.fin.fin_ap import ApBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a

@allure.epic("ERP通业财模块")
@allure.feature("应付管理")
class TestApDocumentQuery(ApBaseTest):
    ap_info = {}

    @classmethod
    def setup_class(cls):
        super().setup_class()

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
            with a.step("查询草稿态应付单详情"):
                # 获取草稿态应付单ID
                draft_id = self.ap_factory.get_latest_ap_doc_id_by_status('DRAFT')
                assert draft_id, "未找到草稿态应付单ID"
                a.text(str(draft_id), "草稿态应付单ID")
                
                # 查询应付单详情
                result = self.query_ap_detail(draft_id)
                
                # 保存查询结果
                TestApDocumentQuery.ap_info.update({"draft_id": draft_id})
                
                # 添加报告附件
                a.json({"id": draft_id}, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_info, "断言结果")
                
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
            with a.step("查询已确认应付单详情"):
                # 获取已确认应付单ID
                confirmed_id = self.ap_factory.get_latest_ap_doc_id_by_status('CONFIRM')
                assert confirmed_id, "未找到已确认应付单ID"
                a.text(str(confirmed_id), "已确认应付单ID")
                
                # 查询应付单详情
                result = self.query_ap_detail(confirmed_id)
                
                # 保存查询结果
                TestApDocumentQuery.ap_info.update({"confirmed_id": confirmed_id})
                
                # 添加报告附件
                a.json({"id": confirmed_id}, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_info, "断言结果")
                
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
            with a.step("查询已完成应付单详情"):
                # 获取已完成应付单ID
                done_id = self.ap_factory.get_latest_ap_doc_id_by_status('DONE')
                assert done_id, "未找到已完成应付单ID"
                a.text(str(done_id), "已完成应付单ID")
                
                # 查询应付单详情
                result = self.query_ap_detail(done_id)
                
                # 保存查询结果
                TestApDocumentQuery.ap_info.update({"done_id": done_id})
                
                # 添加报告附件
                a.json({"id": done_id}, "请求数据")
                a.json(result, "响应结果数据")
                a.json(TestApDocumentQuery.ap_info, "断言结果")
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestApDocumentQuery()
    test.setup_class()
