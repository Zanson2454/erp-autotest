# -*- coding: utf-8 -*-
"""
销售发票单据管理测试用例
包含：销售发票的查询、删除、撤回、反过账等核心功能测试
"""

from re import S
import re
import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP通业财模块")
@allure.feature("销售发票管理")
class TestSbDocManagement(FinBaseTest):
    """销售发票单据管理测试类"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("销售发票管理测试类初始化完成")
    
    def _build_view_condition(self):
        """
        构建viewCondition，筛选状态为UNCOMMITTED和BACK的发票
        :return: viewCondition字典
        """
        return {
            "conditionKey": "-od-1gHxYjcHj3qmGvY25",
            "rightValues": {
                "CmewWscZKc-2UJdARiX6I": [
                    {
                        "constValue": "UNCOMMITTED",
                        "fieldType": "Enum",
                        "type": "ConstValue",
                        "valueType": "CONST"
                    },
                    {
                        "constValue": "BACK",
                        "fieldType": "Enum",
                        "type": "ConstValue",
                        "valueType": "CONST"
                    }
                ]
            }
        }
    
    def _build_sb_head_code_condition(self, prefix="AT_"):
        """
        构建发票编码筛选条件（CONTAINS操作符）
        :param prefix: 发票编码前缀，默认为"AT_"
        :return: ConditionLeaf字典
        """
        return {
            "key": "VnvCjun3l91gFFcFhdKu9",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "xMQU9k1VbX3vri6hhGuy_",
                "key": "xMQU9k1VbX3vri6hhGuy_",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "sbHeadCode",
                        "valueName": "sbHeadCode"
                    }
                ]
            },
            "operator": "CONTAINS",
            "rightValue": {
                "key": "X8V0h4O9FGolS5RnIXnPj",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "CONST",
                "constValue": prefix
            }
        }
    
    def _build_sb_status_condition(self):
        """
        构建发票状态筛选条件（IN操作符）
        :return: ConditionLeaf字典
        """
        return {
            "key": "9Nuxwa9wsSNv-YA8BFlBn",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "ZFv_3FZRk9gpcpnQ1HrGX",
                "key": "ZFv_3FZRk9gpcpnQ1HrGX",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "sbStatus",
                        "valueName": "sbStatus"
                    }
                ]
            },
            "operator": "IN",
            "rightValues": [
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DRAFT"
                },
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "CONFIRM"
                },
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DONE"
                },
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DELETE"
                }
            ]
        }
    
    def _build_create_type_condition(self):
        """
        构建创建类型筛选条件（IN操作符）
        :return: ConditionLeaf字典
        """
        return {
            "key": "sOs0UE8dbaURsImYeAv6q",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "_KCID1Hqv10TFBAzUHa_a",
                "key": "_KCID1Hqv10TFBAzUHa_a",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "createType",
                        "valueName": "createType"
                    }
                ]
            },
            "operator": "IN",
            "rightValues": [
                {
                    "key": "BR2znCq-1DvvE9m6kWJoc",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "AUTO"
                },
                {
                    "key": "BR2znCq-1DvvE9m6kWJoc",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "MANUAL"
                },
                {
                    "key": "BR2znCq-1DvvE9m6kWJoc",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "SETT"
                }
            ]
        }
    
    def _build_aes_dsd_push_status_condition(self):
        """
        构建AES推送状态筛选条件（IN操作符）
        :return: ConditionLeaf字典
        """
        return {
            "key": "SBB0xvc06KthgwNwSETLc",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "ugYTT6KGwHGzOxpYYWKCc",
                "key": "ugYTT6KGwHGzOxpYYWKCc",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "aesDsdPushStatus",
                        "valueName": "aesDsdPushStatus"
                    }
                ]
            },
            "operator": "IN",
            "rightValues": [
                {
                    "key": "qsjpsZQNf4mWlLHEblRy6",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DONE"
                },
                {
                    "key": "qsjpsZQNf4mWlLHEblRy6",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "WAITING"
                },
                {
                    "key": "qsjpsZQNf4mWlLHEblRy6",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "FAIL"
                }
            ]
        }
    
    def _build_condition_group(self, conditions):
        """
        构建conditionGroup（保持与原始curl一致的三层嵌套结构）
        :param conditions: 筛选条件列表
        :return: conditionGroup字典，如果conditions为空则返回None
        """
        if not conditions:
            return None
        
        return {
            "type": "ConditionGroup",
            "logicOperator": "AND",
            "conditions": [
                {
                    "type": "ConditionGroup",
                    "logicOperator": "AND",
                    "conditions": [
                        {
                            "type": "ConditionGroup",
                            "logicOperator": "AND",
                            "conditions": conditions
                        }
                    ]
                }
            ]
        }
    
    def _build_pageable_dict(self, view_condition, condition_group, page_no=1, page_size=20):
        """
        构建分页查询参数字典
        :param view_condition: viewCondition字典
        :param condition_group: conditionGroup字典
        :param page_no: 页码，默认为1
        :param page_size: 每页数量，默认为20
        :return: set_dict字典
        """
        pageable = {
            "pageNo": page_no,
            "pageSize": page_size,
            "needTotal": True,
            "sortOrders": None,
            "systemParams": {
                "viewCondition": view_condition
            },
            "conditionGroup": condition_group
        }
        
        return {
            "pageableDTO": {
                "pageable": pageable
            },
            "pageable": pageable
        }
    
    def _validate_sb_query_results(self, response, filter_config=None):
        """
        验证销售发票查询结果是否符合筛选条件
        :param response: API响应
        :param filter_config: 筛选条件配置字典，如果为None则验证所有条件
        """
        data = response.get("data", {}).get("data", {})
        data_list = data.get("data", [])
        total = data.get("total", 0)
        
        # 验证返回的数据不为空（如果有数据的话）
        if total > 0:
            self.assert_util.assert_by_operator(data_list, "not_empty")
            self.assert_util.assert_by_operator(len(data_list), "<=", 20)
            
            # 定义筛选条件的允许值
            allowed_sb_status = ["DRAFT", "CONFIRM", "DONE", "DELETE"]
            allowed_create_type = ["AUTO", "MANUAL", "SETT"]
            allowed_aes_dsd_push_status = ["DONE", "WAITING", "FAIL"]
            sb_head_code_prefix = "AT_"  # 发票编码前缀
            
            # 验证返回的每条数据都符合所有筛选条件
            for record in data_list:
                # 如果提供了filter_config，只验证启用的条件；否则验证所有条件
                should_check_code = filter_config is None or filter_config.get("sb_head_code", False)
                should_check_status = filter_config is None or filter_config.get("sb_status", False)
                should_check_create_type = filter_config is None or filter_config.get("create_type", False)
                should_check_aes = filter_config is None or filter_config.get("aes_dsd_push_status", False)
                
                # 验证发票编码（如果启用了该筛选条件）
                if should_check_code:
                    sb_head_code = record.get("sbHeadCode") or record.get("bilCode")
                    if sb_head_code is not None:
                        self.assert_util.assert_by_operator(
                            sb_head_code_prefix in str(sb_head_code),
                            "=",
                            True,
                            f"发票编码 {sb_head_code} 不符合查询条件（应包含前缀 {sb_head_code_prefix}）"
                        )
                
                # 验证发票状态（如果启用了该筛选条件）
                if should_check_status:
                    sb_status = record.get("sbStatus")
                    self.assert_util.assert_by_operator(
                        sb_status in allowed_sb_status,
                        "=",
                        True,
                        f"发票状态 {sb_status} 不符合查询条件（应为 {allowed_sb_status} 之一）"
                    )
                
                # 验证创建类型（如果启用了该筛选条件）
                if should_check_create_type:
                    create_type = record.get("createType")
                    if create_type is not None:
                        self.assert_util.assert_by_operator(
                            create_type in allowed_create_type,
                            "=",
                            True,
                            f"创建类型 {create_type} 不符合查询条件（应为 {allowed_create_type} 之一）"
                        )
                
                # 验证AES推送状态（如果启用了该筛选条件）
                if should_check_aes:
                    aes_dsd_push_status = record.get("aesDsdPushStatus")
                    if aes_dsd_push_status is not None:
                        self.assert_util.assert_by_operator(
                            aes_dsd_push_status in allowed_aes_dsd_push_status,
                            "=",
                            True,
                            f"AES推送状态 {aes_dsd_push_status} 不符合查询条件（应为 {allowed_aes_dsd_push_status} 之一）"
                        )
    
    @case_decorator(
        story="销售发票查询",
        title="测试销售发票分页查询",
        description="验证销售发票的分页查询功能，包括条件筛选和分页参数",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["销售发票", "查询", "分页"]
    )
    def test_query_sb_doc_page(self):
        """
        测试销售发票分页查询（带多条件筛选）
        测试方面：
        1. 分页参数设置（页码、每页数量、是否需要总数）
        2. 查询条件筛选：
           - viewCondition筛选：状态为UNCOMMITTED或BACK
           - conditionGroup筛选（AND逻辑）：
             * sbHeadCode CONTAINS "AT_" - 发票编码筛选（模糊匹配测试数据）
             * sbStatus IN (DRAFT, CONFIRM, DONE, DELETE) - 发票状态筛选
             * createType IN (AUTO, MANUAL, SETT) - 创建类型筛选
             * aesDsdPushStatus IN (DONE, WAITING, FAIL) - AES推送状态筛选
        3. 排序功能（按创建时间、发票日期等排序）
        4. 返回数据格式验证（列表数据、总数、分页信息等）
        5. 筛选结果验证（验证返回的数据符合所有筛选条件）
        """
        try:
            # 1. 准备测试数据
            # 构建viewCondition和conditionGroup
            view_condition = self._build_view_condition()
            
            # 构建所有筛选条件
            conditions = [
                self._build_sb_head_code_condition(),
                self._build_sb_status_condition(),
                self._build_create_type_condition(),
                self._build_aes_dsd_push_status_condition()
            ]
            condition_group = self._build_condition_group(conditions)
            
            # 构建分页参数字典
            set_dict = self._build_pageable_dict(view_condition, condition_group)
            fields_to_filter = ["pageableDTO", "pageable"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证（验证所有筛选条件）
            self._validate_sb_query_results(response, filter_config=None)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.parametrize(
        "filter_config,title_suffix",
        [
            # 单个筛选条件
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": False,
                    "aes_dsd_push_status": False
                },
                "仅发票编码筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": False
                },
                "仅发票状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "仅创建类型筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": False,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "仅AES推送状态筛选"
            ),
            # 两个筛选条件组合
            (
                {
                    "sb_head_code": True,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": False
                },
                "发票编码+发票状态筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "发票编码+创建类型筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "发票编码+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "发票状态+创建类型筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "发票状态+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": True
                },
                "创建类型+AES推送状态筛选"
            ),
            # 三个筛选条件组合
            (
                {
                    "sb_head_code": True,
                    "sb_status": True,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "发票编码+发票状态+创建类型筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "发票编码+发票状态+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": True
                },
                "发票编码+创建类型+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": True,
                    "aes_dsd_push_status": True
                },
                "发票状态+创建类型+AES推送状态筛选"
            ),
        ]
    )
    @case_decorator(
        story="销售发票查询",
        title="测试销售发票分页查询-筛选条件组合",
        description="验证不同筛选条件组合的查询功能",
        severity="normal",
        file_level_order=5,
        tags=["销售发票", "查询", "分页", "筛选条件组合"]
    )
    def test_query_sb_doc_page_with_filters(self, filter_config, title_suffix):
        """
        测试销售发票分页查询（不同筛选条件组合）
        测试不同筛选条件的组合场景：
        - 单个筛选条件（发票编码、发票状态、创建类型、AES推送状态）
        - 两个筛选条件组合
        - 三个筛选条件组合
        """
        try:
            import allure
            allure.dynamic.title(f"测试销售发票分页查询-{title_suffix}")
            
            # 1. 准备测试数据
            # 构建viewCondition
            view_condition = self._build_view_condition()
            
            # 根据filter_config动态构建conditionGroup
            conditions = []
            if filter_config.get("sb_head_code"):
                conditions.append(self._build_sb_head_code_condition())
            if filter_config.get("sb_status"):
                conditions.append(self._build_sb_status_condition())
            if filter_config.get("create_type"):
                conditions.append(self._build_create_type_condition())
            if filter_config.get("aes_dsd_push_status"):
                conditions.append(self._build_aes_dsd_push_status_condition())
            
            condition_group = self._build_condition_group(conditions)
            
            # 构建分页参数字典
            set_dict = self._build_pageable_dict(view_condition, condition_group)
            fields_to_filter = ["pageableDTO", "pageable"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证（根据filter_config验证启用的筛选条件）
            self._validate_sb_query_results(response, filter_config=filter_config)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
  
        
if __name__ == "__main__":
    test = TestSbDocManagement()
    test.setup_class()
    test.test_query_sb_doc_page()
