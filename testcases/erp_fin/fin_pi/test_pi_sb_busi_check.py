import sys
from pathlib import Path

# 设置项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest  # noqa: E402
from testcases.comm.utility_mixins import YamlUtilMixin  # noqa: E402
from utils.param_util import ParamUtil  # noqa: E402
from utils.report_util import a, case_decorator  # noqa: E402


class TestPiSbBusiCheck(YamlUtilMixin, BaseTest):
    """发票管理业务测试用例"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.base_api_path = Path(project_root) / "config" / "api" / "erp_fin" / "fin_api_path.yaml"
        cls.base_api_params = Path(project_root) / "config" / "api" / "erp_fin" / "fin_api_params.yaml"
        cls.fin_path = cls.yaml_util.read_yaml(cls.base_api_path).get("apis", {})
        cls.fin_params = cls.yaml_util.read_yaml(cls.base_api_params).get("api_params", {})
        # 兼容 standard_api_call 读取 self.apis / self.api_params 的约定
        cls.apis = cls.fin_path
        cls.api_params = cls.fin_params

    @case_decorator(
        story="发票管理",
        title="测试基于应付单创建发票操作",
        description="测试基于应付单创建发票操作",
        severity="critical",
        order=0,
        smoke=False,
        tags=["发票管理", "创建发票", "FIN_APM_AP_ITEM_TR_PAGING_DATA_SERVICE_PmHKWs1"],
    )
    def test_create_pi_by_api(self):
        try:
            url = self.fin_path["应付单行-分页数据服务_PmHKWs1"]["path"]
            data = self.fin_params.get(url, {})
            data = ParamUtil.filter_post_body_fields(data, ["pageNo", "pageSize"], ["params", "request", "pageable"])
            set_dict = {"pageNo": "1", "pageSize": "20"}
            ParamUtil.set_request_params(data, set_dict)
            result, _ = self.standard_api_call(
                api_key="应付单行-分页数据服务_PmHKWs1",
                set_dict=data.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"],
            )
            self.assert_util.assert_response_success(result)
            assert result.get("data", {}).get("data", {}).get("total", {}) >= 0
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


if __name__ == "__main__":
    test = TestPiSbBusiCheck()
    test.setup_class()
    test.test_create_pi_by_api()
