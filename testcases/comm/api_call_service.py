import json
from urllib.parse import urlencode, urljoin

import requests

from testcases.comm.data_context import TestDataContext
from utils.log_util import Loggers
from utils.param_util import ParamUtil


class ApiCallService:
    """standard_api_call 下沉实现，保持对 BaseTest 现有调用签名兼容。"""

    @staticmethod
    def execute(
        test_obj,
        api_key,
        set_dict=None,
        fields_to_filter=None,
        store_id_as=None,
        use_param_util=True,
        param_path=None,
        method="POST",
        query_params=None,
        cross_module_name=None,
    ):
        method = method.upper() if method else "POST"
        supported_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        if method not in supported_methods:
            raise ValueError(f"不支持的HTTP方法: {method}，支持的方法: {supported_methods}")

        try:
            # 兼容旧代码误传：api_key=self.apis(dict)
            if isinstance(api_key, dict):
                compat_key = getattr(ParamUtil, "_last_api_key", None)
                if not compat_key:
                    raise TypeError(
                        "standard_api_call 收到 dict 类型 api_key 但无可用兼容键。"
                        "请传入字符串 API key（如 'AR-应收单保存服务'）。"
                    )
                Loggers.warning(f"检测到 dict 类型 api_key，已回退使用最近一次 API key: {compat_key}")
                api_key = compat_key

            if cross_module_name:
                if not hasattr(test_obj, "get_cross_module_api_path") or not hasattr(
                    test_obj, "get_cross_module_api_params"
                ):
                    raise ValueError(
                        f"当前测试类不支持跨模块调用: cross_module_name={cross_module_name}, api_key={api_key}"
                    )
                api_path = test_obj.get_cross_module_api_path(cross_module_name, api_key)

                def get_params_fn(path, q):
                    return test_obj.get_cross_module_api_params(cross_module_name, path, q)
            else:
                api_path = test_obj.get_api_path(api_key)

                def get_params_fn(path, q):
                    return test_obj.get_api_params(path, with_query_params=q)

            if api_path is None:
                raise ValueError(
                    f"未找到API配置: {api_key}\n"
                    "请检查:\n"
                    f"1. API key是否正确: '{api_key}'\n"
                    "2. 配置文件是否正确加载 (apis配置是否存在)\n"
                    "3. 配置文件路径是否正确"
                )

            query_params_str = None
            if query_params:
                if isinstance(query_params, dict):
                    query_params_str = urlencode(query_params)
                else:
                    query_params_str = query_params

            if method in ["GET", "DELETE"]:
                params, url = get_params_fn(api_path, query_params_str)
                if url is None:
                    raise ValueError(f"API路径配置错误: api_path={api_path}\n" "请检查API参数配置文件中的路径配置")
                request_kwargs = {"params": set_dict} if set_dict else {}
            else:
                params, url = get_params_fn(api_path, query_params_str)
                if url is None:
                    raise ValueError(f"API路径配置错误: api_path={api_path}\n" "请检查API参数配置文件中的路径配置")

                if use_param_util:
                    if fields_to_filter is None:
                        if set_dict:
                            fields_to_filter = list(set_dict.keys())
                        else:
                            fields_to_filter = []
                    if param_path is None:
                        param_path = ["params", "request"]
                    filtered_params = ParamUtil.filter_post_body_fields(params, fields_to_filter, param_path)
                    if set_dict:
                        ParamUtil.set_request_params(filtered_params, set_dict, path=param_path)
                else:
                    if set_dict is None:
                        set_dict = {}
                    if param_path is None:
                        param_path = ["params", "request"]

                    import copy

                    filtered_params = copy.deepcopy(params) if params else {}
                    current = filtered_params
                    for i, p in enumerate(param_path):
                        if i == len(param_path) - 1:
                            current[p] = set_dict
                        else:
                            if p not in current:
                                current[p] = {}
                            current = current[p]

                ParamUtil.sanitize_payload(filtered_params)
                request_kwargs = {"json": filtered_params} if filtered_params else {}

            full_url = urljoin(test_obj.http.url, url.lstrip("/")) if hasattr(test_obj.http, "url") else url
            if method in ["GET", "DELETE"]:
                test_obj.assert_util.set_request_context(
                    api_key=api_key, url=full_url, method=method, params=request_kwargs.get("params")
                )
            else:
                test_obj.assert_util.set_request_context(
                    api_key=api_key, url=full_url, method=method, body=request_kwargs.get("json")
                )

            if method == "GET":
                response = test_obj.http.get(url, **request_kwargs)
            elif method == "POST":
                response = test_obj.http.post(url, **request_kwargs)
            elif method == "PUT":
                response = test_obj.http.put(url, **request_kwargs)
            elif method == "DELETE":
                response = test_obj.http.delete(url, **request_kwargs)
            elif method == "PATCH":
                if hasattr(test_obj.http, "patch"):
                    response = test_obj.http.patch(url, **request_kwargs)
                else:
                    response = test_obj.http.put(url, **request_kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            resp_success = response.get("success", "N/A") if isinstance(response, dict) else "N/A"
            Loggers.info(f"接口请求完成 [api_key={api_key}, success={resp_success}]")
            Loggers.info(f"响应数据: {json.dumps(response, ensure_ascii=False, indent=2)}")

            extracted_id = None
            if isinstance(response, dict):
                data = response.get("data")
                if isinstance(data, dict):
                    if "data" in data:
                        data_obj = data.get("data")
                        if isinstance(data_obj, dict):
                            extracted_id = data_obj.get("id") if "id" in data_obj else data_obj
                        else:
                            extracted_id = data_obj
                    else:
                        extracted_id = data.get("id") if "id" in data else data
                elif isinstance(data, list):
                    extracted_id = None
                else:
                    extracted_id = data.get("id") if isinstance(data, dict) and "id" in data else data
            elif isinstance(response, list):
                extracted_id = None
            else:
                extracted_id = None

            if store_id_as:
                snake_attr = f"{store_id_as}_id"
                camel_attr = f"{store_id_as}Id"

                # 运行时上下文：当前用例内可读，避免写类属性导致并发污染。
                TestDataContext.set_runtime_value(store_id_as, extracted_id)
                TestDataContext.set_runtime_value(snake_attr, extracted_id)
                TestDataContext.set_runtime_value(camel_attr, extracted_id)

                # 实例属性：同一测试方法内/辅助函数内直接使用 self.xxx_id。
                setattr(test_obj, snake_attr, extracted_id)
                setattr(test_obj, camel_attr, extracted_id)

                # 结构化测试上下文（如果存在）
                if hasattr(test_obj, "test_data") and isinstance(test_obj.test_data, dict):
                    test_obj.test_data[snake_attr] = extracted_id
                    test_obj.test_data[camel_attr] = extracted_id

            return response, extracted_id

        except requests.exceptions.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                status_code = getattr(e.response, "status_code", None)
                content_type = (e.response.headers or {}).get("Content-Type", "")
                raw_text = e.response.text or ""
                try:
                    response = e.response.json()
                    Loggers.error(f"HTTP错误响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
                    return response, None
                except ValueError:
                    fallback_response = {
                        "success": False,
                        "err": {
                            "code": f"HTTP_{status_code}" if status_code is not None else "HTTP_ERROR",
                            "msg": f"HTTP请求失败且响应非JSON (content-type={content_type})",
                        },
                        "info": {"raw": raw_text[:2000]},
                    }
                    test_obj.logger.error(f"错误响应不是JSON格式: status={status_code}, body={raw_text[:500]}")
                    Loggers.error(f"错误响应不是JSON格式: status={status_code}, body={raw_text[:500]}")
                    return fallback_response, None
            else:
                test_obj.logger.error(f"standard_api_call HTTP请求失败 [{api_key}]: {str(e)}")
                Loggers.error(f"HTTP请求失败: {str(e)}")
                raise
        except requests.exceptions.RequestException as e:
            test_obj.logger.error(f"standard_api_call HTTP请求失败 [{api_key}]: {str(e)}")
            Loggers.error(f"HTTP请求失败: {str(e)}")
            raise
        except Exception as e:
            test_obj.logger.error(f"standard_api_call 执行失败 [{api_key}]: {str(e)}")
            Loggers.error(f"执行失败: {str(e)}")
            raise
