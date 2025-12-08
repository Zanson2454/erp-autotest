# -*- coding: utf-8 -*-
"""
存货价值期间账测试用例
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
from utils.mock_util import MockData  # 如果需要额外mock


@allure.epic("ERP财务模块")
@allure.feature("存货价值期间账")
class TestIvPeriodAccountManagement(FinBaseTest):
    """存货价值期间账测试类"""
    
    period_account_id = None
    mock_data = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.period_account_id = None
        cls.mock_data = MockData()
        cls.logger.info("存货价值期间账测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_acc_period_tr",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货价值期间账",
        title="测试分页查询期间账",
        description="验证存货价值期间账分页查询功能",
        severity="normal",
        order=1,
        tags=["iv", "period", "account", "paging"]
    )
    def test_paging_period_account(self):
        """测试分页查询期间账"""
        try:
            api_path = self.get_api_path("FIN_IV_ACC_PERIOD_TR_PAGING_DATA_SERVICE")
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
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值期间账",
        title="测试保存期间账",
        description="验证保存存货价值期间账功能",
        severity="critical",
        order=2,
        smoke=True,
        tags=["iv", "period", "account", "save"]
    )
    def test_save_period_account(self):
        """测试保存期间账"""
        try:
            period_code = self.mock_util.generate_unique_code(tag="IV_PERIOD")
            period_name = f"期间账_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("FIN_IV_ACC_PERIOD_TR_SAVE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "periodStart", "periodEnd"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": period_code,
                "name": period_name,
                "periodStart": "2025-01-01",
                "periodEnd": "2025-12-31",
                "balance": 0.0
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.period_account_id = response.get("data", {}).get("data", {}).get("id")
            assert self.period_account_id, "保存期间账失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值期间账",
        title="测试根据ID查找期间账",
        description="验证根据ID查找存货价值期间账功能",
        severity="normal",
        order=3,
        tags=["iv", "period", "account", "find"]
    )
    def test_find_period_account_by_id(self):
        """测试根据ID查找期间账"""
        try:
            if not self.period_account_id:
                self.test_save_period_account()
            
            api_path = self.get_api_path("FIN_IV_ACC_PERIOD_TR_FIND_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.period_account_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            account_data = response.get("data", {}).get("data", {})
            assert account_data.get("id") == self.period_account_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值期间账",
        title="测试复制数据转换",
        description="验证存货价值期间账复制数据转换功能",
        severity="normal",
        order=4,
        tags=["iv", "period", "account", "copy"]
    )
    def test_copy_data_converter_period(self):
        """测试复制数据转换"""
        try:
            if not self.period_account_id:
                self.test_save_period_account()
            
            api_path = self.get_api_path("FIN_IV_ACC_PERIOD_TR_COPY_DATA_CONVERTER_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.period_account_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货价值期间账",
        title="测试导入导出任务提交",
        description="验证存货价值期间账导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        order=5,
        tags=["iv", "period", "account", "export", "task"]
    )
    def test_export_direct_post_period(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_PERIOD_ACCOUNT_{timestamp}_EXPORT"
            
            # 复杂导出参数模板
            export_params = {
                "serviceKey": "FIN_IV_ACC_PERIOD_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_acc_period_tr",
                            "modelName": "存货价值期间账",
                            "sheetNo": 0,
                            "sheetName": "期间账数据",
                            "headerConfigList": [
                                {"name": "期间编码", "type": "TEXT", "field": "code"},
                                {"name": "期间名称", "type": "TEXT", "field": "name"},
                                {"name": "开始日期", "type": "DATE", "field": "periodStart"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_acc_period_tr",
                        "viewKey": "ERP_FIN$fin_iv_acc_period_tr:list",
                        "sceneKey": "ERP_FIN$fin_iv_acc_period_tr",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"},
                                {"field": "periodStart"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_acc_period_tr"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_acc_period_tr",
                        "modelName": "存货价值期间账",
                        "containerKey": "ERP_FIN$fin_iv_acc_period_tr",
                        "viewKey": "ERP_FIN$fin_iv_acc_period_tr:list",
                        "sceneKey": "ERP_FIN$fin_iv_acc_period_tr"
                    }
                }
            }
            
            api_path = self.get_api_path("FIN_IV_ACC_PERIOD_TR_API_GEI_TASK_EXPORT_DIRECT_POST")
            params, url = self.get_api_params(api_path)
            
            filtered_params = export_params  # 直接使用复杂结构
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            task_id = response.get("data", {}).get("taskId")
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值期间账",
        title="测试标准导出服务",
        description="验证存货价值期间账标准导出服务功能",
        severity="minor",
        order=6,
        tags=["iv", "period", "account", "export", "standard"]
    )
    def test_standard_export_period(self):
        """测试标准导出服务"""
        try:
            if not self.period_account_id:
                self.test_save_period_account()
            
            api_path = self.get_api_path("FIN_IV_ACC_PERIOD_TR_GEI_EXPORT_SERVICE")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "accountIds": [self.period_account_id],
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
    
    @case_decorator(
        story="存货价值期间账",
        title="测试期间账分页查询",
        description="验证期间账分页查询服务",
        severity="normal",
        order=7,
        tags=["iv", "period", "account", "page"]
    )
    def test_page_service_period(self):
        """测试期间账分页查询"""
        try:
            api_path = self.get_api_path("IV_ACC_PERIOD_TR_PAGE_SERVICE")
            params, url = self.get_api_params(api_path)
            
            page_request = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, page_request)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "期间账分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
