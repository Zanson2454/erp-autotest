# -*- coding: utf-8 -*-
"""
存货成本价格测试用例
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
@allure.feature("存货成本价格")
class TestIvCostPriceManagement(FinBaseTest):
    """存货成本价格测试类"""
    
    cost_price_id = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.cost_price_id = None
        cls.logger.info("存货成本价格测试类初始化完成")
        if cls.md_cache_data:
            cls.com_org_id = cls.md_cache_data.get("org_info",{}).get("gr_come_org_info",[])[0].get("id")
            cls.inv_org_id = cls.md_cache_data.get("org_info",{}).get("inv_org_info",[])[0].get("id")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="fin_iv_price_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货成本价格",
        title="测试根据ID查找成本价格",
        description="验证存货成本价格根据ID查找功能",
        severity="normal",
        order=1,
        tags=["iv", "cost", "price", "find"]
    )
    def test_find_cost_price_by_id(self):
        """测试根据ID查找成本价格"""
        try:
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_FIND_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.cost_price_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            price_data = response.get("data", {}).get("data", {})
            assert price_data.get("id") == self.cost_price_id, "查找ID不匹配"
            
            a.json(response, "查找响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试复制数据转换",
        description="验证存货成本价格复制数据转换功能",
        severity="normal",
        order=2,
        tags=["iv", "cost", "price", "copy"]
    )
    def test_copy_data_converter_price(self):
        """测试复制数据转换"""
        try:
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_COPY_DATA_CONVERTER_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sourceId"], ["params", "request"]
            )
            set_dict = {"sourceId": self.cost_price_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(response, "复制转换响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试分页查询成本价格",
        description="验证存货成本价格分页查询功能",
        severity="normal",
        order=3,
        tags=["iv", "cost", "price", "paging"]
    )
    def test_paging_cost_price(self):
        """测试分页查询成本价格"""
        try:
            api_path = self.get_api_path("FIN_IV_PRICE_MD_PAGING_DATA_SERVICE")
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
        story="存货成本价格",
        title="测试保存成本价格",
        description="验证保存存货成本价格功能",
        severity="critical",
        order=4,
        smoke=True,
        tags=["iv", "cost", "price", "save"]
    )
    def test_save_cost_price(self):
        """测试保存成本价格"""
        try:
            price_code = self.mock_util.generate_unique_code(tag="IV_PRICE")
            price_name = f"成本价格_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_SAVE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["comOrgId", "code", "name", "costPrice", "effectiveDate"], ["params", "request"]
            )
            set_dict = {
                "comOrgId": self.com_org_id,
                "code": price_code,
                "name": price_name,
                "costPrice": 100.0,
                "effectiveDate": "2025-01-01",
                "currencyId": self.curr_id if hasattr(self, 'curr_id') else 1
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.cost_price_id = response.get("data", {}).get("data", {}).get("id")
            assert self.cost_price_id, "保存成本价格失败"
            
            a.json(filtered_params, "保存请求")
            a.json(response, "保存响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试批量删除成本价格",
        description="验证批量删除存货成本价格功能",
        severity="normal",
        order=5,
        tags=["iv", "cost", "price", "batch_delete"]
    )
    def test_batch_delete_cost_price(self):
        """测试批量删除成本价格"""
        try:
            price_ids = [self.cost_price_id] if self.cost_price_id else []
            # 创建额外价格用于批量
            self.test_save_cost_price()
            price_ids.append(self.cost_price_id)
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_BATCH_DELETE_DATA_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": price_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "批量删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试标准导出服务",
        description="验证存货成本价格标准导出服务功能",
        severity="minor",
        order=6,
        tags=["iv", "cost", "price", "export", "standard"]
    )
    def test_standard_export_cost_price(self):
        """测试标准导出服务"""
        try:
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_GEI_EXPORT_SERVICE")
            params, url = self.get_api_params(api_path)
            
            export_data = {
                "priceIds": [self.cost_price_id],
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
    
    @case_decorator(
        story="存货成本价格",
        title="测试根据ID删除成本价格",
        description="验证根据ID删除存货成本价格功能",
        severity="normal",
        order=7,
        tags=["iv", "cost", "price", "delete"]
    )
    def test_delete_cost_price_by_id(self):
        """测试根据ID删除成本价格"""
        try:
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_DELETE_DATA_BY_ID_SERVICE")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.cost_price_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "删除响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="导入导出任务需要OSS配置，复杂度较高")
    @case_decorator(
        story="存货成本价格",
        title="测试导入导出任务提交",
        description="验证存货成本价格导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        order=8,
        tags=["iv", "cost", "price", "export", "task"]
    )
    def test_export_task_direct_post_price(self):
        """测试导入导出任务提交（跳过）"""
        try:
            timestamp = self.mock_util.get_timestamp()
            task_name = f"IV_COST_PRICE_{timestamp}_EXPORT"
            
            export_params = {
                "serviceKey": "FIN_IV_PRICE_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": task_name,
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_price_md",
                            "modelName": "存货成本价格",
                            "sheetNo": 0,
                            "sheetName": "成本价格数据",
                            "headerConfigList": [
                                {"name": "价格编码", "type": "TEXT", "field": "code"},
                                {"name": "成本价格", "type": "NUMBER", "field": "costPrice"},
                                {"name": "生效日期", "type": "DATE", "field": "effectiveDate"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$fin_iv_price_md",
                        "viewKey": "ERP_FIN$fin_iv_price_md:list",
                        "sceneKey": "ERP_FIN$fin_iv_price_md",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "costPrice"},
                                {"field": "effectiveDate"}
                            ],
                            "modelKey": "ERP_FIN$fin_iv_price_md"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_price_md",
                        "modelName": "存货成本价格",
                        "containerKey": "ERP_FIN$fin_iv_price_md",
                        "viewKey": "ERP_FIN$fin_iv_price_md:list",
                        "sceneKey": "ERP_FIN$fin_iv_price_md"
                    }
                }
            }
            
            api_path = self.get_api_path("FIN_IV_PRICE_MD_API_GEI_TASK_EXPORT_DIRECT_POST")
            params, url = self.get_api_params(api_path)
            
            filtered_params = export_params
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(export_params, "导出任务请求")
            a.json(response, "导出任务响应")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
