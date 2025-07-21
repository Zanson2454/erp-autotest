import requests
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from urllib.parse import urljoin



class SwaggerParser:
    """Swagger文档解析工具类"""
    
    def __init__(self, base_url: str, cookies: Optional[Dict[str, str]] = None):
        """
        初始化Swagger解析器
        
        Args:
            base_url: Swagger API的基础URL
            cookies: 请求需要的cookies
        """
        self.base_url = base_url.rstrip('/')
        self.cookies = cookies or {}
        self.swagger_data = None
        
    def fetch_swagger_doc(self, team: str, module: str) -> Dict[str, Any]:
        """
        获取指定团队和模块的Swagger文档
        
        Args:
            team: 团队名称
            module: 模块名称
            
        Returns:
            Dict[str, Any]: Swagger文档数据
        """
        try:
            url = urljoin(self.base_url, f'/v3/api-docs/{team}/{module}')
            headers = {
                'Accept': 'application/json,*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, cookies=self.cookies)
            response.raise_for_status()
            self.swagger_data = response.json()
            
            # 添加调试日志
            logger.debug(f"Swagger文档内容: {self.swagger_data}")
            
            # 检查paths
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
                        'responses': self._parse_responses(operation.get('responses', {}))
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
                'schema': self._parse_schema(param.get('schema', {}))
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
            'schema': schema
        }
    
    def _parse_responses(self, responses: dict) -> dict:
        """解析响应信息"""
        parsed_responses = {}
        for status_code, response in responses.items():
            parsed_responses[status_code] = {
                'description': response.get('description', ''),
                'content': self._parse_response_content(response.get('content', {}))
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
        """
        解析Schema信息，包括类型、格式、引用等
        
        Args:
            schema: 原始schema
            
        Returns:
            dict: 解析后的schema信息
        """
        if not schema:
            return {}
            
        # 处理$ref引用
        if '$ref' in schema:
            ref_path = schema['$ref']
            # 只支持本地引用
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
            'required': schema.get('required', False)
        }
        
        # 处理数组类型
        if schema.get('type') == 'array':
            items = schema.get('items', {})
            parsed['items'] = self._parse_schema(items)
            
        # 处理对象类型
        elif schema.get('type') == 'object':
            properties = schema.get('properties', {})
            logger.debug(f"对象类型 properties: {properties}")
            if not properties:
                return {}
            # # 优先处理 params.request
            # if 'params' in properties and isinstance(properties['params'], dict):
            #     params_props = properties['params'].get('properties', {})
            #     logger.debug(f"params properties: {params_props}")
            #     if 'request' in params_props and isinstance(params_props['request'], dict):
            #         request_props = params_props['request'].get('properties', {})
            #         logger.debug(f"request properties: {request_props}")
            #         return {k: self._get_schema_value(v) for k, v in request_props.items()}
            # fallback: 递归所有属性
            return {k: self._get_schema_value(v) for k, v in properties.items()}
            
        # 处理枚举类型
        if 'enum' in schema:
            parsed['enum'] = schema['enum']
            
        # 处理默认值
        if 'default' in schema:
            parsed['default'] = schema['default']
            
        # 处理示例值
        if 'example' in schema:
            parsed['example'] = schema['example']
            
        return parsed
    
    def save_to_yaml(self, endpoints: Dict[str, Dict[str, Any]], output_path: str) -> None:
        """
        将解析后的接口信息保存到YAML文件
        
        Args:
            endpoints: 解析后的接口信息
            output_path: 输出文件路径
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(endpoints, f, allow_unicode=True, sort_keys=False)
                
            logger.info(f"接口文档已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存YAML文件失败: {str(e)}")
            raise

    def save_paths_to_yaml(self, endpoints: Dict[str, Dict[str, Any]], output_path: str = '', module: str = '') -> None:
        """
        将接口路径信息保存到YAML文件，采用扁平化结构，便于调用和阅读
        同时将详细参数信息保存到 gen_api_params.yaml
        
        Args:
            endpoints: 解析后的接口信息
            output_path: gen_path.yaml的输出文件路径，默认为swagger_parser.py同级目录下的gen_path.yaml
            module: 模块名称，用于生成文件名前缀
        """
        try:
            api_dict = {}  # For gen_path.yaml
            params_dict_for_yaml = {}  # For gen_api_params.yaml

            for path, methods in endpoints.items():
                if "$SYS_" in path:
                    continue
                for method, info in methods.items():
                    logger.info(f"\n{'='*50}")
                    logger.info(f"开始解析接口: {path} {method}")
                    logger.info(f"接口信息: {info}")
                    
                    # 处理接口路径信息
                    service_name = info.get('summary', '').strip()
                    if not service_name:
                        service_name = path.split('/')[-1] if '/' in path else path
                    
                    service_name = service_name.replace('【系统服务】', '').replace('【事件服务】', '').replace('【编排服务】', '').strip()
                    
                    api_info_for_gen_path = {
                        'path': path,
                        'method': method.upper()
                    }
                    description = info.get('description', '').strip()
                    if description:
                        api_info_for_gen_path['description'] = description
                    api_dict[service_name] = api_info_for_gen_path
                    
                    # 获取请求体参数
                    request_params = {}
                    # 修复点：自动设置serviceKey为接口路径最后一部分
                   
                    if 'requestBody' in info and info['requestBody']:
                        schema = info['requestBody'].get('schema', {})
                        logger.info(f"请求体schema: {schema}")
                        if schema:
                            # 解析请求体schema
                            request_params = self._get_schema_value(schema)
                            logger.info(f"解析后的请求参数: {request_params}")

                    # 处理URL参数
                    for param in info.get('parameters', []):
                        if param.get('in') == 'query':
                            param_schema = param.get('schema', {})
                            request_params[param['name']] = self._get_schema_value(param_schema)
                            
                     # 过滤掉 teamId 字段
                    if 'teamId' in request_params:
                        del request_params['teamId']
                        logger.info(f"已过滤掉 teamId 字段")

                    # 构建参数结构（直接使用解析后的参数，不再包装）
                    api_entry_data = request_params or {}  # 直接保存真实结构
                    
                    # 修复点：自动设置serviceKey为接口路径最后一部分
                    if api_entry_data and 'serviceKey' in api_entry_data:
                        path_clean = path.rstrip('/')
                        service_key_value = path_clean.split('/')[-1]
                        api_entry_data['serviceKey'] = service_key_value
                        logger.info(f"自动设置 serviceKey: {service_key_value} 对于路径 {path}")
                    
                    # 添加到参数字典
                    params_dict_for_yaml[path] = api_entry_data
                    logger.info(f"最终生成的参数结构: {api_entry_data}")
                    logger.info(f"{'='*50}\n")
            
            # 处理模块名称生成文件名前缀
            if module:
                if '_' in module:
                    prefix = module.split('_')[-1].lower()
                else:
                    prefix = module.lower()
            else:
                prefix = 'api'  # 默认前缀
            
            # --- Saving gen_path.yaml ---
            paths_info_to_save = {
                'version': '1.0',
                'total_apis': len(api_dict),
                'apis': api_dict
            }
            if not output_path:  # 这里改为 not output_path
                gen_path_output_file = Path(__file__).parent / f"{prefix}_api_path.yaml"
            else:
                gen_path_output_file = Path(output_path)
            gen_path_output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(gen_path_output_file, 'w', encoding='utf-8') as f:
                yaml.dump(paths_info_to_save, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            logger.info(f"接口路径信息已保存到: {gen_path_output_file}")
            
            # --- Saving gen_api_params.yaml ---
            if params_dict_for_yaml:
                params_yaml_output_file = gen_path_output_file.parent / f"{prefix}_api_params.yaml"
                final_params_yaml_structure = {'api_params': params_dict_for_yaml}
                with open(params_yaml_output_file, 'w', encoding='utf-8') as f:
                    yaml.dump(final_params_yaml_structure, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                logger.info(f"接口参数信息已保存到: {params_yaml_output_file}")
                
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise
            
    def save_unified_api_yaml(self, endpoints: Dict[str, Dict[str, Any]], output_path: str = '', module: str = '') -> None:
        """
        生成统一结构的API配置YAML
        Args:
            endpoints: 解析后的接口信息
            output_path: 输出文件路径（可选）
            module: 模块名称（用于文件名前缀，可选）
        """
        try:
            unified_dict = {}
            for path, methods in endpoints.items():
                if "$SYS_" in path:
                    continue
                for method, info in methods.items():
                    service_name = info.get('summary', '').strip() or path.split('/')[-1]
                    
                    # 清理服务名称，去掉【编排服务】、【事件服务】等后缀
                    service_name = service_name.replace('【系统服务】', '').replace('【事件服务】', '').replace('【编排服务】', '').strip()
                    
                    entry = {
                        'path': path,
                        'method': method.upper()
                    }
                    # body/params
                    request_params = {}
                    if 'requestBody' in info and info['requestBody']:
                        schema = info['requestBody'].get('schema', {})
                        request_params = self._get_schema_value(schema)
                    for param in info.get('parameters', []):
                        if param.get('in') == 'query':
                            param_schema = param.get('schema', {})
                            request_params[param['name']] = self._get_schema_value(param_schema)
                    if request_params:
                        entry['body'] = request_params
                    unified_dict[service_name] = entry

            # 保存
            if not output_path:
                prefix = module.split('_')[-1].lower() if module else 'api'
                output_path = str(Path(__file__).parent / f"{prefix}_api_info.yaml")
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(unified_dict, f, allow_unicode=True, sort_keys=False)
            logger.info(f"统一API信息已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存统一YAML失败: {str(e)}")
            raise
            
    def _format_request_params(self, info: dict, operation_path: str) -> dict:
        """
        格式化请求参数，只保留 path 和 body 的映射关系
        
        Args:
            info: 接口信息
            operation_path: 接口路径
            
        Returns:
            dict: 格式化后的参数，key 为 path，value 为 body
        """
        request_dict_content = {}

        # 处理请求体
        if 'requestBody' in info and info['requestBody']:
            content = info['requestBody'].get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                if schema:
                    # 获取请求体schema的值
                    body_value = self._get_schema_value(schema)
                    if body_value is not None:
                        request_dict_content[operation_path] = body_value
        
        return request_dict_content
        
    def _get_schema_value(self, schema: dict) -> Any:
        if not schema:
            return {}

        # 1. 处理扁平化结构（无 type/properties/$ref）
        if isinstance(schema, dict) and not any(k in schema for k in ['type', 'properties', '$ref']):
            result = {}
            for key, value in schema.items():
                if isinstance(value, dict):
                    result[key] = self._get_schema_value(value)
                elif isinstance(value, list):
                    # 处理数组元素
                    result[key] = [self._get_schema_value(item) if isinstance(item, dict) else item for item in value]
                else:
                    result[key] = value
            return result

        # 2. 标准 Swagger 结构
        if '$ref' in schema:
            ref_path = schema['$ref']
            logger.info(f"发现$ref引用: {ref_path}")
            if ref_path.startswith('#/components/schemas/'):
                ref_name = ref_path.split('/')[-1]
                if self.swagger_data:
                    ref_schema = self.swagger_data.get('components', {}).get('schemas', {}).get(ref_name, {})
                else:
                    ref_schema = {}
                logger.info(f"解析$ref: {ref_path} => {ref_name}")
                logger.info(f"引用schema内容: {ref_schema}")
                return self._get_schema_value(ref_schema)
            logger.warning(f"不支持的 $ref 路径: {ref_path}")
            return {}

        if 'properties' in schema:
            properties = schema['properties']
            logger.info(f"发现对象类型，properties: {properties}")
            if not properties:
                return {}
            result = {}
            for prop_name, prop_schema in properties.items():
                logger.info(f"处理属性: {prop_name}, schema: {prop_schema}")
                # 处理分页参数
                if prop_name == 'pageNo':
                    result[prop_name] = 1
                elif prop_name == 'pageSize':
                    result[prop_name] = 20
                else:
                    result[prop_name] = self._get_schema_value(prop_schema)
            return result

        if schema.get('type') == 'array':
            items = schema.get('items', {})
            logger.info(f"处理数组类型，items: {items}")
            if not items:
                return [{}]
            return [self._get_schema_value(items)]

        # 处理基本类型
        schema_type = schema.get('type')
        logger.info(f"处理类型: {schema_type}")

        if schema_type == 'string':
            return None
        elif schema_type == 'integer':
            return 0  # 使用整数
        elif schema_type == 'number':
            return 0  # 使用整数
        elif schema_type == 'boolean':
            return False
        elif schema_type == 'object':
            return {}
            
        return {}
        
    def _get_default_value(self, prop_name: str, prop_schema: dict) -> Any:
        """
        获取属性的默认值
        
        Args:
            prop_name: 属性名
            prop_schema: 属性schema
            
        Returns:
            Any: 默认值
        """
        # 处理分页参数
        if prop_name == 'pageNo':
            return 1
        elif prop_name == 'pageSize':
            return 20
            
        # 处理ID字段
        if prop_name == 'id':
            return 1
                
        return self._get_schema_value(prop_schema)
        
    def _create_module_index(self, api_list: list) -> dict:
        """创建按模块索引的字典"""
        index = {}
        for api in api_list:
            if api['module'] not in index:
                index[api['module']] = []
            index[api['module']].append(api['id'])
        return index
        
    def _create_type_index(self, api_list: list) -> dict:
        """创建按服务类型索引的字典"""
        index = {'系统服务': [], '编排服务': []}
        for api in api_list:
            index[api['type']].append(api['id'])
        return index
        
    def _generate_example_request(self, info: dict) -> dict:
        """生成示例请求数据"""
        example = {
            'url': '',
            'method': '',
            'headers': {
                'Content-Type': 'application/json'
            },
            'params': {},
            'body': {}
        }
        
        # 处理参数
        for param in info.get('parameters', []):
            if param.get('in') == 'query':
                example['params'][param['name']] = self._get_example_value(param.get('schema', {}))
            elif param.get('in') == 'header':
                example['headers'][param['name']] = self._get_example_value(param.get('schema', {}))
                
        # 处理请求体
        if 'requestBody' in info:
            schema = info['requestBody'].get('schema', {})
            example['body'] = self._get_example_value(schema)
            
        return example
        
    def _generate_example_response(self, info: dict) -> dict:
        """生成示例响应数据"""
        example = {
            'status_code': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {}
        }
        
        # 获取成功响应的schema
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

if __name__ == "__main__":
    # 使用示例
    cookies = {
        'trantor_v2_lng': 'zh-CN',
        'Trantor2-ORIGIN-ORG-ID': '',
        'taid': '3bf8a069-d478-44ea-8e67-48172305f64f',
        'emp_cookie': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbklkIjoiNDlhZmJlOTc3YTdhNGYwYjg1MDZiYjU5M2Q5YWVhNTEiLCJleHBpcmUiOjEyMDk2MDAsInBhdGgiOiIvIiwiZG9tYWluIjoidGVybWludXMuaW8iLCJodHRwT25seSI6dHJ1ZSwic2VjdXJlIjp0cnVlLCJpc3MiOiJpYW0oMi41LjI0LjExMzAuMC1TTkFQU0hPVCkiLCJzdWIiOiJpYW0gdXNlciIsImV4cCI6MTc0ODkxNDUyNywibmJmIjoxNzQ3NzA0OTI3LCJpYXQiOjE3NDc3MDQ5MjcsImp0aSI6IjgzNjhkOTI0N2I2MTQ3N2Q4OTBlZDFhZDNkMTBiNTYyIn0.A1oO4mP5nS9T5jInIrMptxhmGXvj4OKm4wW3I4XpCRI',
        't_iam_test': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbklkIjoiZWE5MDJjMWFlMDBmNDhmOGI3YWI3NDExYTRlYmQxZjMiLCJleHBpcmUiOjI1OTIwMCwicGF0aCI6Ii8iLCJkb21haW4iOiJ0ZXJtaW51cy5pbyIsImh0dHBPbmx5Ijp0cnVlLCJzZWN1cmUiOmZhbHNlLCJpc3MiOiJpYW0oMi41LjI1LjAxMzAuMC1TTkFQU0hPVCkiLCJzdWIiOiJpYW0gdXNlciIsImV4cCI6MTc0ODAwNTcyMSwibmJmIjoxNzQ3NzQ2NTIxLCJpYXQiOjE3NDc3NDY1MjEsImp0aSI6ImNjMGM4ZjY1ZjZjZDQ0MDViYWRiNmVkMTE4Y2Y5NDBjIn0.dAtadVIBUO72fpqvY8yOM2_70ZAWfLSQ-xA0-8ZCXIo'
    }
    
    parser = SwaggerParser(
        base_url="https://t-erp-console-test.app.terminus.io",
        cookies=cookies
    )
    
    # 获取指定团队和模块的Swagger文档
    swagger_doc = parser.fetch_swagger_doc("TERP", "ERP_FIN")
    
    # 解析所有接口
    endpoints = parser.parse_endpoints()
    
    # 保存路径信息到gen_path.yaml
    parser.save_paths_to_yaml(endpoints, module="ERP_FIN")
    
    # 保存统一结构到unified_api.yaml
    # parser.save_unified_api_yaml(endpoints, module="SCM_PUR") 
