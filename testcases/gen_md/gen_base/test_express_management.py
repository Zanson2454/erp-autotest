import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
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
        # 数据存储
        cls.express_id = None
        cls.express_code = None
        cls.logger.info("快递公司管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="gen_express_com_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 快递公司基础管理 ================
    @case_decorator(
        story="快递公司管理",
        title="测试新增快递公司",
        description="验证GEN-快递公司-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["快递公司", "新增", "GEN_EXPRESS_COM_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_express_company(self):
        """新增快递公司用例 - GEN_EXPRESS_COM_MD_SAVE_ACTION_SERVICE"""
        try:
            express_code = self.mock_util.generate_unique_code(tag="EXPRESS")
            express_name = f"测试快递公司_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-快递公司-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "description"], ["params", "request"]
            )
            set_dict = {
                "code": express_code,
                "name": express_name,
                "contactName": self.mock_util.get_mock_name(),
                "contactPhone": self.mock_util.get_mock_phone_number(),
                "deliveryEnabled": True,
                "desc": f"测试快递公司描述_{self.mock_util.get_timestamp()}",
                "servTypeList":[
                    {
                        "servType": "测试业务类型",
                        "comId": None
                    }
                ],
                "netInfoList":[
                    { 
                        "checkMan": self.mock_util.get_mock_name(),
                        "childTempId": "2",
                        "code": express_code,
                        "comId": None,
                        "net": f"网点名称_{self.mock_util.get_timestamp()}",
                        "partnerId": f"account_{self.mock_util.get_timestamp()}",
                        "partnerKey": f"key_{self.mock_util.get_timestamp()}",
                        "partnerName": f"partner_{self.mock_util.get_timestamp()}",
                        "partnerSecret": f"secret_{self.mock_util.get_timestamp()}",
                        "payType": "MONTHLY",
                        "printType": "NON",
                        "tempId": "1"
                    }
                ],
                "status": "DRAFT",
                "type": "INNER"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.express_id = response.get("data", {}).get("data", {})
            self.express_code = express_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试查询快递公司详情",
        description="验证GEN-快递公司-查询详情服务功能",
        severity="critical",
        order=2,
        tags=["快递公司", "查询", "GEN_EXPRESS_COM_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_express_detail(self):
        """查询快递公司详情用例 - GEN_EXPRESS_COM_MD_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.express_id:
                self.test_save_express_company()

            api_path = self.get_api_path("GEN-快递公司-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.express_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试查询快递公司分页",
        description="验证GEN-快递公司-查询分页服务功能",
        severity="critical",
        order=3,
        tags=["快递公司", "分页查询", "GEN_EXPRESS_COM_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_express_page(self):
        """查询快递公司分页用例 - GEN_EXPRESS_COM_MD_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-快递公司-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
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
                    {"name": "name", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试启用快递公司",
        description="验证GEN-快递公司-启用服务功能",
        severity="normal",
        order=4,
        tags=["快递公司", "启用", "GEN_EXPRESS_COM_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_express_company(self):
        """启用快递公司用例 - GEN_EXPRESS_COM_MD_ENABLED_ACTION_SERVICE"""
        try:
            if not self.express_id:
                self.test_save_express_company()

            api_path = self.get_api_path("GEN-快递公司-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.express_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试禁用快递公司",
        description="验证GEN-快递公司-禁用服务功能",
        severity="normal",
        order=5,
        tags=["快递公司", "禁用", "GEN_EXPRESS_COM_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_express_company(self):
        """禁用快递公司用例 - GEN_EXPRESS_COM_MD_DISABLED_ACTION_SERVICE"""
        try:
            if not self.express_id:
                self.test_save_express_company()

            api_path = self.get_api_path("GEN-快递公司-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.express_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试标准导入快递公司",
        description="验证快递公司标准导入服务功能",
        severity="normal",
        order=6,
        tags=["快递公司", "导入", "GEN_EXPRESS_COM_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_import_express_company(self):
        """标准导入快递公司用例 - GEN_EXPRESS_COM_MD_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("快递公司标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_EXPRESS"),
                    "name": f"导入测试快递公司_{self.mock_util.get_timestamp()}",
                    "description": "导入测试快递公司描述"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sliceData"], ["params", "request"]
            )
            set_dict = {"sliceData": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试标准导出快递公司",
        description="验证快递公司标准导出服务功能",
        severity="normal",
        order=7,
        tags=["快递公司", "导出", "GEN_EXPRESS_COM_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导出需要复杂配置，暂时跳过")
    def test_export_express_company(self):
        """标准导出快递公司用例 - GEN_EXPRESS_COM_MD_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("快递公司标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司任务管理",
        title="测试快递公司导出任务",
        description="验证快递公司-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=8,
        tags=["快递公司", "任务管理", "GEN_EXPRESS_COM_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="任务管理接口配置复杂，暂时跳过")
    def test_express_export_task(self):
        """快递公司导出任务用例 - GEN_EXPRESS_COM_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("快递公司-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            # 构造导出任务参数
            params = {
                "serviceKey": "GEN_EXPRESS_COM_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": f"快递公司_{self.nickname}_{self.mock_util.get_timestamp()}_导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_express_com_md",
                            "modelName": "快递公司",
                            "sheetNo": 0,
                            "sheetName": "快递公司",
                            "headerConfigList": [
                                {
                                    "name": "编码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "名称",
                                    "type": "TEXT",
                                    "field": "name"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$gen_express_com_md",
                        "viewKey": "GEN_MD$gen_express_com_md:list",
                        "sceneKey": "GEN_MD$gen_express_com_md",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"}
                            ],
                            "modelKey": "GEN_MD$gen_express_com_md"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_express_com_md",
                        "modelName": "快递公司",
                        "containerKey": "GEN_MD$gen_express_com_md",
                        "viewKey": "GEN_MD$gen_express_com_md:list",
                        "sceneKey": "GEN_MD$gen_express_com_md"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司任务管理",
        title="测试快递公司OSS导入任务",
        description="验证快递公司-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=9,
        tags=["快递公司", "任务管理", "GEN_EXPRESS_COM_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_express_oss_import_task(self):
        """快递公司OSS导入任务用例 - GEN_EXPRESS_COM_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("快递公司-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 构造OSS导入任务参数
            params = {
                "serviceKey": "GEN_EXPRESS_COM_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "teamId": 22,
                "params": {
                    "taskName": f"快递公司_{self.nickname}_{self.mock_util.get_timestamp()}_OSS导入",
                    "fileKey": "test_express_import.xlsx",
                    "fileName": "快递公司导入模板.xlsx",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_express_com_md",
                            "modelName": "快递公司",
                            "sheetNo": 0,
                            "sheetName": "快递公司"
                        }
                    ],
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_express_com_md",
                        "modelName": "快递公司"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="快递公司管理",
        title="测试删除快递公司",
        description="验证GEN-快递公司-删除服务功能",
        severity="critical",
        order=10,
        tags=["快递公司", "删除", "GEN_EXPRESS_COM_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_express_company(self):
        """删除快递公司用例 - GEN_EXPRESS_COM_MD_DELETE_ACTION_SERVICE"""
        try:
            # 检查是否存在测试数据，如果不存在则创建
            if not self.express_id:
                self.test_save_express_company()

            # 删除快递公司
            api_path = self.get_api_path("GEN-快递公司-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.express_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
