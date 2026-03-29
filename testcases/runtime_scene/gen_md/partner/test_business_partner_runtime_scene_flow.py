import copy

import allure

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a


@allure.epic("合作伙伴管理")
@allure.feature("合作伙伴页面Scene回放")
class TestBusinessPartnerRuntimeSceneFlow(GenMdBaseTest):
    """/api/trantor/runtime/scene/data-manager 前缀页面链路回放用例。"""

    @classmethod
    def _register_direct_api(cls, api_path, method):
        if getattr(cls, "apis", None) is None:
            cls.apis = {}
        if getattr(cls, "api_params", None) is None:
            cls.api_params = {}

        cls.apis[api_path] = {"path": api_path, "method": method}
        cls.api_params.setdefault(api_path, {})

    def _execute_scene_get(self, api_path, query_params=None):
        try:
            self._register_direct_api(api_path=api_path, method="GET")
            response, _ = self.standard_api_call(
                api_key=api_path,
                set_dict=None,
                use_param_util=False,
                method="GET",
                query_params=query_params,
            )
            self.assert_util.assert_response_success(response)
            a.json({"api_path": api_path, "query_params": copy.deepcopy(query_params)}, "request_data")
            a.json(response, "response_data")
            return response
        except Exception as exc:
            a.text(str(exc), "failure_reason")
            raise

    def test_load_partner_list_light_view(self):
        self._execute_scene_get(
            api_path="/api/trantor/runtime/scene/data-manager/light/GEN_MD$GEN_BUSINESS_PARTNER_VIEW",
            query_params={"view": "GEN_MD$GEN_BUSINESS_PARTNER_VIEW:list"},
        )

    def test_load_partner_list_view_permission(self):
        self._execute_scene_get(
            api_path="/api/trantor/runtime/scene/data-manager/view-permission/GEN_MD$GEN_BUSINESS_PARTNER_VIEW:list"
        )

    def test_load_partner_detail_view_permission(self):
        self._execute_scene_get(
            api_path="/api/trantor/runtime/scene/data-manager/view-permission/GEN_MD$GEN_BUSINESS_PARTNER_VIEW:detail"
        )

    def test_load_partner_detail_view(self):
        self._execute_scene_get(
            api_path="/api/trantor/runtime/scene/data-manager/view/GEN_MD$GEN_BUSINESS_PARTNER_VIEW:detail"
        )

    def test_load_partner_edit_view_permission(self):
        self._execute_scene_get(
            api_path="/api/trantor/runtime/scene/data-manager/view-permission/GEN_MD$GEN_BUSINESS_PARTNER_VIEW:edit"
        )

    def test_load_partner_edit_view(self):
        self._execute_scene_get(
            api_path="/api/trantor/runtime/scene/data-manager/view/GEN_MD$GEN_BUSINESS_PARTNER_VIEW:edit"
        )
