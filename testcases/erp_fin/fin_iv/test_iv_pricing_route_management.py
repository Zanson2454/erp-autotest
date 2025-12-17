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
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货计价路由")
class TestIvPricingRouteManagement(FinBaseTest):
    """存货计价路由测试类"""
    
    pricing_route_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.pricing_route_id = None
        cls.logger.info("存货计价路由测试类初始化完成")
        # 初始化MD数据（从md_cache_data获取主数据）
        if cls.md_cache_data:
            gr_come_org_info = cls.md_cache_data.get("org_info", {}).get("gr_come_org_info", [])
            cls.com_org_id = gr_come_org_info[0].get("id") if gr_come_org_info else None
            inv_org_info = cls.md_cache_data.get("org_info", {}).get("inv_org_info", [])
            cls.inv_org_id = inv_org_info[0].get("id") if inv_org_info else None
    
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
        file_level_order=1,
        tags=["iv", "pricing", "route", "paging"]
    )
    def test_paging_pricing_route(self):
        """测试分页查询计价路由"""
        try:
            # 使用标准化API调用
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            fields_to_filter = ["pageable"]
            
            response, _ = self.standard_api_call(
                api_key="计价路由分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试保存计价路由",
        description="验证保存存货计价路由功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["iv", "pricing", "route", "save"]
    )
    def test_save_pricing_route(self):
        """测试保存计价路由"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 准备测试数据
            route_code = self.mock_util.generate_unique_code(tag="IV_ROUTE")
            route_name = f"计价路由_{self.mock_util.get_timestamp()}"
            
            # 使用标准化API调用
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": route_code,
                "name": route_name,
                "routeType": "DIRECT",
                "path": "/pricing/calculate",
                "priority": 1
            }
            fields_to_filter = ["comOrgId", "code", "name", "routeType", "path", "priority"]
            
            response, extracted_id = self.standard_api_call(
                api_key="保存计价路由数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="pricing_route"  # 自动存储为 self.pricing_route_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试根据ID查找计价路由",
        description="验证根据ID查找存货计价路由功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "pricing", "route", "find"]
    )
    def test_find_pricing_route_by_id(self):
        """测试根据ID查找计价路由"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_save_pricing_route()
            
            # 使用标准化API调用
            set_dict = {"id": self.pricing_route_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="根据ID查找计价路由数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            route_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(route_data.get("id"), "=", self.pricing_route_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试批量删除计价路由",
        description="验证批量删除存货计价路由功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "pricing", "route", "batch_delete"]
    )
    def test_batch_delete_pricing_route(self):
        """测试批量删除计价路由"""
        try:
            # 先创建多个记录用于批量删除
            route_ids = []
            for _ in range(2):
                # 保存记录并收集ID
                route_code = self.mock_util.generate_unique_code(tag="IV_ROUTE")
                route_name = f"计价路由_{self.mock_util.get_timestamp()}"
                set_dict = {
                    "comOrgId": self.com_org_id,
                    "code": route_code,
                    "name": route_name,
                    "routeType": "DIRECT",
                    "path": "/pricing/calculate",
                    "priority": 1
                }
                fields_to_filter = ["comOrgId", "code", "name", "routeType", "path", "priority"]
                response, extracted_id = self.standard_api_call(
                    api_key="保存计价路由数据服务",
                    set_dict=set_dict,
                    fields_to_filter=fields_to_filter,
                    store_id_as=None
                )
                self.assert_util.assert_response_data(response)
                if extracted_id:
                    route_ids.append(extracted_id)
            
            if not route_ids:
                raise ValueError("未创建到测试数据，无法进行批量删除测试")
            
            # 使用标准化API调用
            set_dict = {"ids": route_ids}
            fields_to_filter = ["ids"]
            
            response, _ = self.standard_api_call(
                api_key="批量删除计价路由数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试复制数据转换",
        description="验证存货计价路由复制数据转换功能",
        severity="normal",
        file_level_order=5,
        tags=["iv", "pricing", "route", "copy"]
    )
    def test_copy_data_converter_route(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_save_pricing_route()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.pricing_route_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="计价路由复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
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
        file_level_order=7,
        tags=["iv", "pricing", "route", "export", "standard"]
    )
    def test_standard_export_route(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_save_pricing_route()
            
            # 使用标准化API调用
            set_dict = {
                "routeIds": [self.pricing_route_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["routeIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="计价路由标准导出服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
