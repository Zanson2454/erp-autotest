# -*- coding: utf-8 -*-
"""
存货价值明细账测试用例
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
@allure.feature("存货价值明细账")
class TestIvDetailAccountManagement(FinBaseTest):
    """存货价值明细账测试类"""
    
    detail_account_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.detail_account_id = None
        cls.logger.info("存货价值明细账测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_acc_detail_tr",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货价值明细账",
        title="测试分页查询明细账",
        description="验证存货价值明细账分页查询功能",
        severity="normal",
        order=1,
        tags=["iv", "detail", "account", "paging"]
    )
    def test_paging_detail_account(self):
        """测试分页查询明细账"""
        try:
            api_path = self.get_api_path("存货价值明细账-分页数据服务")
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
        story="存货价值明细账",
        title="测试保存明细账",
        description="验证保存存货价值明细账功能",
        severity="critical",
        order=2,
        smoke=True,
        tags=["iv", "detail", "account", "save"]
    )
    def test_save_detail_account(self):
        """测试保存明细账"""
        try:
            detail_code = self.mock_util.generate_unique_code(tag="IV_DETAIL")
            detail_name = f"明细账_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("存货价值明细账-保存数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "amount", "date"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": detail_code,
                "name": detail_name,
                "amount": 500.0,
                "date": "2025-01-01",
                "description": "自动化测试明细"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.detail_account_id = response.get("data", {}).get("data", {}).get("id")
            assert self.detail_account_id, "保存明细账失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值明细账",
        title="测试根据ID查找明细账",
        description="验证根据ID查找存货价值明细账功能",
        severity="normal",
        order=3,
        tags=["iv", "detail", "account", "find"]
    )
    def test_find_detail_account_by_id(self):
        """测试根据ID查找明细账"""
        try:
            if not self.detail_account_id:
                self.test_save_detail_account()
            
            api_path = self.get_api_path("存货价值明细账-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.detail_account_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            detail_data = response.get("data", {}).get("data", {})
            assert detail_data.get("id") == self.detail_account_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值明细账",
        title="测试复制数据转换",
        description="验证存货价值明细账复制数据转换功能",
        severity="normal",
        order=4,
        tags=["iv", "detail", "account", "copy"]
    )
    def test_copy_data_converter_detail(self):
        """测试复制数据转换"""
        try:
            if not self.detail_account_id:
                self.test_save_detail_account()
            
            api_path = self.get_api_path("存货价值明细账-复制数据转换服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.detail_account_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货价值明细账",
        title="测试导入导出任务提交",
        description="验证存货价值明细账导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        order=5,
        tags=["iv", "detail", "account", "export", "task"]
    )
    def test_export_direct_post_detail(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_DETAIL_ACCOUNT_{timestamp}_EXPORT"
            
            export_params = {
                "serviceKey": "FIN_IV_ACC_DETAIL_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_acc_detail_tr",
                            "modelName": "存货价值明细账",
                            "sheetNo": 0,
                            "sheetName": "明细账数据",
                            "headerConfigList": [
                                {"name": "明细编码", "type": "TEXT", "field": "code"},
                                {"name": "金额", "type": "NUMBER", "field": "amount"},
                                {"name": "日期", "type": "DATE", "field": "date"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_acc_detail_tr",
                        "viewKey": "ERP_FIN$fin_iv_acc_detail_tr:list",
                        "sceneKey": "ERP_FIN$fin_iv_acc_detail_tr",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "amount"},
                                {"field": "date"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_acc_detail_tr"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_acc_detail_tr",
                        "modelName": "存货价值明细账",
                        "containerKey": "ERP_FIN$fin_iv_acc_detail_tr",
                        "viewKey": "ERP_FIN$fin_iv_acc_detail_tr:list",
                        "sceneKey": "ERP_FIN$fin_iv_acc_detail_tr"
                    }
                }
            }
            
            api_path = self.get_api_path("存货价值明细账-导入导出任务管理接口-提交导出任务")
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
        story="存货价值明细账",
        title="测试标准导出服务",
        description="验证存货价值明细账标准导出服务功能",
        severity="minor",
        order=6,
        tags=["iv", "detail", "account", "export", "standard"]
    )
    def test_standard_export_detail(self):
        """测试标准导出服务"""
        try:
            if not self.detail_account_id:
                self.test_save_detail_account()
            
            api_path = self.get_api_path("存货价值明细账标准导出服务")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "detailIds": [self.detail_account_id],
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
