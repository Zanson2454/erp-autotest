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

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("存货核算执行记录")
class TestIvExecuteRecordManagement(FinBaseTest):
    """存货核算执行记录测试类"""
    
    execute_record_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.execute_record_id = None
        cls.logger.info("存货核算执行记录测试类初始化完成")
        # 初始化MD数据
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_execute_record_tr",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试保存执行记录",
        description="验证存货核算执行记录保存功能",
        severity="critical",
        order=1,
        smoke=True,
        tags=["iv", "execute", "record", "save"]
    )
    def test_save_execute_record(self):
        """测试保存执行记录"""
        try:
            # 准备测试数据
            record_code = self.mock_util.generate_unique_code(tag="IV_EXEC")
            record_name = f"执行记录_{self.mock_util.get_timestamp()}"
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_SAVE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "invOrgId", "code", "name"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "invOrgId": self.inv_org_id,
                "code": record_code,
                "name": record_name,
                "status": "CREATED"  # 示例状态
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 保存数据
            self.execute_record_id = response.get("data", {}).get("data", {}).get("id")
            assert self.execute_record_id, "保存执行记录失败，未获取到ID"
            
            a.json(filtered_params, "保存请求数据")
            a.json(response, "保存响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试分页查询执行记录",
        description="验证存货核算执行记录分页查询功能",
        severity="normal",
        order=2,
        tags=["iv", "execute", "record", "paging"]
    )
    def test_paging_execute_record(self):
        """测试分页查询执行记录"""
        try:
            if not self.execute_record_id:
                self.test_save_execute_record()
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_PAGING_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            # 分页参数
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
            
            # 验证数据存在
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert records, "分页查询未返回数据"
            assert any(record.get("id") == self.execute_record_id for record in records), "未找到保存的记录"
            
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试根据ID查找执行记录",
        description="验证根据ID查找存货核算执行记录功能",
        severity="normal",
        order=3,
        tags=["iv", "execute", "record", "find"]
    )
    def test_find_execute_record_by_id(self):
        """测试根据ID查找执行记录"""
        try:
            if not self.execute_record_id:
                self.test_save_execute_record()
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_FIND_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.execute_record_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            record_data = response.get("data", {}).get("data", {})
            assert record_data.get("id") == self.execute_record_id, "查找记录ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试更新执行记录",
        description="验证更新存货核算执行记录功能",
        severity="normal",
        order=4,
        tags=["iv", "execute", "record", "update"]
    )
    def test_update_execute_record(self):
        """测试更新执行记录"""
        try:
            if not self.execute_record_id:
                self.test_save_execute_record()
            
            # 调用保存API进行更新（假设使用同一保存接口）
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_SAVE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            updated_name = f"更新执行记录_{self.mock_util.get_timestamp()}"
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "name", "status"], ["params", "request"]
            )
            set_dict = {
                "id": self.execute_record_id,
                "name": updated_name,
                "status": "EXECUTING"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 验证更新
            self.test_find_execute_record_by_id()  # 重新查找验证
            
            a.json(response, "更新响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试根据ID删除执行记录",
        description="验证根据ID删除存货核算执行记录功能",
        severity="normal",
        order=5,
        tags=["iv", "execute", "record", "delete"]
    )
    def test_delete_execute_record_by_id(self):
        """测试根据ID删除执行记录"""
        try:
            if not self.execute_record_id:
                self.test_save_execute_record()
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_DELETE_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.execute_record_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 验证删除（尝试查找应失败或返回空）
            delete_api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_FIND_DATA_BY_ID_SERVICE")
            delete_params, delete_url = self.get_api_params(delete_api_path)
            delete_filtered = ParamUtil.filter_post_body_fields(delete_params, ["id"], ["params", "request"])
            ParamUtil.set_request_params(delete_filtered, {"id": self.execute_record_id})
            delete_response = self.http.post(delete_url, json=delete_filtered)
            assert not delete_response.get("data", {}).get("data"), "删除后仍能找到记录"
            
            a.json(response, "删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试批量删除执行记录",
        description="验证批量删除存货核算执行记录功能",
        severity="normal",
        order=6,
        tags=["iv", "execute", "record", "batch_delete"]
    )
    def test_batch_delete_execute_record(self):
        """测试批量删除执行记录"""
        try:
            # 先创建多个记录用于批量删除
            record_ids = []
            for _ in range(2):
                self.test_save_execute_record()  # 这会覆盖ID，需要调整为收集多个ID
                # 注意：实际实现中需收集多个ID，这里简化
                record_ids.append(self.execute_record_id)
            
            # 调用API
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_BATCH_DELETE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": record_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "批量删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货核算执行记录",
        title="测试复制数据转换",
        description="验证存货核算执行记录复制数据转换功能",
        severity="minor",
        order=7,
        tags=["iv", "execute", "record", "copy"]
    )
    def test_copy_data_converter(self):
        """测试复制数据转换"""
        try:
            if not self.execute_record_id:
                self.test_save_execute_record()
            
            api_path = self.get_api_path("FIN_IV_EXECUTE_RECORD_TR_COPY_DATA_CONVERTER_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId", "targetOrgId"], ["params", "request"]
            )
            set_dict = {
                "sourceId": self.execute_record_id,
                "targetOrgId": self.com_org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
