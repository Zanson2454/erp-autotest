import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.mock_util import MockData
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("监控指标管理")
class TestMonitoringManagement(GenMdBaseTest):
    """监控指标管理测试类 - 整合监控管理、指标管理等功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.mock_data = MockData()
        cls.monitoring_id = None
        cls.monitoring_code = None
        cls.indicator_id = None
        cls.indicator_code = None
        cls.logger.info("监控指标管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            tables = ["gen_monitoring_md", "gen_indicator_md"]
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

    # ================ 指标管理 ================
    @case_decorator(
        story="指标管理",
        title="测试新增指标管理",
        description="验证新增指标管理功能",
        severity="blocker",
        order=5,
        smoke=True,
        tags=["指标管理", "新增"]
    )
    def test_save_indicator(self):
        """新增指标管理用例"""
        try:
            indicator_code = self.mock_data.generate_unique_code(tag="Indicator")
            indicator_name = f"指标管理_{self.mock_data.get_timestamp()}"

            api_path = self.get_api_path("GEN-指标中心-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["indicator_code", "indicator_name"], ["params", "request"]
            )
            set_dict = {"indicator_code": indicator_code, "indicator_name": indicator_name}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.indicator_id = response.get("data", {}).get("data", {})
            self.indicator_code = indicator_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标管理",
        title="测试查询指标管理列表",
        description="验证指标管理列表查询功能",
        severity="normal",
        order=6,
        tags=["指标管理", "查询"]
    )
    def test_query_indicator_list(self):
        """查询指标管理列表用例"""
        try:
            api_path = self.get_api_path("GEN-指标中心-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "indicator_code", "type": "TEXT"},
                    {"name": "indicator_name", "type": "TEXT"}
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
        story="指标管理",
        title="测试查询指标管理详情",
        description="验证指标管理详情查询功能",
        severity="normal",
        order=7,
        tags=["指标管理", "查询"]
    )
    def test_query_indicator_detail(self):
        """查询指标管理详情用例"""
        try:
            if not self.indicator_id:
                self.test_save_indicator()

            api_path = self.get_api_path("GEN-指标中心-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.indicator_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="指标管理",
        title="测试删除指标管理",
        description="验证删除指标管理功能",
        severity="normal",
        order=8,
        tags=["指标管理", "删除"]
    )
    def test_delete_indicator(self):
        """删除指标管理用例"""
        try:
            if not self.indicator_id:
                self.test_save_indicator()

            api_path = self.get_api_path("GEN-指标中心-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.indicator_id]}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
