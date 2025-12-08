# -*- coding: utf-8 -*-
"""
存货价值凭证头测试用例
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
import time


@allure.epic("ERP财务模块")
@allure.feature("存货价值凭证头")
class TestIvVoucherHeadManagement(FinBaseTest):
    """存货价值凭证头测试类"""
    
    voucher_head_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.voucher_head_id = None
        cls.logger.info("存货价值凭证头测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_voucher_head_tr",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试分页查询凭证头",
        description="验证存货价值凭证头分页查询功能",
        severity="normal",
        order=1,
        tags=["iv", "voucher", "head", "paging"]
    )
    def test_paging_voucher_head(self):
        """测试分页查询凭证头"""
        try:
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_PAGING_DATA_SERVICE")
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
        story="存货价值凭证头",
        title="测试根据ID查找凭证头",
        description="验证根据ID查找存货价值凭证头功能",
        severity="normal",
        order=2,
        tags=["iv", "voucher", "head", "find"]
    )
    def test_find_voucher_head_by_id(self):
        """测试根据ID查找凭证头"""
        try:
            # 先保存一个用于查找
            self.test_save_voucher_head()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_FIND_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.voucher_head_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            head_data = response.get("data", {}).get("data", {})
            assert head_data.get("id") == self.voucher_head_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试保存凭证头",
        description="验证保存存货价值凭证头功能",
        severity="critical",
        order=3,
        smoke=True,
        tags=["iv", "voucher", "head", "save"]
    )
    def test_save_voucher_head(self):
        """测试保存凭证头"""
        try:
            head_code = self.mock_util.generate_unique_code(tag="IV_HEAD")
            head_name = f"凭证头_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_SAVE_DATA_SERVICE")  # 假设有保存服务
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": head_code,
                "name": head_name,
                "status": "DRAFT"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.voucher_head_id = response.get("data", {}).get("data", {}).get("id")
            assert self.voucher_head_id, "保存凭证头失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试复制数据转换",
        description="验证存货价值凭证头复制数据转换功能",
        severity="normal",
        order=4,
        tags=["iv", "voucher", "head", "copy"]
    )
    def test_copy_data_converter_head(self):
        """测试复制数据转换"""
        try:
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_COPY_DATA_CONVERTER_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.voucher_head_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试折叠关联关系",
        description="验证存货价值凭证头折叠关联关系功能",
        severity="normal",
        order=5,
        tags=["iv", "voucher", "head", "folding"]
    )
    def test_folding_associated(self):
        """测试折叠关联关系"""
        try:
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_FOLDING_ASSOCIATED_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["headId"], ["params", "request"]
            )
            set_dict = {"headId": self.voucher_head_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "折叠关联响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货价值凭证头",
        title="测试导入导出任务提交",
        description="验证存货价值凭证头导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        order=6,
        tags=["iv", "voucher", "head", "export", "task"]
    )
    def test_export_task_direct_post(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_VOUCHER_HEAD_{timestamp}_EXPORT"
            
            # 复杂导出参数
            export_params = {
                "serviceKey": "FIN_IV_VOUCHER_HEAD_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_voucher_head_tr",
                            "modelName": "存货价值凭证头",
                            "sheetNo": 0,
                            "sheetName": "凭证头数据",
                            "headerConfigList": [
                                {"name": "凭证头编码", "type": "TEXT", "field": "code"},
                                {"name": "凭证头名称", "type": "TEXT", "field": "name"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_voucher_head_tr",
                        "viewKey": "ERP_FIN$fin_iv_voucher_head_tr:list",
                        "sceneKey": "ERP_FIN$fin_iv_voucher_head_tr",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_voucher_head_tr"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_voucher_head_tr",
                        "modelName": "存货价值凭证头",
                        "containerKey": "ERP_FIN$fin_iv_voucher_head_tr",
                        "viewKey": "ERP_FIN$fin_iv_voucher_head_tr:list",
                        "sceneKey": "ERP_FIN$fin_iv_voucher_head_tr"
                    }
                }
            }
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_API_GEI_TASK_EXPORT_DIRECT_POST")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(export_params.keys()), ["params"]
            )
            ParamUtil.set_request_params(filtered_params, export_params)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            task_id = response.get("data", {}).get("taskId")
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            a.text(f"导出任务提交成功，任务ID: {task_id}", "导出结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试标准导出服务",
        description="验证存货价值凭证头标准导出服务功能",
        severity="minor",
        order=7,
        tags=["iv", "voucher", "head", "export", "standard"]
    )
    def test_standard_export(self):
        """测试标准导出服务"""
        try:
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            api_path = self.get_api_path("FIN_IV_VOUCHER_HEAD_TR_GEI_EXPORT_SERVICE")
            params, url = self.get_api_params(api_path)
            
            # 导出参数（简化）
            export_data = {
                "headIds": [self.voucher_head_id],
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
