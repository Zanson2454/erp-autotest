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
        
        # 创建实体名称到中文术语的映射
        entity_keyword_map = {
            # 计量单位相关
            'uom': ['计量单位', 'UOM'],
            'uom_formula': ['计量单位转换', '单位转换'],
            'uom_conversion': ['计量单位转换', '单位转换'],
            
            # 财务配置相关
            'curr': ['币种', '货币'],
            'exchange_rate': ['汇率'],
            'tax': ['税', '税配置'],
            'cust_tax': ['客户税', '客户税分类'],
            'mat_tax': ['物料税', '物料税分类'],
            
            # 地址银行相关
            'addr': ['地址'],
            'country': ['国家'],
            'bank': ['银行'],
            'sub_bank': ['银行支行', '支行'],
            'timezone': ['时区'],
            
            # 其他配置
            'attr': ['特征', '属性'],
            'brand': ['品牌'],
            'mat_cate': ['类目', '物料类目'],
            'mat_type': ['物料类型'],
            'partner': ['合作伙伴', '相关方'],
            'org': ['组织'],
            'business_partner_type': ['合作伙伴类型'],
            'qualifications': ['资质'],
            'attachment': ['附件'],
            'barcode': ['条码'],
            'dict': ['数据字典'],
            'label': ['标签'],
            'monitoring': ['监控'],
            'calendar': ['日历'],
            'bom': ['BOM'],
            
            # 第一阶段新增实体映射
            # 物料扩展
            'mat_value': ['物料价值', '价值配置'],
            'mat_unit_conversion': ['物料单位转换', '单位转换'],
            'mat_price': ['物料价格', '价格'],
            
            # 组织扩展  
            'org_relation': ['组织关联', '组织关系'],
            'org_dimension': ['组织维度'],
            'org_switch': ['组织切换', '多组织'],
            'org_type': ['组织类型'],
            
            # 员工管理
            'employee': ['员工'],
            
            # 快递物流
            'express': ['快递'],
            
            # 文本管理
            'text_type': ['文本类型'],
            'text_group': ['文本组'],
            
            # 第二阶段新增实体映射
            # 动态表单
            'dynamic_form': ['动态表单', '表单'],
            'form_template': ['表单模板', '模板'],
            
            # 指标中心
            'indicator': ['指标'],
            'indicator_config': ['指标配置'],
            
            # 评分问卷
            'questionnaire': ['问卷', '调查问卷'],
            'survey_template': ['调查模板', '问卷模板'],
            
            # 模型系统
            'model_config': ['模型配置', '模型'],
            'model_template': ['模型模板'],
            
            # 取号规则
            'number_rule': ['取号规则', '编号规则', '编码规则'],
            'number_sequence': ['序号', '序列号'],
            'barcode_rule': ['条码规则'],
            
            # 评分系统
            'score_task': ['评分任务'],
            'score_detail': ['评分详情'],
            
            # 导入导出系统
            'import_export': ['导入导出', '导入', '导出'],
        }
        
        # 获取当前实体的关键词
        keywords = entity_keyword_map.get(self.entity.lower(), [self.entity.lower(), self.entity.upper(), self.entity.title()])
        
        # 添加原始实体名称作为备选关键词
        all_keywords = keywords + [self.entity.lower(), self.entity.upper(), self.entity.title()]
        
        for api_name, api_info in apis.items():
            api_lower = api_name.lower()
            
            # 检查是否包含实体关键词
            if not any(keyword in api_name for keyword in all_keywords):
                continue
                
            # 分类API
            if any(word in api_lower for word in ['保存', 'save', '新增', 'create']):
                entity_apis['create'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['查询分页', 'query_page', 'paging', '分页数据']):
                entity_apis['query'].append({'name': api_name, **api_info})
            elif any(word in api_lower for word in ['查询详情', 'query_detail', 'find_by_id', '根据id查找']):
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
            # 计量单位相关
            "uom": "计量单位管理",
            "uom_formula": "计量单位转换管理", 
            "uom_conversion": "计量单位换算管理",
            
            # 财务配置相关
            "curr": "币种管理",
            "exchange_rate": "汇率管理",
            "tax": "税配置管理",
            "cust_tax": "客户税分类管理",
            "mat_tax": "物料税分类管理",
            
            # 地址银行相关
            "addr": "地址管理",
            "country": "国家管理",
            "bank": "银行管理",
            "sub_bank": "银行支行管理",
            "timezone": "时区管理",
            
            # 其他配置
            "attr": "属性管理",
            "brand": "品牌管理",
            "mat_cate": "类目管理", 
            "mat": "物料管理",
            "mat_type": "物料类型管理",
            "partner": "合作伙伴管理",
            "org": "组织管理",
            "business_partner_type": "合作伙伴类型管理",
            "qualifications": "资质管理",
            "attachment": "附件管理",
            "barcode": "条码管理",
            "dict": "数据字典管理",
            "label": "标签管理",
            "monitoring": "监控管理",
            "calendar": "日历管理",
            "bom": "BOM管理",
            
            # 第一阶段新增实体功能映射
            # 物料扩展
            "mat_value": "物料价值管理",
            "mat_unit_conversion": "物料单位转换管理",
            "mat_price": "物料价格管理",
            
            # 组织扩展
            "org_relation": "组织关联管理",
            "org_dimension": "组织维度管理", 
            "org_switch": "组织切换管理",
            "org_type": "组织类型管理",
            
            # 员工管理
            "employee": "员工管理",
            
            # 快递物流
            "express": "快递公司管理",
            
            # 文本管理
            "text_type": "文本类型管理",
            "text_group": "文本组管理",
            
            # 第二阶段新增实体映射
            # 动态表单
            "dynamic_form": "动态表单管理",
            "form_template": "表单模板管理",
            
            # 指标中心
            "indicator": "指标管理",
            "indicator_config": "指标配置管理",
            
            # 评分问卷
            "questionnaire": "问卷管理",
            "survey_template": "调查模板管理",
            
            # 模型系统
            "model_config": "模型配置管理",
            "model_template": "模型模板管理",
            
            # 取号规则
            "number_rule": "取号规则管理",
            "number_sequence": "序号管理",
            "barcode_rule": "条码规则管理",
            
            # 评分系统
            "score_task": "评分任务管理",
            "score_detail": "评分详情管理",
            
            # 导入导出系统
            "import_export": "导入导出管理",
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


class BatchGenerator:
    """批量用例生成器"""
    
    def __init__(self, module: str):
        self.module = module
        self.project_root = Path(__file__).parent.parent
        
        # 预定义的实体组配置
        self.entity_groups = {
            "gen_md": {
                # 核心业务实体
                "core": {
                    "description": "核心业务实体",
                    "entities": [
                        {"name": "brand", "output": "mat", "desc": "品牌管理"},
                        {"name": "mat_cate", "output": "mat", "desc": "物料类目管理"},
                        {"name": "mat", "output": "mat", "desc": "标准物料管理"},
                        {"name": "partner", "output": "partner", "desc": "合作伙伴管理"},
                        {"name": "org", "output": "org", "desc": "组织管理"},
                    ]
                },
                
                # 第一阶段：核心业务扩展
                "phase1": {
                    "description": "核心业务扩展",
                    "entities": [
                        {"name": "mat_value", "output": "mat", "desc": "物料价值管理"},
                        {"name": "mat_unit_conversion", "output": "mat", "desc": "物料单位转换管理"},
                        {"name": "mat_price", "output": "mat", "desc": "物料价格管理"},
                        {"name": "org_relation", "output": "org", "desc": "组织关联管理"},
                        {"name": "org_dimension", "output": "org", "desc": "组织维度管理"},
                        {"name": "org_switch", "output": "org", "desc": "组织切换管理"},
                        {"name": "org_type", "output": "org", "desc": "组织类型管理"},
                        {"name": "employee", "output": "org", "desc": "员工管理"},
                        {"name": "express", "output": "cf_logistics", "desc": "快递公司管理"},
                        {"name": "text_type", "output": "cf_text", "desc": "文本类型管理"},
                        {"name": "text_group", "output": "cf_text", "desc": "文本组管理"},
                    ]
                },
                
                # 第二阶段：系统功能
                "phase2": {
                    "description": "系统功能接口",
                    "entities": [
                        {"name": "dynamic_form", "output": "cf_form", "desc": "动态表单管理"},
                        {"name": "score_task", "output": "cf_score", "desc": "评分任务管理"},
                        {"name": "score_detail", "output": "cf_score", "desc": "评分详情管理"},
                        {"name": "number_rule", "output": "cf_rule", "desc": "编码规则管理"},
                        {"name": "barcode_rule", "output": "cf_rule", "desc": "条码规则管理"},
                        {"name": "indicator", "output": "cf_indicator", "desc": "指标管理"},
                        {"name": "import_export", "output": "cf_import", "desc": "导入导出管理"},
                    ]
                },
                
                # 配置模块：按功能分组
                "config": {
                    "description": "配置管理模块",
                    "entities": [
                        # 计量单位
                        {"name": "uom", "output": "cf_measurement", "desc": "计量单位管理"},
                        {"name": "uom_formula", "output": "cf_measurement", "desc": "计量单位转换管理"},
                        {"name": "uom_conversion", "output": "cf_measurement", "desc": "计量单位换算管理"},
                        
                        # 财务配置
                        {"name": "curr", "output": "cf_finance", "desc": "币种管理"},
                        {"name": "exchange_rate", "output": "cf_finance", "desc": "汇率管理"},
                        {"name": "tax", "output": "cf_finance", "desc": "税配置管理"},
                        {"name": "cust_tax", "output": "cf_finance", "desc": "客户税分类管理"},
                        {"name": "mat_tax", "output": "cf_finance", "desc": "物料税分类管理"},
                        
                        # 地址银行
                        {"name": "addr", "output": "cf_location_bank", "desc": "地址管理"},
                        {"name": "country", "output": "cf_location_bank", "desc": "国家管理"},
                        {"name": "bank", "output": "cf_location_bank", "desc": "银行管理"},
                        {"name": "sub_bank", "output": "cf_location_bank", "desc": "银行支行管理"},
                        {"name": "timezone", "output": "cf_location_bank", "desc": "时区管理"},
                        
                        # 其他配置
                        {"name": "bom", "output": "cf_bom", "desc": "BOM管理"},
                        {"name": "barcode", "output": "cf_barcode", "desc": "条码管理"},
                        {"name": "dict", "output": "cf_data_dict", "desc": "数据字典管理"},
                        {"name": "label", "output": "cf_label_attr", "desc": "标签管理"},
                        {"name": "attr", "output": "cf_label_attr", "desc": "属性管理"},
                        {"name": "attachment", "output": "cf_attachment", "desc": "附件管理"},
                        {"name": "qualifications", "output": "cf_qualification", "desc": "资质管理"},
                        {"name": "monitoring", "output": "cf_monitoring", "desc": "监控管理"},
                        {"name": "calendar", "output": "cf_calendar", "desc": "日历管理"},
                        {"name": "business_partner_type", "output": "cf_business_partner", "desc": "业务伙伴类型管理"},
                    ]
                }
            }
        }
    
    def list_groups(self):
        """列出可用的实体组"""
        if self.module not in self.entity_groups:
            print(f"❌ 模块 {self.module} 没有预定义的实体组")
            return
            
        groups = self.entity_groups[self.module]
        print(f"\n📋 {self.module.upper()} 模块可用的实体组:")
        
        for group_name, group_config in groups.items():
            entity_count = len(group_config["entities"])
            print(f"\n📁 {group_name} - {group_config['description']}")
            print(f"   实体数量: {entity_count}个")
            
            # 按输出目录分组显示
            by_output = {}
            for entity in group_config["entities"]:
                output = entity["output"]
                if output not in by_output:
                    by_output[output] = []
                by_output[output].append(entity)
            
            for output_dir, entities in by_output.items():
                print(f"   📂 {output_dir}/ ({len(entities)}个)")
                for entity in entities[:3]:  # 只显示前3个
                    print(f"      - {entity['desc']}")
                if len(entities) > 3:
                    print(f"      ... 还有{len(entities)-3}个")
    
    def analyze_group(self, group_name: str):
        """分析实体组的API"""
        if self.module not in self.entity_groups:
            print(f"❌ 模块 {self.module} 没有预定义的实体组")
            return
            
        groups = self.entity_groups[self.module]
        if group_name not in groups:
            print(f"❌ 实体组 {group_name} 不存在")
            print(f"可用组: {', '.join(groups.keys())}")
            return
            
        group_config = groups[group_name]
        print(f"\n🔍 分析实体组: {group_name} - {group_config['description']}")
        
        for entity in group_config["entities"]:
            print(f"\n--- 分析 {entity['desc']} ({entity['name']}) ---")
            
            generator = CaseGenerator(self.module, entity["name"], f"testcases/{self.module}/{entity['output']}")
            generator.analyze_apis()
    
    def generate_group(self, group_name: str, case_type: str = "crud", with_config: bool = False):
        """生成实体组的用例"""
        if self.module not in self.entity_groups:
            print(f"❌ 模块 {self.module} 没有预定义的实体组")
            return
            
        groups = self.entity_groups[self.module]
        if group_name not in groups:
            print(f"❌ 实体组 {group_name} 不存在")
            print(f"可用组: {', '.join(groups.keys())}")
            return
            
        group_config = groups[group_name]
        print(f"\n🚀 生成实体组: {group_name} - {group_config['description']}")
        
        success_count = 0
        fail_count = 0
        
        # 按输出目录分组处理
        by_output = {}
        for entity in group_config["entities"]:
            output = entity["output"]
            if output not in by_output:
                by_output[output] = []
            by_output[output].append(entity)
        
        for output_dir, entities in by_output.items():
            print(f"\n--- 生成 {output_dir}/ 目录的用例 ---")
            
            # 创建输出目录
            output_path = Path(f"testcases/{self.module}/{output_dir}")
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 生成配置检查用例
            if with_config:
                config_file = output_path / f"test_00_{output_dir}_config_check.py"
                if not config_file.exists() and entities:
                    print(f"📝 生成配置检查用例 - {config_file.name}")
                    try:
                        generator = CaseGenerator(self.module, entities[0]["name"], str(output_path))
                        content = generator.generate_config_check_case()
                        generator.save_to_file(content, config_file.name)
                        success_count += 1
                    except Exception as e:
                        print(f"❌ 配置检查用例生成失败: {str(e)}")
                        fail_count += 1
            
            # 生成CRUD用例
            for entity in entities:
                file_name = f"test_{entity['name']}_management.py"
                file_path = output_path / file_name
                
                if file_path.exists():
                    print(f"⏭️  跳过 {file_name} - 文件已存在")
                    continue
                
                print(f"📝 生成 {entity['desc']} - {file_name}")
                
                try:
                    generator = CaseGenerator(self.module, entity["name"], str(output_path))
                    content = generator.generate(case_type)
                    generator.save_to_file(content, file_name)
                    print(f"✅ 生成成功: {file_name}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ 生成失败: {str(e)}")
                    fail_count += 1
        
        print(f"\n📊 实体组 {group_name} 生成完成: 成功{success_count}个，失败{fail_count}个")
        
        if success_count > 0:
            print(f"\n🎉 建议下一步:")
            print(f"1. 运行覆盖率统计:")
            print(f"   python script/case_coverage_stat.py --api_path_yaml testdata/{self.module}/{self.module.split('_')[-1]}_api_path.yaml --case_dir testcases/{self.module} --output_json reports/{self.module}_coverage_{group_name}.json")
            print(f"2. 检查和调试生成的用例")


def parse_args_enhanced():
    """增强的参数解析"""
    parser = argparse.ArgumentParser(description="ERP自动化测试用例生成器（增强版）")
    
    # 原有的单个用例生成参数
    parser.add_argument('--module', help='模块名称，如: gen_md, prd, fin, scm')
    parser.add_argument('--entity', help='业务实体名称，如: brand, mat_cate, partner')
    parser.add_argument('--output', help='输出目录，如: testcases/gen_md/mat/')
    parser.add_argument('--type', default='crud', choices=['crud', 'config'], help='用例类型: crud(增删改查) 或 config(配置检查)')
    parser.add_argument('--analyze', action='store_true', help='只分析API，不生成用例')
    
    # 新增的批量生成参数
    parser.add_argument('--batch', help='批量模式，可选: list, analyze, generate')
    parser.add_argument('--group', help='实体组名称，如: core, phase1, phase2, config')
    parser.add_argument('--with-config', action='store_true', help='同时生成配置检查用例')
    
    return parser.parse_args()


def main_enhanced():
    """增强的主函数"""
    args = parse_args_enhanced()
    
    # 批量模式
    if args.batch:
        if not args.module:
            print("❌ 批量模式需要指定 --module 参数")
            return
            
        batch_generator = BatchGenerator(args.module)
        
        if args.batch == "list":
            batch_generator.list_groups()
        elif args.batch == "analyze":
            if not args.group:
                print("❌ 分析模式需要指定 --group 参数")
                return
            batch_generator.analyze_group(args.group)
        elif args.batch == "generate":
            if not args.group:
                print("❌ 生成模式需要指定 --group 参数")
                return
            batch_generator.generate_group(args.group, args.type, args.with_config)
        else:
            print(f"❌ 不支持的批量模式: {args.batch}")
            print("支持的批量模式: list, analyze, generate")
        return
    
    # 单个用例生成模式（原有逻辑）
    if not all([args.module, args.entity, args.output]):
        print("❌ 单个用例生成模式需要指定 --module, --entity, --output 参数")
        print("\n💡 提示: 使用批量模式可以快速生成多个用例:")
        print("   python script/case_generator.py --module gen_md --batch list")
        return
    
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
    # 使用增强的主函数
    main_enhanced()