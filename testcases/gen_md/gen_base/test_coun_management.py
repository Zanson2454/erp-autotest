import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("国家管理")
class TestCountryManagement(GenMdBaseTest):
    """国家管理测试类 - 覆盖所有国家配置相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 数据存储
        cls.country_id = None
        cls.country_code = None
        cls.logger.info("国家管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            tables = ["gen_coun_type_cf"]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="code like %s",
                        params=["AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 国家配置基础管理 ================
    @case_decorator(
        story="国家配置管理",
        title="测试新增国家配置",
        description="验证GEN-国家配置表-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["国家管理", "新增", "GEN_COUN_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_country(self):
        """新增国家配置用例 - GEN_COUN_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            country_code = self.mock_data.generate_unique_code(tag="COUN")
            country_name = f"测试国家_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-国家配置表-保存服务")
            params, url = self.get_api_params(api_path)

            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "engName", "isoCode"], ["params", "request"]
            )
            set_dict = {
                "code": country_code,
                "name": country_name,
                "engName": f"Test Country {self.mock_data.get_timestamp()}",
                "isoCode": country_code[:2].upper()  # ISO代码通常是2位
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.country_id = response.get("data", {}).get("data", {})
            self.country_code = country_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试查询国家配置分页列表",
        description="验证GEN-国家配置表-查询分页服务功能",
        severity="normal",
        order=2,
        tags=["国家管理", "查询", "GEN_COUN_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_country_page(self):
        """查询国家配置分页列表用例 - GEN_COUN_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-国家配置表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "engName", "type": "TEXT"},
                    {"name": "isoCode", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试查询国家配置详情",
        description="验证GEN-国家配置表-查询详情服务功能",
        severity="normal",
        order=3,
        tags=["国家管理", "查询", "GEN_COUN_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_country_detail(self):
        """查询国家配置详情用例 - GEN_COUN_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.country_id:
                self.test_save_country()

            api_path = self.get_api_path("GEN-国家配置表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.country_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的详情数据包含必要字段
            detail_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data.get("code"), "not_empty")
            self.assert_util.assert_by_operator(detail_data.get("name"), "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置管理",
        title="测试删除国家配置",
        description="验证GEN-国家配置表-删除服务功能",
        severity="normal",
        order=4,
        tags=["国家管理", "删除", "GEN_COUN_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_country(self):
        """删除国家配置用例 - GEN_COUN_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.country_id:
                self.test_save_country()

            api_path = self.get_api_path("GEN-国家配置表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.country_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

            # 重置ID，避免后续测试使用已删除的数据
            self.country_id = None

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 国家配置导入导出管理 ================
    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置标准导入",
        description="验证国家配置标准导入服务功能",
        severity="normal",
        order=5,
        tags=["国家管理", "导入", "GEN_COUN_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    def test_country_import(self):
        """国家配置标准导入用例 - GEN_COUN_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("国家配置标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_data.generate_unique_code(tag="IMPORT_COUN"),
                    "name": f"导入测试国家_{self.mock_data.get_timestamp()}",
                    "engName": f"Import Test Country {self.mock_data.get_timestamp()}",
                    "isoCode": "TC"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["data"], ["params", "request"]
            )
            set_dict = {"data": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="国家配置导入导出管理",
        title="测试国家配置标准导出",
        description="验证国家配置标准导出服务功能",
        severity="normal",
        order=6,
        tags=["国家管理", "导出", "GEN_COUN_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    def test_country_export(self):
        """国家配置标准导出用例 - GEN_COUN_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("国家配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "engName", "type": "TEXT"},
                    {"name": "isoCode", "type": "TEXT"}
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
        story="国家配置导入导出管理",
        title="测试国家配置OSS导入任务",
        description="验证国家配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=7,
        tags=["国家管理", "导入", "GEN_COUN_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_country_oss_import_task(self):
        """国家配置OSS导入任务用例 - GEN_COUN_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("国家配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_country_import_file.xlsx",
                "taskName": f"国家配置导入任务_{self.mock_data.get_timestamp()}",
                "templateId": 1
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
        story="国家配置导入导出管理",
        title="测试国家配置导出任务",
        description="验证国家配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=8,
        tags=["国家管理", "导出", "GEN_COUN_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_country_export_task(self):
        """国家配置导出任务用例 - GEN_COUN_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("国家配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "queryData"], ["params", "request"]
            )
            set_dict = {
                "taskName": f"国家配置导出任务_{self.mock_data.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "engName", "type": "TEXT"},
                        {"name": "isoCode", "type": "TEXT"}
                    ]
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 综合测试场景 ================
    @case_decorator(
        story="国家配置综合测试",
        title="测试国家配置完整流程",
        description="验证国家配置从创建到删除的完整业务流程",
        severity="critical",
        order=9,
        tags=["国家管理", "综合测试", "业务流程"]
    )
    def test_country_complete_workflow(self):
        """国家配置完整流程测试用例"""
        try:
            # 1. 创建国家配置
            country_code = self.mock_data.generate_unique_code(tag="WORKFLOW_COUN")
            country_name = f"流程测试国家_{self.mock_data.get_timestamp()}"

            # 创建
            api_path = self.get_api_path("GEN-国家配置表-保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "engName", "isoCode"], ["params", "request"]
            )
            set_dict = {
                "code": country_code,
                "name": country_name,
                "engName": f"Workflow Test Country {self.mock_data.get_timestamp()}",
                "isoCode": country_code[:2].upper()
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            create_response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(create_response)
            
            workflow_country_id = create_response.get("data", {}).get("data", {})
            
            # 2. 查询详情验证
            detail_api_path = self.get_api_path("GEN-国家配置表-查询详情服务")
            detail_params, detail_url = self.get_api_params(detail_api_path)
            
            detail_filtered_params = ParamUtil.filter_post_body_fields(
                detail_params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(detail_filtered_params, {"id": workflow_country_id})

            detail_response = self.http.post(detail_url, json=detail_filtered_params)
            self.assert_util.assert_response_data(detail_response)
            
            detail_data = detail_response.get("data", {}).get("data", {})
            assert detail_data.get("code") == country_code, "国家代码不匹配"
            assert detail_data.get("name") == country_name, "国家名称不匹配"

            # 3. 删除验证
            delete_api_path = self.get_api_path("GEN-国家配置表-删除服务")
            delete_params, delete_url = self.get_api_params(delete_api_path)
            
            delete_filtered_params = ParamUtil.filter_post_body_fields(
                delete_params, ["ids"], ["params", "request"]
            )
            ParamUtil.set_request_params(delete_filtered_params, {"ids": [workflow_country_id]})

            delete_response = self.http.post(delete_url, json=delete_filtered_params)
            self.assert_util.assert_response_data(delete_response)

            a.json({"workflow": "complete"}, "完整流程执行成功")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 