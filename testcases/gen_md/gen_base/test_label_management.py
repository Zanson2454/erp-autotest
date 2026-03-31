import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("标签管理")
class TestLabelManagement(GenMdBaseTest):
    """标签管理测试类 - 覆盖所有标签表相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 数据存储
        cls.label_id = None
        cls.label_code = None
        cls.logger.info("标签管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()
    # ================ 标签表基础管理 ================
    @case_decorator(
        story="标签表管理",
        title="测试新增标签",
        description="验证GEN-标签表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["标签管理", "新增", "GEN_LABEL_MD_SAVE_ACTION_SERVICE"]
    )
    @pytest.mark.parametrize("usageType", ["MAT", "SO_HEAD","CRM_MEMBER",""])
    def test_save_label(self, usageType):
        """新增标签用例 - GEN_LABEL_MD_SAVE_ACTION_SERVICE"""
        try:
            # 1. 准备测试数据（原有业务逻辑完全保留，包括唯一命名避免主键冲突）
            timestamp = self.mock_util.get_timestamp()
            random_num = self.mock_util.generate_unique_code(tag="LABEL")[-4:]  # 取后4位随机数
            label_name = f"测试标签_{timestamp}_{random_num}"

            # 2. 使用标准化API调用（替换重复逻辑）
            set_dict = {
                "name": label_name,
                "color": "#FF5722",  # 标签颜色
                "usageType": usageType
            }
            fields_to_filter = ["name", "color", "usageType"]
            
            response, label_id = self.standard_api_call(
                api_key="GEN-标签表-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="label"
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
            # 4. 原有数据保存逻辑（完全保留）
            self.label_id = label_id
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表管理",
        title="测试查询标签分页列表",
        description="验证GEN-标签表-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["标签管理", "查询", "GEN_LABEL_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_label_page(self):
        """查询标签分页列表用例 - GEN_LABEL_MD_QUERY_PAGE_ACTION_SERVICE"""
        try:
            # 1. 准备分页参数（原有逻辑完全保留）
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "color", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-标签表-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表管理",
        title="测试查询标签详情",
        description="验证GEN-标签表-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["标签管理", "查询", "GEN_LABEL_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_label_detail(self):
        """查询标签详情用例 - GEN_LABEL_MD_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            # 1. 确保标签存在（原有依赖逻辑完全保留，包含参数化调用）
            if not self.label_id:
                self.test_save_label(usageType="MAT")

            # 2. 使用标准化API调用
            set_dict = {"id": self.label_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-标签表-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表管理",
        title="测试启用标签",
        description="验证GEN-标签表-启用服务功能",
        severity="normal",
        file_level_order=4,
        tags=["标签管理", "启用", "GEN_LABEL_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_label(self):
        """启用标签用例 - GEN_LABEL_MD_ENABLED_ACTION_SERVICE"""
        try:
            # 1. 确保标签存在（原有依赖逻辑完全保留）
            if not self.label_id:
                self.test_save_label(usageType="MAT")

            # 2. 使用标准化API调用
            set_dict = {"id": self.label_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-标签表-启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表管理",
        title="测试禁用标签",
        description="验证GEN-标签表-禁用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["标签管理", "禁用", "GEN_LABEL_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_label(self):
        """禁用标签用例 - GEN_LABEL_MD_DISABLED_ACTION_SERVICE"""
        try:
            # 1. 确保标签存在（原有依赖逻辑完全保留）
            if not self.label_id:
                self.test_save_label(usageType="MAT")

            # 2. 使用标准化API调用
            set_dict = {"id": self.label_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-标签表-禁用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表管理",
        title="测试删除标签",
        description="验证GEN-标签表-删除服务功能",
        severity="critical",
        file_level_order=6,
        tags=["标签管理", "删除", "GEN_LABEL_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_label(self):
        """删除标签用例 - GEN_LABEL_MD_DELETE_ACTION_SERVICE"""
        try:
            # 1. 确保标签存在（原有依赖逻辑完全保留）
            if not self.label_id:
                self.test_save_label(usageType="MAT")

            # 2. 使用标准化API调用
            set_dict = {"id": self.label_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="GEN-标签表-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 标签表导入导出管理 ================
    @case_decorator(
        story="标签表导入导出管理",
        title="测试标签表标准导入",
        description="验证标签表标准导入服务功能",
        severity="normal",
        file_level_order=7,
        tags=["标签管理", "导入", "GEN_LABEL_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_label_import(self):
        """标签表标准导入用例 - GEN_LABEL_MD_GEI_IMPORT_SERVICE"""
        try:
            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_LABEL"),
                    "name": f"导入测试标签_{self.mock_util.get_timestamp()}",
                    "color": "#4CAF50",
                    "description": "导入的标签描述"
                }
            ]

            set_dict = {"data": import_data}
            response, _ = self.standard_api_call(
                api_key="标签表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表导入导出管理",
        title="测试标签表标准导出",
        description="验证标签表标准导出服务功能",
        severity="normal",
        file_level_order=8,
        tags=["标签管理", "导出", "GEN_LABEL_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_label_export(self):
        """标签表标准导出用例 - GEN_LABEL_MD_GEI_EXPORT_SERVICE"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "color", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            response, _ = self.standard_api_call(
                api_key="标签表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表任务管理",
        title="测试标签表OSS导入任务",
        description="验证标签表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=9,
        tags=["标签管理", "任务管理", "GEN_LABEL_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_label_oss_import_task(self):
        """标签表OSS导入任务用例 - GEN_LABEL_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            set_dict = {
                "fileKey": "test_label_import_file.xlsx",
                "taskName": f"标签表导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            response, _ = self.standard_api_call(
                api_key="标签表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="标签表任务管理",
        title="测试标签表导出任务",
        description="验证标签表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=10,
        tags=["标签管理", "任务管理", "GEN_LABEL_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_label_export_task(self):
        """标签表导出任务用例 - GEN_LABEL_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            set_dict = {
                "taskName": f"标签表导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "color", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ]
                }
            }
            response, _ = self.standard_api_call(
                api_key="标签表-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
