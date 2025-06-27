import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("组织切换管理")
class TestOrg_SwitchManagement(GenMdBaseTest):
    """组织切换管理测试类"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        cls.org_switch_id = None
        cls.org_switch_code = None
        cls.org_switch_model_id = None
        cls.modelKey = None
        cls.modelName = None
        cls.logger.info("组织切换管理测试类初始化完成")
        
        
        cls.orgDimensionId = cls.md_cache_data["org_info"].get("org_dimension_cf",[])[0]["id"]
        cls.com_org_id = cls.md_cache_data["org_info"].get("com_org_info",[])[0]["id"]
    @classmethod
    def teardown_class(cls):
        """
        测试类结束后执行清理
        清理所有测试过程中创建的组织切换管理数据
        """
        try:
            # 使用SQL删除测试数据
            cls.db.delete(
                table="org_switch_list_cf",
                where="switch_describe like %s",
                params=["AT_OrgSwitch%"]
            )
            cls.db.delete(
                table="org_switch_model_cf",
                where="model_key like %s",
                params=["org_switch_model_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="组织切换管理",
        title="测试新增组织切换模型",
        description="验证新增组织切换模型功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["组织切换管理", "新增模型"]
    )
    def test_save_org_switch_model(self):
        """
        新增组织切换模型用例
        """
        try:
            # 调用保存接口
            api_path = self.get_api_path("ORG-多组织-保存组织切换模型服务")
            params, url = self.get_api_params(api_path)
            
             # 准备组织切换模型数据
            menu = f"菜单名称_{self.mock_util.get_timestamp(timestamp=True)}"
            self.modelKey =f"org_switch_model_{self.mock_util.get_timestamp(timestamp=True)}"
            self.modelName = f"组织切换模型表名_{self.mock_util.get_timestamp(timestamp=True)}"     


            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["menu", "modelKey", "modelName", "isOpen", "describe"],
                ["params", "request"]
            )
            set_dict = {
                "menu": menu,
                "modelKey": self.modelKey,
                "modelName": self.modelName,
                "isOpen": True,
                "describe": f"自动化测试组织切换模型-{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            

            # 保存组织切换模型信息供后续用例使用
            sql = f"select id from org_switch_model_cf where model_key = '{self.modelKey}'"
            self.org_switch_model_id = self.db.query(sql)[0]["id"]
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试分页查询组织切换模型",
        description="验证分页查询组织切换模型功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["组织切换管理", "模型分页查询"]
    )
    def test_query_org_switch_model_page(self):
        """
        分页查询组织切换模型用例
        """
        try:
            if not self.modelKey:
                self.test_save_org_switch_model()
                
            # 调用分页查询接口
            api_path = self.get_api_path("ORG-多组织-分页查询组织切换模型服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields","systemParams"],
                ["params", "request"]
            )
            set_dict = {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": {
                            "type": "ConditionItems",
                            "conditions": {
                                "modelKey": {
                                    "operator": "CONTAINS",
                                    "value": self.modelKey
                                }
                            },
                            "logicOperator": "AND"
                        }
                    },
                    "fields": [
                        {
                            "name": "modelKey",
                            "type": "TEXT"
                        },
                        {
                            "name": "modelName",
                            "type": "TEXT"
                        },
                        {
                            "name": "isOpen",
                            "type": "BOOL"
                        },
                        {
                            "name": "menu",
                            "type": "TEXT"
                        }
                    ],
                    "systemParams": None
                }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            total = response.get("data", {}).get("data", {}).get("total", 0)
            self.assert_util.assert_by_operator(total, "=", 1)
            

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试查询组织切换模型详情",
        description="验证查询组织切换模型详情功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["组织切换管理", "模型详情查询"]
    )
    def test_query_org_switch_model_detail(self):
        """
        查询组织切换模型详情用例
        """
        try:
            # 获取组织切换模型信息
            if not self.org_switch_model_id:
                self.test_save_org_switch_model()

            # 调用详情查询接口
            api_path = self.get_api_path("ORG-多组织-查询组织切换模型详情服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.org_switch_model_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise




    @pytest.mark.skip(
        reason="实际未引用"
    )
    @case_decorator(
        story="组织切换管理",
        title="测试模型是否开启了组织切换",
        description="验证模型是否开启了组织切换功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["组织切换管理", "模型开启判断"]
    )
    def test_judge_model_org_switch_enable(self):
        """
        判断模型是否开启了组织切换用例
        """
        try:
            # 调用判断接口
            api_path = self.get_api_path("ORG-多组织-模型是否开启了组织切换服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["model_key"],
                ["params", "request"]
            )
            set_dict = {"model_key": "GEN_MD$ORG_SWITCH_MODEL_CF"}
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="组织切换管理",
        title="测试新增组织切换",
        description="验证新增组织切换功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["组织切换管理", "新增"]
    )
    def test_save_org_switch(self):
        """
        新增组织切换用例
        """
        try:
            # 获取组织切换模型信息
            if not self.org_switch_model_id:
                self.test_save_org_switch_model()

            # 准备组织切换数据
            org_switch_des = self.mock_util.generate_unique_code(tag="OrgSwitch")
            org_switch_name = f"组织切换_{self.mock_util.get_timestamp(timestamp=True)}"

            # 调用保存接口
            api_path = self.get_api_path("ORG-多组织-保存组织切换服务")
            params, url = self.get_api_params(api_path)

            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["switchName","switchOrgId","orgDimensionId","switchStatus","switchName","switchDesc"],
                ["params", "request"]
            )
            set_dict = {
                "switchName": org_switch_name,
                "switchDescribe": org_switch_des,
                "switchOrgId": {"id": self.com_org_id},
                "switchStatus": "ENABLED", 
                "orgDimensionId": {"id": self.orgDimensionId}
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            self.logger.info(f"请求参数: {filtered_params}")

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            sql = f"select id from org_switch_list_cf where org_switch_des = '{org_switch_des}'"
            self.org_switch_id = self.db.query(sql)[0]["id"]

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试启用组织切换",
    #     description="验证启用组织切换功能",
    #     severity="normal",
    #     order=6,
    #     smoke=True,
    #     tags=["组织切换管理", "启用"]
    # )
    # def test_enable_org_switch(self):
    #     """
    #     启用组织切换用例
    #     """
    #     try:
    #         # 获取组织切换信息
    #         if not self.org_switch_id:
    #             self.test_save_org_switch()

    #         # 调用启用接口
    #         api_path = self.get_api_path("ORG-多组织-启用组织切换服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["ids"],
    #             ["params", "request"]
    #         )
    #         set_dict = {"ids": [self.org_switch_id]}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试停用组织切换",
    #     description="验证停用组织切换功能",
    #     severity="normal",
    #     order=7,
    #     smoke=True,
    #     tags=["组织切换管理", "停用"]
    # )
    # def test_disable_org_switch(self):
    #     """
    #     停用组织切换用例
    #     """
    #     try:
    #         # 获取组织切换信息
    #         if not self.org_switch_id:
    #             self.test_enable_org_switch()

    #         # 调用停用接口
    #         api_path = self.get_api_path("ORG-多组织-停用组织切换服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["ids"],
    #             ["params", "request"]
    #         )
    #         set_dict = {"ids": [self.org_switch_id]}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试分页查询组织切换",
    #     description="验证分页查询组织切换功能",
    #     severity="normal",
    #     order=8,
    #     smoke=True,
    #     tags=["组织切换管理", "分页查询"]
    # )
    # def test_query_org_switch_page(self):
    #     """
    #     分页查询组织切换用例
    #     """
    #     try:
    #         # 调用分页查询接口
    #         api_path = self.get_api_path("ORG-多组织-分页查询组织切换服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["pageable", "fields"],
    #             ["params", "request"]
    #         )
    #         set_dict = {
    #             "pageable": {
    #                 "pageNo": 1,
    #                 "pageSize": 20,
    #                 "needTotal": True
    #             },
    #             "fields": [
    #                 {"name": "org_switch_code", "type": "TEXT"},
    #                 {"name": "org_switch_name", "type": "TEXT"},
    #                 {"name": "status", "type": "SELECT"}
    #             ]
    #         }
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试查询组织切换详情",
    #     description="验证查询组织切换详情功能",
    #     severity="normal",
    #     order=9,
    #     smoke=True,
    #     tags=["组织切换管理", "详情查询"]
    # )
    # def test_query_org_switch_detail(self):
    #     """
    #     查询组织切换详情用例
    #     """
    #     try:
    #         # 获取组织切换信息
    #         if not self.org_switch_id:
    #             self.test_save_org_switch()

    #         # 调用详情查询接口
    #         api_path = self.get_api_path("ORG-多组织-查询组织切换详情服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["id"],
    #             ["params", "request"]
    #         )
    #         set_dict = {"id": self.org_switch_id}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_data(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试查询用户所在的公司",
    #     description="验证查询用户所在的公司功能",
    #     severity="normal",
    #     order=10,
    #     smoke=True,
    #     tags=["组织切换管理", "用户公司查询"]
    # )
    # def test_query_user_company(self):
    #     """
    #     查询用户所在的公司用例
    #     """
    #     try:
    #         # 调用查询用户所在公司接口
    #         api_path = self.get_api_path("ORG-多组织-查询用户所在的公司服务")
    #         params, url = self.get_api_params(api_path)

    #         # 这个接口可能不需要参数或参数很少
    #         self.logger.info(f"请求参数: {params}")

    #         response = self.http.post(url, json=params)
    #         self.assert_util.assert_response_data(response)

    #         a.json(params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司列表标准导出",
    #     description="验证切换公司列表标准导出功能",
    #     severity="normal",
    #     order=11,
    #     smoke=True,
    #     tags=["组织切换管理", "列表导出"]
    # )
    # def test_export_org_switch_list(self):
    #     """
    #     切换公司列表标准导出用例
    #     """
    #     try:
    #         # 调用标准导出接口
    #         api_path = self.get_api_path("切换公司列表标准导出服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["exportConfig"],
    #             ["params", "request"]
    #         )
    #         set_dict = {
    #             "exportConfig": {
    #                 "exportType": "EXCEL",
    #                 "conditions": {}
    #             }
    #         }
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司模型表标准导出",
    #     description="验证切换公司模型表标准导出功能",
    #     severity="normal",
    #     order=12,
    #     smoke=True,
    #     tags=["组织切换管理", "模型导出"]
    # )
    # def test_export_org_switch_model(self):
    #     """
    #     切换公司模型表标准导出用例
    #     """
    #     try:
    #         # 调用标准导出接口
    #         api_path = self.get_api_path("切换公司模型表标准导出服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["exportConfig"],
    #             ["params", "request"]
    #         )
    #         set_dict = {
    #             "exportConfig": {
    #                 "exportType": "EXCEL",
    #                 "conditions": {}
    #             }
    #         }
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @pytest.mark.skip(reason="标准导入需要上传文件，暂时跳过")
    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司列表标准导入",
    #     description="验证切换公司列表标准导入功能",
    #     severity="normal",
    #     order=13,
    #     smoke=True,
    #     tags=["组织切换管理", "列表导入"]
    # )
    # def test_import_org_switch_list(self):
    #     """
    #     切换公司列表标准导入用例
    #     """
    #     try:
    #         # 调用标准导入接口
    #         api_path = self.get_api_path("切换公司列表标准导入服务")
    #         params, url = self.get_api_params(api_path)

    #         # 标准导入需要文件上传，这里暂时跳过实现
    #         self.logger.info("标准导入需要文件上传，暂时跳过")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @pytest.mark.skip(reason="标准导入需要上传文件，暂时跳过")
    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司模型表标准导入",
    #     description="验证切换公司模型表标准导入功能",
    #     severity="normal",
    #     order=14,
    #     smoke=True,
    #     tags=["组织切换管理", "模型导入"]
    # )
    # def test_import_org_switch_model(self):
    #     """
    #     切换公司模型表标准导入用例
    #     """
    #     try:
    #         # 调用标准导入接口
    #         api_path = self.get_api_path("切换公司模型表标准导入服务")
    #         params, url = self.get_api_params(api_path)

    #         # 标准导入需要文件上传，这里暂时跳过实现
    #         self.logger.info("切换公司模型表标准导入需要文件上传，暂时跳过")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试删除组织切换",
    #     description="验证删除组织切换功能",
    #     severity="normal",
    #     order=15,
    #     smoke=True,
    #     tags=["组织切换管理", "删除"]
    # )
    # def test_delete_org_switch(self):
    #     """
    #     删除组织切换用例
    #     """
    #     try:
    #         # 获取组织切换信息
    #         if not self.org_switch_id:
    #             self.test_save_org_switch()

    #         # 调用删除接口
    #         api_path = self.get_api_path("ORG-多组织-删除组织切换服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["ids"],
    #             ["params", "request"]
    #         )
    #         set_dict = {"ids": [self.org_switch_id]}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试删除组织切换模型",
    #     description="验证删除组织切换模型功能",
    #     severity="normal",
    #     order=16,
    #     smoke=True,
    #     tags=["组织切换管理", "删除模型"]
    # )
    # def test_delete_org_switch_model(self):
    #     """
    #     删除组织切换模型用例
    #     """
    #     try:
    #         # 获取组织切换模型信息
    #         if not self.org_switch_model_id:
    #             self.test_save_org_switch_model()

    #         # 调用删除接口
    #         api_path = self.get_api_path("ORG-多组织-删除组织切换模型服务")
    #         params, url = self.get_api_params(api_path)

    #         # 过滤和设置参数
    #         filtered_params = ParamUtil.filter_post_body_fields(
    #             params,
    #             ["ids"],
    #             ["params", "request"]
    #         )
    #         set_dict = {"ids": [self.org_switch_model_id]}
    #         ParamUtil.set_request_params(filtered_params, set_dict)
    #         self.logger.info(f"请求参数: {filtered_params}")

    #         response = self.http.post(url, json=filtered_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(filtered_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司列表导出任务提交",
    #     description="验证切换公司列表导入导出任务管理接口-提交导出任务功能",
    #     severity="normal",
    #     order=17,
    #     smoke=True,
    #     tags=["组织切换管理", "列表导出任务"]
    # )
    # def test_submit_org_switch_list_export_task(self):
    #     """
    #     切换公司列表-导入导出任务管理接口-提交导出任务用例
    #     """
    #     try:
    #         # 调用提交导出任务接口
    #         api_path = self.get_api_path("切换公司列表-导入导出任务管理接口-提交导出任务")
    #         params, url = self.get_api_params(api_path)

    #         # 获取用户信息
    #         user_name = self.md_cache_data.get("user_info", {}).get("username", "AutoTest")

    #         # 构建导出任务参数
    #         export_params = {
    #             "serviceKey": "GEN_MD$ORG_SWITCH_LIST_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
    #             "params": {
    #                 "taskName": f"切换公司列表-{user_name}-{self.mock_util.get_timestamp()}-导出",
    #                 "multiSheetConfig": [
    #                     {
    #                         "sheetName": "切换公司列表",
    #                         "exportConfig": {
    #                             "exportType": "EXCEL",
    #                             "conditions": {}
    #                         }
    #                     }
    #                 ],
    #                 "queryData": {
    #                     "containerKey": "GEN_MD$ORG_SWITCH_LIST_VIEW-table-container-GEN_MD$org_switch_list_cf",
    #                     "viewKey": "GEN_MD$ORG_SWITCH_LIST_VIEW:list",
    #                     "sceneKey": "GEN_MD$ORG_SWITCH_LIST_VIEW",
    #                     "params": {
    #                         "request": {
    #                             "pageable": {}
    #                         },
    #                         "selectFields": [
    #                             "switchName",
    #                             "switchDescribe", 
    #                             "switchStatus",
    #                             "switchOrgId",
    #                             "orgDimensionId"
    #                         ]
    #                     }
    #                 }
    #             }
    #         }

    #         self.logger.info(f"请求参数: {export_params}")
    #         response = self.http.post(url, json=export_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(export_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司模型表导出任务提交",
    #     description="验证切换公司模型表导入导出任务管理接口-提交导出任务功能",
    #     severity="normal",
    #     order=18,
    #     smoke=True,
    #     tags=["组织切换管理", "模型导出任务"]
    # )
    # def test_submit_org_switch_model_export_task(self):
    #     """
    #     切换公司模型表-导入导出任务管理接口-提交导出任务用例
    #     """
    #     try:
    #         # 调用提交导出任务接口
    #         api_path = self.get_api_path("切换公司模型表-导入导出任务管理接口-提交导出任务")
    #         params, url = self.get_api_params(api_path)

    #         # 获取用户信息
    #         user_name = self.md_cache_data.get("user_info", {}).get("username", "AutoTest")

    #         # 构建导出任务参数
    #         export_params = {
    #             "serviceKey": "GEN_MD$ORG_SWITCH_MODEL_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
    #             "params": {
    #                 "taskName": f"切换公司模型表-{user_name}-{self.mock_util.get_timestamp()}-导出",
    #                 "multiSheetConfig": [
    #                     {
    #                         "sheetName": "切换公司模型表",
    #                         "exportConfig": {
    #                             "exportType": "EXCEL",
    #                             "conditions": {}
    #                         }
    #                     }
    #                 ],
    #                 "queryData": {
    #                     "containerKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW-table-container-GEN_MD$org_switch_model_cf",
    #                     "viewKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW:list",
    #                     "sceneKey": "GEN_MD$ORG_SWITCH_MODEL_VIEW",
    #                     "params": {
    #                         "request": {
    #                             "pageable": {}
    #                         },
    #                         "selectFields": [
    #                             "model_code",
    #                             "model_name",
    #                             "description",
    #                             "status"
    #                         ]
    #                     }
    #                 }
    #             }
    #         }

    #         self.logger.info(f"请求参数: {export_params}")
    #         response = self.http.post(url, json=export_params)
    #         self.assert_util.assert_response_success(response)

    #         a.json(export_params, "请求数据")
    #         a.json(response, "响应数据")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @pytest.mark.skip(reason="OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")
    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司列表OSS导入任务提交",
    #     description="验证切换公司列表导入导出任务管理接口-通过OSS提交导入任务功能",
    #     severity="normal",
    #     order=19,
    #     smoke=True,
    #     tags=["组织切换管理", "列表OSS导入任务"]
    # )
    # def test_submit_org_switch_list_import_task_by_oss(self):
    #     """
    #     切换公司列表-导入导出任务管理接口-通过OSS提交导入任务用例
    #     """
    #     try:
    #         # 调用通过OSS提交导入任务接口
    #         api_path = self.get_api_path("切换公司列表-导入导出任务管理接口-通过OSS提交导入任务")
    #         params, url = self.get_api_params(api_path)

    #         # OSS导入任务需要复杂的文件上传和OSS配置，这里暂时跳过实现
    #         self.logger.info("OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise

    # @pytest.mark.skip(reason="OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")
    # @case_decorator(
    #     story="组织切换管理",
    #     title="测试切换公司模型表OSS导入任务提交",
    #     description="验证切换公司模型表导入导出任务管理接口-通过OSS提交导入任务功能",
    #     severity="normal",
    #     order=20,
    #     smoke=True,
    #     tags=["组织切换管理", "模型OSS导入任务"]
    # )
    # def test_submit_org_switch_model_import_task_by_oss(self):
    #     """
    #     切换公司模型表-导入导出任务管理接口-通过OSS提交导入任务用例
    #     """
    #     try:
    #         # 调用通过OSS提交导入任务接口
    #         api_path = self.get_api_path("切换公司模型表-导入导出任务管理接口-通过OSS提交导入任务")
    #         params, url = self.get_api_params(api_path)

    #         # OSS导入任务需要复杂的文件上传和OSS配置，这里暂时跳过实现
    #         self.logger.info("OSS导入任务需要复杂的文件上传和OSS配置，暂时跳过")

    #     except Exception as e:
    #         a.text(str(e), "失败原因")
    #         raise
