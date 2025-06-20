import allure
import requests
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator
import pytest


@allure.epic("组织管理")
@allure.feature("组织保存")
class TestOrgSave(GenMdBaseTest):

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
        
        # 获取md_cache_data中的第一个数据
        cls.orgBusinessTypeIds = cls.md_cache_data["org_info"]["org_biz_type_cf"] if cls.md_cache_data.get("org_info") else None
        cls.logger.info(f"orgBusinessTypeIds: {cls.orgBusinessTypeIds}")
        for org_biz_type in  cls.orgBusinessTypeIds:
            if org_biz_type["code"] == "COM_ORG":
                cls.comOrgId = org_biz_type["id"]
            elif org_biz_type["code"] == "PUR_ORG":
                cls.purOrgId = org_biz_type["id"]
            elif org_biz_type["code"] == "SLS_ORG":
                cls.slsOrgId = org_biz_type["id"]
            elif org_biz_type["code"] == "SLS_DC":
                cls.slsDcId = org_biz_type["id"]
            elif org_biz_type["code"] == "INV_ORG":
                cls.invOrgId = org_biz_type["id"]
            elif org_biz_type["code"] == "INV_LOC":
                cls.invLocId = org_biz_type["id"]

    @pytest.mark.parametrize("org_type, tag, name_prefix, type_id_attr, order, allure_title", [
        ("com_org_info", "ComOrg", "公司组织", "comOrgId", 1, "测试公司组织保存接口"),
        ("pur_org_info", "PurOrg", "采购组织", "purOrgId", 2, "测试采购组织保存接口"),
        ("sls_org_info", "SlsOrg", "销售组织", "slsOrgId", 3, "测试销售组织保存接口"),
        ("inv_org_info", "InvOrg", "库存组织", "invOrgId", 4, "测试库存组织保存接口"),
    ])
    def test_save_org(self, org_type, tag, name_prefix, type_id_attr, order, allure_title):
        """
        通用组织保存用例
        """
        try:
            import allure
            allure.dynamic.title(allure_title)
            # 获取父公司组织信息
            com_org_info = TestOrgSave.org_info.get("com_org_info", {})
            org_parent_code = com_org_info.get("org_code")
            com_org_id = com_org_info.get("id")
            # 公司组织不需要父级
            if org_type != "com_org_info":
                assert org_parent_code and com_org_id, "请先执行test_save_org并成功保存公司组织"

            org_code = self.mock_data.generate_unique_code(tag=tag)
            org_name = f"{name_prefix}_{self.mock_data.get_timestamp()}"
            org_enable_date = self.mock_data.get_mock_date(include_time=False, days_offset=1)

            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            # 组织类型ID
            org_type_id = getattr(self, type_id_attr)

            # 过滤和设置参数
            param_keys = ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "orgDimensionCode"]
            if org_type != "com_org_info":
                param_keys += ["orgParentCode", "orgParentId", "comOrgId"]
            filtered_params = ParamUtil.filter_post_body_fields(params, param_keys, ["params", "request"])
            set_dict = {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 1 if org_type != "com_org_info" else 9999,
                "orgEnableDate": f"{org_enable_date}",
                "orgBusinessTypeIds": [org_type_id],
                "orgDimensionCode": "SCM_ORG_GRP"
            }
            if org_type != "com_org_info":
                set_dict.update({
                    "orgParentCode": org_parent_code,
                    "orgParentId": com_org_id,
                    "comOrgId": com_org_id
                })
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"filtered_params: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            org_id = response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_response_data(response)

            # 保存数据
            TestOrgSave.org_info.update({
                org_type: {
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
            com_org_id = TestOrgSave.org_info.get("com_org_info", {}).get("id")
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

    