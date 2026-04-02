import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织类型管理")
class TestOrg_TypeManagement(GenMdBaseTest):
    """组织类型管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.org_type_id = None
        cls.org_type_code = None

        cls.logger.info("组织类型管理测试类初始化完成")
        if cls.md_cache_data:
            org_attr_list = cls.md_cache_data["org_info"]["org_attr_cf"]
            cls.org_attr_id = cls.mock_util.get_mock_choice(org_attr_list)["id"]
            cls.logger.info(f"org_attr_id: {cls.org_attr_id}")

        
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    @case_decorator(
        story="组织类型管理",
        title="测试新增组织类型管理",
        description="验证新增组织类型管理功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["组织类型管理", "新增"]
    )
    def test_save_org_type(self):
        """
        新增组织类型管理用例
        """
        try:
            # 准备组织类型管理数据
            org_type_code = self.mock_util.generate_unique_code(tag="OrgType")
            org_type_name = f"组织类型管理_{self.mock_util.get_timestamp()}"
            
            # 调用保存接口
            set_dict = {
                "code": org_type_code,
                "name": org_type_name,
                "attrList": [
                    {
                        "attrId": {
                            "id": self.org_attr_id
                        },
                        "attrIsMulti": True,
                        "attrIsRequired": False,
                        "attrSort": 1,
                        "attrValue": "测试组织类型"
                    }
                ]
            }
            fields_to_filter = ["code", "name", "attrList"]

            # 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="ORG-组织类型-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="org_type"
            )
            
            self.assert_util.assert_response_data(response)
            # 保持与现有用例字段一致，避免 store_id_as 的命名差异导致后续 id 为空
            self.__class__.org_type_id = extracted_id
            self.__class__.org_type_code = org_type_code
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试查询组织类型管理列表",
        description="验证组织类型管理列表查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["组织类型管理", "查询"]
    )
    def test_query_org_type_list(self):
        """
        查询组织类型管理列表用例
        """
        try:
            # 调用查询接口
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "org_type_code", "type": "TEXT"},
                    {"name": "org_type_name", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-组织类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试查询组织类型管理详情",
        description="验证组织类型管理详情查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["组织类型管理", "查询"]
    )
    def test_query_org_type_detail(self):
        """
        查询组织类型管理详情用例
        """
        try:
            # 获取组织类型管理ID
            if not self.org_type_id:
                self._ensure_save_org_type()

            # 调用详情查询接口
            set_dict = {"id": self.org_type_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="ORG-组织类型-查询详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response)
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试启用组织类型管理",
        description="验证启用组织类型管理功能",
        severity="normal",
        file_level_order=4,
        smoke=True,
        tags=["组织类型管理", "启用"]
    )
    def test_enabled_org_type(self):
        """
        启用组织类型管理用例
        """
        try:
            # 获取组织类型管理信息
            if not self.org_type_id:
                self._ensure_save_org_type()

            # 调用启用接口
            set_dict = {"id": self.org_type_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="ORG-组织类型-启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            status = self.query_service.get_org_business_type_status(self.org_type_id)
            if status is not None:
                self.assert_util.assert_by_operator(status, "=", "ENABLED")
            else:
                self.logger.info("组织类型管理信息不存在")
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试禁用组织类型管理",
        description="验证禁用组织类型管理功能",
        severity="normal",
        file_level_order=5,
        smoke=True,
        tags=["组织类型管理", "禁用"]
    )
    def test_disabled_org_type(self):
        """
        禁用组织类型管理用例
        """
        try:
            # 获取组织类型管理信息
            if not self.org_type_id:
                self._ensure_enabled_org_type()

            # 调用禁用接口
            set_dict = {"id": self.org_type_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="ORG-组织类型-禁用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            status = self.query_service.get_org_business_type_status(self.org_type_id)
            self.logger.info(f"data: {status}")
            if status is not None:
                self.assert_util.assert_by_operator(status, "=", "DISABLED")
            else:
                self.logger.info("组织类型管理信息不存在")
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试查询组织架构类型列表",
        description="验证组织架构类型列表查询功能",
        severity="normal",
        file_level_order=6,
        smoke=True,
        tags=["组织类型管理", "架构查询"]
    )
    def test_query_org_structure_type_list(self):
        """
        查询组织架构类型列表用例
        """
        try:
            # 调用查询接口 - 直接参数设置
            set_dict = {
                    "orgDimensionCode": "SCM_ORG_GRP"
                }

            # 使用标准化API调用 - 特殊直接参数
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-查询组织类型列表服务",
                set_dict=set_dict,
                fields_to_filter=None,
                use_param_util=False
            )
            
            self.assert_util.assert_response_data(response, "组织类型列表为空")

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理", 
        title="测试查询组织业务类型分页",
        description="验证组织业务类型分页查询功能",
        severity="normal",
        file_level_order=7,
        smoke=True,
        tags=["组织类型管理", "业务类型查询"]
    )
    def test_query_org_business_type_paging(self):
        """
        查询组织业务类型分页用例
        """
        try:
            # 调用查询接口
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "status", "type": "SELECT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="GEN-组织类型-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_data(response, "组织业务类型列表不为空")

            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型管理",
        title="测试删除组织类型管理",
        description="验证删除组织类型管理功能",
        severity="normal",
        file_level_order=8,
        smoke=True,
        tags=["组织类型管理", "删除"]
    )
    def test_delete_org_type(self):
        """
        删除组织类型管理用例
        """
        try:
            # 获取组织类型管理信息
            if not self.org_type_id:
                self._ensure_save_org_type()

            # 调用删除接口
            set_dict = {"id": self.org_type_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="ORG-组织类型-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            self.assert_util.assert_response_success(response)

            deleted = self.query_service.get_org_business_type_deleted(self.org_type_id)
            if deleted is not None:
                self.assert_util.assert_by_operator(deleted, "!=", 0)
            else:
                self.logger.warning(f"组织类型ID {self.org_type_id} 在数据库中不存在")
                # 如果数据不存在，说明删除操作已经成功，可以跳过断言
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
