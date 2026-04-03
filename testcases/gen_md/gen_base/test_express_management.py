from typing import Any

import allure
import pytest

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("快递公司管理")
class TestExpressManagement(GenMdBaseTest):
    """快递公司管理测试类 - 覆盖所有快递公司相关服务"""
    
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
        cls.logger.info("快递公司管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_express_company(self):
        express_code = self.mock_util.generate_unique_code(tag="EXPRESS")
        express_name = f"测试快递_{self.mock_util.get_timestamp()}"

        set_dict = {
            "expressCode": express_code,
            "expressName": express_name,
            "remark": f"快递描述_{self.mock_util.get_timestamp()}"
        }

        response, express_id = self.standard_api_call(
            api_key="GEN-快递公司-保存服务",
            set_dict=set_dict,
            fields_to_filter=["code", "name", "remark"],
            store_id_as="express"
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("express", express_id)
        self.test_data["express_code"] = express_code
        return express_id

    def _ensure_save_express_company(self):
        express_id = self.get_runtime_id("express")
        if express_id:
            return express_id
        return self._create_express_company()

    @case_decorator(
        story="快递公司管理",
        title="测试新增快递公司",
        description="验证GEN-快递公司-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["快递公司", "新增", "GEN_EXPRESS_COM_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_express_company(self):
        """新增快递公司用例"""
        try:
            self._create_express_company()

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试查询快递公司详情",
        description="验证GEN-快递公司-查询详情服务功能",
        severity="critical",
        file_level_order=2,
        tags=["快递公司", "查询", "GEN_EXPRESS_COM_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_express_detail(self):
        """查询快递公司详情用例"""
        try:
            express_id = self._ensure_save_express_company()
            set_dict = {"id": express_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-快递公司-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试查询快递公司分页",
        description="验证GEN-快递公司-查询分页服务功能",
        severity="critical",
        file_level_order=3,
        tags=["快递公司", "分页查询", "GEN_EXPRESS_COM_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_express_page(self):
        """查询快递公司分页用例"""
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
                api_key="GEN-快递公司-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试启用快递公司",
        description="验证GEN-快递公司-启用服务功能",
        severity="normal",
        file_level_order=4,
        tags=["快递公司", "启用", "GEN_EXPRESS_COM_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_express_company(self):
        """启用快递公司用例"""
        try:
            express_id = self._ensure_save_express_company()
            set_dict = {"id": express_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-快递公司-启用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试禁用快递公司",
        description="验证GEN-快递公司-禁用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["快递公司", "禁用", "GEN_EXPRESS_COM_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_express_company(self):
        """禁用快递公司用例"""
        try:
            express_id = self._ensure_save_express_company()
            set_dict = {"id": express_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-快递公司-禁用服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="快递公司管理",
        title="测试标准导出快递公司",
        description="验证快递公司标准导出服务功能",
        severity="normal",
        file_level_order=7,
        tags=["快递公司", "导出", "GEN_EXPRESS_COM_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导出需要复杂配置，暂时跳过")
    def test_export_express_company(self):
        """标准导出快递公司用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="快递公司标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司任务管理",
        title="测试快递公司导出任务",
        description="验证快递公司-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=8,
        tags=["快递公司", "任务管理", "GEN_EXPRESS_COM_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="任务管理接口配置复杂，暂时跳过")
    def test_express_export_task(self):
        """快递公司导出任务用例"""
        try:
            set_dict = {
                "taskName": f"快递公司导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="快递公司-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @case_decorator(
        story="快递公司管理",
        title="测试删除快递公司",
        description="验证GEN-快递公司-删除服务功能",
        severity="critical",
        file_level_order=10,
        tags=["快递公司", "删除", "GEN_EXPRESS_COM_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_express_company(self):
        """删除快递公司用例"""
        try:
            express_id = self._ensure_save_express_company()
            set_dict = {"id": express_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-快递公司-删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
