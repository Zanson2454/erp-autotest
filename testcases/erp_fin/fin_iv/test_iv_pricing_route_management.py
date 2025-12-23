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

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-存货价值")
@allure.feature("存货计价路由")
class TestIvPricingRouteManagement(IvBaseTest):
    """存货计价路由测试类"""
    
    pricing_route_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id
        cls.pricing_route_id = None
        cls.inv_mvn_code = None
        cls.inv_mvn_name = None
        cls.logger.info("存货计价路由测试类初始化完成")
        # 注意：com_org_id 和 inv_org_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
        
        # 从数据库查询移动类型数据（用于计价路由创建）
        try:
            sql = """
                SELECT code, name 
                FROM inv_mvn_type_cf 
                WHERE deleted = 0 
                AND enable_status = 'ENABLE'
                LIMIT 1
            """
            result = cls.db.query(sql)
            if result and len(result) > 0:
                cls.inv_mvn_code = result[0].get("code")
                cls.inv_mvn_name = result[0].get("name")
                cls.logger.info(f"获取到移动类型: code={cls.inv_mvn_code}, name={cls.inv_mvn_name}")
            else:
                # 如果查询不到，使用默认值（从 curl 请求中提取）
                cls.inv_mvn_code = "20301100"
                cls.inv_mvn_name = "销售-无正逆向-无参考单业务-非限制-非限制-常规业务"
                cls.logger.warning(f"未查询到移动类型，使用默认值: code={cls.inv_mvn_code}")
        except Exception as e:
            cls.logger.warning(f"查询移动类型失败: {str(e)}，使用默认值")
            cls.inv_mvn_code = "20301100"
            cls.inv_mvn_name = "销售-无正逆向-无参考单业务-非限制-非限制-常规业务"
    
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
            # 注意：需要添加 modelKey 参数（从 curl 请求中提取）
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {
                            "fieldAlias": "createdAt",
                            "id": "createdAt-0",
                            "sortType": "DESC"
                        }
                    ],
                    "conditionItems": None
                },
                "modelKey": "ERP_FIN$fin_iv_route_cf"
            }
            fields_to_filter = ["pageable", "modelKey"]
            
            response, _ = self.standard_api_call(
                api_key="存货计价路由-分页数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据结构
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty", "分页查询应返回数据列表")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试提交计价路由",
        description="验证提交存货计价路由功能（使用IV_ROUTE_SUBMIT_EVENT_SERVICE）",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["iv", "pricing", "route", "submit"]
    )
    def test_submit_pricing_route(self):
        """测试提交计价路由"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            
            # 检查依赖数据
            if not self.inv_mvn_code or not self.inv_mvn_name:
                raise ValueError("移动类型数据未初始化，请检查数据库或使用默认值")
            
            # 准备测试数据
            # 从 curl 请求中提取的字段：invMvnCode, invMvnName, ivType, priceStrategy, enableStatus
            # invMvnCode 和 invMvnName 从 setup_class 中获取（从数据库查询）
            inv_mvn_code = self.inv_mvn_code
            inv_mvn_name = self.inv_mvn_name
            
            # 构造公司组织对象（从 curl 看，comOrgId 是一个完整的对象，但测试中只需传递 id）
            # 后端会自动填充其他字段
            com_org_obj = {"id": self.com_org_id}
            
            # 使用标准化API调用
            # 根据 curl 请求，使用 IV-计价路由-数据提交服务
            set_dict = {
                "invMvnCode": inv_mvn_code,
                "invMvnName": inv_mvn_name,
                "comOrgId": com_org_obj,
                "ivType": "PERIOD_METHOD",  # 期间成本法
                "priceStrategy": "END_METHOD",  # 期末计价策略
                "enableStatus": "ENABLE",  # 启用状态
                "id": None,  # 新建时 id 为 None
                "createdBy": None,
                "updatedBy": None,
                "createdAt": None,
                "updatedAt": None,
                "version": 0,
                "deleted": 0,
                "originOrgId": 0
            }
            fields_to_filter = [
                "invMvnCode", "invMvnName", "comOrgId", "ivType", 
                "priceStrategy", "enableStatus", "id", "createdBy", 
                "updatedBy", "createdAt", "updatedAt", "version", 
                "deleted", "originOrgId"
            ]
            
            response, extracted_id = self.standard_api_call(
                api_key="IV-计价路由-数据提交服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="pricing_route"  # 自动存储为 self.pricing_route_id
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            route_data = response.get("data", {}).get("data", {})
            if route_data and route_data.get("id"):
                self.pricing_route_id = route_data.get("id")
                self.assert_util.assert_by_operator(
                    route_data.get("invMvnCode"), "=", inv_mvn_code,
                    "移动类型编码不匹配"
                )
                self.assert_util.assert_by_operator(
                    route_data.get("enableStatus"), "=", "ENABLE",
                    "启用状态应为ENABLE"
                )
            
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
                self.test_submit_pricing_route()
            
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
        title="测试启用计价路由",
        description="验证启用存货计价路由功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "pricing", "route", "enable"]
    )
    def test_enable_pricing_route(self):
        """测试启用计价路由"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_submit_pricing_route()
            
            # 先查询计价路由详情，获取完整数据（包括 ivRouteCode 等字段）
            response, _ = self.standard_api_call(
                api_key="存货计价路由-根据ID查找数据服务",
                set_dict={"id": self.pricing_route_id},
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_data(response)
            route_data = response.get("data", {}).get("data", {})
            
            # 获取当前状态
            current_status = route_data.get("enableStatus")
            
            # 如果已经是启用状态，先停用（确保可以测试启用功能）
            if current_status == "ENABLE":
                # 先停用
                disable_set_dict = {
                    "ivRouteCode": route_data.get("ivRouteCode") or route_data.get("code"),
                    "comOrgId": {"id": self.com_org_id},
                    "invMvnCode": route_data.get("invMvnCode") or self.inv_mvn_code,
                    "invMvnName": route_data.get("invMvnName") or self.inv_mvn_name,
                    "priceStrategy": route_data.get("priceStrategy") or "END_METHOD",
                    "enableStatus": "ENABLE",  # 当前状态
                    "ivType": route_data.get("ivType") or "PERIOD_METHOD",
                    "id": self.pricing_route_id,
                    "createdBy": route_data.get("createdBy"),
                    "updatedBy": route_data.get("updatedBy"),
                    "createdAt": route_data.get("createdAt"),
                    "updatedAt": route_data.get("updatedAt"),
                    "version": route_data.get("version", 0),
                    "deleted": route_data.get("deleted", 0),
                    "originOrgId": route_data.get("originOrgId", 0)
                }
                disable_fields = [
                    "ivRouteCode", "comOrgId", "invMvnCode", "invMvnName",
                    "priceStrategy", "enableStatus", "ivType", "id",
                    "createdBy", "updatedBy", "createdAt", "updatedAt",
                    "version", "deleted", "originOrgId"
                ]
                self.standard_api_call(
                    api_key="IV-计价路由-反启用服务",
                    set_dict=disable_set_dict,
                    fields_to_filter=disable_fields
                )
                # 重新查询获取最新数据
                response, _ = self.standard_api_call(
                    api_key="存货计价路由-根据ID查找数据服务",
                    set_dict={"id": self.pricing_route_id},
                    fields_to_filter=["id"]
                )
                self.assert_util.assert_response_data(response)
                route_data = response.get("data", {}).get("data", {})
            
            # 准备启用参数（从 curl 请求中提取的字段结构）
            # 启用接口需要传递当前状态（DISABLE），接口会将其改为 ENABLE
            set_dict = {
                "ivRouteCode": route_data.get("ivRouteCode") or route_data.get("code"),
                "comOrgId": {"id": self.com_org_id},  # 从 curl 看，comOrgId 是对象
                "invMvnCode": route_data.get("invMvnCode") or self.inv_mvn_code,
                "invMvnName": route_data.get("invMvnName") or self.inv_mvn_name,
                "priceStrategy": route_data.get("priceStrategy") or "END_METHOD",
                "enableStatus": route_data.get("enableStatus"),  # 使用当前状态（应该是 DISABLE）
                "ivType": route_data.get("ivType") or "PERIOD_METHOD",
                "id": self.pricing_route_id,
                "createdBy": route_data.get("createdBy"),
                "updatedBy": route_data.get("updatedBy"),
                "createdAt": route_data.get("createdAt"),
                "updatedAt": route_data.get("updatedAt"),
                "version": route_data.get("version", 0),
                "deleted": route_data.get("deleted", 0),
                "originOrgId": route_data.get("originOrgId", 0)
            }
            fields_to_filter = [
                "ivRouteCode", "comOrgId", "invMvnCode", "invMvnName",
                "priceStrategy", "enableStatus", "ivType", "id",
                "createdBy", "updatedBy", "createdAt", "updatedAt",
                "version", "deleted", "originOrgId"
            ]
            
            # 调用启用接口
            response, _ = self.standard_api_call(
                api_key="IV-计价路由-启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证启用状态
            enabled_route_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(
                enabled_route_data.get("enableStatus"), "=", "ENABLE",
                "启用后状态应为ENABLE"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试停用计价路由",
        description="验证停用存货计价路由功能",
        severity="normal",
        file_level_order=5,
        tags=["iv", "pricing", "route", "disable"]
    )
    def test_disable_pricing_route(self):
        """测试停用计价路由"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_submit_pricing_route()
            
            # 先查询计价路由详情，获取完整数据
            response, _ = self.standard_api_call(
                api_key="存货计价路由-根据ID查找数据服务",
                set_dict={"id": self.pricing_route_id},
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_data(response)
            route_data = response.get("data", {}).get("data", {})
            
            # 如果当前状态是 DISABLE，先启用（确保可以测试停用功能）
            if route_data.get("enableStatus") == "DISABLE":
                self.test_enable_pricing_route()
                # 重新查询获取最新数据
                response, _ = self.standard_api_call(
                    api_key="存货计价路由-根据ID查找数据服务",
                    set_dict={"id": self.pricing_route_id},
                    fields_to_filter=["id"]
                )
                self.assert_util.assert_response_data(response)
                route_data = response.get("data", {}).get("data", {})
            
            # 准备停用参数
            # 停用接口需要传递当前状态（ENABLE），接口会将其改为 DISABLE
            set_dict = {
                "ivRouteCode": route_data.get("ivRouteCode") or route_data.get("code"),
                "comOrgId": {"id": self.com_org_id},
                "invMvnCode": route_data.get("invMvnCode") or self.inv_mvn_code,
                "invMvnName": route_data.get("invMvnName") or self.inv_mvn_name,
                "priceStrategy": route_data.get("priceStrategy") or "END_METHOD",
                "enableStatus": route_data.get("enableStatus"),  # 使用当前状态（应该是 ENABLE）
                "ivType": route_data.get("ivType") or "PERIOD_METHOD",
                "id": self.pricing_route_id,
                "createdBy": route_data.get("createdBy"),
                "updatedBy": route_data.get("updatedBy"),
                "createdAt": route_data.get("createdAt"),
                "updatedAt": route_data.get("updatedAt"),
                "version": route_data.get("version", 0),
                "deleted": route_data.get("deleted", 0),
                "originOrgId": route_data.get("originOrgId", 0)
            }
            fields_to_filter = [
                "ivRouteCode", "comOrgId", "invMvnCode", "invMvnName",
                "priceStrategy", "enableStatus", "ivType", "id",
                "createdBy", "updatedBy", "createdAt", "updatedAt",
                "version", "deleted", "originOrgId"
            ]
            
            # 调用停用接口
            response, _ = self.standard_api_call(
                api_key="IV-计价路由-反启用服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证停用状态
            disabled_route_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(
                disabled_route_data.get("enableStatus"), "=", "DISABLE",
                "停用后状态应为DISABLE"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试批量删除计价路由",
        description="验证批量删除存货计价路由功能",
        severity="normal",
        file_level_order=6,
        tags=["iv", "pricing", "route", "batch_delete"]
    )
    def test_batch_delete_pricing_route(self):
        """测试批量删除计价路由"""
        try:
            # 先创建多个记录用于批量删除
            route_ids = []
            for _ in range(2):
                # 使用提交接口创建计价路由（与 test_submit_pricing_route 逻辑一致）
                if not self.inv_mvn_code or not self.inv_mvn_name:
                    raise ValueError("移动类型数据未初始化，请检查数据库或使用默认值")
                
                # 准备测试数据
                inv_mvn_code = self.inv_mvn_code
                inv_mvn_name = self.inv_mvn_name
                com_org_obj = {"id": self.com_org_id}
                
                set_dict = {
                    "invMvnCode": inv_mvn_code,
                    "invMvnName": inv_mvn_name,
                    "comOrgId": com_org_obj,
                    "ivType": "PERIOD_METHOD",
                    "priceStrategy": "END_METHOD",
                    "enableStatus": "ENABLE",
                    "id": None,
                    "createdBy": None,
                    "updatedBy": None,
                    "createdAt": None,
                    "updatedAt": None,
                    "version": 0,
                    "deleted": 0,
                    "originOrgId": 0
                }
                fields_to_filter = [
                    "invMvnCode", "invMvnName", "comOrgId", "ivType",
                    "priceStrategy", "enableStatus", "id", "createdBy",
                    "updatedBy", "createdAt", "updatedAt", "version",
                    "deleted", "originOrgId"
                ]
                
                response, extracted_id = self.standard_api_call(
                    api_key="IV-计价路由-数据提交服务",
                    set_dict=set_dict,
                    fields_to_filter=fields_to_filter,
                    store_id_as=None
                )
                self.assert_util.assert_response_data(response)
                
                # 从响应中提取ID
                route_data = response.get("data", {}).get("data", {})
                if route_data and route_data.get("id"):
                    route_ids.append(route_data.get("id"))
            
            if not route_ids:
                raise ValueError("未创建到测试数据，无法进行批量删除测试")
            
            # 根据 curl 请求，批量删除接口需要：
            # 1. ids 参数（在 request 层级）
            # 2. modelKey 参数（在 params 层级和 URL 参数中）
            # 3. tmodule 参数（在 URL 参数中）
            set_dict = {"ids": route_ids}
            fields_to_filter = ["ids"]
            
            # 获取 API 路径和参数
            api_path = self.get_api_path("存货计价路由-批量删除数据服务")
            
            # 构建 URL 查询参数（从 curl 请求中提取）
            # tmodule=ERP_FIN&modelKey=ERP_FIN%24fin_iv_route_cf
            query_params = "tmodule=ERP_FIN&modelKey=ERP_FIN%24fin_iv_route_cf"
            params, url = self.get_api_params(api_path, with_query_params=query_params)
            
            # 过滤和设置参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, set_dict, path=["params", "request"])
            
            # 添加 modelKey 到请求体的 params 层级（从 curl 请求中提取）
            # 注意：modelKey 在 params 层级，不在 request 层级
            if "params" not in filtered_params:
                filtered_params["params"] = {}
            filtered_params["params"]["modelKey"] = "ERP_FIN$fin_iv_route_cf"
            
            # 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 记录请求和响应
            a.json(filtered_params, "批量删除请求参数")
            a.json(response, "批量删除响应数据")
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
            # 验证删除结果（可选：查询确认数据已删除）
            self.logger.info(f"批量删除完成，删除的计价路由ID: {route_ids}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货计价路由",
        title="测试复制数据转换",
        description="验证存货计价路由复制数据转换功能",
        severity="normal",
        file_level_order=7,
        tags=["iv", "pricing", "route", "copy"]
    )
    def test_copy_data_converter_route(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_submit_pricing_route()
            
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
        file_level_order=8,
        tags=["iv", "pricing", "route", "export", "standard"]
    )
    def test_standard_export_route(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.pricing_route_id:
                self.test_submit_pricing_route()
            
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
