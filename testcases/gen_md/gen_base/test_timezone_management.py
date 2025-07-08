import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator



@allure.epic("通用基础数据")
@allure.feature("时区管理")
class TestTimezoneManagement(GenMdBaseTest):
    """时区管理测试类 - 覆盖所有时区配置相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        # 数据存储
        cls.timezone_id = None
        cls.timezone_code = None

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            tables = ["gen_timezone_type_cf"]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="timezone_code like %s",
                        params=["AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 时区配置基础管理 ================
    @case_decorator(
        story="时区配置管理",
        title="测试新增时区配置",
        description="验证GEN-时区配置-保存服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["时区管理", "新增", "GEN_TIMEZONE_TYPE_CF_SAVE_ACTION_SERVICE"]
    )
    def test_save_timezone(self):
        """新增时区配置用例 - GEN_TIMEZONE_TYPE_CF_SAVE_ACTION_SERVICE"""
        try:
            timezone_code = self.mock_data.generate_unique_code(tag="TZ")
            timezone_name = f"测试时区_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-时区配置-保存服务")
            params, url = self.get_api_params(api_path)

            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "offset", "description"], ["params", "request"]
            )
            set_dict = {
                "code": timezone_code,
                "name": timezone_name,
                "offset": "+08:00",  # 东八区
                "description": f"测试时区描述_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.timezone_id = response.get("data", {}).get("data", {})
            self.timezone_code = timezone_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试查询时区配置分页列表",
        description="验证GEN-时区配置-查询分页服务功能",
        severity="normal",
        order=2,
        tags=["时区管理", "查询", "GEN_TIMEZONE_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_timezone_page(self):
        """查询时区配置分页列表用例 - GEN_TIMEZONE_TYPE_CF_QUERY_PAGE_ACTION_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-时区配置-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "offset", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
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
        story="时区配置管理",
        title="测试查询时区配置详情",
        description="验证GEN-时区配置-查询详情服务功能",
        severity="normal",
        order=3,
        tags=["时区管理", "查询", "GEN_TIMEZONE_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_timezone_detail(self):
        """查询时区配置详情用例 - GEN_TIMEZONE_TYPE_CF_QUERY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            api_path = self.get_api_path("GEN-时区配置-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.timezone_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的详情数据包含必要字段
            detail_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(detail_data.get("code"), "not_empty")
            self.assert_util.assert_by_operator(detail_data.get("name"), "not_empty")
            self.assert_util.assert_by_operator(detail_data.get("offset"), "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置管理",
        title="测试删除时区配置",
        description="验证GEN-时区配置-删除服务功能",
        severity="normal",
        order=4,
        tags=["时区管理", "删除", "GEN_TIMEZONE_TYPE_CF_DELETE_ACTION_SERVICE"]
    )
    def test_delete_timezone(self):
        """删除时区配置用例 - GEN_TIMEZONE_TYPE_CF_DELETE_ACTION_SERVICE"""
        try:
            if not self.timezone_id:
                self.test_save_timezone()

            api_path = self.get_api_path("GEN-时区配置-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.timezone_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

            # 重置ID，避免后续测试使用已删除的数据
            self.timezone_id = None

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 时区配置导入导出管理 ================
    @case_decorator(
        story="时区配置导入导出管理",
        title="测试时区配置标准导入",
        description="验证时区配置标准导入服务功能",
        severity="normal",
        order=5,
        tags=["时区管理", "导入", "GEN_TIMEZONE_TYPE_CF_GEI_IMPORT_SERVICE"]
    )
    def test_timezone_import(self):
        """时区配置标准导入用例 - GEN_TIMEZONE_TYPE_CF_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("时区配置标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_data.generate_unique_code(tag="IMPORT_TZ"),
                    "name": f"导入测试时区_{self.mock_data.get_timestamp()}",
                    "offset": "+09:00",  # 东九区
                    "description": "导入的时区配置"
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
        story="时区配置导入导出管理",
        title="测试时区配置标准导出",
        description="验证时区配置标准导出服务功能",
        severity="normal",
        order=6,
        tags=["时区管理", "导出", "GEN_TIMEZONE_TYPE_CF_GEI_EXPORT_SERVICE"]
    )
    def test_timezone_export(self):
        """时区配置标准导出用例 - GEN_TIMEZONE_TYPE_CF_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("时区配置标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "offset", "type": "TEXT"},
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
        story="时区配置导入导出管理",
        title="测试时区配置OSS导入任务",
        description="验证时区配置-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=7,
        tags=["时区管理", "导入", "GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    def test_timezone_oss_import_task(self):
        """时区配置OSS导入任务用例 - GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("时区配置-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_timezone_import_file.xlsx",
                "taskName": f"时区配置导入任务_{self.mock_data.get_timestamp()}",
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
        story="时区配置导入导出管理",
        title="测试时区配置导出任务",
        description="验证时区配置-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=8,
        tags=["时区管理", "导出", "GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    def test_timezone_export_task(self):
        """时区配置导出任务用例 - GEN_TIMEZONE_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("时区配置-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "queryData"], ["params", "request"]
            )
            set_dict = {
                "taskName": f"时区配置导出任务_{self.mock_data.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "offset", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
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

    # ================ 时区配置业务场景测试 ================
    @case_decorator(
        story="时区配置业务场景",
        title="测试时区配置边界值验证",
        description="验证时区偏移量的边界值处理",
        severity="normal",
        order=9,
        tags=["时区管理", "边界值测试", "业务验证"]
    )
    def test_timezone_boundary_values(self):
        """时区配置边界值测试用例"""
        try:
            # 测试不同的时区偏移量
            boundary_test_cases = [
                {
                    "code": self.mock_data.generate_unique_code(tag="TZ_MIN"),
                    "name": "最小时区偏移",
                    "offset": "-12:00",  # 最小时区偏移
                    "description": "西十二区"
                },
                {
                    "code": self.mock_data.generate_unique_code(tag="TZ_MAX"),
                    "name": "最大时区偏移",
                    "offset": "+14:00",  # 最大时区偏移
                    "description": "东十四区"
                },
                {
                    "code": self.mock_data.generate_unique_code(tag="TZ_UTC"),
                    "name": "UTC时区",
                    "offset": "+00:00",  # UTC时区
                    "description": "世界协调时"
                }
            ]

            api_path = self.get_api_path("GEN-时区配置-保存服务")
            params, url = self.get_api_params(api_path)

            created_ids = []
            
            for test_case in boundary_test_cases:
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["code", "name", "offset", "description"], ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, test_case)

                response = self.http.post(url, json=filtered_params)
                self.assert_util.assert_response_data(response)
                
                created_id = response.get("data", {}).get("data", {})
                created_ids.append(created_id)

            # 清理测试数据
            if created_ids:
                delete_api_path = self.get_api_path("GEN-时区配置-删除服务")
                delete_params, delete_url = self.get_api_params(delete_api_path)
                
                delete_filtered_params = ParamUtil.filter_post_body_fields(
                    delete_params, ["ids"], ["params", "request"]
                )
                ParamUtil.set_request_params(delete_filtered_params, {"ids": created_ids})

                delete_response = self.http.post(delete_url, json=delete_filtered_params)
                self.assert_util.assert_response_data(delete_response)

            a.json({"test_cases": len(boundary_test_cases)}, "边界值测试完成")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="时区配置综合测试",
        title="测试时区配置完整流程",
        description="验证时区配置从创建到删除的完整业务流程",
        severity="critical",
        order=10,
        tags=["时区管理", "综合测试", "业务流程"]
    )
    def test_timezone_complete_workflow(self):
        """时区配置完整流程测试用例"""
        try:
            # 1. 创建时区配置
            timezone_code = self.mock_data.generate_unique_code(tag="WORKFLOW_TZ")
            timezone_name = f"流程测试时区_{self.mock_data.get_timestamp()}"

            # 创建
            api_path = self.get_api_path("GEN-时区配置-保存服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "offset", "description"], ["params", "request"]
            )
            set_dict = {
                "code": timezone_code,
                "name": timezone_name,
                "offset": "+07:00",  # 东七区
                "description": f"流程测试时区描述_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            create_response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(create_response)
            
            workflow_timezone_id = create_response.get("data", {}).get("data", {})
            
            # 2. 查询详情验证
            detail_api_path = self.get_api_path("GEN-时区配置-查询详情服务")
            detail_params, detail_url = self.get_api_params(detail_api_path)
            
            detail_filtered_params = ParamUtil.filter_post_body_fields(
                detail_params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(detail_filtered_params, {"id": workflow_timezone_id})

            detail_response = self.http.post(detail_url, json=detail_filtered_params)
            self.assert_util.assert_response_data(detail_response)
            
            detail_data = detail_response.get("data", {}).get("data", {})
            assert detail_data.get("code") == timezone_code, "时区代码不匹配"
            assert detail_data.get("name") == timezone_name, "时区名称不匹配"
            assert detail_data.get("offset") == "+07:00", "时区偏移量不匹配"

            # 3. 更新时区配置（修改描述）
            update_description = f"更新后的时区描述_{self.mock_data.get_timestamp()}"
            update_filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "code", "name", "offset", "description"], ["params", "request"]
            )
            update_set_dict = {
                "id": workflow_timezone_id,
                "code": timezone_code,
                "name": timezone_name,
                "offset": "+07:00",
                "description": update_description
            }
            ParamUtil.set_request_params(update_filtered_params, update_set_dict)

            update_response = self.http.post(url, json=update_filtered_params)
            self.assert_util.assert_response_data(update_response)

            # 4. 删除验证
            delete_api_path = self.get_api_path("GEN-时区配置-删除服务")
            delete_params, delete_url = self.get_api_params(delete_api_path)
            
            delete_filtered_params = ParamUtil.filter_post_body_fields(
                delete_params, ["ids"], ["params", "request"]
            )
            ParamUtil.set_request_params(delete_filtered_params, {"ids": [workflow_timezone_id]})

            delete_response = self.http.post(delete_url, json=delete_filtered_params)
            self.assert_util.assert_response_data(delete_response)

            a.json({"workflow": "complete"}, "完整流程执行成功")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise 