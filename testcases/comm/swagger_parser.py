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
        """解析Schema信息"""
        if not schema:
            return {}
            
        return {
            'type': schema.get('type'),
            'format': schema.get('format'),
            'items': self._parse_schema(schema.get('items', {})),
            'properties': {
                prop: self._parse_schema(prop_schema)
                for prop, prop_schema in schema.get('properties', {}).items()
            }
        }
    
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

    def save_paths_to_yaml(self, endpoints: Dict[str, Dict[str, Any]], output_path: str = None) -> None:
        """
        将接口路径信息保存到YAML文件，按照系统服务和编排服务分类
        
        Args:
            endpoints: 解析后的接口信息
            output_path: 输出文件路径，默认为swagger_parser.py同级目录下的gen_path.yaml
        """
        try:
            # 初始化分类结构
            paths_info = {
                "系统服务": {},
                "编排服务": {}
            }
            
            # 用于临时存储分组信息
            temp_groups = {
                "系统服务": {},
                "编排服务": {}
            }
            
            # 遍历所有路径和方法
            for path, methods in endpoints.items():
                for method, info in methods.items():
                    # 提取服务名称（从summary中）
                    service_name = info.get('summary', '').strip()
                    if not service_name:
                        service_name = path.split('/')[-1]
                    
                    # 移除标题末尾的服务类型标记
                    service_name = service_name.replace('【系统服务】', '').replace('【事件服务】', '').replace('【编排服务】', '').strip()
                    
                    # 构建API路径
                    api_path = path
                    
                    # 根据API路径判断是系统服务还是编排服务
                    if '$SYS_' in api_path:
                        category = "系统服务"
                        # 系统服务直接放在系统服务目录下
                        paths_info[category][service_name] = api_path
                    else:
                        category = "编排服务"
                        # 获取服务前缀（第一个下划线或横线前的部分）
                        prefix = service_name.split('_')[0].split('-')[0] if '_' in service_name or '-' in service_name else service_name
                        
                        # 如果前缀目录不存在，创建它
                        if prefix not in temp_groups[category]:
                            temp_groups[category][prefix] = {}
                        
                        # 移除标题中的前缀（如果存在）
                        display_name = service_name
                        if service_name.startswith(prefix + '-') or service_name.startswith(prefix + '_'):
                            display_name = service_name[len(prefix)+1:].strip()
                        
                        # 将API信息添加到临时分组中
                        temp_groups[category][prefix][display_name] = api_path
            
            # 处理临时分组，如果分组下只有一个API，则直接使用前缀作为标题
            for category in ["系统服务", "编排服务"]:
                for prefix, apis in temp_groups[category].items():
                    if len(apis) == 1:
                        # 如果分组下只有一个API，直接使用前缀作为标题
                        api_path = list(apis.values())[0]
                        paths_info[category][prefix] = api_path
                    else:
                        # 如果分组下有多个API，保持分组结构
                        paths_info[category][prefix] = apis
            
            # 设置默认输出路径为swagger_parser.py同级目录
            if output_path is None:
                output_path = Path(__file__).parent / "gen_path.yaml"
            else:
                output_path = Path(output_path)
                
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(paths_info, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                
            logger.info(f"接口路径信息已保存到: {output_path}")
        except Exception as e:
            logger.error(f"保存路径信息失败: {str(e)}")
            raise

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
        base_url="https://t-erp-console-dev.app.terminus.io",
        cookies=cookies
    )
    
    # 获取指定团队和模块的Swagger文档
    swagger_doc = parser.fetch_swagger_doc("TERP", "ERP_FIN")
    
    # 解析所有接口
    endpoints = parser.parse_endpoints()
    
    # 保存路径信息到gen_path.yaml
    parser.save_paths_to_yaml(endpoints) 