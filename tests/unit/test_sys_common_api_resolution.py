import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from testcases.comm.base_test import BaseTest
from utils.param_util import ParamUtil


class _DummyLogger:
    def warning(self, *_args, **_kwargs):
        return None


class _DummyAssertUtil:
    def set_request_context(self, **_kwargs):
        return None


class _DummyHttp:
    url = "http://localhost"

    def __init__(self):
        self.last_json = None

    def post(self, _url, **kwargs):
        self.last_json = kwargs.get("json")
        return {"success": True, "data": {"data": {}}}


def _dummy_base_test():
    obj = BaseTest.__new__(BaseTest)
    obj.logger = _DummyLogger()
    return obj


def test_get_api_path_supports_compact_key_with_parenthesized_config_key():
    tester = _dummy_base_test()
    apis = {
        "打印场景-保存(/api/print/printScene/save#POST)": {"path": "/mock/save"},
    }

    assert tester.get_api_path("打印场景-保存", apis) == "/mock/save"


def test_get_api_path_supports_path_key_without_method_suffix():
    tester = _dummy_base_test()
    apis = {
        "/api/async-task/task-instance/create#POST": {"path": "/mock/create"},
    }

    assert tester.get_api_path("/api/async-task/task-instance/create", apis) == "/mock/create"


def test_get_api_path_supports_signature_match_when_text_drifted():
    tester = _dummy_base_test()
    apis = {
        "异步任务-任务实例-查询今日任务计数(/api/async-task/task-instance/count#GET)": {"path": "/mock/count"},
    }

    assert tester.get_api_path("异步任务-任务实例-查询任务数量(/api/async-task/task-instance/count#GET)", apis) == "/mock/count"


def test_filter_post_body_fields_handles_list_template_without_crashing():
    template = {
        "params": {
            "request": [
                {"id": 1, "name": "n"}
            ]
        },
        "serviceKey": "mock",
    }

    filtered = ParamUtil.filter_post_body_fields(template, ["dataList"], ["params", "request"])
    ParamUtil.set_request_params(filtered, {"dataList": [{"id": 1}]})

    assert isinstance(filtered["params"]["request"], list)
    assert filtered["params"]["request"][0]["id"] == 1


def test_set_request_params_supports_empty_path_top_level_write():
    params = {"foo": 1}
    ParamUtil.set_request_params(params, {"bar": 2}, path=[])
    assert params["bar"] == 2


def test_set_request_params_maps_data_list_to_list_request():
    params = {"params": {"request": {}}}
    ParamUtil.set_request_params(params, {"dataList": [{"id": 10}]}, path=["params", "request"])
    assert isinstance(params["params"]["request"], list)
    assert params["params"]["request"][0]["id"] == 10


def test_sanitize_payload_cleans_invalid_sort_orders():
    payload = {
        "pageable": {
            "sortOrders": [{}, {"field": ""}, {"field": "createTime", "direction": "DESC"}],
            "conditionItems": None,
            "conditionGroup": None,
        }
    }

    ParamUtil.sanitize_payload(payload)

    pageable = payload["pageable"]
    assert pageable["sortOrders"] == [{"field": "createTime", "direction": "DESC"}]
    assert pageable["conditionItems"] is None
    assert pageable["conditionGroup"] is None


def test_standard_api_call_sanitizes_pageable_when_use_param_util_false():
    tester = _dummy_base_test()
    tester.assert_util = _DummyAssertUtil()
    tester.http = _DummyHttp()
    tester.get_api_path = lambda *_args, **_kwargs: "/mock/paging"
    tester.get_api_params = lambda *_args, **_kwargs: ({}, "/mock/paging")

    response, _ = tester.standard_api_call(
        api_key="mock-api",
        set_dict={
            "pageable": {
                "pageNo": 1,
                "pageSize": 20,
                "sortOrders": [{}],
                "conditionItems": None,
                "conditionGroup": None,
            }
        },
        use_param_util=False,
        param_path=["params"],
        method="POST",
    )

    assert response["success"] is True
    sent_pageable = tester.http.last_json["params"]["pageable"]
    assert sent_pageable["sortOrders"] == []
    assert sent_pageable["conditionItems"] is None
    assert sent_pageable["conditionGroup"] is None
