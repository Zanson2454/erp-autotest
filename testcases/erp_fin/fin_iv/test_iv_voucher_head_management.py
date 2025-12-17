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
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货价值凭证头")
class TestIvVoucherHeadManagement(FinBaseTest):
    """存货价值凭证头测试类"""
    
    voucher_head_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.voucher_head_id = None
        cls.logger.info("存货价值凭证头测试类初始化完成")
        # 初始化MD数据（从md_cache_data获取主数据）
        if cls.md_cache_data:
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
            inv_org_info = cls.md_cache_data.get("org_info", {}).get("inv_org_info", [])
            cls.inv_org_id = inv_org_info[0].get("id") if inv_org_info else None
    
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
        file_level_order=1,
        tags=["iv", "voucher", "head", "paging"]
    )
    def test_paging_voucher_head(self):
        """测试分页查询凭证头"""
        try:
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
                api_key="凭证头分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试根据ID查找凭证头",
        description="验证根据ID查找存货价值凭证头功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "voucher", "head", "find"]
    )
    def test_find_voucher_head_by_id(self):
        """测试根据ID查找凭证头"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            # 使用标准化API调用
            set_dict = {"id": self.voucher_head_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="根据ID查找凭证头数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            head_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(head_data.get("id"), "=", self.voucher_head_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试保存凭证头",
        description="验证保存存货价值凭证头功能",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["iv", "voucher", "head", "save"]
    )
    def test_save_voucher_head(self):
        """测试保存凭证头"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            head_code = self.mock_util.generate_unique_code(tag="IV_HEAD")
            head_name = f"凭证头_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": head_code,
                "name": head_name,
                "status": "DRAFT"
            }
            fields_to_filter = ["comOrgId", "code", "name", "status"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存凭证头数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="voucher_head"  # 自动存储为 self.voucher_head_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试复制数据转换",
        description="验证存货价值凭证头复制数据转换功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "voucher", "head", "copy"]
    )
    def test_copy_data_converter_head(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.voucher_head_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="凭证头复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试折叠关联关系",
        description="验证存货价值凭证头折叠关联关系功能",
        severity="normal",
        file_level_order=5,
        tags=["iv", "voucher", "head", "folding"]
    )
    def test_folding_associated(self):
        """测试折叠关联关系"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            # 使用标准化API调用
            set_dict = {"headId": self.voucher_head_id}
            fields_to_filter = ["headId"]
            
            response, _ = self.standard_api_call(
                api_key="凭证头折叠关联服务",
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
        story="存货价值凭证头",
        title="测试导入导出任务提交",
        description="验证存货价值凭证头导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        file_level_order=6,
        tags=["iv", "voucher", "head", "export", "task"]
    )
    def test_export_task_direct_post(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_VOUCHER_HEAD_{timestamp}_EXPORT"
            
            # 复杂导出参数（使用use_param_util=False直接传递）
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
            
            # 使用标准化API调用（use_param_util=False用于复杂参数）
            response, _ = self.standard_api_call(
                api_key="FIN_IV_VOUCHER_HEAD_TR_API_GEI_TASK_EXPORT_DIRECT_POST",
                set_dict=export_params,
                fields_to_filter=None,
                store_id_as=None,
                use_param_util=False
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值凭证头",
        title="测试标准导出服务",
        description="验证存货价值凭证头标准导出服务功能",
        severity="minor",
        file_level_order=7,
        tags=["iv", "voucher", "head", "export", "standard"]
    )
    def test_standard_export(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.voucher_head_id:
                self.test_save_voucher_head()
            
            # 使用标准化API调用
            set_dict = {
                "headIds": [self.voucher_head_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["headIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="凭证头标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
