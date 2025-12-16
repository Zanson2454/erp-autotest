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
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("账户参考配置和物料关联配置")
class TestIvAccRefConfigAndLinkManagement(FinBaseTest):
    """账户参考配置表和物料类型与分类参考关联表测试类 (合并)"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.acc_ref_id = None
        cls.mat_link_id = None
        cls.logger.info("账户参考和物料关联配置测试类初始化完成")
        # 初始化MD（从md_cache_data获取主数据）
        # md_cache_data 在 FinBaseTest.setup_class() 中通过 CacheUtil.get('md_init_cache') 获取
        # 对于复杂嵌套结构，先获取列表，再判断是否非空，最后获取第一个元素
        if cls.md_cache_data:
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
            mat_type_info = cls.md_cache_data.get("mat_info", {}).get("mat_type_cf", {}).get("FINP", [])
            cls.mat_type_id = mat_type_info[0].get("id") if mat_type_info else None
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 账户参考配置表：使用 acc_cate_code 字段（数据库字段名）
            cls.db.delete(
                table="fin_iv_acc_cate_type_cf",
                where="acc_cate_code like %s",
                params=["AT_%"]
            )
            # 物料关联表：通过关联账户参考的 acc_cate_code 来清理
            cls.db.delete(
                table="fin_iv_mat_acc_cate_link_cf",
                where="acc_cate_id in (select id from fin_iv_acc_cate_type_cf where acc_cate_code like %s)",
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
        file_level_order=4,
        tags=["iv", "acc", "ref", "paging"]
    )
    def test_acc_ref_paging(self):
        """测试账户参考分页查询"""
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
                api_key="账户参考配置表-分页数据服务",
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
        story="账户参考配置表",
        title="测试保存账户参考配置",
        description="验证保存账户参考配置表功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "acc", "ref", "save"]
    )
    def test_acc_ref_save(self):
        """测试保存账户参考配置"""
        try:
            # 准备测试数据
            ref_code = self.mock_util.generate_unique_code(tag="IV_ACC_REF")
            ref_name = f"账户参考_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            # 注意：字段名使用 accCateCode 和 accCateName（不是 code 和 name）
            set_dict = {
                "accCateCode": ref_code,
                "accCateName": ref_name
            }
            fields_to_filter = ["accCateCode", "accCateName"]
            
            response, extracted_id = self.standard_api_call(
                api_key="账户参考配置表-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="acc_ref"  # 自动存储为 self.acc_ref_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试根据ID查找账户参考",
        description="验证根据ID查找账户参考配置功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "acc", "ref", "find"]
    )
    def test_acc_ref_find_by_id(self):
        """测试根据ID查找账户参考"""
        try:
            # 检查并创建依赖数据
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            # 使用标准化API调用
            set_dict = {"id": self.acc_ref_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="账户参考配置表-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            ref_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(ref_data.get("id"), "=", self.acc_ref_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试批量删除账户参考",
        description="验证批量删除账户参考配置功能（后端接口要求批量操作）",
        severity="normal",
        file_level_order=17,
        tags=["iv", "acc", "ref", "batch_delete"]
    )
    def test_acc_ref_batch_delete(self):
        """测试批量删除账户参考（后端接口明确要求批量操作）"""
        try:
            # 创建测试数据用于批量删除
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            # 创建额外的测试数据
            ref_code2 = self.mock_util.generate_unique_code(tag="IV_ACC_REF")
            ref_name2 = f"账户参考_{self.mock_util.get_timestamp()}_批量删除"
            set_dict2 = {
                "accCateCode": ref_code2,
                "accCateName": ref_name2
            }
            fields_to_filter2 = ["accCateCode", "accCateName"]
            response2, extracted_id2 = self.standard_api_call(
                api_key="账户参考配置表-保存主数据服务",
                set_dict=set_dict2,
                fields_to_filter=fields_to_filter2,
                store_id_as=None
            )
            self.assert_util.assert_response_data(response2)
            
            # 批量删除（后端接口明确要求批量操作）
            ref_ids = [self.acc_ref_id, extracted_id2]
            set_dict = {"ids": ref_ids}
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="账户参考配置表-批量删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试复制数据转换",
        description="验证账户参考配置复制数据转换功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "acc", "ref", "copy"]
    )
    def test_acc_ref_copy_converter(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.acc_ref_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="账户参考配置表-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考导出任务",
        description="验证账户参考配置表导入导出任务提交功能",
        severity="minor",
        file_level_order=10,
        tags=["iv", "acc", "ref", "export", "task"]
    )
    def test_acc_ref_export_direct_post(self):
        """测试账户参考导出任务（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_ACC_REF_{self.nickname}_{timestamp}_导出"
            
            # 复杂API参数，使用use_param_util=False
            export_params = {
                "serviceKey": "账户参考配置表-导入导出任务管理接口-提交导出任务",
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
            
            # 使用standard_api_call的use_param_util=False处理复杂参数
            response, _ = self.standard_api_call(
                api_key="账户参考配置表-导入导出任务管理接口-提交导出任务",
                set_dict=export_params,
                use_param_util=False  # 复杂参数，直接使用set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考标准导入",
        description="验证账户参考配置表标准导入服务功能",
        severity="minor",
        file_level_order=13,
        tags=["iv", "acc", "ref", "import"]
    )
    def test_acc_ref_gei_import(self):
        """测试账户参考标准导入（跳过）"""
        try:
            # 导入参数示例 (实际需文件)
            set_dict = {
                "filePath": "test_acc_ref_import.xlsx",  # 假设文件
                "importType": "EXCEL"
            }
            fields_to_filter = ["filePath", "importType"]
            
            response, _ = self.standard_api_call(
                api_key="账户参考配置表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="账户参考配置表",
        title="测试根据ID删除账户参考",
        description="验证根据ID删除账户参考配置功能",
        severity="normal",
        file_level_order=18,
        tags=["iv", "acc", "ref", "delete"]
    )
    def test_acc_ref_delete_by_id(self):
        """测试根据ID删除账户参考"""
        try:
            # 检查并创建依赖数据
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            # 使用标准化API调用
            set_dict = {"id": self.acc_ref_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="账户参考配置表-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # === 物料类型与分类参考关联表测试 ===
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联分页查询",
        description="验证物料类型与分类参考关联表分页查询功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "mat", "link", "paging"]
    )
    def test_mat_link_paging(self):
        """测试物料关联分页查询"""
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
                api_key="物料类型与分类参考关联表-分页数据服务",
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
        story="物料类型与分类参考关联表",
        title="测试保存物料关联配置",
        description="验证保存物料类型与分类参考关联表功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "mat", "link", "save"]
    )
    def test_mat_link_save(self):
        """测试保存物料关联配置"""
        try:
            # 检查并创建依赖数据（账户参考）
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            # 注意：物料关联表可能没有 code 字段，需要通过 acc_cate_id 关联清理
            self.db.execute(
                "DELETE FROM fin_iv_mat_acc_cate_link_cf WHERE mat_type_id = %s and acc_cate_id = %s",
                [self.mat_type_id, self.acc_ref_id]
            )
            # 使用标准化API调用
            # 注意：物料关联表只需要 matTypeId 和 accCateId 字段
            set_dict = {
                "matTypeId":  self.mat_type_id,  # 示例物料类型ID
                "accCateId":  self.acc_ref_id  # 关联账户参考
            }
            fields_to_filter = ["matTypeId", "accCateId"]
            
            response, extracted_id = self.standard_api_call(
                api_key="物料类型与分类参考关联表-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="mat_link"  # 自动存储为 self.mat_link_id
            )
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 重复创建（应该返回错误）
            # standard_api_call 统一返回响应数据，由业务断言来判断是否正确
            response2, extracted_id2 = self.standard_api_call(
                api_key="物料类型与分类参考关联表-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="mat_link"  # 自动存储为 self.mat_link_id
            )
            # 业务断言-接口报错，数据已存在
            err_code = response2.get("err", {}).get("code")
            msg = response2.get("info", {}).get("msg")
            # 业务断言
            self.assert_util.assert_by_operator(err_code, "=", "M1017")
            self.assert_util.assert_by_operator(msg, "=", "物料类型与分类参考关联表数据已存在")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
        

    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试根据ID查找物料关联",
        description="验证根据ID查找物料类型与分类参考关联功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "mat", "link", "find"]
    )
    def test_mat_link_find_by_id(self):
        """测试根据ID查找物料关联"""
        try:
            # 检查并创建依赖数据
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            # 使用标准化API调用
            set_dict = {"id": self.mat_link_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            link_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(link_data.get("id"), "=", self.mat_link_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试批量删除物料关联",
        description="验证批量删除物料类型与分类参考关联功能（后端接口要求批量操作）",
        severity="normal",
        file_level_order=16,
        tags=["iv", "mat", "link", "batch_delete"]
    )
    def test_mat_link_batch_delete(self):
        """测试批量删除物料关联（后端接口明确要求批量操作）"""
        try:
            # 创建测试数据用于批量删除
            if not self.mat_link_id:
                self.test_mat_link_save()       
            # 批量删除（后端接口明确要求批量操作）
            link_ids = [self.mat_link_id]
            set_dict = {"ids": link_ids}
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表-批量删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试复制数据转换",
        description="验证物料关联复制数据转换功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "mat", "link", "copy"]
    )
    def test_mat_link_copy_converter(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.mat_link_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None  
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联导出任务",
        description="验证物料关联导入导出任务提交功能",
        severity="minor",
        file_level_order=10,
        tags=["iv", "mat", "link", "export", "task"]
    )
    def test_mat_link_export_direct_post(self):
        """测试物料关联导出任务（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_MAT_LINK_{self.nickname}_{timestamp}_导出"
            
            # 复杂API参数，使用use_param_util=False
            export_params = {
                "serviceKey": "物料类型与分类参考关联表-导入导出任务管理接口-提交导出任务",
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
            
            # 使用standard_api_call的use_param_util=False处理复杂参数
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表-导入导出任务管理接口-提交导出任务",
                set_dict=export_params,
                use_param_util=False  # 复杂参数，直接使用set_dict
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联标准导入",
        description="验证物料关联标准导入服务功能",
        severity="minor",
        file_level_order=13,
        tags=["iv", "mat", "link", "import"]
    )
    def test_mat_link_gei_import(self):
        """测试物料关联标准导入（跳过）"""
        try:
            # 导入参数示例 (实际需文件)
            set_dict = {
                "filePath": "test_mat_link_import.xlsx",
                "importType": "EXCEL"
            }
            fields_to_filter = ["filePath", "importType"]
            
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试根据ID删除物料关联",
        description="验证根据ID删除物料关联功能",
        severity="normal",
        file_level_order=18,
        tags=["iv", "mat", "link", "delete"]
    )
    def test_mat_link_delete_by_id(self):
        """测试根据ID删除物料关联"""
        try:
            # 检查并创建依赖数据
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            # 使用标准化API调用
            set_dict = {"id": self.mat_link_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导出实际未引用")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考标准导出",
        description="验证账户参考配置表标准导出服务功能",
        severity="minor",
        file_level_order=11,
        tags=["iv", "acc", "ref", "export", "standard"]
    )
    def test_acc_ref_standard_export(self):
        """测试账户参考标准导出"""
        try:
            # 检查并创建依赖数据
            if not self.acc_ref_id:
                self.test_acc_ref_save()
            
            # 使用标准化API调用
            set_dict = {
                "refIds": [self.acc_ref_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["refIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="账户参考配置表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导出实际未引用")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联标准导出",
        description="验证物料关联标准导出服务功能",
        severity="minor",
        file_level_order=11,
        tags=["iv", "mat", "link", "export", "standard"]
    )
    def test_mat_link_standard_export(self):
        """测试物料关联标准导出"""
        try:
            # 检查并创建依赖数据
            if not self.mat_link_id:
                self.test_mat_link_save()
            
            # 使用标准化API调用
            set_dict = {
                "linkIds": [self.mat_link_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["linkIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="物料类型与分类参考关联表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="账户参考配置表",
        title="测试账户参考OSS导入",
        description="验证账户参考配置表通过OSS提交导入任务功能",
        severity="minor",
        file_level_order=15,
        tags=["iv", "acc", "ref", "import", "oss"]
    )
    def test_acc_ref_import_oss_post(self):
        """测试账户参考OSS导入（跳过）"""
        try:
            # OSS导入任务需要OSS配置，复杂度较高，暂时跳过
            pass
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="物料类型与分类参考关联表",
        title="测试物料关联OSS导入",
        description="验证物料关联通过OSS提交导入任务功能",
        severity="minor",
        file_level_order=15,
        tags=["iv", "mat", "link", "import", "oss"]
    )
    def test_mat_link_import_oss_post(self):
        """测试物料关联OSS导入（跳过）"""
        try:
            # OSS导入任务需要OSS配置，复杂度较高，暂时跳过
            pass
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
