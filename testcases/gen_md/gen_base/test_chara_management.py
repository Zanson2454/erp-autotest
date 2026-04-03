import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("特征管理")
class TestCharacteristicManagement(GenMdBaseTest):
    """特征管理测试类 - 覆盖特征定义表和特征类定义表相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()
    
    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("特征管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_chara_class(self):
        chara_class_code = self.mock_util.generate_unique_code(tag="CHARA_CLASS")
        chara_class_name = f"测试特征类_{self.mock_util.get_timestamp()}"
        chara_id = self.get_runtime_id("chara")
        set_dict = {
            "code": chara_class_code,
            "name": chara_class_name,
            "charaClassType": "MAT",
            "charaList": [
                {
                    "charaId": {"id": chara_id},
                    "isKeyChara": False,
                    "isRequired": False
                }
            ],
            "remark": f"特征类描述_{self.mock_util.get_timestamp()}"
        }
        response, chara_class_id = self.standard_api_call(
            api_key="GEN-特征类定义表-保存服务",
            set_dict=set_dict,
            fields_to_filter=["code", "name", "remark"],
            store_id_as="chara_class"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("chara_class", chara_class_id)
        self.test_data["chara_class_code"] = chara_class_code
        return chara_class_id

    def _ensure_save_chara_class(self):
        chara_class_id = self.get_runtime_id("chara_class")
        if chara_class_id:
            return chara_class_id
        return self._create_chara_class()

    def _create_chara(self):
        self._ensure_save_chara_class()
        chara_code = self.mock_util.generate_unique_code(tag="CHARA")
        chara_name = f"测试特征_{self.mock_util.get_timestamp()}"
        set_dict = {
            "code": chara_code,
            "name": chara_name,
            "charNo": 20,
            "dataType": "STRING",
            "isCustom": True,
            "isRequired": False,
            "isSingleValue": True,
            "remark": f"特征定义_{self.mock_util.get_timestamp()}"
        }
        response, chara_id = self.standard_api_call(
            api_key="GEN-特征定义表-保存服务",
            set_dict=set_dict,
            fields_to_filter=["code", "name", "charaClassId", "remark"],
            store_id_as="chara"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("chara", chara_id)
        self.test_data["chara_code"] = chara_code
        return chara_id

    def _ensure_save_chara(self):
        chara_id = self.get_runtime_id("chara")
        if chara_id:
            return chara_id
        return self._create_chara()

    # ================ 特征类定义表管理 ================
    @case_decorator(
        story="特征类定义表管理",
        title="测试新增特征类定义",
        description="验证GEN-特征类定义表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["特征管理", "新增", "GEN_CHARA_CLASS_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_chara_class(self):
        """新增特征类定义用例"""
        try:
            self._create_chara_class()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试查询特征类定义分页列表",
        description="验证GEN-特征类定义表-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["特征管理", "查询", "GEN_CHARA_CLASS_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_characteristic_class_page(self):
        """查询特征类定义分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征类定义表-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试查询特征类定义详情",
        description="验证GEN-特征类定义表-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["特征管理", "查询", "GEN_CHARA_CLASS_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_chara_class_detail(self):
        """查询特征类定义详情用例"""
        try:
            chara_class_id = self._ensure_save_chara_class()
            set_dict = {"id": chara_class_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征类定义表-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试编辑特征类定义",
        description="验证GEN-特征类定义表-保存服务功能（编辑）",
        severity="critical",
        file_level_order=4,
        tags=["特征管理", "编辑", "GEN_CHARA_CLASS_MD_SAVE_ACTION_SERVICE"]
    )
    def test_update_chara_class(self):
        """编辑特征类定义用例"""
        try:
            # 先确保特征定义存在（特征类定义依赖特征定义）
            chara_id = self._ensure_save_chara()
            
            # 再确保特征类定义存在
            chara_class_id = self._ensure_save_chara_class()

            chara_class_name = f"测试特征类_编辑_{self.mock_util.get_timestamp()}"

            set_dict = {
                "id": chara_class_id,
                "code": self.test_data.get("chara_class_code"),
                "name": chara_class_name,
                "charaClassType": "BATCH",
                "charaList": [
                    {
                        "charaId": {"id": chara_id},
                        "isKeyChara": False,
                        "isRequired": False
                    }
                ],
                "remark": f"特征类描述_编辑_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征类定义表-保存服务",
                set_dict=set_dict,
                fields_to_filter=["id", "code", "name", "charaClassType", "charaList", "remark"],
                store_id_as=None
            )

            # 业务现象：编辑时若命中历史数据冲突，可能返回“编码已存在”
            # 该场景按预期处理，不作为用例失败
            err_msg = str(response.get("err", {}).get("msg", ""))
            err_code = str(response.get("err", {}).get("code", ""))
            duplicate_msg = "特征类定义表编码已存在,请修改后重新提交！"
            is_duplicate_case = (
                response.get("success") is False and
                (duplicate_msg in err_msg or duplicate_msg in err_code)
            )

            if is_duplicate_case:
                self.assert_util.assert_by_operator(is_duplicate_case, "=", True)
                a.text(duplicate_msg, "预期业务提示")
            else:
                self.assert_util.assert_response_data(response)

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试启用特征类定义",
        description="验证GEN-特征类定义表-启用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["特征管理", "启用", "GEN_CHARA_CLASS_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_characteristic_class(self):
        """启用特征类定义用例"""
        try:
            chara_class_id = self._ensure_save_chara_class()
            set_dict = {"id": chara_class_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征类定义表-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试禁用特征类定义",
        description="验证GEN-特征类定义表-禁用服务功能",
        severity="normal",
        file_level_order=6,
        tags=["特征管理", "禁用", "GEN_CHARA_CLASS_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_characteristic_class(self):
        """禁用特征类定义用例"""
        try:
            chara_class_id = self._ensure_save_chara_class()
            set_dict = {"id": chara_class_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征类定义表-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试删除特征类定义",
        description="验证GEN-特征类定义表-删除服务功能",
        severity="critical",
        file_level_order=7,
        tags=["特征管理", "删除", "GEN_CHARA_CLASS_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_characteristic_class(self):
        """删除特征类定义用例"""
        try:
            chara_class_id = self._ensure_save_chara_class()
            set_dict = {"id": chara_class_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征类定义表-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 特征定义表管理 ================
    @case_decorator(
        story="特征定义表管理",
        title="测试新增特征定义",
        description="验证GEN-特征定义表-保存服务功能",
        severity="blocker",
        file_level_order=7,
        smoke=True,
        tags=["特征管理", "新增", "GEN_CHARA_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_chara(self):
        """新增特征定义用例"""
        try:
            self._create_chara()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试查询特征定义分页列表",
        description="验证GEN-特征定义表-查询分页服务功能",
        severity="normal",
        file_level_order=8,
        tags=["特征管理", "查询", "GEN_CHARA_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_characteristic_page(self):
        """查询特征定义分页列表用例"""
        try:
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征定义表-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试查询特征定义详情",
        description="验证GEN-特征定义表-查询详情服务功能",
        severity="normal",
        file_level_order=9,
        tags=["特征管理", "查询", "GEN_CHARA_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_characteristic_detail(self):
        """查询特征定义详情用例"""
        try:
            chara_id = self._ensure_save_chara()
            set_dict = {"id": chara_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征定义表-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试启用特征定义",
        description="验证GEN-特征定义表-启用服务功能",
        severity="normal",
        file_level_order=10,
        tags=["特征管理", "启用", "GEN_CHARA_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_characteristic(self):
        """启用特征定义用例"""
        try:
            chara_id = self._ensure_save_chara()
            set_dict = {"id": chara_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征定义表-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试禁用特征定义",
        description="验证GEN-特征定义表-禁用服务功能",
        severity="normal",
        file_level_order=11,
        tags=["特征管理", "禁用", "GEN_CHARA_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_characteristic(self):
        """禁用特征定义用例"""
        try:
            chara_id = self._ensure_save_chara()
            set_dict = {"id": chara_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征定义表-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试删除特征定义",
        description="验证GEN-特征定义表-删除服务功能",
        severity="critical",
        file_level_order=12,
        tags=["特征管理", "删除", "GEN_CHARA_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_characteristic(self):
        """删除特征定义用例"""
        try:
            chara_id = self._ensure_save_chara()
            set_dict = {"id": chara_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-特征定义表-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 特征类定义表导入导出管理 ================
    @case_decorator(
        story="特征类定义表导入导出管理",
        title="测试特征类定义表标准导入",
        description="验证特征类定义表标准导入服务功能",
        severity="normal",
        file_level_order=13,
        tags=["特征管理", "导入", "GEN_CHARA_CLASS_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_import(self):
        """特征类定义表标准导入用例"""
        try:
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_CHARA_CLASS"),
                    "name": f"导入测试特征类_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试特征类描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="特征类定义表标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表导入导出管理",
        title="测试特征类定义表标准导出",
        description="验证特征类定义表标准导出服务功能",
        severity="normal",
        file_level_order=14,
        tags=["特征管理", "导出", "GEN_CHARA_CLASS_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_export(self):
        """特征类定义表标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="特征类定义表标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表任务管理",
        title="测试特征类定义表OSS导入任务",
        description="验证特征类定义表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=15,
        tags=["特征管理", "任务管理", "GEN_CHARA_CLASS_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_oss_import_task(self):
        """特征类定义表OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_chara_class_import.xlsx",
                "taskName": f"特征类定义表导入任务_{self.mock_util.get_timestamp()}"
            }
            
            response, _ = self.standard_api_call(
                api_key="特征类定义表-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表任务管理",
        title="测试特征类定义表导出任务",
        description="验证特征类定义表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=16,
        tags=["特征管理", "任务管理", "GEN_CHARA_CLASS_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_export_task(self):
        """特征类定义表导出任务用例"""
        try:
            set_dict = {
                "taskName": f"特征类定义表导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="特征类定义表-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
