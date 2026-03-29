import copy
import json
from pathlib import Path

import allure

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a


PROJECT_ROOT = Path(__file__).resolve().parents[4]


@allure.epic("合作伙伴管理")
@allure.feature("合作伙伴录制回放")
class TestBusinessPartnerRecordedFlow(GenMdBaseTest):
    """手工录制沉淀的 service/engine 回放用例。"""

    @classmethod
    def _register_direct_api(cls, api_path, method, body_template=None):
        if getattr(cls, "apis", None) is None:
            cls.apis = {}
        if getattr(cls, "api_params", None) is None:
            cls.api_params = {}

        cls.apis[api_path] = {"path": api_path, "method": method}
        if method in {"POST", "PUT", "PATCH"}:
            cls.api_params[api_path] = copy.deepcopy(body_template) if body_template is not None else {}
        else:
            cls.api_params.setdefault(api_path, {})

    @staticmethod
    def _split_recorded_payload(set_dict):
        if isinstance(set_dict, dict):
            query_params = copy.deepcopy(set_dict.get("__recorded_query_params__", {}))
            body_payload = copy.deepcopy(set_dict.get("__recorded_body__", {}))
            if "__recorded_query_params__" in set_dict or "__recorded_body__" in set_dict:
                return query_params or None, body_payload
        return None, copy.deepcopy(set_dict)

    def _load_recorded_payload(self, relative_path):
        with open(PROJECT_ROOT / relative_path, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    def _execute_recorded_case(self, api_path, method, set_dict):
        try:
            query_params, request_body = self._split_recorded_payload(set_dict)
            self._register_direct_api(
                api_path=api_path,
                method=method,
                body_template=request_body,
            )

            response, _ = self.standard_api_call(
                api_key=api_path,
                set_dict=None,
                use_param_util=False,
                param_path=[],
                method=method,
                query_params=query_params,
            )
            self.assert_util.assert_response_success(response)
            a.json(set_dict, "recorded_set_dict")
            a.json(response, "response_data")
            return response
        except Exception as exc:
            a.text(str(exc), "failure_reason")
            raise

    def test_query_user_company(self):
        set_dict = {
            "serviceKey": "GEN_MD$ORG_SWITCH_QUERY_USER_COM_ACTION_SERVICE",
            "params": {"request": {}},
            "__recorded_query_params__": {},
            "__recorded_body__": {
                "serviceKey": "GEN_MD$ORG_SWITCH_QUERY_USER_COM_ACTION_SERVICE",
                "params": {"request": {}},
            },
        }
        self._execute_recorded_case(
            api_path="/api/trantor/service/engine/execute/GEN_MD$ORG_SWITCH_QUERY_USER_COM_ACTION_SERVICE",
            method="POST",
            set_dict=set_dict,
        )

    def test_query_partner_page(self):
        set_dict = self._load_recorded_payload(
            "testdata/recorded/gen_md_gen_business_partner_md_query_page_action_service_1774779747_055.json"
        )
        self._execute_recorded_case(
            api_path="/api/trantor/service/engine/execute/GEN_MD$GEN_BUSINESS_PARTNER_MD_QUERY_PAGE_ACTION_SERVICE",
            method="POST",
            set_dict=set_dict,
        )

    def test_query_partner_detail(self):
        set_dict = self._load_recorded_payload(
            "testdata/recorded/gen_md_gen_business_partner_md_query_detail_action_service_1774779747_059.json"
        )
        self._execute_recorded_case(
            api_path="/api/trantor/service/engine/execute/GEN_MD$GEN_BUSINESS_PARTNER_MD_QUERY_DETAIL_ACTION_SERVICE",
            method="POST",
            set_dict=set_dict,
        )

    def test_query_partner_tree(self):
        set_dict = self._load_recorded_payload(
            "testdata/recorded/gen_md_sys_reverseconstructtreeservice_1774779747_064.json"
        )
        self._execute_recorded_case(
            api_path="/api/trantor/service/engine/execute/GEN_MD$SYS_ReverseConstructTreeService",
            method="POST",
            set_dict=set_dict,
        )

    def test_query_partner_sys_page(self):
        set_dict = self._load_recorded_payload(
            "testdata/recorded/gen_md_sys_pagingdataservice_1774779747_065.json"
        )
        self._execute_recorded_case(
            api_path="/api/trantor/service/engine/execute/GEN_MD$SYS_PagingDataService",
            method="POST",
            set_dict=set_dict,
        )

    def test_save_partner_recorded_payload(self):
        set_dict = self._load_recorded_payload(
            "testdata/recorded/gen_md_gen_business_partner_md_save_action_service_1774779747_066.json"
        )
        self._execute_recorded_case(
            api_path="/api/trantor/service/engine/execute/GEN_MD$GEN_BUSINESS_PARTNER_MD_SAVE_ACTION_SERVICE",
            method="POST",
            set_dict=set_dict,
        )
