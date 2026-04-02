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

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货价值明细账")
class TestIvDetailAccountManagement(IvBaseTest):
    """存货价值明细账测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.detail_account_id = None
        cls.logger.info("存货价值明细账测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
        # - com_org_id: 从 com_org_info 获取（IvBaseTest 已映射，用于 CONTINUOUS_METHOD）
        # - gr_com_org_id: 从 gr_come_org_info 获取（IvBaseTest 已映射，用于 PERIOD_METHOD）
        # - inv_org_id: 从 inv_org_info 获取（FinBaseTest 已初始化）
        # 如果业务需要 gr_come_org_info，可以使用 self.gr_com_org_id
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="存货价值明细账",
        title="测试分页查询明细账",
        description="验证存货价值明细账分页查询功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "detail", "account", "paging"]
    )
    def test_paging_detail_account(self):
        """测试分页查询明细账"""
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
                api_key="存货价值明细账-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="业务未引用")
    @case_decorator(
        story="存货价值明细账",
        title="测试保存明细账",
        description="验证保存存货价值明细账功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "detail", "account", "save"]
    )
    def test_save_detail_account(self):
        """测试保存明细账"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            detail_code = self.mock_util.generate_unique_code(tag="IV_DETAIL")
            detail_name = f"明细账_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": detail_code,
                "name": detail_name,
                "amount": 500.0,
                "date": "2025-01-01",
                "description": "自动化测试明细"
            }
            fields_to_filter = ["comOrgId", "code", "name", "amount", "date", "description"]
            
            response, extracted_id = self.standard_api_call(
                api_key="存货价值明细账-保存数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="detail_account"  # 自动存储为 self.detail_account_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 保存数据（如果store_id_as未设置）
            if not hasattr(self, 'detail_account_id') or not self.detail_account_id:
                self.detail_account_id = extracted_id
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值明细账",
        title="测试根据ID查找明细账",
        description="验证根据ID查找存货价值明细账功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "detail", "account", "find"]
    )
    def test_find_detail_account_by_id(self):
        """测试根据ID查找明细账"""
        try:
            # 检查并创建依赖数据
        
            sql = "select id  from fin_iv_acc_detail_tr where deleted=0 and com_org_id=%s and inv_org_id=%s order by created_at desc limit 1"
            self.detail_account_id = self.query_service.execute(sql, [self.com_org_id, self.inv_org_id])

            # 使用标准化API调用
            set_dict = {"id": self.detail_account_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值明细账-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            detail_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data.get("id"), "=", self.detail_account_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值明细账",
        title="测试复制数据转换",
        description="验证存货价值明细账复制数据转换功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "detail", "account", "copy"]
    )
    def test_copy_data_converter_detail(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            sql = "select id  from fin_iv_acc_detail_tr where deleted=0 and com_org_id=%s and inv_org_id=%s order by created_at desc limit 1"
            self.detail_account_id = self.query_service.execute(sql, [self.com_org_id, self.inv_org_id])

            
            # 使用标准化API调用
            set_dict = {"sourceId": self.detail_account_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值明细账-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货价值明细账",
        title="测试导入导出任务提交",
        description="验证存货价值明细账导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        file_level_order=11,
        tags=["iv", "detail", "account", "export", "task"]
    )
    def test_export_direct_post_detail(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_DETAIL_ACCOUNT_{timestamp}_EXPORT"
            
            # 复杂API参数，使用use_param_util=False
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
            
            # 使用standard_api_call的use_param_util=False处理复杂参数
            response, _ = self.standard_api_call(
                api_key="存货价值明细账-导入导出任务管理接口-提交导出任务",
                set_dict=export_params,
                use_param_util=False  # 复杂参数，直接使用set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货价值明细账",
        title="测试标准导出服务",
        description="验证存货价值明细账标准导出服务功能",
        severity="minor",
        file_level_order=10,
        tags=["iv", "detail", "account", "export", "standard"]
    )
    @pytest.mark.skip(reason="业务未引用")
    def test_standard_export_detail(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.detail_account_id:
                self._ensure_save_detail_account()
            
            # 使用标准化API调用
            set_dict = {
                "detailIds": [self.detail_account_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["detailIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="存货价值明细账标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
