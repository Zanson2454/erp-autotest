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

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("存货计价规则明细")
class TestIvRuleDetailManagement(FinBaseTest):
    """存货计价规则明细测试类"""
    
    rule_detail_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.rule_detail_id = None
        cls.logger.info("存货计价规则明细测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_rule_detail_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货计价规则明细",
        title="测试标准导出规则明细",
        description="验证存货计价规则明细标准导出服务功能",
        severity="normal",
        order=1,
        tags=["iv", "rule", "detail", "export", "standard"]
    )
    def test_standard_export_rule_detail(self):
        """测试标准导出规则明细"""
        try:
            api_path = self.get_api_path("规则明细标准导出服务")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "detailIds": [],  # 可为空或指定ID
                "exportType": "EXCEL"
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(export_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, export_data)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "标准导出响应")
            
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
            response = self.http.post(url, json=filtered_params)
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
        order=3,
        tags=["iv", "rule", "detail", "save"]
    )
    def test_save_rule_detail(self):
        """测试保存规则明细"""
        try:
            detail_code = self.mock_util.generate_unique_code(tag="IV_RULE_D")
            detail_name = f"规则明细_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("保存规则明细数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "paramValue"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": detail_code,
                "name": detail_name,
                "paramValue": "test_param",
                "description": "自动化规则明细"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.rule_detail_id = response.get("data", {}).get("data", {}).get("id")
            assert self.rule_detail_id, "保存规则明细失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价规则明细",
        title="测试分页查询规则明细",
        description="验证存货计价规则明细分页查询功能",
        severity="normal",
        order=4,
        tags=["iv", "rule", "detail", "paging"]
    )
    def test_paging_rule_detail(self):
        """测试分页查询规则明细"""
        try:
            if not self.rule_detail_id:
                self.test_save_rule_detail()
            
            api_path = self.get_api_path("规则明细分页数据服务")
            params, url = self.get_api_params(api_path)
            
            pageable = {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": None
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"pageable": pageable})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert any(record.get("id") == self.rule_detail_id for record in records), "未找到保存的明细"
            
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
