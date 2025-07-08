import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("监控管理")
class TestMonitoringManagement(GenMdBaseTest):
    """监控管理测试类 - 监控方案和监控预警结果信息管理"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.monitoring_id = None
        cls.monitoring_code = None
        cls.logger.info("监控管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_monitoring_plan_info_md", "gen_monitoring_alert_result_md"]
            for table in tables:
                try:
                    cls.db.delete(table=table, where="code like %s", params=["AT_%"])
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 监控管理 ================
    @case_decorator(
        story="监控管理",
        title="测试新增监控管理",
        description="验证新增监控管理功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["监控管理", "新增"]
    )
    def test_save_monitoring(self):
        """新增监控管理用例"""
        try:
            monitoring_code = self.mock_data.generate_unique_code(tag="Monitoring")
            monitoring_name = f"监控管理_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-监控方案-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["monitoring_code", "monitoring_name"], ["params", "request"]
            )
            set_dict = {"monitoring_code": monitoring_code, "monitoring_name": monitoring_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.monitoring_id = response.get("data", {}).get("data", {})
            self.monitoring_code = monitoring_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控管理",
        title="测试查询监控管理列表",
        description="验证监控管理列表查询功能",
        severity="normal",
        order=2,
        smoke=True,
        tags=["监控管理", "查询"]
    )
    def test_query_monitoring_list(self):
        """查询监控管理列表用例"""
        try:
            api_path = self.get_api_path("GEN-监控预警结果信息-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "monitoring_code", "type": "TEXT"},
                    {"name": "monitoring_name", "type": "TEXT"}
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
        story="监控管理",
        title="测试查询监控管理详情",
        description="验证监控管理详情查询功能",
        severity="normal",
        order=3,
        smoke=True,
        tags=["监控管理", "查询"]
    )
    def test_query_monitoring_detail(self):
        """查询监控管理详情用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            api_path = self.get_api_path("GEN-监控方案-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.monitoring_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控管理",
        title="测试删除监控管理",
        description="验证删除监控管理功能",
        severity="normal",
        order=4,
        smoke=True,
        tags=["监控管理", "删除"]
    )
    def test_delete_monitoring(self):
        """删除监控管理用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            api_path = self.get_api_path("GEN-监控预警结果信息-批量删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.monitoring_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控方案分页查询服务 ================
    @case_decorator(
        story="监控方案管理",
        title="测试监控方案查询分页服务",
        description="验证监控方案-查询分页服务功能",
        severity="normal",
        order=5,
        tags=["监控方案管理", "查询", "GEN_MONITORING_PLAN_INFO_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_monitoring_plan_page(self):
        """监控方案查询分页服务用例"""
        try:
            api_path = self.get_api_path("GEN-监控方案-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "plan_code", "type": "TEXT"},
                    {"name": "plan_name", "type": "TEXT"}
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
        story="监控方案管理",
        title="测试监控方案启用服务",
        description="验证监控方案-启用服务功能",
        severity="normal",
        order=6,
        tags=["监控方案管理", "启用", "GEN_MONITORING_PLAN_INFO_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_monitoring_plan(self):
        """监控方案启用服务用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            api_path = self.get_api_path("GEN-监控方案-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.monitoring_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控方案管理",
        title="测试监控方案删除服务",
        description="验证监控方案-删除服务功能",
        severity="normal",
        order=7,
        tags=["监控方案管理", "删除", "GEN_MONITORING_PLAN_INFO_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_monitoring_plan(self):
        """监控方案删除服务用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            api_path = self.get_api_path("GEN-监控方案-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.monitoring_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控预警结果信息管理 ================
    @case_decorator(
        story="监控预警结果管理",
        title="测试监控预警结果信息保存服务",
        description="验证监控预警结果信息-保存服务功能",
        severity="normal",
        order=8,
        tags=["监控预警结果管理", "保存", "GEN_MONITORING_ALERT_RESULT_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_monitoring_alert_result(self):
        """监控预警结果信息保存服务用例"""
        try:
            alert_code = self.mock_data.generate_unique_code(tag="AlertResult")
            alert_name = f"监控预警结果_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-监控预警结果信息-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["alert_code", "alert_name"], ["params", "request"]
            )
            set_dict = {"alert_code": alert_code, "alert_name": alert_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果管理",
        title="测试监控预警结果信息查询详情服务",
        description="验证监控预警结果信息-查询详情服务功能",
        severity="normal",
        order=9,
        tags=["监控预警结果管理", "查询", "GEN_MONITORING_ALERT_RESULT_MD_DETAIL_ACTION_SERVICE"]
    )
    def test_query_monitoring_alert_result_detail(self):
        """监控预警结果信息查询详情服务用例"""
        try:
            # 使用已有的监控ID作为测试数据
            if not self.monitoring_id:
                self.test_save_monitoring()

            api_path = self.get_api_path("GEN-监控预警结果信息-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.monitoring_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="监控预警结果管理",
        title="测试监控预警结果信息删除服务",
        description="验证监控预警结果信息-删除服务功能",
        severity="normal",
        order=10,
        tags=["监控预警结果管理", "删除", "GEN_MONITORING_ALERT_RESULT_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_monitoring_alert_result(self):
        """监控预警结果信息删除服务用例"""
        try:
            if not self.monitoring_id:
                self.test_save_monitoring()

            api_path = self.get_api_path("GEN-监控预警结果信息-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.monitoring_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控方案导入导出管理 ================
    @case_decorator(
        story="监控方案导入导出管理",
        title="测试监控方案标准导入服务",
        description="验证监控方案标准导入服务功能",
        severity="normal",
        order=11,
        tags=["监控方案管理", "导入", "GEN_MONITORING_PLAN_INFO_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_import(self):
        """监控方案标准导入服务用例"""
        try:
            api_path = self.get_api_path("监控方案标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "plan_code": self.mock_data.generate_unique_code(tag="IMPORT_PLAN"),
                    "plan_name": f"导入测试监控方案_{self.mock_data.get_timestamp()}"
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
        story="监控方案导入导出管理",
        title="测试监控方案标准导出服务",
        description="验证监控方案标准导出服务功能",
        severity="normal",
        order=12,
        tags=["监控方案管理", "导出", "GEN_MONITORING_PLAN_INFO_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_export(self):
        """监控方案标准导出服务用例"""
        try:
            api_path = self.get_api_path("监控方案标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "plan_code", "type": "TEXT"},
                    {"name": "plan_name", "type": "TEXT"}
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

    # ================ 监控预警结果信息导入导出管理 ================
    @case_decorator(
        story="监控预警结果导入导出管理",
        title="测试监控预警结果信息标准导入服务",
        description="验证监控预警结果信息标准导入服务功能",
        severity="normal",
        order=13,
        tags=["监控预警结果管理", "导入", "GEN_MONITORING_ALERT_RESULT_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_import(self):
        """监控预警结果信息标准导入服务用例"""
        try:
            api_path = self.get_api_path("监控预警结果信息标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "alert_code": self.mock_data.generate_unique_code(tag="IMPORT_ALERT"),
                    "alert_name": f"导入测试监控预警结果_{self.mock_data.get_timestamp()}"
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
        story="监控预警结果导入导出管理",
        title="测试监控预警结果信息标准导出服务",
        description="验证监控预警结果信息标准导出服务功能",
        severity="normal",
        order=14,
        tags=["监控预警结果管理", "导出", "GEN_MONITORING_ALERT_RESULT_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_export(self):
        """监控预警结果信息标准导出服务用例"""
        try:
            api_path = self.get_api_path("监控预警结果信息标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "alert_code", "type": "TEXT"},
                    {"name": "alert_name", "type": "TEXT"}
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

    # ================ 监控方案任务管理接口 ================
    @case_decorator(
        story="监控方案任务管理",
        title="测试监控方案OSS导入任务",
        description="验证监控方案-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=15,
        tags=["监控方案管理", "任务管理", "GEN_MONITORING_PLAN_INFO_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_oss_import_task(self):
        """监控方案OSS导入任务用例"""
        try:
            api_path = self.get_api_path("监控方案-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ossPath", "taskName"], ["params", "request"]
            )
            set_dict = {
                "ossPath": "/test/monitoring_plan_import.xlsx",
                "taskName": f"监控方案导入任务_{self.mock_data.get_timestamp()}"
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
        story="监控方案任务管理",
        title="测试监控方案导出任务",
        description="验证监控方案-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=16,
        tags=["监控方案管理", "任务管理", "GEN_MONITORING_PLAN_INFO_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_plan_export_task(self):
        """监控方案导出任务用例"""
        try:
            api_path = self.get_api_path("监控方案-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["exportConfig", "taskName"], ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fields": [
                        {"name": "plan_code", "type": "TEXT"},
                        {"name": "plan_name", "type": "TEXT"}
                    ],
                    "condition": {}
                },
                "taskName": f"监控方案导出任务_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 监控预警结果信息任务管理接口 ================
    @case_decorator(
        story="监控预警结果任务管理",
        title="测试监控预警结果信息OSS导入任务",
        description="验证监控预警结果信息-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=17,
        tags=["监控预警结果管理", "任务管理", "GEN_MONITORING_ALERT_RESULT_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_oss_import_task(self):
        """监控预警结果信息OSS导入任务用例"""
        try:
            api_path = self.get_api_path("监控预警结果信息-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ossPath", "taskName"], ["params", "request"]
            )
            set_dict = {
                "ossPath": "/test/monitoring_alert_result_import.xlsx",
                "taskName": f"监控预警结果导入任务_{self.mock_data.get_timestamp()}"
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
        story="监控预警结果任务管理",
        title="测试监控预警结果信息导出任务",
        description="验证监控预警结果信息-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=18,
        tags=["监控预警结果管理", "任务管理", "GEN_MONITORING_ALERT_RESULT_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_monitoring_alert_result_export_task(self):
        """监控预警结果信息导出任务用例"""
        try:
            api_path = self.get_api_path("监控预警结果信息-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["exportConfig", "taskName"], ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fields": [
                        {"name": "alert_code", "type": "TEXT"},
                        {"name": "alert_name", "type": "TEXT"}
                    ],
                    "condition": {}
                },
                "taskName": f"监控预警结果导出任务_{self.mock_data.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
