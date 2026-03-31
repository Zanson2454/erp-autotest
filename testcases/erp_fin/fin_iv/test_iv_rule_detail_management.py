# -*- coding: utf-8 -*-
"""
存货计价规则明细测试用例
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货计价规则明细")
class TestIvRuleDetailManagement(IvBaseTest):
    """存货计价规则明细测试类"""
    
    rule_detail_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.rule_detail_id = None
        cls.logger.info("存货计价规则明细测试类初始化完成")
        # 注意：com_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="存货计价规则明细",
        title="测试标准导出规则明细",
        description="验证存货计价规则明细标准导出服务功能",
        severity="normal",
        file_level_order=1,
        tags=["iv", "rule", "detail", "export", "standard"]
    )
    def test_standard_export_rule_detail(self):
        """测试标准导出规则明细"""
        try:
            # 使用标准化API调用
            set_dict = {
                "detailIds": [],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["detailIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="规则明细标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货计价规则明细",
        title="测试导入导出任务提交",
        description="验证存货计价规则明细导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        order=2,
        tags=["iv", "rule", "detail", "export", "task"]
    )
    def test_export_task_direct_post_rule_detail(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_RULE_DETAIL_{timestamp}_EXPORT"
            
            export_params = {
                "serviceKey": "FIN_IV_RULE_DETAIL_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_rule_detail_cf",
                            "modelName": "存货计价规则明细",
                            "sheetNo": 0,
                            "sheetName": "规则明细数据",
                            "headerConfigList": [
                                {"name": "明细编码", "type": "TEXT", "field": "code"},
                                {"name": "规则参数", "type": "TEXT", "field": "param"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_rule_detail_cf",
                        "viewKey": "ERP_FIN$fin_iv_rule_detail_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_rule_detail_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "param"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_rule_detail_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_rule_detail_cf",
                        "modelName": "存货计价规则明细",
                        "containerKey": "ERP_FIN$fin_iv_rule_detail_cf",
                        "viewKey": "ERP_FIN$fin_iv_rule_detail_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_rule_detail_cf"
                    }
                }
            }
            
            api_path = self.get_api_path("FIN_IV_RULE_DETAIL_CF_API_GEI_TASK_EXPORT_DIRECT_POST")
            params, url = self.get_api_params(api_path)
            
            filtered_params = export_params
            response, _ = self.standard_api_call(
                api_key="FIN_IV_RULE_DETAIL_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则明细",
        title="测试保存规则明细",
        description="验证保存存货计价规则明细功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "rule", "detail", "save"]
    )
    def test_save_rule_detail(self):
        """测试保存规则明细"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            detail_code = self.mock_util.generate_unique_code(tag="IV_RULE_D")
            detail_name = f"规则明细_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": detail_code,
                "name": detail_name,
                "paramValue": "test_param",
                "description": "自动化规则明细"
            }
            fields_to_filter = ["comOrgId", "code", "name", "paramValue", "description"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存规则明细数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="rule_detail"  # 自动存储为 self.rule_detail_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则明细",
        title="测试分页查询规则明细",
        description="验证存货计价规则明细分页查询功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "rule", "detail", "paging"]
    )
    def test_paging_rule_detail(self):
        """测试分页查询规则明细"""
        try:
            # 检查并创建依赖数据
            if not self.rule_detail_id:
                self.test_save_rule_detail()
            
            # 使用标准化API调用
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="规则明细分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证数据存在
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert any(record.get("id") == self.rule_detail_id for record in records), "未找到保存的明细"
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
