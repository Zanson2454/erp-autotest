import allure
import requests
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.report_util import a, case_decorator
import pytest
import time


@allure.epic("组织管理")
@allure.feature("组织保存")
class TestBizOrgManagement(GenMdBaseTest):

    @classmethod
    def setup_class(cls):

        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.org_info = {}
        cls.enabled_org_id = None
        
        # 获取初始化数据中的第一个数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.genWcHeadId = cls.init_data["gen_wc_head_info"][0]["gen_wc_head_id"] if cls.init_data.get("gen_wc_head_info") else None
        # calenderId 由 GenMdBaseTest.bind_context 从 fin_cache_data（fin_init_sql）解析
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
     
        
        # 获取md_cache_data中的第一个数据
        if cls.md_cache_data:
            cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
            cls.slsDcId = cls.md_cache_data.get("org_info", {}).get("sls_dc_md", [])[0]["id"] if cls.md_cache_data.get("org_info", {}).get("sls_dc_md") else None
            cls.whId = cls.md_cache_data.get("org_info", {}).get("inv_wh_md", [])[0]["id"] if cls.md_cache_data.get("org_info", {}).get("inv_wh_md") else None

        # cls.logger.info(f"slsDcId:{cls.slsDcId}")
        # cls.logger.info(f"orgBusinessTypeIds: {cls.orgBusinessTypeIds}")
        if cls.orgBusinessTypeIds:
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

    @pytest.mark.run(file_level_order=1)
    @case_decorator(
        story="保存组织",
        title="测试保存公司组织",
        description="验证保存公司组织接口的功能性",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_com_org(self):
        """
        保存公司组织用例
        """
        try:
            # 1. 准备测试数据（原有业务逻辑完全保留）
            org_code = self.mock_util.generate_unique_code(tag="ComOrg")
            org_name = self.mock_util.get_mock_company()
            org_enable_date = self.mock_util.get_mock_date(include_time=False, days_offset=0)

            # 2. 使用标准化API调用（替换重复逻辑）
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 9999,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.comOrgTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "def3": self.counId,
                "def4": self.genWcHeadId,
                "def6": self.currId,
                "def12": self.calenderId
            }
            fields_to_filter = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "def3", "def4", "def6", "def12"]
            
            response, org_id = self.standard_api_call(
                api_key="ORG-组织架构-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="org"  # 可选：自动存储 self.org_id
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
            # 4. 原有数据保存逻辑（完全保留）
            TestBizOrgManagement.org_info.update({
                "com_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })
            
            # 5. 原有日志（可选）
            self.logger.info(f"保存公司组织完成，ID: {org_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存采购组织",
        description="验证保存采购组织接口的功能性",
        severity="blocker",
        file_level_order=2,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_pur_org(self):
        """
        保存采购组织用例
        """
        try:
            # 1. 获取父公司组织信息（原有依赖逻辑完全保留）
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            if not org_parent_code and not com_org_id:
                self._ensure_save_com_org()
                org_parent_code = TestBizOrgManagement.org_info.get("com_org_info", {}).get("org_code")
                com_org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")

            # 2. 准备测试数据
            org_code = self.mock_util.generate_unique_code(tag="PurOrg")
            org_name = f"采购组织_{self.mock_util.get_timestamp()}"
            org_enable_date = self.mock_util.get_mock_date(include_time=False, days_offset=0)

            # 3. 使用标准化API调用
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 1,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.purOrgTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgParentCode": org_parent_code,
                "orgParentId": com_org_id,
                "comOrgId": com_org_id
            }
            fields_to_filter = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "comOrgId"]
            
            response, org_id = self.standard_api_call(
                api_key="ORG-组织架构-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
            # 5. 原有数据保存逻辑（完全保留）
            TestBizOrgManagement.org_info.update({
                "pur_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存销售组织",
        description="验证保存销售组织接口的功能性",
        severity="blocker",
        file_level_order=3,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_sls_org(self):
        """
        保存销售组织用例
        """
        try:
            # 1. 获取父公司组织信息（原有依赖逻辑完全保留）
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            
            if not org_parent_code and not com_org_id:
                self._ensure_save_com_org()
                org_parent_code = TestBizOrgManagement.org_info.get("com_org_info", {}).get("org_code")
                com_org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")

            # 2. 准备测试数据
            org_code = self.mock_util.generate_unique_code(tag="SlsOrg")
            org_name = f"销售组织_{self.mock_util.get_timestamp()}"
            org_enable_date = self.mock_util.get_mock_date(include_time=False, days_offset=0)

            # 3. 使用标准化API调用
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 1,
                "def13": [self.slsDcId],
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.slsOrgTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgParentCode": org_parent_code,
                "orgParentId": com_org_id,
                "comOrgId": com_org_id
            }
            fields_to_filter = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "comOrgId", "def13"]
            
            response, org_id = self.standard_api_call(
                api_key="ORG-组织架构-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
            # 5. 原有数据保存逻辑（完全保留）
            TestBizOrgManagement.org_info.update({
                "sls_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存库存组织",
        description="验证保存库存组织接口的功能性",
        severity="blocker",
        file_level_order=4,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_inv_org(self):
        """
        保存库存组织用例
        """
        try:
            # 1. 获取父公司组织信息（原有依赖逻辑完全保留）
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            if not org_parent_code and not com_org_id:
                self._ensure_save_com_org()
                org_parent_code = TestBizOrgManagement.org_info.get("com_org_info", {}).get("org_code")
                com_org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")

            # 2. 准备测试数据
            org_code = self.mock_util.generate_unique_code(tag="InvOrg")
            org_name = f"库存组织_{self.mock_util.get_timestamp()}"
            org_enable_date = self.mock_util.get_mock_date(include_time=False, days_offset=0)

            # 3. 使用标准化API调用
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "def14": self.addrId,
                "orgSort": 1,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.invOrgTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgParentCode": org_parent_code,
                "orgParentId": com_org_id,
                "comOrgId": com_org_id
            }
            fields_to_filter = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "comOrgId", "def14"]
            
            response, org_id = self.standard_api_call(
                api_key="ORG-组织架构-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
            # 5. 原有数据保存逻辑（完全保留）
            TestBizOrgManagement.org_info.update({
                "inv_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存库存地点",
        description="验证保存库存地点接口的功能性",
        severity="blocker",
        file_level_order=5,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_inv_loc(self):
        """
        保存库存地点用例
        """
        try:
            # 1. 获取父库存组织信息（原有依赖逻辑完全保留）
            inv_org_info = TestBizOrgManagement.org_info.get("inv_org_info", {})
            org_parent_code = inv_org_info.get("org_code")
            inv_org_id = inv_org_info.get("id")
            if not org_parent_code and not inv_org_id:
                self._ensure_save_inv_org()
                org_parent_code = TestBizOrgManagement.org_info.get("inv_org_info", {}).get("org_code")
                inv_org_id = TestBizOrgManagement.org_info.get("inv_org_info", {}).get("id")

            # 2. 准备测试数据
            org_code = self.mock_util.generate_unique_code(tag="InvLoc")
            org_name = f"库存地点_{self.mock_util.get_timestamp()}"
            org_enable_date = self.mock_util.get_mock_date(include_time=False, days_offset=0)
            contact_phone = self.mock_util.get_mock_phone_number()
            contact_name = self.mock_util.get_mock_name()

            # 3. 使用标准化API调用
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 9999,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.invLocTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgParentCode": org_parent_code,
                "orgParentId": inv_org_id,
                "def2": self.addrId,  # 库存地点地址
                "def7": contact_name,    # 库存地点负责人
                "def8": contact_phone,  # 联系电话
                "def9": "详细地址信息",  # 详细地址
                "def10": self.whId # 仓库ID
            }
            fields_to_filter = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "def2", "def7", "def8", "def9", "def10"]
            
            response, org_id = self.standard_api_call(
                api_key="ORG-组织架构-保存服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
            # 5. 原有数据保存逻辑（完全保留）
            TestBizOrgManagement.org_info.update({
                "inv_loc_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="查询当前公司信息",
        title="测试当前公司信息查询接口",
        description="验证当前公司信息查询接口的功能性",
        severity="blocker",
        file_level_order=2,
        smoke=True,
        tags=["组织", "公司查询"]
    )
    def test_query_current_com_org(self):
        try:
            # 1. 获取公司ID（原有逻辑完全保留）
            com_org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")
            if not com_org_id:
                self._ensure_save_com_org()
                com_org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")

            # 2. 使用标准化API调用（查询操作）
            set_dict = {"id": com_org_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-查询当前组织的公司组织服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.parametrize("org_parent_id, title", [
        (None, "测试查询根节点组织树"),
        ("db_query", "测试查询指定节点下级组织树")
    ])
    @case_decorator(
        story="查询组织树",
        title="测试组织树查询接口",
        description="验证组织树查询接口的功能性",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["组织", "组织树查询"]
    )
    def test_query_org_tree(self, org_parent_id, title):
        try:
            import allure
            allure.dynamic.title(title)
            
            # 1. 如果需要查询数据库获取组织ID（原有复杂逻辑完全保留）
            if org_parent_id == "db_query":
                org_parent_id = self.query_service.get_first_org_struct_id(
                    org_dimension_code="SCM_ORG_GRP",
                    org_code_like="AT_%",
                    deleted=0,
                    org_status="ENABLED",
                )
                if not org_parent_id:
                    org_parent_id = self.query_service.get_first_org_struct_id(
                        org_dimension_code="SCM_ORG_GRP",
                        org_code_like="%",
                        deleted=0,
                        org_status="ENABLED",
                    )
                if not org_parent_id and self.md_cache_data:
                    inv_org_info = self.md_cache_data.get("org_info", {}).get("inv_org_info", [])
                    if inv_org_info:
                        org_parent_id = inv_org_info[0].get("id")
                self.assert_util.assert_by_operator(org_parent_id, "not_empty")
                self.logger.info(f"查询到的组织ID: {org_parent_id}")

            # 2. 使用标准化API调用
            set_dict = {
                "orgParentId": org_parent_id,
                "orgStatus": ["ENABLED", "INACTIVE", "DRAFT"],
                "orgDimensionCode": "SCM_ORG_GRP"
            }
            fields_to_filter = ["orgParentId", "orgStatus", "orgDimensionCode"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-查询下级服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留，包括复杂验证）
            self.assert_util.assert_response_data(response)
            
            # 4. 原有日志（保留）
            self.logger.info(f"组织树查询完成")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="查询组织架构",
        title="测试组织架构分页查询",
        description="验证组织架构分页查询接口的功能性",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["组织", "分页查询"]
    )
    @pytest.mark.parametrize("orgBusinessTypeCode", ["SLS_ORG", "PUR_ORG", "INV_ORG", "INV_LOC"])
    def test_query_org_struct_page(self,orgBusinessTypeCode):
        """
        组织架构分页查询用例
        """
        try:
            # 1. 使用标准化API调用（参数化保持不变）
            set_dict = {
                "orgStatus": "ENABLED",
                "orgBusinessTypeCode": orgBusinessTypeCode,
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "keyword": True,
                    "sortOrders": [],
                    "conditionGroup": None
                }
            }
            fields_to_filter = ["orgStatus", "orgBusinessTypeCode", "pageable"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="搜索组织",
        title="测试组织架构搜索",
        description="验证组织架构搜索接口的功能性",
        severity="critical",
        file_level_order=5,
        smoke=True,
        tags=["组织", "组织搜索"]
    )
    def test_search_org_struct(self):
        """
        组织架构搜索用例
        """
        try:
            # 1. 使用标准化API调用
            set_dict = {
                "orgName": "自动化",
                "orgStatus": ["ENABLED", "INACTIVE", "DRAFT"],
                "orgDimensionCode": "SCM_ORG_GRP"
            }
            fields_to_filter = ["orgName", "orgStatus", "orgDimensionCode"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-新组织搜索服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有复杂断言（完全保留）
            self.assert_util.assert_response_data(response)
            org_list = response.get("data",{}).get("data",[])
            self.assert_util.assert_by_operator(org_list,"not_empty")
            for org in org_list:
                self.assert_util.assert_by_operator(org.get("orgName"),"contain","自动化")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="暂时跳过，实际没有页面引用")
    @case_decorator(
        story="构建组织树",
        title="测试根据维度构建组织树",
        description="验证根据维度构建组织树接口的功能性",
        severity="critical",
        file_level_order=6,
        smoke=True,
        tags=["组织", "组织树构建"]
    )
    def test_build_org_tree_by_dimension(self, orgDimensionCode="SCM_ORG_GRP"):
        """
        根据维度构建组织树用例
        """
        try:
            # 设置查询参数
            set_dict = {
               # todo
            }
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-根据维度构建一个组织树服务",
                set_dict=set_dict,
                fields_to_filter=["orgDimensionCode", "orgStatus"]
            )
            self.logger.info(f"响应: {response}")

            # 断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的组织树数据
            data_result = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_result, "is_list")

            # Allure 附件
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="暂时跳过，实际没有页面引用")
    @case_decorator(
        story="组织导入",
        title="测试组织调整导入",
        description="验证组织调整导入接口的功能性",
        severity="normal",
        file_level_order=7,
        smoke=False,
        tags=["组织", "组织导入", "调整导入"]
    )
    def test_org_struct_update_import(self):
        """
        组织调整导入用例
        """
        try:
            # 设置导入参数（模拟数据）
            set_dict = {
                "sliceData": [
                    {
                        "id": "test_org_id",
                        "orgCode": "TEST_ORG_001",
                        "orgName": "测试组织001",
                        "orgDimensionCode": "SCM_ORG_GRP",
                        "orgStatus": "ENABLED"
                    }
                ],
                "context": {
                    "importMode": "UPDATE"
                }
            }
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-组织调整导入服务",
                set_dict=set_dict,
                fields_to_filter=["sliceData", "context"]
            )
            self.logger.info(f"响应: {response}")

            # 断言
            self.assert_util.assert_response_data(response)
            
            # Allure 附件
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="暂时跳过，实际没有页面引用")
    @case_decorator(
        story="组织导入",
        title="测试组织禁用导入",
        description="验证组织禁用导入接口的功能性",
        severity="normal",
        file_level_order=8,
        smoke=False,
        tags=["组织", "组织导入", "禁用导入"]
    )
    def test_org_struct_disable_import(self):
        """
        组织禁用导入用例
        """
        try:
            # 设置导入参数（模拟数据）
            set_dict = {
                "sliceData": [
                    {
                        "id": "test_org_id",
                        "orgCode": "TEST_ORG_001",
                        "orgName": "测试组织001",
                        "orgDimensionCode": "SCM_ORG_GRP",
                        "orgStatus": "DISABLED"
                    }
                ],
                "context": {
                    "importMode": "DISABLE"
                }
            }
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-组织禁用导入服务",
                set_dict=set_dict,
                fields_to_filter=["sliceData", "context"]
            )
            self.logger.info(f"响应: {response}")

            # 断言
            self.assert_util.assert_response_data(response)
            
            # Allure 附件
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织详情",
        title="测试查询组织单元详情",
        description="验证查询组织单元详情接口的功能性",
        severity="critical",
        file_level_order=9,
        smoke=True,
        tags=["组织", "详情查询"]
    )
    def test_query_org_struct_detail(self):
        """
        查询组织单元详情用例
        """
        try:
            # 1. 获取已创建的组织ID（原有数据库查询逻辑完全保留）
            org_id = self.query_service.get_first_org_struct_id(
                org_dimension_code="SCM_ORG_GRP",
                org_code_like="AT_%",
                deleted=0,
                org_status="ENABLED",
            )
            if not org_id:
                self._ensure_save_com_org()
                org_id = self.org_info.get("com_org_info", {}).get("id")
            
            # 2. 使用标准化API调用
            set_dict = {
                "id": org_id,
                "historyId": None
            }
            fields_to_filter = ["id", "historyId"]
            
            response, detail_id = self.standard_api_call(
                api_key="ORG-组织架构-查询组织单元详情服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言（完全保留）
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


    @pytest.mark.skip(reason="暂时跳过，实际没有页面引用")           
    @case_decorator(
        story="组织历史",
        title="测试查询组织历史版本",
        description="验证查询组织历史版本接口的功能性",
        severity="normal",
        file_level_order=10,
        smoke=False,
        tags=["组织", "历史版本"]
    )
    def test_query_org_struct_history(self):
        """
        查询组织历史版本用例
        """
        try:
            # 获取已创建的组织ID
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_id = com_org_info.get("id")
            if not org_id:
                self._ensure_save_com_org()
                org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")

            # 设置查询参数
            set_dict = {
                "id": org_id
            }
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-组织历史版本查看服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.logger.info(f"响应: {response}")

            # 断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的历史版本数据
            data_result = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_result, "is_list")
            
            self.logger.info(f"查询到组织历史版本数量: {len(data_result)}")
            
            # Allure 附件
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织管理",
        title="测试启用组织单元",
        description="验证启用组织单元接口的功能性",
        severity="normal",
        file_level_order=11,
        smoke=False,
        tags=["组织", "启用组织"]
    )
    def test_enable_org_struct(self):
        """
        启用组织单元用例
        """
        try:
            # 1. 获取组织ID（原有依赖逻辑完全保留）
            org_id_obj = self.org_info.get("com_org_info",{}).get("id")
            if not org_id_obj:
                self._ensure_save_com_org()
                org_id_obj = self.org_info.get("com_org_info",{}).get("id")

            # 提取数字ID
            org_id_value = org_id_obj.get('id') if isinstance(org_id_obj, dict) else org_id_obj
            if not org_id_value:
                raise ValueError(f"无法从响应获取有效的组织ID: {org_id_obj}")

            # 2. 使用标准化API调用
            set_dict = {"id": org_id_value}  # 使用数字ID
            fields_to_filter = ["id"]

            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-启用组织单元服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )

            # 3. 数据库验证 - 使用参数化查询
            org_status = self.query_service.get_org_struct_status(org_id_value)
            if org_status is None:
                raise ValueError(f"未找到组织记录，ID: {org_id_value}")
            self.assert_util.assert_by_operator(org_status,"=","ENABLED")
            self.enabled_org_id = org_id_value  # 存储数字ID
            self.logger.info(f"成功启用组织: {org_id_value}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织管理",
        title="测试停用组织单元",
        description="验证停用组织单元接口的功能性",
        severity="normal",
        file_level_order=12,
        smoke=False,
        tags=["组织", "停用组织"]
    )
    def test_disable_org_struct(self):
        """
        停用组织单元用例
        """
        try:
            # 1. 获取组织ID（原有重复检查逻辑完全保留）
            org_id_obj = self.org_info.get("com_org_info",{}).get("id")
            if not org_id_obj:
                self._ensure_save_com_org()
                org_id_obj = self.org_info.get("com_org_info",{}).get("id")

            # 提取数字ID
            org_id_value = org_id_obj.get('id') if isinstance(org_id_obj, dict) else org_id_obj
            if not org_id_value:
                raise ValueError(f"无法从响应获取有效的组织ID: {org_id_obj}")

            # 2. 使用标准化API调用
            set_dict = {"id": org_id_value}  # 使用数字ID
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-停用组织单元服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )

            # 3. 数据库验证 - 使用参数化查询
            org_status = self.query_service.get_org_struct_status(org_id_value)
            if org_status is None:
                raise ValueError(f"未找到组织记录，ID: {org_id_value}")
            self.assert_util.assert_by_operator(org_status,"=","DISABLED")
            self.logger.info(f"成功停用组织: {org_id_value}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织管理",
        title="测试删除组织单元",
        description="验证删除组织单元接口的功能性",
        severity="critical",
        file_level_order=13,
        smoke=False,
        tags=["组织", "删除组织"]
    )
    def test_delete_org_struct(self):
        """
        删除组织单元用例
        """
        try:
            # 1. 获取已停用的组织ID（原有数据库查询逻辑完全保留）
            org_id = self.query_service.get_first_org_struct_id(
                org_dimension_code="SCM_ORG_GRP",
                org_code_like="AT_%",
                deleted=0,
            )
            if not org_id:
                self._ensure_save_com_org()
                org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")
                
            # 2. 使用标准化API调用
            set_dict = {"id": org_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-删除组织单元服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 原有断言和数据库验证（完全保留）
            self.assert_util.assert_response_success(response)
            deleted = self.query_service.get_org_struct_deleted(org_id)
            if deleted is None:
                deleted = 0
            self.assert_util.assert_by_operator(deleted,"!=",0)
            self.logger.info(f"成功删除组织: {org_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织类型",
        title="测试查询组织类型列表",
        description="验证查询组织类型列表接口的功能性",
        severity="normal",
        file_level_order=14,
        smoke=True,
        tags=["组织", "类型查询"]
    )
    def test_query_org_type_list(self):
        """
        查询组织类型列表用例
        """
        try:
            # 1. 使用标准化API调用
            set_dict = {
                "orgDimensionCode": "SCM_ORG_GRP"
            }
            fields_to_filter = ["orgDimensionCode"]
            
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-查询组织类型列表服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 2. 原有复杂断言（完全保留）
            self.assert_util.assert_response_data(response)
            org_type_list = response.get("data",{}).get("data",[])
            self.assert_util.assert_by_operator(org_type_list,"not_empty")
            org_type_codes=[]
            for org_type in org_type_list:
                 org_type_codes.append(org_type.get("code"))
            # 验证返回的组织类型
            self.assert_util.assert_all_in(["COM_ORG","SLS_ORG","PUR_ORG","INV_ORG"],org_type_codes)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织导入",
        title="测试获取组织导入模版",
        description="验证获取组织导入模版接口的功能性",
        severity="normal",
        file_level_order=15,
        smoke=False,
        tags=["组织", "导入模版"]
    )
    @pytest.mark.skip(reason="需要准备模板，手工验证")
    def test_get_org_import_template(self):
        """
        获取组织导入模版用例
        """
        try:
            set_dict = {
                "orgDimensionCode": "SCM_ORG_GRP",
                "templateType": "ORG_CREATE"
            }
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-获取组织导入的模版服务",
                set_dict=set_dict,
                fields_to_filter=["orgDimensionCode", "templateType"]
            )
            self.assert_util.assert_response_data(response)
            template_data = response.get("data",{}).get("data",{})
            # 验证返回的导入模版数据
            self.assert_util.assert_by_operator(template_data.get("importHeaderContextList"),"not_empty")
            
            # Allure 附件
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.skip(reason="暂时跳过，实际没有页面引用")
    @case_decorator(
        story="组织导入",
        title="测试组织新增导入",
        description="验证组织新增导入接口的功能性",
        severity="normal",
        file_level_order=16,
        smoke=False,
        tags=["组织", "组织导入", "新增导入"]
    )
    def test_org_struct_create_import(self):
        """
        组织新增导入用例
        """
        try:
            # 设置导入参数（模拟数据）
            set_dict = {
                "sliceData": [
                    {
                        "orgCode": "NEW_ORG_001",
                        "orgName": "新增组织001",
                        "orgDimensionCode": "SCM_ORG_GRP",
                        "orgStatus": "ENABLED",
                        "orgBusinessTypeIds": [self.comOrgTypeId]
                    }
                ],
                "context": {
                    "importMode": "CREATE"
                }
            }
            response, _ = self.standard_api_call(
                api_key="ORG-组织架构-组织新增导入服务",
                set_dict=set_dict,
                fields_to_filter=["sliceData", "context"]
            )
            self.logger.info(f"响应: {response}")

            # 断言
            self.assert_util.assert_response_data(response)
            
            # Allure 附件
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
