# -*- coding: utf-8 -*-
"""
存货计价路由测试用例
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin import FinBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("存货计价路由")
class TestIvPricingRouteManagement(FinBaseTest):
    """存货计价路由测试类"""
    
    pricing_route_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.pricing_route_id = None
        cls.logger.info("存货计价路由测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_route_cf",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货计价路由",
        title="测试分页查询计价路由",
        description="验证存货计价路由分页查询功能",
        severity="normal",
        order=1,
        tags=["iv", "pricing", "route", "paging"]
    )
    def test_paging_pricing_route(self):
        """测试分页查询计价路由"""
        try:
            api_path = self.get_api_path("计价路由分页数据服务")
            params, url = self.get_api_params(api_path)
            
            pageable = {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": None
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"pageable": pageable})
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            a.json(response, "分页查询响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试保存计价路由",
        description="验证保存存货计价路由功能",
        severity="critical",
        order=2,
        smoke=True,
        tags=["iv", "pricing", "route", "save"]
    )
    def test_save_pricing_route(self):
        """测试保存计价路由"""
        try:
            route_code = self.mock_util.generate_unique_code(tag="IV_ROUTE")
            route_name = f"计价路由_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("保存计价路由数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "routeType", "path"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": route_code,
                "name": route_name,
                "routeType": "DIRECT",  # 示例类型：直接路由
                "path": "/pricing/calculate",
                "priority": 1
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.pricing_route_id = response.get("data", {}).get("data", {}).get("id")
            assert self.pricing_route_id, "保存计价路由失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试根据ID查找计价路由",
        description="验证根据ID查找存货计价路由功能",
        severity="normal",
        order=3,
        tags=["iv", "pricing", "route", "find"]
    )
    def test_find_pricing_route_by_id(self):
        """测试根据ID查找计价路由"""
        try:
            if not self.pricing_route_id:
                self.test_save_pricing_route()
            
            api_path = self.get_api_path("根据ID查找计价路由数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.pricing_route_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            route_data = response.get("data", {}).get("data", {})
            assert route_data.get("id") == self.pricing_route_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试批量删除计价路由",
        description="验证批量删除存货计价路由功能",
        severity="normal",
        order=4,
        tags=["iv", "pricing", "route", "batch_delete"]
    )
    def test_batch_delete_pricing_route(self):
        """测试批量删除计价路由"""
        try:
            route_ids = [self.pricing_route_id] if self.pricing_route_id else []
            # 创建额外路由用于批量
            self.test_save_pricing_route()
            route_ids.append(self.pricing_route_id)
            
            api_path = self.get_api_path("批量删除计价路由数据服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": route_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "批量删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试复制数据转换",
        description="验证存货计价路由复制数据转换功能",
        severity="normal",
        order=5,
        tags=["iv", "pricing", "route", "copy"]
    )
    def test_copy_data_converter_route(self):
        """测试复制数据转换"""
        try:
            if not self.pricing_route_id:
                self.test_save_pricing_route()
            
            api_path = self.get_api_path("计价路由复制数据转换服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.pricing_route_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货计价路由",
        title="测试导入导出任务提交",
        description="验证存货计价路由导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        order=6,
        tags=["iv", "pricing", "route", "export", "task"]
    )
    def test_export_direct_post_route(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_PRICING_ROUTE_{timestamp}_EXPORT"
            
            export_params = {
                "serviceKey": "FIN_IV_ROUTE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_route_cf",
                            "modelName": "存货计价路由",
                            "sheetNo": 0,
                            "sheetName": "路由数据",
                            "headerConfigList": [
                                {"name": "路由编码", "type": "TEXT", "field": "code"},
                                {"name": "路由类型", "type": "TEXT", "field": "routeType"},
                                {"name": "路径", "type": "TEXT", "field": "path"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_route_cf",
                        "viewKey": "ERP_FIN$fin_iv_route_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_route_cf",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "routeType"},
                                {"field": "path"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_route_cf"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_route_cf",
                        "modelName": "存货计价路由",
                        "containerKey": "ERP_FIN$fin_iv_route_cf",
                        "viewKey": "ERP_FIN$fin_iv_route_cf:list",
                        "sceneKey": "ERP_FIN$fin_iv_route_cf"
                    }
                }
            }
            
            api_path = self.get_api_path("FIN_IV_ROUTE_CF_API_GEI_TASK_EXPORT_DIRECT_POST")
            params, url = self.get_api_params(api_path)
            
            filtered_params = export_params
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试标准导出服务",
        description="验证存货计价路由标准导出服务功能",
        severity="minor",
        order=7,
        tags=["iv", "pricing", "route", "export", "standard"]
    )
    def test_standard_export_route(self):
        """测试标准导出服务"""
        try:
            if not self.pricing_route_id:
                self.test_save_pricing_route()
            
            api_path = self.get_api_path("计价路由标准导出服务")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "routeIds": [self.pricing_route_id],
                "exportType": "EXCEL"
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(export_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, export_data)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "标准导出响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
