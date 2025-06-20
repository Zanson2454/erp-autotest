import allure
import requests
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


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
    @case_decorator(
        story="保存组织信息",
        title="测试组织保存接口",
        description="验证组织保存接口的功能性",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织", "保存"]
    )
    def test_save_org(self):
        try:
            # 1. 生成测试数据
            
            org_code = self.mock_data.generate_unique_code(tag="ComOrg")
            org_name = self.mock_data.get_mock_company()
            org_enable_date = self.mock_data.get_mock_date(include_time=False)

            # 2. 获取API配置
            api_path = self.get_api_path("ORG-组织架构-保存服务")
            params, url = self.get_api_params(api_path)

            # 3. 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["orgCode", "orgName", "orgSort", "orgEnableDate", "orgBusinessTypeIds", "def6", "def3", "def4", "def12", "orgDimensionCode"],
                ["params", "request"]
            )
            filtered_params["serviceKey"] = "GEN_MD$ORG_STRUCT_MD_SAVE_ACTION_SERVICE"
            ParamUtil.set_request_params(filtered_params, {
                "orgCode": org_code,
                "orgName": org_name,
                "orgSort": 9999,
                "orgEnableDate": f'{org_enable_date}',
                "orgBusinessTypeIds": [self.comOrgId],
                "def6": self.currId, # currId 币种
                "def3": self.counId, # counId 国家
                "def4": self.genWcHeadId, # genWcHeadId 工作日日历
                "def12": self.calenderId, # calenderId 期间类型
                "orgDimensionCode": "SCM_ORG_GRP"
            })
            self.logger.info(f"filtered_params: {filtered_params}")
            # 4. 发送请求
            response = self.http.post(url, json=filtered_params)
            com_org_id = response.get("data", {}).get("data", {}).get("id")
            # 5. 验证响应
            self.assert_util.assert_response_data(response)

            # 6. 保存数据
            TestOrgSave.org_info.update({
                "com_org_info": {
                    "id":com_org_id,
                    "org_code": org_code,
                    "org_name": org_name,
                    } 
            })

            # 7. 添加Allure附件
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
            params["serviceKey"] = "GEN_MD$ORG_STRUCT_QUERY_CURRENT_COM_ORG_ACTION_SERVICE"
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "id": com_org_id
            })
            self.logger.info(f"请求参数: {params}")

            # 4. 发送请求
            response = self.http.post(url, json=params)
            self.logger.info(f"响应: {response}")

            # 5. 断言
            self.assert_util.assert_response_data(response)

            # 6. Allure 附件
            a.json(params, "请求数据")
            a.json(response, "响应数据")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

