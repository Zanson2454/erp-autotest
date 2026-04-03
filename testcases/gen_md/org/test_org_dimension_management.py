import allure

from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织维度管理")
class TestOrg_DimensionManagement(GenMdBaseTest):
    """组织维度管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 准备组织维度管理数据
        # 获取md_cache_data中的第一个数据
        cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
   
        # 初始化组织类型数据
        for org_biz_type in  cls.orgBusinessTypeIds:
            if org_biz_type["code"] == "COM_ORG":
                cls.comOrgTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "PUR_ORG":
                cls.purOrgTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "SLS_ORG":
                cls.slsOrgTypeId  = org_biz_type["id"]
            elif org_biz_type["code"] == "SLS_DC":
                cls.slsDcTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "INV_ORG":
                cls.invOrgTypeId = org_biz_type["id"]
            elif org_biz_type["code"] == "INV_LOC":
                cls.invLocTypeId = org_biz_type["id"]

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    def _create_org_dimension(self):
        org_dimension_code = self.mock_util.generate_unique_code(tag="Org_Dimension")
        org_dimension_name = f"组织维度(自动化)_{self.mock_util.get_timestamp()}"
        set_dict = {
            "orgDimensionCode": org_dimension_code,
            "orgDimensionName": org_dimension_name,
            "orgDimensionDescribe": f"测试组织维度-{self.mock_util.get_timestamp()}",
            "isSupMultiRoot": True,
            "orgBusinessTypeList": [
                {"orgBusinessTypeId": {"id": self.slsOrgTypeId}},
                {"orgBusinessTypeId": {"id": self.purOrgTypeId}},
                {"orgBusinessTypeId": {"id": self.invOrgTypeId}},
                {"orgBusinessTypeId": {"id": self.invLocTypeId}},
            ],
        }
        response, extracted_id = self.standard_api_call(
            api_key="ORG-组织维度-保存服务",
            set_dict=set_dict,
            fields_to_filter=["orgDimensionCode", "orgDimensionName", "orgDimensionDescribe", "isSupMultiRoot", "orgBusinessTypeList"],
            store_id_as="org_dimension",
        )
        self.assert_util.assert_response_data(response)
        self.set_runtime_id("org_dimension", extracted_id)
        self.set_runtime_id("org_dimension_code", org_dimension_code)
        self.set_runtime_id("org_dimension_name", org_dimension_name)
        return extracted_id

    def _ensure_save_org_dimension(self):
        org_dimension_id = self.get_runtime_id("org_dimension")
        if org_dimension_id:
            return org_dimension_id
        return self._create_org_dimension()

    def _ensure_enabled_org_dimension(self):
        org_dimension_id = self._ensure_save_org_dimension()
        response, _ = self.standard_api_call(
            api_key="ORG-组织维度-启用服务",
            set_dict={"id": org_dimension_id},
            fields_to_filter=["id"],
            store_id_as=None,
        )
        self.assert_util.assert_response_success(response)
        return org_dimension_id

    @case_decorator(
        story="组织维度管理",
        title="测试新增组织维度管理",
        description="验证新增组织维度管理功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["组织维度管理", "新增"]
    )
    def test_save_org_dimension(self):
        """
        新增组织维度管理用例
        """
        try:
            org_dimension_id = self._create_org_dimension()
            a.json({"org_dimension_id": org_dimension_id}, "组织维度新增结果")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试查询组织维度管理详情",
        description="验证组织维度管理详情查询功能",
        severity="normal",
        file_level_order=2,
        smoke=True,
        tags=["组织维度管理", "查询详情"]
    )
    def test_query_org_dimension_detail(self):
        """
        查询组织维度管理详情用例
        """
        try:
            org_dimension_id = self._ensure_save_org_dimension()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": org_dimension_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织维度-详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            status = response.get("data", {}).get("data", {}).get("status", None)
            self.assert_util.assert_by_operator(status, "=", "INACTIVE")
            
            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise



    @case_decorator(
        story="组织维度管理",
        title="测试查询组织维度管理列表",
        description="验证组织维度管理列表查询功能",
        severity="normal",
        file_level_order=3,
        smoke=True,
        tags=["组织维度管理", "查询"]
    )
    def test_query_org_dimension_list(self):
        """
        查询组织维度管理列表用例
        """
        try:
            self._ensure_save_org_dimension()
            org_dimension_code = self.get_runtime_id("org_dimension_code")
                
            # 准备测试数据（业务逻辑保持不变）
            set_dict =  {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "orgDimensionCode": {
                                "operator": "CONTAINS",
                                "value": org_dimension_code
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {
                        "name": "orgDimensionCode",
                        "type": "TEXT"
                    },
                    {
                        "name": "orgDimensionName",
                        "type": "TEXT"
                    }
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织维度-查询分页服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            total = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total, "=", 1)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
    @case_decorator(
        story="组织维度管理",
        title="测试启用组织维度管理",
        description="验证启用组织维度管理功能",
        severity="normal",
        file_level_order=4,
        smoke=True,
        tags=["组织维度管理", "启用"]
    )
    def test_enabled_org_dimension(self):
        """
        启用组织维度管理用例
        """
        try:
            org_dimension_id = self._ensure_save_org_dimension()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": org_dimension_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织维度-启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            
            status = self.query_service.get_org_dimension_status(org_dimension_id)
            self.assert_util.assert_by_operator(status, "=", "ENABLED")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试禁用组织维度管理",
        description="验证禁用组织维度管理功能",
        severity="normal",
        file_level_order=5,
        smoke=True,
        tags=["组织维度管理", "禁用"]
    )
    def test_disabled_org_dimension(self):
        """
        禁用组织维度管理用例
        """
        try:
            org_dimension_id = self._ensure_enabled_org_dimension()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": org_dimension_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织维度-禁用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            status = self.query_service.get_org_dimension_status(org_dimension_id)
            self.assert_util.assert_by_operator(status, "=", "DISABLED")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试查询启用的组织维度列表",
        description="验证查询启用的组织维度列表功能",
        severity="normal",
        file_level_order=6,
        smoke=True,
        tags=["组织维度管理", "查询启用列表"]
    )
    def test_query_enabled_org_dimension_list(self):
        """
        查询启用的组织维度列表用例
        """
        try:
            self._ensure_enabled_org_dimension()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {}
            fields_to_filter = []

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织维度-查询启用的组织维度列表服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 验证返回的数据列表
            data_list = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织维度管理",
        title="测试删除组织维度管理",
        description="验证删除组织维度管理功能",
        severity="normal",
        file_level_order=7,
        smoke=True,
        tags=["组织维度管理", "删除"]
    )
    def test_delete_org_dimension(self):
        """
        删除组织维度管理用例
        """
        try:
            org_dimension_id = self._ensure_save_org_dimension()

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {"id": org_dimension_id}
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织维度-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            deleted = self.query_service.get_org_dimension_deleted(org_dimension_id)
            self.assert_util.assert_by_operator(deleted, "!=", 0)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
