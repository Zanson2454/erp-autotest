import allure
import pytest
from pathlib import Path
import sys
from typing import Any

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from . import ErpCondBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP条件模块")
@allure.feature("存取顺序管理")
class TestMatchSeqManagement(ErpCondBaseTest):
    """存取顺序管理测试类 - 覆盖存取顺序相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.match_seq_id = None
        cls.logger.info("存取顺序管理测试类初始化完成")
        
        # 初始化依赖数据，如果需要
        if cls.cond_cache_data:
            # 示例：如果需要模型ID等依赖
            pass

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="match_seq_head_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 存取顺序创建 ================
    @case_decorator(
        story="存取顺序管理",
        title="测试保存主数据",
        description="验证GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_SAVE_DATA_SERVICE功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["存取顺序", "创建", "GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_SAVE_DATA_SERVICE"]
    )
    def test_save_master_data(self):
        """保存主数据用例 - GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_SAVE_DATA_SERVICE"""
        try:
            # 准备测试数据
            code = self.mock_util.generate_unique_code(tag="MSQ")
            name = f"测试存取顺序_{self.mock_util.get_timestamp()}"
            
            set_dict = {
                "code": code,
                "name": name,
                # 示例字段，根据实际业务调整
                "remark": "测试存取顺序备注",
                "enabled": True
            }
            fields_to_filter = ["code", "name", "remark", "enabled"]
            
            # 标准化API调用
            response, extracted_data = self.standard_api_call(
                api_key="存取顺序-保存主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="match_seq"
            )
            
            # 保存ID
            self.match_seq_id = extracted_data
            self.assert_util.assert_by_operator(self.match_seq_id, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 存取顺序查询 ================
    @case_decorator(
        story="存取顺序管理",
        title="测试根据ID查找数据",
        description="验证GEN_MATCH_SEQ_HEAD_CF_FIND_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=2,
        tags=["存取顺序", "详情查询", "GEN_MATCH_SEQ_HEAD_CF_FIND_DATA_BY_ID_SERVICE"]
    )
    def test_find_by_id(self):
        """根据ID查找用例 - GEN_MATCH_SEQ_HEAD_CF_FIND_DATA_BY_ID_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_seq_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试单表ID查询",
        description="验证GEN_MATCH_SEQ_HEAD_CF_FIND_SINGLE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=3,
        tags=["存取顺序", "单表查询", "GEN_MATCH_SEQ_HEAD_CF_FIND_SINGLE_DATA_BY_ID_SERVICE"]
    )
    def test_find_single_by_id(self):
        """单表ID查询用例 - GEN_MATCH_SEQ_HEAD_CF_FIND_SINGLE_DATA_BY_ID_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_seq_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-根据ID查找单表数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试标准分页查询",
        description="验证GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE功能",
        severity="critical",
        file_level_order=4,
        tags=["存取顺序", "分页查询", "GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE"]
    )
    def test_paging_query(self):
        """标准分页查询用例 - GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试特殊场景分页查询",
        description="验证GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE_oyQmuH1功能",
        severity="normal",
        file_level_order=5,
        tags=["存取顺序", "特殊分页", "GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE_oyQmuH1"]
    )
    def test_paging_query_special(self):
        """特殊场景分页查询用例 - GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE_oyQmuH1"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "filters": {
                    "status": "ENABLED"
                }
            }
            fields_to_filter = ["pageable", "filters"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-分页数据服务_oyQmuH1",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试存取顺序分页数据服务_oyQmuH1",
        description="验证GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE_oyQmuH1功能",
        severity="normal",
        file_level_order=6,
        tags=["存取顺序", "特殊分页2", "GEN_MATCH_SEQ_HEAD_CF_PAGING_DATA_SERVICE_oyQmuH1"]
    )
    def test_paging_query_oyQmuH1(self):
        """存取顺序分页数据服务_oyQmuH1用例"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True
                },
                "specialParam": "oyQmuH1"  # 特殊参数标识
            }
            fields_to_filter = ["pageable", "specialParam"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-分页数据服务_oyQmuH1",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            self.logger.info("存取顺序分页数据服务_oyQmuH1查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 存取顺序启用/禁用 ================
    @case_decorator(
        story="存取顺序管理",
        title="测试单个启用",
        description="验证GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_ENABLE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=6,
        tags=["存取顺序", "启用", "GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_ENABLE_DATA_SERVICE"]
    )
    def test_enable_master_data(self):
        """单个启用主数据用例 - GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_ENABLE_DATA_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_seq_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-启用主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 数据库验证（可选）
            # sql = "SELECT enabled FROM match_seq_head_md WHERE id = %s"
            # result = self.db.query(sql, (self.match_seq_id,))
            # self.assert_util.assert_by_operator(result[0]["enabled"], "=", True)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试批量启用",
        description="验证GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=7,
        tags=["存取顺序", "批量启用", "GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE"]
    )
    def test_batch_enable_master_data(self):
        """批量启用主数据用例 - GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_MULTI_ENABLE_DATA_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            # 创建第二个测试数据用于批量启用
            code2 = self.mock_util.generate_unique_code(tag="MSQ")
            name2 = f"批量启用测试_{self.mock_util.get_timestamp()}"
            
            set_dict2 = {
                "code": code2,
                "name": name2,
                "remark": "批量启用测试",
                "enabled": False  # 创建禁用状态
            }
            fields_to_filter2 = ["code", "name", "remark", "enabled"]
            
            response2, second_id = self.standard_api_call(
                api_key="存取顺序-保存主数据服务",
                set_dict=set_dict2,
                fields_to_filter=fields_to_filter2,
                store_id_as=None
            )
            self.assert_util.assert_response_data(response2)
            
            # 批量启用参数
            set_dict = {
                "ids": [self.match_seq_id, second_id]
            }
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-批量启用主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试单个禁用",
        description="验证GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_DISABLE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=8,
        tags=["存取顺序", "禁用", "GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_DISABLE_DATA_SERVICE"]
    )
    def test_disable_master_data(self):
        """单个禁用主数据用例 - GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_DISABLE_DATA_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_seq_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-禁用主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试批量禁用",
        description="验证GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=9,
        tags=["存取顺序", "批量禁用", "GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE"]
    )
    def test_batch_disable_master_data(self):
        """批量禁用主数据用例 - GEN_MATCH_SEQ_HEAD_CF_MASTER_DATA_MULTI_DISABLE_DATA_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            # 创建第二个测试数据用于批量禁用
            code2 = self.mock_util.generate_unique_code(tag="MSQ")
            name2 = f"批量禁用测试_{self.mock_util.get_timestamp()}"
            
            set_dict2 = {
                "code": code2,
                "name": name2,
                "remark": "批量禁用测试",
                "enabled": True  # 创建启用状态
            }
            fields_to_filter2 = ["code", "name", "remark", "enabled"]
            
            response2, second_id = self.standard_api_call(
                api_key="存取顺序-保存主数据服务",
                set_dict=set_dict2,
                fields_to_filter=fields_to_filter2,
                store_id_as=None
            )
            self.assert_util.assert_response_data(response2)
            
            # 批量禁用参数
            set_dict = {
                "ids": [self.match_seq_id, second_id]
            }
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-批量禁用主数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 存取顺序删除 ================
    @case_decorator(
        story="存取顺序管理",
        title="测试批量删除",
        description="验证GEN_MATCH_SEQ_HEAD_CF_BATCH_DELETE_DATA_SERVICE功能",
        severity="critical",
        file_level_order=10,
        tags=["存取顺序", "批量删除", "GEN_MATCH_SEQ_HEAD_CF_BATCH_DELETE_DATA_SERVICE"]
    )
    def test_batch_delete(self):
        """批量删除用例 - GEN_MATCH_SEQ_HEAD_CF_BATCH_DELETE_DATA_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            # 创建第二个测试数据用于批量删除
            code2 = self.mock_util.generate_unique_code(tag="MSQ")
            name2 = f"批量删除测试_{self.mock_util.get_timestamp()}"
            
            set_dict2 = {
                "code": code2,
                "name": name2,
                "remark": "批量删除测试"
            }
            fields_to_filter2 = ["code", "name", "remark"]
            
            response2, second_id = self.standard_api_call(
                api_key="存取顺序-保存主数据服务",
                set_dict=set_dict2,
                fields_to_filter=fields_to_filter2,
                store_id_as=None
            )
            self.assert_util.assert_response_data(response2)
            
            # 批量删除参数
            set_dict = {
                "ids": [self.match_seq_id, second_id]
            }
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-批量删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.match_seq_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试单个删除",
        description="验证GEN_MATCH_SEQ_HEAD_CF_DELETE_DATA_BY_ID_SERVICE功能",
        severity="critical",
        file_level_order=11,
        tags=["存取顺序", "删除", "GEN_MATCH_SEQ_HEAD_CF_DELETE_DATA_BY_ID_SERVICE"]
    )
    def test_delete_by_id(self):
        """单个删除用例 - GEN_MATCH_SEQ_HEAD_CF_DELETE_DATA_BY_ID_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {"id": self.match_seq_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
            # 重置ID
            self.match_seq_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 存取顺序导出/导入 (跳过) ================
    @case_decorator(
        story="存取顺序管理",
        title="测试标准导出",
        description="验证GEN_MATCH_SEQ_HEAD_CF_GEI_EXPORT_SERVICE功能",
        severity="normal",
        file_level_order=12,
        tags=["存取顺序", "导出", "GEN_MATCH_SEQ_HEAD_CF_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export(self):
        """标准导出用例 - GEN_MATCH_SEQ_HEAD_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("存取顺序标准导出服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试导出任务提交",
        description="验证GEN_MATCH_SEQ_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST功能",
        severity="normal",
        file_level_order=13,
        tags=["存取顺序", "导出任务", "GEN_MATCH_SEQ_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="任务管理接口配置复杂，暂时跳过")
    def test_export_task(self):
        """导出任务用例 - GEN_MATCH_SEQ_HEAD_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            # 复杂导出任务参数构造（按规范跳过）
            a.text("任务管理接口配置复杂，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试标准导入",
        description="验证GEN_MATCH_SEQ_HEAD_CF_GEI_IMPORT_SERVICE功能",
        severity="normal",
        file_level_order=14,
        tags=["存取顺序", "导入", "GEN_MATCH_SEQ_HEAD_CF_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import(self):
        """标准导入用例 - GEN_MATCH_SEQ_HEAD_CF_GEI_IMPORT_SERVICE"""
        try:
            # 导入需要文件上传，跳过
            a.text("标准导入需要文件上传，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试OSS导入任务",
        description="验证GEN_MATCH_SEQ_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST功能",
        severity="normal",
        file_level_order=15,
        tags=["存取顺序", "导入任务", "GEN_MATCH_SEQ_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_oss_import_task(self):
        """OSS导入任务用例 - GEN_MATCH_SEQ_HEAD_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            # OSS导入复杂，跳过
            a.text("OSS导入任务需要OSS配置，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 扩展服务 (复制等) ================
    @case_decorator(
        story="存取顺序管理",
        title="测试复制数据转换",
        description="验证GEN_MATCH_SEQ_HEAD_CF_COPY_DATA_CONVERTER_SERVICE功能",
        severity="normal",
        file_level_order=16,
        tags=["存取顺序", "复制", "GEN_MATCH_SEQ_HEAD_CF_COPY_DATA_CONVERTER_SERVICE"]
    )
    @pytest.mark.skip(reason="复制服务依赖特定业务场景，暂时跳过")
    def test_copy_data_converter(self):
        """复制数据转换用例 - GEN_MATCH_SEQ_HEAD_CF_COPY_DATA_CONVERTER_SERVICE"""
        try:
            if not self.match_seq_id:
                self.test_save_master_data()
            
            set_dict = {"sourceId": self.match_seq_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="存取顺序-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="存取顺序管理",
        title="测试复制数据转换子服务",
        description="验证GEN_MATCH_SEQ_HEAD_CF_COPY_DATA_CONVERTER_SERVICE_CHILD功能",
        severity="normal",
        file_level_order=17,
        tags=["存取顺序", "复制子服务", "GEN_MATCH_SEQ_HEAD_CF_COPY_DATA_CONVERTER_SERVICE_CHILD"]
    )
    @pytest.mark.skip(reason="子服务依赖父服务，暂时跳过")
    def test_copy_data_converter_child(self):
        """复制数据转换子服务用例"""
        try:
            a.text("子服务依赖父服务，暂时跳过", "跳过说明")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
