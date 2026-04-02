import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from testcases.comm.base_test import BaseTest
from testcases.comm.test_data_context import TestDataContext
from utils.param_util import ParamUtil


class _DummyLogger:
    def error(self, *_args, **_kwargs):
        return None

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


def test_get_api_path_requires_strict_key_match_for_compact_key():
    tester = _dummy_base_test()
    apis = {
        "打印场景-保存(/api/print/printScene/save#POST)": {"path": "/mock/save"},
    }

    assert tester.get_api_path("打印场景-保存", apis) is None


def test_get_api_path_requires_strict_key_match_for_path_without_method_suffix():
    tester = _dummy_base_test()
    apis = {
        "/api/async-task/task-instance/create#POST": {"path": "/mock/create"},
    }

    assert tester.get_api_path("/api/async-task/task-instance/create", apis) is None


def test_get_api_path_requires_strict_key_match_when_signature_text_drifted():
    tester = _dummy_base_test()
    apis = {
        "异步任务-任务实例-查询今日任务计数(/api/async-task/task-instance/count#GET)": {"path": "/mock/count"},
    }

    assert tester.get_api_path("异步任务-任务实例-查询任务数量(/api/async-task/task-instance/count#GET)", apis) is None


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


def test_store_id_as_writes_instance_and_runtime_context_without_class_pollution(monkeypatch):
    tester = _dummy_base_test()
    tester.assert_util = _DummyAssertUtil()
    tester.http = _DummyHttp()
    tester.test_data = {}
    tester.get_api_path = lambda *_args, **_kwargs: "/mock/save"
    tester.get_api_params = lambda *_args, **_kwargs: ({}, "/mock/save")
    TestDataContext.clear_runtime_values()
    if hasattr(BaseTest, "demo_id"):
        delattr(BaseTest, "demo_id")
    if hasattr(BaseTest, "demoId"):
        delattr(BaseTest, "demoId")

    _, extracted_id = tester.standard_api_call(
        api_key="mock-save",
        set_dict={"name": "demo"},
        use_param_util=False,
        param_path=["params"],
        method="POST",
        store_id_as="demo",
    )

    assert extracted_id is not None
    assert getattr(tester, "demo_id") == extracted_id
    assert getattr(tester, "demoId") == extracted_id
    assert tester.test_data["demo_id"] == extracted_id
    assert TestDataContext.get_runtime_value("demo_id") == extracted_id
    assert not hasattr(BaseTest, "demo_id")
    assert not hasattr(BaseTest, "demoId")


class _EnsureCase(BaseTest):
    def test_seed_data(self):
        self.counter += 1
        return self.counter


def test_ensure_wrapper_is_idempotent_within_same_runtime_context():
    tester = _EnsureCase.__new__(_EnsureCase)
    tester.counter = 0
    TestDataContext.clear_runtime_values()

    first = tester._ensure_seed_data()
    second = tester._ensure_seed_data()

    assert first == 1
    assert second == 1
    assert tester.counter == 1

    TestDataContext.clear_runtime_values()
    third = tester._ensure_seed_data()
    assert third == 2
