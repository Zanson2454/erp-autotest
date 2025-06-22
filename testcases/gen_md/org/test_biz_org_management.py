import allure
import requests
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
import pytest


@allure.epic("组织管理")
@allure.feature("组织保存")
class TestBizOrgManagement(GenMdBaseTest):

    @classmethod
    def setup_class(cls):
      
        super().setup_class()
        cls.org_info = {}
        cls.mock_data = MockData()
        cls.logger.info(f"init_data: {cls.init_data}")
        cls.logger.info(f"md_cache_data: {cls.md_cache_data}")
        
        # 获取初始化数据中的第一个数据
        cls.currId = cls.init_data["currency_info"][0]["curr_id"] if cls.init_data.get("currency_info") else None
        cls.counId = cls.init_data["country_info"][0]["coun_id"] if cls.init_data.get("country_info") else None
        cls.genWcHeadId = cls.init_data["gen_wc_head_info"][0]["gen_wc_head_id"] if cls.init_data.get("gen_wc_head_info") else None
        cls.calenderId = cls.init_data["calender_info"][0]["id"] if cls.init_data.get("calender_info") else None
        cls.addrId = cls.init_data["addr_info"][0]["id"] if cls.init_data.get("addr_info") else None
     
        
        # 获取md_cache_data中的第一个数据
        cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
        cls.slsDcId = cls.md_cache_data.get("org_info", {}).get("sls_dc_md", [])[0]["id"] if cls.md_cache_data.get("org_info", {}).get("sls_dc_md") else None
        cls.whId = cls.md_cache_data.get("org_info", {}).get("inv_wh_md", [])[0]["id"] if cls.md_cache_data.get("org_info", {}).get("inv_wh_md") else None

        cls.logger.debug(f"slsDcId:{cls.slsDcId}")
        cls.logger.info(f"orgBusinessTypeIds: {cls.orgBusinessTypeIds}")
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

    @case_decorator(
        story="保存组织",
        title="测试保存公司组织",
        description="验证保存公司组织接口的功能性",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_com_org(self):
        """
        保存公司组织用例
        """
        try:
            org_code = self.mock_data.generate_unique_code(tag="ComOrg")
            org_name = self.mock_data.get_mock_company()
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "def3", "def4", "def6", "def12"],
                ["params", "request"]
            )
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
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestBizOrgManagement.org_info.update({
                "com_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存采购组织",
        description="验证保存采购组织接口的功能性",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_pur_org(self):
        """
        保存采购组织用例
        """
        try:
            # 获取父公司组织信息
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            assert org_parent_code and com_org_id, "请先执行test_save_com_org并成功保存公司组织"

            org_code = self.mock_data.generate_unique_code(tag="PurOrg")
            org_name = f"采购组织_{self.mock_data.get_timestamp()}"
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "comOrgId"],
                ["params", "request"]
            )
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
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestBizOrgManagement.org_info.update({
                "pur_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存销售组织",
        description="验证保存销售组织接口的功能性",
        severity="blocker",
        order=3,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_sls_org(self):
        """
        保存销售组织用例
        """
        try:
            # 获取父公司组织信息
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            assert org_parent_code and com_org_id, "请先执行test_save_com_org并成功保存公司组织"

            org_code = self.mock_data.generate_unique_code(tag="SlsOrg")
            org_name = f"销售组织_{self.mock_data.get_timestamp()}"
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "comOrgId","def13"],
                ["params", "request"]
            )
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 1,
                "def13":[self.slsDcId],
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.slsOrgTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgParentCode": org_parent_code,
                "orgParentId": com_org_id,
                "comOrgId": com_org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestBizOrgManagement.org_info.update({
                "sls_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存库存组织",
        description="验证保存库存组织接口的功能性",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_inv_org(self):
        """
        保存库存组织用例
        """
        try:
            # 获取父公司组织信息
            com_org_info = TestBizOrgManagement.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            assert org_parent_code and com_org_id, "请先执行test_save_com_org并成功保存公司组织"

            org_code = self.mock_data.generate_unique_code(tag="InvOrg")
            org_name = f"库存组织_{self.mock_data.get_timestamp()}"
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "comOrgId"],
                ["params", "request"]
            )
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "def14":self.addrId,
                "orgSort": 1,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [self.invOrgTypeId],
                "orgDimensionCode": "SCM_ORG_GRP",
                "orgParentCode": org_parent_code,
                "orgParentId": com_org_id,
                "comOrgId": com_org_id
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestBizOrgManagement.org_info.update({
                "inv_org_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="保存组织",
        title="测试保存库存地点",
        description="验证保存库存地点接口的功能性",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["组织", "保存组织"]
    )
    def test_save_inv_loc(self):
        """
        保存库存地点用例
        """
        try:
            # 获取父库存组织信息
            inv_org_info = TestBizOrgManagement.org_info.get("inv_org_info", {})
            org_parent_code = inv_org_info.get("org_code")
            inv_org_id = inv_org_info.get("id")
            assert org_parent_code and inv_org_id, "请先执行test_save_inv_org并成功保存库存组织"

            org_code = self.mock_data.generate_unique_code(tag="InvLoc")
            org_name = f"库存地点_{self.mock_data.get_timestamp()}"
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode", "orgParentCode", "orgParentId", "def2", "def7", "def8", "def9","def10"],
                ["params", "request"]
            )
            
            contact_phone = self.mock_data.get_mock_phone_number()
            contact_name = self.mock_data.get_mock_name()
            
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
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestBizOrgManagement.org_info.update({
                "inv_loc_info": {
                    "id": org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                }
            })

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="查询当前公司信息",
        title="测试当前公司信息查询接口",
        description="验证当前公司信息查询接口的功能性",
        severity="blocker",
        order=2,
        smoke=True,
        tags=["组织", "公司查询"]
    )
    def test_query_current_com_org(self):
        try:
            # 1. 获取公司ID
            com_org_id = TestBizOrgManagement.org_info.get("com_org_info", {}).get("id")
            assert com_org_id, "请先执行test_save_org并成功保存公司组织"

            # 2. 获取API配置
            api_path = self.get_api_path("ORG-组织架构-查询当前组织的公司组织服务")  # key以md_api_path.yaml为准
            params, url = self.get_api_params(api_path)

            # 3. 设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            filtered_params['params']['request']['id'] =com_org_id
            self.logger.info(f"请求参数: {filtered_params}")

            # 4. 发送请求
            response = self.http.post(url, json=filtered_params)
            self.logger.info(f"响应: {response}")

            # 5. 断言
            self.assert_util.assert_response_data(response)

            # 6. Allure 附件
            a.json(params, "请求数据")
            a.json(response, "响应数据")
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
        order=3,
        smoke=True,
        tags=["组织", "组织树查询"]
    )
    def test_query_org_tree(self, org_parent_id, title):
        try:
            import allure
            allure.dynamic.title(title)
            
            # 1. 如果需要查询数据库获取组织ID
            if org_parent_id == "db_query":
                sql = """
                    SELECT id, org_code, org_name 
                    FROM org_struct_md 
                    WHERE org_status = 'ENABLED' 
                        AND org_dimension_code = 'SCM_ORG_GRP'
                        AND deleted = 0 
                    ORDER BY org_sort DESC
                    LIMIT 1
                """
                result = self.db.query(sql)
                self.assert_util.assert_not_empty(result, "组织列表")
                org_parent_id = result[0]["id"]
                self.logger.info(f"查询到的组织ID: {org_parent_id}")

            # 2. 获取API配置
            api_path = self.get_api_path("ORG-组织架构-查询下级服务")
            params, url = self.get_api_params(api_path)

            # 3. 设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgParentId", "orgStatus", "orgDimensionCode"],
                ["params", "request"]
            )
            filtered_params['params']['request'].update({
                "orgParentId": org_parent_id,
                "orgStatus": ["ENABLED", "INACTIVE", "DRAFT"],
                "orgDimensionCode": "SCM_ORG_GRP"
            })
            self.logger.info(f"请求参数: {filtered_params}")

            # 4. 发送请求
            response = self.http.post(url, json=filtered_params)
            self.logger.info(f"响应: {response}")

            # 5. 断言
            self.assert_util.assert_response_data(response)

            # 6. Allure 附件
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    