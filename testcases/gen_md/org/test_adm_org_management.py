import allure
import requests
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
import pytest


@allure.epic("组织管理")
@allure.feature("行政组织管理")
class TestAdmOrgManagement(GenMdBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.org_info = {}
        # cls.mock_data = MockData()  # Remove, use self.mock_util singleton
        
        # 获取初始化数据中的第一个数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.genWcHeadId = cls.init_data["gen_wc_head_info"][0]["gen_wc_head_id"] if cls.init_data.get("gen_wc_head_info") else None
        # calenderId 由 GenMdBaseTest.bind_context 从 fin_cache_data（fin_init_sql）解析
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
        
        # 获取md_cache_data中的第一个数据
        if cls.md_cache_data:
            cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
            cls.logger.info(f"orgBusinessTypeIds: {cls.orgBusinessTypeIds}")
            if cls.orgBusinessTypeIds:
                for org_biz_type in cls.orgBusinessTypeIds:
                    if org_biz_type["code"] == "ADM_ORG":  # 行政组织类型
                        cls.admOrgTypeId = org_biz_type["id"]
            else:
                cls.admOrgTypeId = None
                cls.logger.info("orgBusinessTypeIds为空")
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理（已迁移到 cleanup_registry）。"""
        cls.logger.info("测试数据清理已迁移至 session 末尾统一执行")
        super().teardown_class()

    @case_decorator(
        story="保存行政组织",
        title="测试保存行政组织",
        description="验证保存行政组织接口的功能性",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["行政组织", "保存组织"]
    )
    def test_save_adm_org(self):
        """
        保存行政组织用例
        """
        try:
            org_code = self.mock_util.generate_unique_code(tag="AdmOrg")
            org_name = self.mock_util.get_mock_company()
            org_enable_date = self.mock_util.get_mock_date(include_time=False, days_offset=1)

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 9999,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.admOrgTypeId],
                "orgDimensionCode": "ADM_ORG_GRP"
            }
            fields_to_filter = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode"]

            # 使用标准化API调用（无任何断言）
            response, extracted_id = self.standard_api_call(
                api_key="ORG-组织架构-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.org_info.update({
                "adm_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="启用行政组织",
        title="测试启用行政组织",
        description="验证启用行政组织接口的功能性",
        severity="blocker",
        file_level_order=2,
        smoke=True,
        tags=["行政组织", "启用组织"]
    )
    def test_enable_adm_org(self):
        """
        启用行政组织用例
        """
        try:
            # 获取行政组织信息
            adm_org_info = TestAdmOrgManagement.org_info.get("adm_org_info", {})
            org_id = adm_org_info.get("id")
            if not org_id:
                self.test_save_adm_org()
                org_id = TestAdmOrgManagement.org_info.get("adm_org_info", {}).get("id")

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "id": org_id
            }
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-启用组织单元服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="停用行政组织",
        title="测试停用行政组织",
        description="验证停用行政组织接口的功能性",
        severity="blocker",
        file_level_order=3,
        smoke=True,
        tags=["行政组织", "停用组织"]
    )
    def test_disable_adm_org(self):
        """
        停用行政组织用例
        """
        try:
            # 获取行政组织信息
            adm_org_info = TestAdmOrgManagement.org_info.get("adm_org_info", {})
            org_id = adm_org_info.get("id")
            if not org_id:
                self.test_save_adm_org()
                org_id = TestAdmOrgManagement.org_info.get("adm_org_info", {}).get("id")

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "id": org_id
            }
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-停用组织单元服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="删除行政组织",
        title="测试删除行政组织",
        description="验证删除行政组织接口的功能性",
        severity="blocker",
        file_level_order=4,
        smoke=True,
        tags=["行政组织", "删除组织"]
    )
    def test_delete_adm_org(self):
        """
        删除行政组织用例
        """
        try:
            # 获取行政组织信息（保持原有SQL逻辑）
            sql ="""
                select id  from org_struct_md where org_status="DRAFT" and org_dimension_code="ADM_ORG_GRP" and org_code like "AT_%" and deleted=0 limit 1;
            """
            result = self.db.query(sql)
            if not result:
                self.test_save_adm_org()
                org_id = self.org_info.get("adm_org_info", {}).get("id")
            else:
                org_id = result[0]["id"]

            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "id": org_id
            }
            fields_to_filter = ["id"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-删除组织单元服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_success(response)

            # 清除组织信息（保持原有逻辑）
            TestAdmOrgManagement.org_info = {}

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="查询行政组织",
        title="测试查询行政组织",
        description="验证查询行政组织接口的功能性",
        severity="blocker",
        file_level_order=5,
        smoke=True,
        tags=["行政组织", "查询组织"]
    )
    def test_query_adm_org(self):
        """
        查询行政组织用例
        """
        try:
            # 准备测试数据（业务逻辑保持不变）
            set_dict = {
                "orgDimensionCode": "ADM_ORG_GRP",
                "orgStatus": ["ENABLED", "INACTIVE", "DRAFT", "DISABLED"]
            }
            fields_to_filter = ["orgDimensionCode", "orgStatus"]

            # 使用标准化API调用（无任何断言）
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-新组织搜索服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )

            # 业务验证（保持原有逻辑）
            self.assert_util.assert_response_data(response)

            # 日志记录（Allure报告已由standard_api_call处理）

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
