"""
swagger_parser.py — 从 Swagger 文档自动生成 API 配置 YAML

用法（推荐，自动从 config/env/test.yaml 登录）：
  python script/swagger_parser.py --module gen_md --team TERP
  python script/swagger_parser.py --module scm_pur --team TERP --env staging
  python script/swagger_parser.py --module gen_md --team TERP --project my_project

用法（手动 Cookie，跳过自动登录）：
  python script/swagger_parser.py --module gen_md --team TERP \\
      --base-url https://your-erp-host:8080 \\
      --cookie "t_iam_test=eyJ..."

输出（自动写入项目 config/api/ 目录）：
  config/api/{module}/{prefix}_api_path.yaml
  config/api/{module}/{prefix}_api_params.yaml
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
import yaml
from dotenv import load_dotenv
from loguru import logger


# ─────────────────────────────────────────────────────────────────────────────
# SwaggerParser — 核心解析器（保持不变）
# ─────────────────────────────────────────────────────────────────────────────

class SwaggerParser:
    """Swagger文档解析工具类"""

    def __init__(
        self,
        base_url: str,
        cookies: Optional[Dict[str, str]] = None,
        session: Optional[requests.Session] = None,
        *,
        verbose: bool = False,
        quiet: bool = False,
    ):
        """
        初始化Swagger解析器

        Args:
            base_url: Swagger API的基础URL
            cookies: 请求需要的cookies（手动传入时使用）
            session: 已登录的 requests.Session（自动登录时优先使用）
        """
        self.base_url = base_url.rstrip('/')
        self.cookies = cookies or {}
        self._session = session
        self.verbose = verbose
        self.quiet = quiet
        self.swagger_data = None

    def _detail_log(self, message: str) -> None:
        """逐接口明细日志：默认开启，--quiet 时关闭。"""
        if not self.quiet:
            logger.info(message)

    def _get(self, url: str, **kwargs) -> requests.Response:
        """统一 GET，优先用已登录 session，否则传 cookies"""
        headers = {
            'Accept': 'application/json,*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/136.0.0.0 Safari/537.36'
            ),
        }
        if self._session:
            return self._session.get(url, headers=headers, timeout=30, **kwargs)
        return requests.get(url, headers=headers, cookies=self.cookies, timeout=30, **kwargs)

    def fetch_swagger_doc(self, team: Optional[str] = None,
                          module: Optional[str] = None) -> Dict[str, Any]:
        """
        获取指定团队和模块的Swagger文档

        Args:
            team: 团队名称，可选。当为None时，使用swagger-config路径
            module: 模块名称，可选。当为None时，使用swagger-config路径

        Returns:
            Dict[str, Any]: Swagger文档数据（如果是swagger-config，会合并所有API文档）
        """
        try:
            if team is None and module is None:
                # 先尝试 /v3/api-docs（可能直接返回文档或文档列表）
                url = urljoin(self.base_url, '/v3/api-docs')
                logger.info(f"正在获取Swagger文档，URL: {url}")
                try:
                    response = self._get(url)
                    response.raise_for_status()
                    api_docs_data = response.json()

                    if isinstance(api_docs_data, dict) and 'paths' in api_docs_data:
                        logger.info("检测到直接的Swagger文档格式")
                        self.swagger_data = api_docs_data
                        return self.swagger_data

                    if isinstance(api_docs_data, dict) and 'urls' in api_docs_data and isinstance(api_docs_data['urls'], list):
                        logger.info(f"检测到文档列表格式，包含 {len(api_docs_data['urls'])} 个API文档")
                        config_data = api_docs_data
                    elif isinstance(api_docs_data, list) and len(api_docs_data) > 0:
                        logger.info(f"检测到数组格式，包含 {len(api_docs_data)} 个文档项")
                        config_data = {'urls': api_docs_data}
                    else:
                        logger.warning(f"/v3/api-docs 返回的数据格式不符合预期")
                        if isinstance(api_docs_data, dict):
                            logger.warning(f"返回数据的键: {list(api_docs_data.keys())}")
                        raise ValueError("不是预期的文档格式，尝试swagger-config")

                except (requests.RequestException, ValueError) as e:
                    logger.info(f"/v3/api-docs 获取失败或格式不符: {str(e)}，尝试 swagger-config")
                    url = urljoin(self.base_url, '/v3/api-docs/swagger-config')
                    logger.info(f"正在获取Swagger配置，URL: {url}")
                    response = self._get(url)
                    response.raise_for_status()
                    config_data = response.json()
                    logger.info(f"swagger-config 返回数据的键: {list(config_data.keys()) if isinstance(config_data, dict) else '不是字典类型'}")

                if 'urls' in config_data and isinstance(config_data['urls'], list) and len(config_data['urls']) > 0:
                    logger.info(f"检测到swagger-config格式，包含 {len(config_data['urls'])} 个API文档")
                    merged_doc: Dict[str, Any] = {
                        'openapi': '3.0.0',
                        'info': {'title': 'Merged API', 'version': '1.0.0'},
                        'paths': {},
                        'components': {'schemas': {}},
                    }

                    for url_item in config_data['urls']:
                        if isinstance(url_item, dict):
                            doc_url = url_item.get('url') or url_item.get('name')
                            doc_name = url_item.get('name', '')
                        elif isinstance(url_item, str):
                            doc_url = url_item
                            doc_name = ''
                        else:
                            continue

                        if not doc_url:
                            continue

                        full_url = doc_url if doc_url.startswith('http') else urljoin(self.base_url, doc_url.lstrip('/'))
                        logger.info(f"正在获取API文档: {full_url} ({doc_name})")
                        try:
                            doc_response = self._get(full_url)
                            doc_response.raise_for_status()
                            doc_data = doc_response.json()

                            if 'paths' in doc_data:
                                merged_doc['paths'].update(doc_data['paths'])
                                logger.info(f"成功合并 {len(doc_data['paths'])} 个接口路径")

                            if 'components' in doc_data and 'schemas' in doc_data['components']:
                                merged_doc['components']['schemas'].update(doc_data['components']['schemas'])

                        except Exception as e:
                            logger.warning(f"获取API文档失败 {full_url}: {str(e)}")
                            continue

                    self.swagger_data = merged_doc
                    logger.info(f"合并完成，共 {len(merged_doc['paths'])} 个接口路径")
                else:
                    logger.warning("返回的数据不是swagger-config格式（没有urls字段或urls为空），直接使用返回数据")
                    self.swagger_data = config_data

            elif team is not None and module is not None:
                url = urljoin(self.base_url, f'/v3/api-docs/{team}/{module}')
                logger.info(f"正在获取Swagger文档，URL: {url}")
                response = self._get(url)
                response.raise_for_status()
                self.swagger_data = response.json()
            else:
                raise ValueError("team和module必须同时提供或同时为None")

            if self.verbose:
                logger.debug(f"Swagger文档内容: {self.swagger_data}")

            paths = self.swagger_data.get('paths', {})
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                        request_body = operation.get('requestBody', {})
                        if request_body:
                            logger.debug(f"Path: {path}, Method: {method}")
                            logger.debug(f"RequestBody: {request_body}")

            return self.swagger_data
        except requests.RequestException as e:
            logger.error(f"获取Swagger文档失败: {str(e)}")
            raise

    def parse_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """
        解析所有接口路径和参数

        Returns:
            Dict[str, Dict[str, Any]]: 接口路径和参数的映射
        """
        if not self.swagger_data:
            raise ValueError("请先调用fetch_swagger_doc获取Swagger文档")

        endpoints = {}

        for path, path_item in self.swagger_data.get('paths', {}).items():
            endpoint_info = {}

            for method, operation in path_item.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint_info[method.upper()] = {
                        'summary': operation.get('summary', ''),
                        'description': operation.get('description', ''),
                        'parameters': self._parse_parameters(operation.get('parameters', [])),
                        'requestBody': self._parse_request_body(operation.get('requestBody', {})),
                        'responses': self._parse_responses(operation.get('responses', {})),
                    }

            if endpoint_info:
                endpoints[path] = endpoint_info

        return endpoints

    def _parse_parameters(self, parameters: list) -> list:
        """解析接口参数"""
        parsed_params = []
        for param in parameters:
            param_info = {
                'name': param.get('name'),
                'in': param.get('in'),
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': self._parse_schema(param.get('schema', {})),
            }
            parsed_params.append(param_info)
        return parsed_params

    def _parse_request_body(self, request_body: dict) -> dict:
        """解析请求体"""
        if not request_body:
            return {}

        content = request_body.get('content', {})
        schema = {}

        for content_type, content_info in content.items():
            schema = self._parse_schema(content_info.get('schema', {}))

        return {
            'description': request_body.get('description', ''),
            'required': request_body.get('required', False),
            'schema': schema,
        }

    def _parse_responses(self, responses: dict) -> dict:
        """解析响应信息"""
        parsed_responses = {}
        for status_code, response in responses.items():
            parsed_responses[status_code] = {
                'description': response.get('description', ''),
                'content': self._parse_response_content(response.get('content', {})),
            }
        return parsed_responses

    def _parse_response_content(self, content: dict) -> dict:
        """解析响应内容"""
        parsed_content = {}
        for content_type, content_info in content.items():
            parsed_content[content_type] = {
                'schema': self._parse_schema(content_info.get('schema', {}))
            }
        return parsed_content

    def _parse_schema(self, schema: dict) -> dict:
        """解析Schema信息，包括类型、格式、引用等"""
        if not schema:
            return {}

        if '$ref' in schema:
            ref_path = schema['$ref']
            if ref_path.startswith('#/components/schemas/'):
                ref_name = ref_path.split('/')[-1]
                if self.swagger_data:
                    ref_schema = self.swagger_data.get('components', {}).get('schemas', {}).get(ref_name, {})
                logger.debug(f"递归解析 $ref: {ref_path} => {ref_name}, schema: {ref_schema}")
                return self._get_schema_value(ref_schema)
            logger.warning(f"不支持的 $ref 路径: {ref_path}")
            return {}

        parsed = {
            'type': schema.get('type'),
            'format': schema.get('format'),
            'description': schema.get('description', ''),
            'required': schema.get('required', False),
        }

        if schema.get('type') == 'array':
            items = schema.get('items', {})
            parsed['items'] = self._parse_schema(items)
        elif schema.get('type') == 'object':
            properties = schema.get('properties', {})
            logger.debug(f"对象类型 properties: {properties}")
            if not properties:
                return {}
            return {k: self._get_schema_value(v) for k, v in properties.items()}

        if 'enum' in schema:
            parsed['enum'] = schema['enum']
        if 'default' in schema:
            parsed['default'] = schema['default']
        if 'example' in schema:
            parsed['example'] = schema['example']

        return parsed

    def save_to_yaml(self, endpoints: Dict[str, Dict[str, Any]], output_path: str) -> None:
        """将解析后的接口信息保存到YAML文件"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(endpoints, f, allow_unicode=True, sort_keys=False)

            logger.info(f"接口文档已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存YAML文件失败: {str(e)}")
            raise

    def save_paths_to_yaml(self, endpoints: Dict[str, Dict[str, Any]],
                           output_path: str = '',
                           module: str = '',
                           include_sys_services: bool = False) -> None:
        """
        将接口路径信息保存到 {prefix}_api_path.yaml，
        同时将参数模板保存到 {prefix}_api_params.yaml。

        Args:
            endpoints: 解析后的接口信息
            output_path: _api_path.yaml 完整路径；为空时输出到脚本同级目录
            module: 模块名称，用于生成文件名前缀（gen_md → md）
            include_sys_services: 是否包含 $SYS_ 接口，默认过滤
        """
        try:
            api_dict: Dict[str, Any] = {}
            params_dict_for_yaml: Dict[str, Any] = {}

            for path, methods in endpoints.items():
                if "$SYS_" in path and not include_sys_services:
                    continue
                for method, info in methods.items():
                    self._detail_log(f"\n{'='*50}")
                    self._detail_log(f"开始解析接口: {path} {method}")
                    self._detail_log(f"接口信息: {info}")

                    service_name = info.get('summary', '').strip()
                    if not service_name:
                        service_name = path.split('/')[-1] if '/' in path else path

                    service_name = (service_name
                                    .replace('【系统服务】', '')
                                    .replace('【事件服务】', '')
                                    .replace('【编排服务】', '')
                                    .strip())

                    api_info_for_gen_path: Dict[str, Any] = {
                        'path': path,
                        'method': method.upper(),
                    }
                    description = info.get('description', '').strip()
                    if description:
                        api_info_for_gen_path['description'] = description
                    api_dict[service_name] = api_info_for_gen_path

                    request_params: Any = {}
                    if 'requestBody' in info and info['requestBody']:
                        schema = info['requestBody'].get('schema', {})
                        self._detail_log(f"请求体schema: {schema}")
                        if schema:
                            parsed_params = self._get_schema_value(schema)
                            request_params = parsed_params if isinstance(parsed_params, dict) else {}
                            self._detail_log(f"解析后的请求参数: {request_params}")

                    for param in info.get('parameters', []):
                        if param.get('in') == 'query':
                            param_schema = param.get('schema', {})
                            if not isinstance(request_params, dict):
                                request_params = {}
                            request_params[param['name']] = self._get_schema_value(param_schema)

                    if isinstance(request_params, dict) and 'teamId' in request_params:
                        del request_params['teamId']
                        self._detail_log("已过滤掉 teamId 字段")

                    api_entry_data = request_params or {}

                    if api_entry_data and 'serviceKey' in api_entry_data:
                        path_clean = path.rstrip('/')
                        service_key_value = path_clean.split('/')[-1]
                        api_entry_data['serviceKey'] = service_key_value
                        self._detail_log(f"自动设置 serviceKey: {service_key_value} 对于路径 {path}")

                    params_dict_for_yaml[path] = api_entry_data
                    self._detail_log(f"最终生成的参数结构: {api_entry_data}")
                    self._detail_log(f"{'='*50}\n")

            # 文件名前缀：gen_md → md，scm_pur → pur
            if module:
                prefix = module.split('_')[-1].lower() if '_' in module else module.lower()
            else:
                prefix = 'api'

            # 保存 _api_path.yaml
            paths_info_to_save = {
                'version': '1.0',
                'total_apis': len(api_dict),
                'apis': api_dict,
            }
            gen_path_output_file = Path(output_path) if output_path else Path(__file__).parent / f"{prefix}_api_path.yaml"
            gen_path_output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(gen_path_output_file, 'w', encoding='utf-8') as f:
                yaml.dump(paths_info_to_save, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            logger.info(f"接口路径信息已保存到: {gen_path_output_file}")

            # 保存 _api_params.yaml
            if params_dict_for_yaml:
                params_yaml_output_file = gen_path_output_file.parent / f"{prefix}_api_params.yaml"
                final_params_yaml_structure = {'api_params': params_dict_for_yaml}
                with open(params_yaml_output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(final_params_yaml_structure, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                logger.info(f"接口参数信息已保存到: {params_yaml_output_file}")

        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise

    def _format_request_params(self, info: dict, operation_path: str) -> dict:
        """格式化请求参数，只保留 path 和 body 的映射关系"""
        request_dict_content = {}

        if 'requestBody' in info and info['requestBody']:
            content = info['requestBody'].get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                if schema:
                    body_value = self._get_schema_value(schema)
                    if body_value is not None:
                        request_dict_content[operation_path] = body_value

        return request_dict_content

    def _get_schema_value(self, schema: dict, visited_refs: Optional[set] = None) -> Any:
        """解析schema值，支持循环引用检测"""
        if visited_refs is None:
            visited_refs = set()

        if not schema:
            return {}

        # 处理扁平化结构（无 type/properties/$ref）
        if isinstance(schema, dict) and not any(k in schema for k in ['type', 'properties', '$ref']):
            result = {}
            for key, value in schema.items():
                if isinstance(value, dict):
                    result[key] = self._get_schema_value(value, visited_refs)
                elif isinstance(value, list):
                    result[key] = [
                        self._get_schema_value(item, visited_refs) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    result[key] = value
            return result

        if '$ref' in schema:
            ref_path = schema['$ref']
            logger.debug(f"发现$ref引用: {ref_path}")
            if ref_path.startswith('#/components/schemas/'):
                ref_name = ref_path.split('/')[-1]

                if ref_name in visited_refs:
                    logger.warning(f"检测到循环引用: {ref_name}，跳过以避免无限递归")
                    return {}

                visited_refs.add(ref_name)

                ref_schema = (
                    self.swagger_data.get('components', {}).get('schemas', {}).get(ref_name, {})
                    if self.swagger_data else {}
                )
                logger.debug(f"解析$ref: {ref_path} => {ref_name}")
                logger.debug(f"引用schema内容: {ref_schema}")

                try:
                    result = self._get_schema_value(ref_schema, visited_refs)
                finally:
                    visited_refs.discard(ref_name)

                return result
            logger.warning(f"不支持的 $ref 路径: {ref_path}")
            return {}

        if 'properties' in schema:
            properties = schema['properties']
            logger.debug(f"发现对象类型，properties: {properties}")
            if not properties:
                return {}
            result = {}
            for prop_name, prop_schema in properties.items():
                logger.debug(f"处理属性: {prop_name}, schema: {prop_schema}")
                if prop_name == 'pageNo':
                    result[prop_name] = 1
                elif prop_name == 'pageSize':
                    result[prop_name] = 20
                else:
                    result[prop_name] = self._get_schema_value(prop_schema, visited_refs)
            return result

        if schema.get('type') == 'array':
            items = schema.get('items', {})
            logger.debug(f"处理数组类型，items: {items}")
            return [self._get_schema_value(items, visited_refs)] if items else [{}]

        schema_type = schema.get('type')
        logger.debug(f"处理类型: {schema_type}")

        if schema_type == 'string':
            return None
        elif schema_type in ('integer', 'number'):
            return 0
        elif schema_type == 'boolean':
            return False
        elif schema_type == 'object':
            return {}

        return {}

    def _get_default_value(self, prop_name: str, prop_schema: dict) -> Any:
        """获取属性的默认值"""
        if prop_name == 'pageNo':
            return 1
        elif prop_name == 'pageSize':
            return 20
        elif prop_name == 'id':
            return 1
        return self._get_schema_value(prop_schema)

    def _create_module_index(self, api_list: list) -> dict:
        """创建按模块索引的字典"""
        index: Dict[str, list] = {}
        for api in api_list:
            if api['module'] not in index:
                index[api['module']] = []
            index[api['module']].append(api['id'])
        return index

    def _create_type_index(self, api_list: list) -> dict:
        """创建按服务类型索引的字典"""
        index: Dict[str, list] = {'系统服务': [], '编排服务': []}
        for api in api_list:
            index[api['type']].append(api['id'])
        return index

    def _generate_example_request(self, info: dict) -> dict:
        """生成示例请求数据"""
        example: Dict[str, Any] = {
            'url': '',
            'method': '',
            'headers': {'Content-Type': 'application/json'},
            'params': {},
            'body': {},
        }

        for param in info.get('parameters', []):
            if param.get('in') == 'query':
                example['params'][param['name']] = self._get_example_value(param.get('schema', {}))
            elif param.get('in') == 'header':
                example['headers'][param['name']] = self._get_example_value(param.get('schema', {}))

        if 'requestBody' in info:
            schema = info['requestBody'].get('schema', {})
            example['body'] = self._get_example_value(schema)

        return example

    def _generate_example_response(self, info: dict) -> dict:
        """生成示例响应数据"""
        example: Dict[str, Any] = {
            'status_code': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': {},
        }

        success_response = info.get('responses', {}).get('200', {})
        if success_response:
            content = success_response.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                example['body'] = self._get_example_value(schema)

        return example

    def _get_example_value(self, schema: dict) -> Any:
        """根据schema生成示例值"""
        if not schema:
            return None

        schema_type = schema.get('type')
        if schema_type == 'string':
            return 'string'
        elif schema_type == 'integer':
            return 0
        elif schema_type == 'number':
            return 0.0
        elif schema_type == 'boolean':
            return False
        elif schema_type == 'array':
            items = schema.get('items', {})
            return [self._get_example_value(items)]
        elif schema_type == 'object':
            properties = schema.get('properties', {})
            return {prop: self._get_example_value(prop_schema)
                    for prop, prop_schema in properties.items()}
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 自动登录助手（不依赖测试框架，脚本独立可运行）
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGIN_ENDPOINT = "/iam/api/v1/user/login/account"
SWAGGER_MODULES_CONFIG = PROJECT_ROOT / "config" / "api" / "swagger_modules.yaml"


def _load_env_config(env: str, project: Optional[str]) -> Dict[str, Any]:
    """加载 config/env/{project}/{env}.yaml 或 config/env/{env}.yaml，并替换 ${VAR} 占位符"""
    # 按优先级加载 .env 文件
    dotenv_candidates = [
        PROJECT_ROOT / "config" / "env" / (project or "_none_") / ".env",
        PROJECT_ROOT / "config" / "env" / ".env",
        PROJECT_ROOT / ".env",
    ]
    for dotenv_path in dotenv_candidates:
        if dotenv_path.exists():
            load_dotenv(dotenv_path, override=False)
            logger.info(f"加载环境变量: {dotenv_path}")
            break

    # 定位 YAML
    if project:
        yaml_path = PROJECT_ROOT / "config" / "env" / project / f"{env}.yaml"
        if not yaml_path.exists():
            logger.warning(f"项目配置 {yaml_path} 不存在，回退到默认配置")
            yaml_path = PROJECT_ROOT / "config" / "env" / f"{env}.yaml"
    else:
        yaml_path = PROJECT_ROOT / "config" / "env" / f"{env}.yaml"

    if not yaml_path.exists():
        logger.error(f"环境配置文件不存在: {yaml_path}")
        return {}

    with open(yaml_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    _replace_env_vars(config)
    logger.info(f"加载配置文件: {yaml_path}")
    return config


def _replace_env_vars(obj: Any) -> None:
    """递归将配置中的 ${VAR} 替换为实际环境变量值"""
    pattern = re.compile(r'^\$\{([^}]+)\}$')
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                m = pattern.match(v)
                if m:
                    obj[k] = os.getenv(m.group(1), v)
            else:
                _replace_env_vars(v)
    elif isinstance(obj, list):
        for item in obj:
            _replace_env_vars(item)


def _auto_login(env_config: Dict[str, Any],
                portal_key: str,
                tenant_key: str = "terp") -> requests.Session:
    """
    使用 config/env/{env}.yaml 中的账密自动登录，返回带 Cookie 的 Session。

    portal_config 结构示例：
        portal_config:
          terp:
            TERP_PORTAL:
              iam_url: http://...
              username: admin
              password: xxx
    """
    portal_cfg = (
        env_config.get("portal_config", {})
                  .get(tenant_key, {})
                  .get(portal_key, {})
    )
    if not portal_cfg:
        raise ValueError(
            f"未找到 portal 配置: portal_config.{tenant_key}.{portal_key}\n"
            f"请检查 config/env/{{env}}.yaml"
        )

    iam_url = portal_cfg.get("iam_url", "").rstrip("/")
    cookie = portal_cfg.get("cookie", "")
    username = portal_cfg.get("username", "")
    password = portal_cfg.get("password", "")

    # 优先使用已配置 cookie（支持 config/env/*.yaml 的 ${TEST_XXX_COOKIE}）
    # 与测试框架 LoginService 行为保持一致：有可用 cookie 时跳过账号登录。
    if isinstance(cookie, str) and cookie and not (cookie.startswith("${") and cookie.endswith("}")):
        session = requests.Session()
        session.headers.update({"Cookie": cookie})
        logger.info("检测到 portal cookie，已使用 cookie 模式初始化 Session（跳过账号登录）")
        return session

    if not all([iam_url, username, password]):
        raise ValueError(
            f"portal 配置缺少必要字段 (iam_url / username / password):\n{portal_cfg}"
        )

    session = requests.Session()
    login_url = f"{iam_url}{LOGIN_ENDPOINT}"
    logger.info(f"正在登录: {login_url}  用户: {username}")

    resp = session.post(
        login_url,
        json={"account": username, "password": password},
        headers={
            "Content-Type": "application/json",
            "Origin": iam_url,
            "Referer": f"{iam_url}/",
        },
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    if not (body.get("success") or resp.status_code == 200):
        raise RuntimeError(f"登录失败: {resp.text}")

    logger.info("登录成功，Session Cookie 已保存")
    return session


def _resolve_base_url(env_config: Dict[str, Any],
                      portal_key: str,
                      tenant_key: str = "terp") -> str:
    """从 portal 配置推导 Swagger base URL（优先 swagger_url）。"""
    portal_cfg = (
        env_config.get("portal_config", {})
                  .get(tenant_key, {})
                  .get(portal_key, {})
    )
    return (
        portal_cfg.get("swagger_url")
        or portal_cfg.get("url")
        or portal_cfg.get("portal_url", "")
    ).rstrip("/")


def _module_prefix(module: str) -> str:
    """gen_md → md，scm_pur → pur，erp_fin → fin"""
    return module.split("_")[-1].lower() if "_" in module else module.lower()


def _load_swagger_modules_config() -> Dict[str, Any]:
    """加载 Swagger 模块配置（可选）。"""
    if not SWAGGER_MODULES_CONFIG.exists():
        return {}
    try:
        with open(SWAGGER_MODULES_CONFIG, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            logger.warning(f"模块配置格式异常（应为字典）: {SWAGGER_MODULES_CONFIG}")
            return {}
        return data
    except Exception as exc:
        logger.warning(f"加载模块配置失败，已回退默认行为: {exc}")
        return {}


def _resolve_module_name(input_module: str, module_cfg: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """按配置解析模块名（支持大小写和 aliases）。"""
    normalized = (input_module or "").strip()
    modules = module_cfg.get("modules", {}) if isinstance(module_cfg, dict) else {}
    if not isinstance(modules, dict) or not modules:
        return normalized, {}

    if normalized in modules:
        return normalized, modules.get(normalized) or {}

    for module_name in modules.keys():
        if str(module_name).lower() == normalized.lower():
            return module_name, modules.get(module_name) or {}

    for module_name, meta in modules.items():
        aliases = (meta or {}).get("aliases", [])
        for alias in aliases:
            if str(alias).lower() == normalized.lower():
                return module_name, meta or {}

    return normalized, {}


def _resolve_output_dir(
    cli_output_dir: Optional[str], module_name: str, module_meta: Dict[str, Any]
) -> Path:
    """解析输出目录：命令行 > 配置文件 > 默认规则。"""
    if cli_output_dir:
        return Path(cli_output_dir)

    configured_output = (module_meta or {}).get("output_dir")
    if configured_output:
        configured_path = Path(str(configured_output))
        if configured_path.is_absolute():
            return configured_path
        return PROJECT_ROOT / configured_path

    return PROJECT_ROOT / "config" / "api" / module_name.lower()


def _print_available_modules(module_cfg: Dict[str, Any]) -> None:
    """打印配置文件中维护的可用模块列表。"""
    modules = module_cfg.get("modules", {}) if isinstance(module_cfg, dict) else {}
    if not isinstance(modules, dict) or not modules:
        logger.info(f"未配置模块清单，请维护文件: {SWAGGER_MODULES_CONFIG}")
        return

    logger.info("可用模块清单：")
    for module_name, meta in modules.items():
        aliases = (meta or {}).get("aliases", [])
        output_dir = (meta or {}).get("output_dir", f"config/api/{module_name.lower()}")
        alias_text = f" aliases={aliases}" if aliases else ""
        logger.info(f"  - {module_name} -> {output_dir}{alias_text}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────────────────────────────────────

def _build_arg_parser() -> argparse.ArgumentParser:
    module_cfg = _load_swagger_modules_config()
    configured_modules = module_cfg.get("modules", {}) if isinstance(module_cfg, dict) else {}
    module_hint = ", ".join(list(configured_modules.keys())[:10]) if configured_modules else "gen_md / scm_pur / erp_fin"

    p = argparse.ArgumentParser(
        prog="swagger_parser",
        description="从 Swagger 文档自动生成 {module}_api_path.yaml 和 {module}_api_params.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 最简用法（从 config/env/test.yaml 自动登录）
  python script/swagger_parser.py --module gen_md --team TERP
  python script/swagger_parser.py --module ERP_PLN --team TERP --output-dir config/api/erp_pln

  # 指定环境 + 多项目模式
  python script/swagger_parser.py --module scm_pur --team TERP \\
      --env staging --project my_project

  # 手动传入 Cookie（不自动登录）
  python script/swagger_parser.py --module gen_md --team TERP \\
      --base-url https://your-erp-host:8080 \\
      --cookie "t_iam_test=eyJ..."

  # 包含 $SYS_ 系统服务接口（默认过滤）
  python script/swagger_parser.py --module gen_md --team TERP --include-sys

  # 仅预览，不写入文件
  python script/swagger_parser.py --module gen_md --team TERP --dry-run

  # 自定义输出目录
  python script/swagger_parser.py --module gen_md --team TERP \\
      --output-dir /tmp/api_config

  # 查看配置文件中维护的可用模块
  python script/swagger_parser.py --list-modules
        """,
    )

    # 必填
    p.add_argument("--module", required=False,
                   help=f"模块名称，例如 {module_hint}")
    p.add_argument("--team", required=False,
                   help="Swagger 团队名称，例如 TERP")

    # 登录配置
    p.add_argument("--env", default="test",
                   help="环境名称，对应 config/env/{env}.yaml（默认: test）")
    p.add_argument("--project", default=None,
                   help="多项目模式时的项目名称（对应 config/env/{project}/{env}.yaml）")
    p.add_argument("--portal-key", default="TERP_PORTAL",
                   help="portal 配置 key（默认: TERP_PORTAL）")
    p.add_argument("--tenant-key", default="terp",
                   help="tenant 配置 key（默认: terp）")

    # 手动覆盖
    p.add_argument("--cookie", default=None,
                   help="手动传入 Cookie 字符串，跳过自动登录（需同时指定 --base-url）")
    p.add_argument("--base-url", default=None,
                   help="手动指定 Swagger base URL（自动登录时从 portal_url 配置读取）")

    # 行为控制
    p.add_argument("--include-sys", action="store_true",
                   help="包含 $SYS_ 系统服务接口（默认过滤）")
    p.add_argument("--output-dir", default=None,
                   help="输出目录（默认: config/api/{module}/）")
    p.add_argument("--dry-run", action="store_true",
                   help="仅打印解析结果，不写入文件")
    p.add_argument("--list-modules", action="store_true",
                   help="显示 config/api/swagger_modules.yaml 中维护的可用模块并退出")
    vgroup = p.add_mutually_exclusive_group()
    vgroup.add_argument("--quiet", action="store_true",
                        help="安静模式：仅输出关键进度与结果，不输出逐接口解析明细")
    vgroup.add_argument("--verbose", action="store_true",
                        help="详细模式：输出 DEBUG 日志（含 Swagger 原始文档调试信息）")

    return p


def _configure_logger(*, verbose: bool = False, quiet: bool = False) -> None:
    """统一日志级别：默认 INFO，--verbose 才开启 DEBUG。"""
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level)


def main() -> None:
    args = _build_arg_parser().parse_args()
    _configure_logger(verbose=args.verbose, quiet=args.quiet)
    module_cfg = _load_swagger_modules_config()

    if args.list_modules:
        _print_available_modules(module_cfg)
        return

    if not args.module or not args.team:
        logger.error("缺少必要参数：--module 和 --team（或使用 --list-modules 查看模块清单）")
        sys.exit(2)

    resolved_module, resolved_meta = _resolve_module_name(args.module, module_cfg)
    if resolved_module != args.module:
        logger.info(f"模块名已从 '{args.module}' 解析为 '{resolved_module}'")
    elif module_cfg.get("modules") and resolved_module not in module_cfg.get("modules", {}):
        logger.warning(
            f"模块 '{args.module}' 未在 {SWAGGER_MODULES_CONFIG} 中声明，按原值继续执行"
        )

    # ── 1. 确定 base_url 和 session ──────────────────────────────────────────
    session: Optional[requests.Session] = None
    manual_cookies: Dict[str, str] = {}
    base_url: str = args.base_url or ""

    if args.cookie:
        # 手动 Cookie 模式
        for pair in args.cookie.split(";"):
            pair = pair.strip()
            if "=" in pair:
                k, v = pair.split("=", 1)
                manual_cookies[k.strip()] = v.strip()
        if not base_url:
            logger.error("使用 --cookie 时必须同时指定 --base-url")
            sys.exit(1)
        logger.info(f"使用手动 Cookie，base_url: {base_url}")
    else:
        # 自动登录模式
        env_config = _load_env_config(args.env, args.project)
        if not env_config:
            logger.error("无法加载环境配置，退出")
            sys.exit(1)

        session = _auto_login(env_config, args.portal_key, args.tenant_key)

        if not base_url:
            base_url = _resolve_base_url(env_config, args.portal_key, args.tenant_key)
        if not base_url:
            logger.error(
                "无法确定 base_url，请在配置中设置 portal_url / url，或使用 --base-url"
            )
            sys.exit(1)

    # ── 2. 拉取并解析 Swagger 文档 ───────────────────────────────────────────
    swagger = SwaggerParser(
        base_url=base_url,
        cookies=manual_cookies,
        session=session,
        verbose=args.verbose,
        quiet=args.quiet,
    )

    logger.info(f"拉取 Swagger 文档: team={args.team}, module={resolved_module}")
    swagger.fetch_swagger_doc(team=args.team, module=resolved_module)

    endpoints = swagger.parse_endpoints()
    logger.info(f"共解析到 {len(endpoints)} 个接口路径")

    if not endpoints:
        logger.warning("未解析到任何接口，请检查 team/module 参数或 Cookie 是否有效")
        sys.exit(1)

    # ── 3. 输出 YAML 文件 ────────────────────────────────────────────────────
    output_dir = _resolve_output_dir(args.output_dir, resolved_module, resolved_meta)

    if args.dry_run:
        logger.info("[dry-run] 解析结果预览（前 10 个接口）：")
        preview = dict(list(endpoints.items())[:10])
        print(yaml.dump(preview, allow_unicode=True, sort_keys=False))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = _module_prefix(resolved_module)
    path_yaml = str(output_dir / f"{prefix}_api_path.yaml")

    swagger.save_paths_to_yaml(
        endpoints,
        output_path=path_yaml,
        module=resolved_module,
        include_sys_services=args.include_sys,
    )

    logger.info("✅ 生成完成:")
    logger.info(f"   {output_dir / f'{prefix}_api_path.yaml'}")
    logger.info(f"   {output_dir / f'{prefix}_api_params.yaml'}")


if __name__ == "__main__":
    main()
