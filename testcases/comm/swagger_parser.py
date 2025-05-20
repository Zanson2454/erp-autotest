import requests
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from urllib.parse import urljoin



class SwaggerParser:
    """Swagger文档解析工具类"""
    
    def __init__(self, base_url: str):
        """
        初始化Swagger解析器
        
        Args:
            base_url: Swagger API的基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.swagger_data = None
        
    def fetch_swagger_doc(self, module: str) -> Dict[str, Any]:
        """
        获取指定模块的Swagger文档
        
        Args:
            module: 模块名称
            
        Returns:
            Dict[str, Any]: Swagger文档数据
        """
        try:
            url = urljoin(self.base_url, f'/swagger/{module}/swagger.json')
            response = requests.get(url)
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

if __name__ == "__main__":
    # 使用示例
    parser = SwaggerParser("http://your-api-base-url")
    
    # 获取指定模块的Swagger文档
    swagger_doc = parser.fetch_swagger_doc("your-module")
    
    # 解析所有接口
    endpoints = parser.parse_endpoints()
    
    # 保存到YAML文件
    parser.save_to_yaml(endpoints, "api_docs.yaml") 