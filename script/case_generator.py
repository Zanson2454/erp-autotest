#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP自动化测试用例生成器

基于API配置文件自动生成标准CRUD测试用例
支持：
1. 标准CRUD操作用例生成
2. 配置检查用例生成  
3. 批量操作用例生成
4. 自定义模板支持

用法：
python script/case_generator.py --module gen_md --entity brand --output testcases/gen_md/mat/
"""

import argparse
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class CaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, module: str, entity: str, output_dir: str):
        self.module = module
        self.entity = entity
        self.output_dir = Path(output_dir)
        self.project_root = Path(__file__).parent.parent
        
        # 加载配置
        self.api_config = self._load_api_config()
        self.param_config = self._load_param_config()
        
        # 分析API
        self.entity_apis = self._extract_entity_apis()
        
    def _load_api_config(self) -> Dict:
        """加载API路径配置"""
        config_path = self.project_root / f"testdata/{self.module}/{self.module.split('_')[-1]}_api_path.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _load_param_config(self) -> Dict:
        """加载API参数配置"""
        config_path = self.project_root / f"testdata/{self.module}/{self.module.split('_')[-1]}_api_params.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _extract_entity_apis(self) -> Dict[str, List[Dict]]:
        """提取实体相关的API"""
        apis = self.api_config.get('apis', {})
        entity_apis = {
            'create': [],
            'query': [],
            'update': [],
            'delete': [],
            'detail': [],
            'batch': [],
            'import_export': []
        }
        
        entity_keywords = [self.entity.lower(), self.entity.upper(), self.entity.title()]
        
        for api_name, api_info in apis.items():
            api_lower = api_name.lower()
            
            # 检查是否包含实体关键词
            if not any(keyword in api_name for keyword in entity_keywords):
                continue
                
            # 分类API
            if any(word in api_lower for word in ['保存', 'save', '新增', 'create']):
                entity_apis['create'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['查询分页', 'query_page', 'paging']):
                entity_apis['query'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['查询详情', 'query_detail', 'find_by_id']):
                entity_apis['detail'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['修改', 'update', '编辑']):
                entity_apis['update'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['删除', 'delete']):
                entity_apis['delete'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['批量', 'batch']):
                entity_apis['batch'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['导入', 'import', '导出', 'export']):
                entity_apis['import_export'].append({'name': api_name, **api_info})
                
        return entity_apis
        
    def generate_crud_case(self) -> str:
        """生成标准CRUD测试用例"""
        template = f'''import allure
import pytest
from testcases.{self.module} import {self._get_base_test_class()}
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("{self._get_epic_name()}")
@allure.feature("{self._get_feature_name()}")
class Test{self.entity.title()}Management({self._get_base_test_class()}):
    """{self._get_feature_name()}测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.{self.entity.lower()}_id = None
        cls.{self.entity.lower()}_code = None
        cls.logger.info("{self._get_feature_name()}测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的{self._get_feature_name()}数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="{self._get_table_name()}",
                where="{self.entity.lower()}_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {{str(e)}}")

{self._generate_create_case()}

{self._generate_query_case()}

{self._generate_detail_case()}

{self._generate_update_case()}

{self._generate_delete_case()}
'''
        return template
        
    def _generate_create_case(self) -> str:
        """生成新增用例"""
        if not self.entity_apis['create']:
            return ""
            
        api_info = self.entity_apis['create'][0]
        api_name = api_info['name']
        
        return f'''    @case_decorator(
        story="{self._get_feature_name()}",
        title="测试新增{self._get_feature_name()}",
        description="验证新增{self._get_feature_name()}功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["{self._get_feature_name()}", "新增"]
    )
    def test_save_{self.entity.lower()}(self):
        """
        新增{self._get_feature_name()}用例
        """
        try:
            # 准备{self._get_feature_name()}数据
            {self.entity.lower()}_code = self.mock_data.generate_unique_code(tag="{self.entity.title()}")
            {self.entity.lower()}_name = f"{self._get_feature_name()}_{{self.mock_data.get_timestamp()}}"

            # 调用保存接口
            api_path = self.get_api_path("{api_name}")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["{self.entity.lower()}_code", "{self.entity.lower()}_name"],
                ["params", "request"]
            )
            set_dict = {{
                "{self.entity.lower()}_code": {self.entity.lower()}_code,
                "{self.entity.lower()}_name": {self.entity.lower()}_name
            }}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {{filtered_params}}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            {self.entity.lower()}_id = response.get("data", {{}}).get("data", {{}})

            # 保存{self._get_feature_name()}信息供后续用例使用
            self.{self.entity.lower()}_id = {self.entity.lower()}_id
            self.{self.entity.lower()}_code = {self.entity.lower()}_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise'''
            
    def _generate_query_case(self) -> str:
        """生成查询列表用例"""
        if not self.entity_apis['query']:
            return ""
            
        api_info = self.entity_apis['query'][0]
        api_name = api_info['name']
        
        return f'''    @case_decorator(
        story="{self._get_feature_name()}",
        title="测试查询{self._get_feature_name()}列表",
        description="验证{self._get_feature_name()}列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["{self._get_feature_name()}", "查询"]
    )
    def test_query_{self.entity.lower()}_list(self):
        """
        查询{self._get_feature_name()}列表用例
        """
        try:
            # 调用查询接口
            api_path = self.get_api_path("{api_name}")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )
            set_dict = {{
                "pageable": {{
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }},
                "fields": [
                    {{"name": "{self.entity.lower()}_code", "type": "TEXT"}},
                    {{"name": "{self.entity.lower()}_name", "type": "TEXT"}}
                ]
            }}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {{filtered_params}}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {{}}).get("data", {{}}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise'''
            
    def _generate_detail_case(self) -> str:
        """生成查询详情用例"""
        if not self.entity_apis['detail']:
            return ""
            
        api_info = self.entity_apis['detail'][0]
        api_name = api_info['name']
        
        return f'''    @case_decorator(
        story="{self._get_feature_name()}",
        title="测试查询{self._get_feature_name()}详情",
        description="验证{self._get_feature_name()}详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["{self._get_feature_name()}", "查询"]
    )
    def test_query_{self.entity.lower()}_detail(self):
        """
        查询{self._get_feature_name()}详情用例
        """
        try:
            # 获取{self._get_feature_name()}ID
            if not self.{self.entity.lower()}_id:
                self.test_save_{self.entity.lower()}()

            # 调用详情查询接口
            api_path = self.get_api_path("{api_name}")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {{"id": self.{self.entity.lower()}_id}}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {{filtered_params}}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise'''
            
    def _generate_update_case(self) -> str:
        """生成修改用例"""
        if not self.entity_apis['update']:
            return ""
            
        api_info = self.entity_apis['update'][0]
        api_name = api_info['name']
        
        return f'''    @case_decorator(
        story="{self._get_feature_name()}",
        title="测试修改{self._get_feature_name()}",
        description="验证修改{self._get_feature_name()}功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["{self._get_feature_name()}", "修改"]
    )
    def test_update_{self.entity.lower()}(self):
        """
        修改{self._get_feature_name()}用例
        """
        try:
            # 获取{self._get_feature_name()}信息
            if not self.{self.entity.lower()}_id:
                self.test_save_{self.entity.lower()}()

            # 调用修改接口
            api_path = self.get_api_path("{api_name}")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id", "{self.entity.lower()}_code", "{self.entity.lower()}_name"],
                ["params", "request"]
            )
            set_dict = {{
                "id": self.{self.entity.lower()}_id,
                "{self.entity.lower()}_code": self.{self.entity.lower()}_code,
                "{self.entity.lower()}_name": f"修改_{self._get_feature_name()}_{{self.mock_data.get_timestamp()}}"
            }}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {{filtered_params}}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise'''
            
    def _generate_delete_case(self) -> str:
        """生成删除用例"""
        if not self.entity_apis['delete']:
            return ""
            
        api_info = self.entity_apis['delete'][0]
        api_name = api_info['name']
        
        return f'''    @case_decorator(
        story="{self._get_feature_name()}",
        title="测试删除{self._get_feature_name()}",
        description="验证删除{self._get_feature_name()}功能",
        severity="normal",
        order=5,
        smoke=True,
        tags=["{self._get_feature_name()}", "删除"]
    )
    def test_delete_{self.entity.lower()}(self):
        """
        删除{self._get_feature_name()}用例
        """
        try:
            # 获取{self._get_feature_name()}信息
            if not self.{self.entity.lower()}_id:
                self.test_save_{self.entity.lower()}()

            # 调用删除接口
            api_path = self.get_api_path("{api_name}")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["ids"],
                ["params", "request"]
            )
            set_dict = {{"ids": [self.{self.entity.lower()}_id]}}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {{filtered_params}}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise'''
            
    def _get_base_test_class(self) -> str:
        """获取基础测试类名"""
        if self.module == "gen_md":
            return "GenMdBaseTest"
        elif self.module == "prd":
            return "PrdBaseTest"
        elif self.module == "fin":
            return "FinBaseTest"
        elif self.module == "scm":
            return "ScmBaseTest"
        else:
            return "BaseTest"
            
    def _get_epic_name(self) -> str:
        """获取Epic名称"""
        epic_map = {
            "gen_md": "通用基础数据",
            "prd": "生产管理",
            "fin": "财务管理", 
            "scm": "供应链管理"
        }
        return epic_map.get(self.module, "业务模块")
        
    def _get_feature_name(self) -> str:
        """获取Feature名称"""
        entity_map = {
            "brand": "品牌管理",
            "mat_cate": "类目管理", 
            "mat": "物料管理",
            "partner": "合作伙伴管理",
            "org": "组织管理"
        }
        return entity_map.get(self.entity.lower(), f"{self.entity.title()}管理")
        
    def _get_table_name(self) -> str:
        """获取数据表名"""
        if self.module == "gen_md":
            return f"gen_{self.entity.lower()}_md"
        else:
            return f"{self.module}_{self.entity.lower()}_md"
            
    def generate_config_check_case(self) -> str:
        """生成配置检查用例"""
        template = f'''import allure
import pytest
from testcases.{self.module} import {self._get_base_test_class()}
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("{self._get_epic_name()}")
@allure.feature("{self._get_feature_name()}配置检查")
class Test{self.entity.title()}ConfigCheck({self._get_base_test_class()}):
    """{self._get_feature_name()}配置检查测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.required_{self.entity.lower()}_types = ["TYPE1", "TYPE2"]  # 必需的{self._get_feature_name()}类型编码

    @case_decorator(
        story="{self._get_feature_name()}配置检查",
        title="测试{self._get_feature_name()}配置是否完整",
        description="验证系统中是否包含所需的基础{self._get_feature_name()}配置",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["{self._get_feature_name()}", "配置检查"]
    )
    def test_{self.entity.lower()}_type_config(self):
        """
        检查{self._get_feature_name()}配置用例
        验证系统中是否包含必需的{self._get_feature_name()}类型编码
        """
        try:
            # 这里需要根据实际API进行调整
            api_path = self.get_api_path("待补充具体API名称")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields"],
                ["params", "request"]
            )

            # 设置分页和查询字段参数
            set_dict = {{
                "pageable": {{
                    "pageNo": 1,
                    "pageSize": 100,
                    "needTotal": True
                }},
                "fields": [
                    {{"name": "{self.entity.lower()}_type_code", "type": "TEXT"}},
                    {{"name": "{self.entity.lower()}_type_name", "type": "TEXT"}}
                ]
            }}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {{filtered_params}}")

            # 发送请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            {self.entity.lower()}_type_list = response.get("data", {{}}).get("data", {{}}).get("data", [])
            {self.entity.lower()}_type_codes = [item.get("{self.entity.lower()}_type_code") for item in {self.entity.lower()}_type_list]
            self.logger.info(f"{self.entity.lower()}_type_codes: {{{self.entity.lower()}_type_codes}}")
            
            # 检查所有必需的{self._get_feature_name()}类型是否都存在
            self.assert_util.assert_all_in(
                self.required_{self.entity.lower()}_types, 
                {self.entity.lower()}_type_codes,
                "{self._get_feature_name()}配置不完整"
            )

            # 记录到Allure报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"所有必需的{self._get_feature_name()}类型均已配置: {{', '.join(self.required_{self.entity.lower()}_types)}}", "检查结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
'''
        return template
        
    def generate(self, case_type: str = "crud") -> str:
        """生成测试用例"""
        if case_type == "crud":
            return self.generate_crud_case()
        elif case_type == "config":
            return self.generate_config_check_case()
        else:
            raise ValueError(f"不支持的用例类型: {case_type}")
            
    def save_to_file(self, content: str, filename: str) -> None:
        """保存用例到文件"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"用例文件已生成: {file_path}")
        
    def analyze_apis(self) -> None:
        """分析实体相关API"""
        print(f"\n=== {self.entity.title()} 实体API分析 ===")
        
        for operation, apis in self.entity_apis.items():
            if apis:
                print(f"\n{operation.upper()}操作 ({len(apis)}个API):")
                for api in apis[:3]:  # 只显示前3个
                    print(f"  - {api['name']}")
                if len(apis) > 3:
                    print(f"  ... 还有{len(apis)-3}个API")
            else:
                print(f"\n{operation.upper()}操作: 未找到相关API")


def parse_args():
    parser = argparse.ArgumentParser(description="ERP自动化测试用例生成器")
    parser.add_argument('--module', required=True, help='模块名称，如: gen_md, prd, fin, scm')
    parser.add_argument('--entity', required=True, help='业务实体名称，如: brand, mat_cate, partner')
    parser.add_argument('--output', required=True, help='输出目录，如: testcases/gen_md/mat/')
    parser.add_argument('--type', default='crud', choices=['crud', 'config'], help='用例类型: crud(增删改查) 或 config(配置检查)')
    parser.add_argument('--analyze', action='store_true', help='只分析API，不生成用例')
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        generator = CaseGenerator(args.module, args.entity, args.output)
        
        if args.analyze:
            generator.analyze_apis()
            return
            
        # 生成用例
        content = generator.generate(args.type)
        
        # 确定文件名
        if args.type == "crud":
            filename = f"test_{args.entity.lower()}_management.py"
        else:
            filename = f"test_00_{args.entity.lower()}_config_check.py"
            
        # 保存文件
        generator.save_to_file(content, filename)
        
        print(f"\n✅ 用例生成成功！")
        print(f"模块: {args.module}")
        print(f"实体: {args.entity}")
        print(f"类型: {args.type}")
        print(f"文件: {Path(args.output) / filename}")
        
    except Exception as e:
        print(f"❌ 用例生成失败: {str(e)}")
        raise


if __name__ == '__main__':
    main()