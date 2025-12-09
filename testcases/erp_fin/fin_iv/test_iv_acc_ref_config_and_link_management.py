# -*- coding: utf-8 -*-
"""
账户参考配置表和物料类型与分类参考关联表测试用例 (合并)
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
@allure.feature("账户参考配置和物料关联配置")
class TestIvAccRefConfigAndLinkManagement(FinBaseTest):
    """账户参考配置表和物料类型与分类参考关联表测试类 (合并)"""
    
    acc_ref_id = None
    mat_link_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.acc_ref_id = None
        cls.mat_link_id = None
        cls.logger.info("账户参考和物料关联配置测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_acc_cate_type_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="fin_iv_mat_acc_cate_link_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    # === 账户参考配置表测试 ===
    
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考分页查询",
        description="验证账户参考配置表分页查询功能",
        severity="normal",
        order=1,
        tags=["iv", "acc", "ref", "paging"]
    )
    def test_acc_ref_paging(self):
        """测试账户参考分页查询"""
        try:
            api_path = self.get_api_path("账户参考配置表-分页数据服务")
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
            
            a.json(response, "账户参考分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试保存账户参考配置",
        description="验证保存账户参考配置表功能",
        severity="critical",
        order=2,
        smoke=True,
        tags=["iv", "acc", "ref", "save"]
    )
    def test_acc_ref_save(self):
        """测试保存账户参考配置"""
        try:
            ref_code = self.mock_util.generate_unique_code(tag="IV_ACC_REF")
            ref_name = f"账户参考_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("账户参考配置表-保存主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "accCateType"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": ref_code,
                "name": ref_name,
                "accCateType": "ASSET",  # 示例：资产
                "description": "自动化账户参考"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.acc_ref_id = response.get("data", {}).get("data", {}).get("id")
            assert self.acc_ref_id, "保存账户参考失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试根据ID查找账户参考",
        description="验证根据ID查找账户参考配置功能",
        severity="normal",
        order=3,
        tags=["iv", "acc", "ref", "find"]
    )
    def test_acc_ref_find_by_id(self):
        """测试根据ID查找账户参考"""
        try:
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            api_path = self.get_api_path("账户参考配置表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.acc_ref_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            ref_data = response.get("data", {}).get("data", {})
            assert ref_data.get("id") == self.acc_ref_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试批量删除账户参考",
        description="验证批量删除账户参考配置功能",
        severity="normal",
        order=4,
        tags=["iv", "acc", "ref", "batch_delete"]
    )
    def test_acc_ref_batch_delete(self):
        """测试批量删除账户参考"""
        try:
            ref_ids = [self.acc_ref_id] if self.acc_ref_id else []
            # 创建额外用于批量
            self.test_acc_ref_save()
            ref_ids.append(self.acc_ref_id)
            
            api_path = self.get_api_path("账户参考配置表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": ref_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "批量删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试复制数据转换",
        description="验证账户参考配置复制数据转换功能",
        severity="normal",
        order=5,
        tags=["iv", "acc", "ref", "copy"]
    )
    def test_acc_ref_copy_converter(self):
        """测试复制数据转换"""
        try:
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            api_path = self.get_api_path("账户参考配置表-复制数据转换服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.acc_ref_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考导出任务",
        description="验证账户参考配置表导入导出任务提交功能",
        severity="minor",
        order=6,
        tags=["iv", "acc", "ref", "export", "task"]
    )
    def test_acc_ref_export_direct_post(self):
        """测试账户参考导出任务（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_ACC_REF_{timestamp}_EXPORT"
            
            export_params = {
                "serviceKey": "账户参考配置表-导入导出任务管理接口-提交导出任务",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_acc_cate_type_cf",
                            "modelName": "账户参考配置表",
                            "sheetNo": 0,
                            "sheetName": "账户参考数据",
                            "headerConfigList": [
                                {"name": "配置编码", "type": "TEXT", "field": "code"},
                                {"name": "账户类别", "type": "TEXT", "field": "accCateType"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_acc_cate_type_cf",
                        "viewKey": "ERP_FIN$fin_iv_acc_cate_type_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_acc_cate_type_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "accCateType"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_acc_cate_type_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_acc_cate_type_cf",
                        "modelName": "账户参考配置表",
                        "containerKey": "ERP_FIN$fin_iv_acc_cate_type_cf",
                        "viewKey": "ERP_FIN$fin_iv_acc_cate_type_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_acc_cate_type_cf"
                    }
                }
            }
            
            api_path = self.get_api_path("账户参考配置表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = export_params
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入需要文件上传，复杂度较高")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考标准导入",
        description="验证账户参考配置表标准导入服务功能",
        severity="minor",
        order=7,
        tags=["iv", "acc", "ref", "import"]
    )
    def test_acc_ref_gei_import(self):
        """测试账户参考标准导入（跳过）"""
        try:
            api_path = self.get_api_path("账户参考配置表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            # 导入参数示例 (实际需文件)
            import_data = {
                "filePath": "test_acc_ref_import.xlsx",  # 假设文件
                "importType": "EXCEL"
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(import_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, import_data)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "标准导入响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试根据ID删除账户参考",
        description="验证根据ID删除账户参考配置功能",
        severity="normal",
        order=8,
        tags=["iv", "acc", "ref", "delete"]
    )
    def test_acc_ref_delete_by_id(self):
        """测试根据ID删除账户参考"""
        try:
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            api_path = self.get_api_path("账户参考配置表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.acc_ref_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # === 物料类型与分类参考关联表测试 ===
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联分页查询",
        description="验证物料类型与分类参考关联表分页查询功能",
        severity="normal",
        order=9,
        tags=["iv", "mat", "link", "paging"]
    )
    def test_mat_link_paging(self):
        """测试物料关联分页查询"""
        try:
            api_path = self.get_api_path("物料类型与分类参考关联表-分页数据服务")
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
            
            a.json(response, "物料关联分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试保存物料关联配置",
        description="验证保存物料类型与分类参考关联表功能",
        severity="critical",
        order=10,
        tags=["iv", "mat", "link", "save"]
    )
    def test_mat_link_save(self):
        """测试保存物料关联配置"""
        try:
            link_code = self.mock_util.generate_unique_code(tag="IV_MAT_LINK")
            link_name = f"物料关联_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("物料类型与分类参考关联表-保存主数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "matTypeId", "accCateId"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": link_code,
                "name": link_name,
                "matTypeId": 1,  # 示例物料类型ID
                "accCateId": self.acc_ref_id if self.acc_ref_id else 1,  # 关联账户参考
                "description": "自动化物料关联"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.mat_link_id = response.get("data", {}).get("data", {}).get("id")
            assert self.mat_link_id, "保存物料关联失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试根据ID查找物料关联",
        description="验证根据ID查找物料类型与分类参考关联功能",
        severity="normal",
        order=11,
        tags=["iv", "mat", "link", "find"]
    )
    def test_mat_link_find_by_id(self):
        """测试根据ID查找物料关联"""
        try:
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            api_path = self.get_api_path("物料类型与分类参考关联表-根据ID查找数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.mat_link_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            link_data = response.get("data", {}).get("data", {})
            assert link_data.get("id") == self.mat_link_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试批量删除物料关联",
        description="验证批量删除物料类型与分类参考关联功能",
        severity="normal",
        order=12,
        tags=["iv", "mat", "link", "batch_delete"]
    )
    def test_mat_link_batch_delete(self):
        """测试批量删除物料关联"""
        try:
            link_ids = [self.mat_link_id] if self.mat_link_id else []
            # 创建额外用于批量
            self.test_mat_link_save()
            link_ids.append(self.mat_link_id)
            
            api_path = self.get_api_path("物料类型与分类参考关联表-批量删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": link_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "批量删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试复制数据转换",
        description="验证物料关联复制数据转换功能",
        severity="normal",
        order=13,
        tags=["iv", "mat", "link", "copy"]
    )
    def test_mat_link_copy_converter(self):
        """测试复制数据转换"""
        try:
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            api_path = self.get_api_path("物料类型与分类参考关联表-复制数据转换服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.mat_link_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联导出任务",
        description="验证物料关联导入导出任务提交功能",
        severity="minor",
        order=14,
        tags=["iv", "mat", "link", "export", "task"]
    )
    def test_mat_link_export_direct_post(self):
        """测试物料关联导出任务（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_MAT_LINK_{timestamp}_EXPORT"
            
            export_params = {
                "serviceKey": "物料类型与分类参考关联表-导入导出任务管理接口-提交导出任务",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf",
                            "modelName": "物料类型与分类参考关联表",
                            "sheetNo": 0,
                            "sheetName": "物料关联数据",
                            "headerConfigList": [
                                {"name": "关联编码", "type": "TEXT", "field": "code"},
                                {"name": "物料类型ID", "type": "NUMBER", "field": "matTypeId"},
                                {"name": "账户类别ID", "type": "NUMBER", "field": "accCateId"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf",
                        "viewKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "matTypeId"},
                                {"field": "accCateId"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_mat_acc_cate_link_cf",
                        "modelName": "物料类型与分类参考关联表",
                        "containerKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf",
                        "viewKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_mat_acc_cate_link_cf"
                    }
                }
            }
            
            api_path = self.get_api_path("物料类型与分类参考关联表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = export_params
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入需要文件上传，复杂度较高")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联标准导入",
        description="验证物料关联标准导入服务功能",
        severity="minor",
        order=15,
        tags=["iv", "mat", "link", "import"]
    )
    def test_mat_link_gei_import(self):
        """测试物料关联标准导入（跳过）"""
        try:
            api_path = self.get_api_path("物料类型与分类参考关联表标准导入服务")
            params, url = self.get_api_params(api_path)
            
            import_data = {
                "filePath": "test_mat_link_import.xlsx",
                "importType": "EXCEL"
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(import_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, import_data)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "标准导入响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试根据ID删除物料关联",
        description="验证根据ID删除物料关联功能",
        severity="normal",
        order=16,
        tags=["iv", "mat", "link", "delete"]
    )
    def test_mat_link_delete_by_id(self):
        """测试根据ID删除物料关联"""
        try:
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            api_path = self.get_api_path("物料类型与分类参考关联表-根据ID删除数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.mat_link_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考标准导出",
        description="验证账户参考配置表标准导出服务功能",
        severity="minor",
        order=17,
        tags=["iv", "acc", "ref", "export", "standard"]
    )
    def test_acc_ref_standard_export(self):
        """测试账户参考标准导出"""
        try:
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            api_path = self.get_api_path("账户参考配置表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "refIds": [self.acc_ref_id],
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
        story="物料类型与分类参考关联表",
        title="测试物料关联标准导出",
        description="验证物料关联标准导出服务功能",
        severity="minor",
        order=18,
        tags=["iv", "mat", "link", "export", "standard"]
    )
    def test_mat_link_standard_export(self):
        """测试物料关联标准导出"""
        try:
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            api_path = self.get_api_path("物料类型与分类参考关联表标准导出服务")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "linkIds": [self.mat_link_id],
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
    
    @pytest.mark.skip(reason="通过OSS提交导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考OSS导入",
        description="验证账户参考配置表通过OSS提交导入任务功能",
        severity="minor",
        order=19,
        tags=["iv", "acc", "ref", "import", "oss"]
    )
    def test_acc_ref_import_oss_post(self):
        """测试账户参考OSS导入（跳过）"""
        pass
    
    @pytest.mark.skip(reason="通过OSS提交导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联OSS导入",
        description="验证物料关联通过OSS提交导入任务功能",
        severity="minor",
        order=20,
        tags=["iv", "mat", "link", "import", "oss"]
    )
    def test_mat_link_import_oss_post(self):
        """测试物料关联OSS导入（跳过）"""
        pass
