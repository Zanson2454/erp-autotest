# -*- coding: utf-8 -*-
"""
存货核算执行记录测试用例
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
@allure.feature("存货核算执行记录")
class TestIvExecuteRecordManagement(IvBaseTest):
    """存货核算执行记录测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.execute_record_id = None
        cls.logger.info("存货核算执行记录测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    @case_decorator(
        story="存货核算执行记录",
        title="测试保存执行记录",
        description="验证存货核算执行记录保存功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "execute", "record", "save"]
    )
    def test_save_execute_record(self):
        """测试保存执行记录"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            record_code = self.mock_util.generate_unique_code(tag="IV_EXEC")
            task_code = f"TASK_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            # 注意：根据 API 参数定义，fin_iv_execute_record_tr 表没有 invOrgId 字段
            # 字段包括：comOrgId, periodId, executeStatus, executeType, taskCode, requestId 等
            set_dict = {
                "comOrgId": {"id": self.com_org_id},
                "taskCode": task_code,
                "executeType": "INIT",
                "executeStatus": "CREATED",
                "matchHeadQty": 0,
                "matchItemQty": 0,
                "executeItemQty": 0
            }
            fields_to_filter = ["comOrgId", "taskCode", "executeType", "executeStatus", "matchHeadQty", "matchItemQty", "executeItemQty"]
            
            response, extracted_id = self.standard_api_call(
                api_key="存货核算执行记录-保存数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="execute_record"  # 自动存储为 self.execute_record_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试分页查询执行记录",
        description="验证存货核算执行记录分页查询功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "execute", "record", "paging"]
    )
    def test_paging_execute_record(self):
        """测试分页查询执行记录"""
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
                api_key="存货核算执行记录-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证数据存在
            total = response.get("data", {}).get("data", {}).get("total")
            self.assert_util.assert_by_operator(total, ">", 0, "总记录数应大于0")
            # self.assert_util.assert_by_operator(records, "not_empty", "分页查询未返回数据")  # 注释：日志输出过长
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试根据ID查找执行记录",
        description="验证根据ID查找存货核算执行记录功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "execute", "record", "find"]
    )
    def test_find_execute_record_by_id(self):
        """测试根据ID查找执行记录"""
        try:
            # 注意：fin_iv_execute_record_tr 表没有 inv_org_id 字段，只有 com_org_id
            sql = "SELECT id FROM fin_iv_execute_record_tr WHERE deleted=0 AND com_org_id=%s ORDER BY created_at DESC LIMIT 1"
            result = self.db.query(sql, [self.com_org_id])
            if result and len(result) > 0:
                self.execute_record_id = result[0].get("id")
            else:
                # 如果没有现有记录，先创建一个
                self.test_save_execute_record()
                # test_save_execute_record 已通过 store_id_as="execute_record" 设置了 self.execute_record_id
            
            # 使用标准化API调用
            set_dict = {"id": self.execute_record_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货核算执行记录-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            record_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(record_data.get("id"), "=", self.execute_record_id, "查找记录ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # @case_decorator(
    #     story="存货核算执行记录",
    #     title="测试更新执行记录",
    #     description="验证更新存货核算执行记录功能",
    #     severity="normal",
    #     file_level_order=4,
    #     tags=["iv", "execute", "record", "update"]
    # )
    # def test_update_execute_record(self):
    #     """测试更新执行记录"""
    #     try:
    #         # 检查并创建依赖数据
    #         if not self.execute_record_id:
    #             self.test_save_execute_record()
            
    #         # 使用标准化API调用（使用保存接口进行更新）
    #         updated_name = f"更新执行记录_{self.mock_util.get_timestamp()}"
    #         set_dict = {
    #             "id": self.execute_record_id,
    #             "comOrgId": self.com_org_id,
    #             "invOrgId": self.inv_org_id,
    #             "name": updated_name,
    #             "status": "EXECUTING"
    #         }
    #         fields_to_filter = ["id", "comOrgId", "invOrgId", "name", "status"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算执行记录-保存数据服务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_data(response)
            
    #         # 验证更新（重新查找验证）
    #         self.test_find_execute_record_by_id()
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算执行记录",
    #     title="测试根据ID删除执行记录",
    #     description="验证根据ID删除存货核算执行记录功能",
    #     severity="normal",
    #     file_level_order=5,
    #     tags=["iv", "execute", "record", "delete"]
    # )
    # def test_delete_execute_record_by_id(self):
    #     """测试根据ID删除执行记录"""
    #     try:
    #         # 检查并创建依赖数据
    #         if not self.execute_record_id:
    #             self.test_save_execute_record()
            
    #         # 使用标准化API调用
    #         set_dict = {"id": self.execute_record_id}
    #         fields_to_filter = ["id"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算执行记录-根据ID删除数据服务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_success(response)
            
    #         # 验证删除（尝试查找应失败或返回空）
    #         find_response, _ = self.standard_api_call(
    #             api_key="存货核算执行记录-根据ID查找数据服务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
    #         record_data = find_response.get("data", {}).get("data", {})
    #         self.assert_util.assert_by_operator(record_data, "=", None, "删除后仍能找到记录")
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算执行记录",
    #     title="测试批量删除执行记录",
    #     description="验证批量删除存货核算执行记录功能",
    #     severity="normal",
    #     file_level_order=6,
    #     tags=["iv", "execute", "record", "batch_delete"]
    # )
    # def test_batch_delete_execute_record(self):
    #     """测试批量删除执行记录"""
    #     try:
    #         # 先创建多个记录用于批量删除
    #         record_ids = []
    #         for _ in range(2):
    #             # 保存记录并收集ID
    #             record_code = self.mock_util.generate_unique_code(tag="IV_EXEC")
    #             record_name = f"执行记录_{self.mock_util.get_timestamp()}"
    #             set_dict = {
    #                 "comOrgId": self.com_org_id,
    #                 "invOrgId": self.inv_org_id,
    #                 "code": record_code,
    #                 "name": record_name,
    #                 "status": "CREATED"
    #             }
    #             fields_to_filter = ["comOrgId", "invOrgId", "code", "name", "status"]
    #             response, extracted_id = self.standard_api_call(
    #                 api_key="存货核算执行记录-保存数据服务",
    #                 set_dict=set_dict,
    #                 fields_to_filter=fields_to_filter,
    #                 store_id_as=None
    #             )
    #             self.assert_util.assert_response_data(response)
    #             if extracted_id:
    #                 record_ids.append(extracted_id)
            
    #         if not record_ids:
    #             raise ValueError("未创建到测试数据，无法进行批量删除测试")
            
    #         # 使用标准化API调用
    #         set_dict = {"ids": record_ids}
    #         fields_to_filter = ["ids"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算执行记录-批量删除数据服务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_success(response)
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
    
    # @case_decorator(
    #     story="存货核算执行记录",
    #     title="测试复制数据转换",
    #     description="验证存货核算执行记录复制数据转换功能",
    #     severity="minor",
    #     file_level_order=7,
    #     tags=["iv", "execute", "record", "copy"]
    # )
    # def test_copy_data_converter(self):
    #     """测试复制数据转换"""
    #     try:
    #         # 检查并创建依赖数据
    #         if not self.execute_record_id:
    #             self.test_save_execute_record()
            
    #         # 使用标准化API调用
    #         set_dict = {
    #             "sourceId": self.execute_record_id,
    #             "targetOrgId": self.com_org_id
    #         }
    #         fields_to_filter = ["sourceId", "targetOrgId"]
            
    #         response, _ = self.standard_api_call(
    #             api_key="存货核算执行记录-复制数据转换服务",
    #             set_dict=set_dict,
    #             fields_to_filter=fields_to_filter,
    #             store_id_as=None
    #         )
            
    #         # 业务断言
    #         self.assert_util.assert_response_data(response)
            
    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
