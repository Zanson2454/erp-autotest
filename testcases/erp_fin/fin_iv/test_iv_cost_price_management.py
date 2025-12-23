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

from testcases.erp_fin.fin_iv import IvBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP财务模块")
@allure.feature("存货成本价格")
class TestIvCostPriceManagement(IvBaseTest):
    """存货成本价格测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()  # IvBaseTest 会自动初始化存货核算配置和 com_org_id/gr_com_org_id/inv_org_id/mat_id
        cls.cost_price_id = None
        cls.logger.info("存货成本价格测试类初始化完成")
        # 注意：com_org_id、inv_org_id、mat_id 已在 FinBaseTest/IvBaseTest 中初始化，无需重复获取
        # - com_org_id: 从 com_org_info 获取（IvBaseTest 已映射）
        # - inv_org_id: 从 inv_org_info 获取（FinBaseTest 已初始化）
        # - mat_id: 从 mat_md.FINP 获取（FinBaseTest 已初始化）
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # cls.db.delete(
            #     table="fin_iv_price_md",
            #     where="code like %s",
            #     params=["AT_%"]
            # )
            pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="存货成本价格",
        title="测试保存成本价格",
        description="验证保存存货成本价格功能",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["iv", "cost", "price", "save"]
    )
    def test_save_cost_price(self):
        """测试保存成本价格"""
        try:
            # 检查依赖数据
            if not self.com_org_id:
                raise ValueError("com_org_id 未初始化，请检查 md_cache_data")
            if not self.inv_org_id:
                raise ValueError("inv_org_id 未初始化，请检查 md_cache_data")
            if not self.mat_id:
                raise ValueError("mat_id 未初始化，请检查 md_cache_data")
            
            # 确保唯一，能新增成功
            sql = self.db.delete(
                table="fin_iv_price_md",
                where="com_org_id = %s and mat_id =%s and  inv_org_id=%s",
                params=(self.com_org_id, self.mat_id, self.inv_org_id)
            )
            
            # 使用标准化API调用
            # 根据 curl 请求，参数需要是对象格式，且包含 ivType、costPrice、enableStatus 等字段
            set_dict = {
                "comOrgId": {"id": self.com_org_id},
                "invOrgId": {"id": self.inv_org_id},
                "matId": {"id": self.mat_id},
                "ivType": "PERIOD_METHOD",
                "costPrice": 100.0,
                "enableStatus": "ENABLE",
                "batchCode": None,
                "currId": None
            }
            fields_to_filter = ["comOrgId", "invOrgId", "matId", "ivType", "costPrice", "enableStatus", "batchCode", "currId"]
            
            response, extracted_id = self.standard_api_call(
                api_key="IV-存货成本-数据提交服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="cost_price"  # 自动存储为 self.cost_price_id
            )
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 唯一键验证
            response2,extracted_id2 = self.standard_api_call(
                api_key="IV-存货成本-数据提交服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None  
            )
            
            errCode = response2.get("err", {}).get("code")
            errMsg = response2.get("err", {}).get("msg")
            self.assert_util.assert_by_operator(errCode, "=", "FIN_IV_PRICE_EXIST", "唯一键验证失败")
            self.assert_util.assert_by_operator(errMsg, "=", "新增失败,成本价格已存在", "唯一键验证失败")
            
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试根据ID查找成本价格",
        description="验证存货成本价格根据ID查找功能",
        severity="normal",
        file_level_order=2,
        tags=["iv", "cost", "price", "find"]
    )
    def test_find_cost_price_by_id(self):
        """测试根据ID查找成本价格"""
        try:
            # 检查并创建依赖数据
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            # 使用标准化API调用
            set_dict = {"id": self.cost_price_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货成本价格-根据ID查找数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
            # 验证返回的数据
            price_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(price_data.get("id"), "=", self.cost_price_id, "查找ID不匹配")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试分页查询成本价格",
        description="验证存货成本价格分页查询功能",
        severity="normal",
        file_level_order=3,
        tags=["iv", "cost", "price", "paging"]
    )
    def test_paging_cost_price(self):
        """测试分页查询成本价格"""
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
                api_key="存货成本价格-分页数据服务",
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
        story="存货成本价格",
        title="测试复制数据转换",
        description="验证存货成本价格复制数据转换功能",
        severity="normal",
        file_level_order=4,
        tags=["iv", "cost", "price", "copy"]
    )
    def test_copy_data_converter_price(self):
        """测试复制数据转换"""
        try:
            # 检查并创建依赖数据
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            # 使用标准化API调用
            set_dict = {"sourceId": self.cost_price_id}
            fields_to_filter = ["sourceId"]
            
            response, _ = self.standard_api_call(
                api_key="存货成本价格-复制数据转换服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导出服务未引用")
    @case_decorator(
        story="存货成本价格",
        title="测试标准导出服务",
        description="验证存货成本价格标准导出服务功能",
        severity="minor",
        file_level_order=10,
        tags=["iv", "cost", "price", "export", "standard"]
    )
    def test_standard_export_cost_price(self):
        """测试标准导出服务"""
        try:
            # 检查并创建依赖数据
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            # 使用标准化API调用
            set_dict = {
                "priceIds": [self.cost_price_id],
                "exportType": "EXCEL"
            }
            fields_to_filter = ["priceIds", "exportType"]
            
            response, _ = self.standard_api_call(
                api_key="存货成本价格标准导出服务",
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
        story="存货成本价格",
        title="测试导入导出任务提交",
        description="验证存货成本价格导入导出任务管理接口-提交导出任务功能",
        severity="minor",
        file_level_order=11,
        tags=["iv", "cost", "price", "export", "task"]
    )
    def test_export_task_direct_post_price(self):
        """测试导入导出任务提交"""
        try:
            # 检查并创建依赖数据
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            # 获取API路径和URL
            api_path = self.get_api_path("存货成本价格-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 按照CURL真实入参格式构建参数
            params = {
                "serviceKey": "ERP_FIN$FIN_IV_PRICE_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "params": {
                    "taskName": f"存货成本价格-{self.nickname or '自动化测试'}-{self.mock_util.get_timestamp()}-导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ERP_FIN$fin_iv_price_md",
                            "modelName": "存货成本价格",
                            "sheetNo": 0,
                            "sheetName": "存货成本价格",
                            "headerConfigList": [
                                {
                                    "name": "公司组织",
                                    "type": "TEXT",
                                    "field": "comOrgId.orgName"
                                },
                                {
                                    "name": "库存组织",
                                    "type": "TEXT",
                                    "field": "invOrgId.orgName"
                                },
                                {
                                    "name": "存货核算类型",
                                    "type": "ENUM",
                                    "field": "ivType",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "_row_id_": "tzQaRtC",
                                            "label": "永续成本法",
                                            "value": "CONTINUOUS_METHOD"
                                        },
                                        {
                                            "_row_id_": "7nuaKMp",
                                            "label": "期间成本法",
                                            "value": "PERIOD_METHOD"
                                        }
                                    ]
                                },
                                {
                                    "name": "物料",
                                    "type": "TEXT",
                                    "field": "matId.matName"
                                },
                                {
                                    "name": "批次",
                                    "type": "TEXT",
                                    "field": "batchCode"
                                },
                                {
                                    "name": "币别",
                                    "type": "TEXT",
                                    "field": "currId.currName"
                                },
                                {
                                    "name": "成本价格",
                                    "type": "DECIMAL",
                                    "field": "costPrice",
                                    "precision": 6
                                },
                                {
                                    "name": "启用状态",
                                    "type": "ENUM",
                                    "field": "enableStatus",
                                    "multiSelect": False,
                                    "dictValues": [
                                        {
                                            "label": "已启用",
                                            "value": "ENABLE"
                                        },
                                        {
                                            "label": "未启用",
                                            "value": "DISABLE"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ERP_FIN$IV_PRICE_MD_VIEW-table-container-ERP_FIN$fin_iv_price_md",
                        "viewKey": "ERP_FIN$IV_PRICE_MD_VIEW:list",
                        "sceneKey": "ERP_FIN$IV_PRICE_MD_VIEW",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 20
                                }
                            },
                            "selectFields": [
                                {
                                    "field": "ivType"
                                },
                                {
                                    "field": "batchCode"
                                },
                                {
                                    "field": "costPrice"
                                },
                                {
                                    "field": "enableStatus"
                                },
                                {
                                    "field": "comOrgId",
                                    "selectFields": [
                                        {
                                            "field": "orgName"
                                        }
                                    ]
                                },
                                {
                                    "field": "invOrgId",
                                    "selectFields": [
                                        {
                                            "field": "orgName"
                                        }
                                    ]
                                },
                                {
                                    "field": "matId",
                                    "selectFields": [
                                        {
                                            "field": "matName"
                                        }
                                    ]
                                },
                                {
                                    "field": "currId",
                                    "selectFields": [
                                        {
                                            "field": "currName"
                                        }
                                    ]
                                }
                            ],
                            "modelKey": "ERP_FIN$fin_iv_price_md"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ERP_FIN$fin_iv_price_md",
                        "modelName": "存货成本价格",
                        "containerKey": "ERP_FIN$IV_PRICE_MD_VIEW-table-container-ERP_FIN$fin_iv_price_md",
                        "viewKey": "ERP_FIN$IV_PRICE_MD_VIEW:list",
                        "sceneKey": "ERP_FIN$IV_PRICE_MD_VIEW"
                    }
                }
            }
            
            response = self.http.post(url, json=params)
            self.assert_util.assert_response_success(response)
            
            a.json(params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="存货成本价格",
        title="测试批量删除成本价格",
        description="验证批量删除存货成本价格功能",
        severity="normal",
        file_level_order=17,
        tags=["iv", "cost", "price", "batch_delete"]
    )
    def test_batch_delete_cost_price(self):
        """测试批量删除成本价格"""
        try:
            # 创建测试数据用于批量删除
            if not self.cost_price_id:
                self.test_save_cost_price()
          
            # 批量删除
            price_ids = [self.cost_price_id]
            set_dict = {"ids": price_ids}
            fields_to_filter = ["ids"]
            response, _ = self.standard_api_call(
                api_key="存货成本价格-批量删除数据服务",
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
        story="存货成本价格",
        title="测试根据ID删除成本价格",
        description="验证根据ID删除存货成本价格功能",
        severity="normal",
        file_level_order=18,
        tags=["iv", "cost", "price", "delete"]
    )
    def test_delete_cost_price_by_id(self):
        """测试根据ID删除成本价格"""
        try:
            # 检查并创建依赖数据
            if not self.cost_price_id:
                self.test_save_cost_price()
            
            # 使用标准化API调用
            set_dict = {"id": self.cost_price_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="存货成本价格-根据ID删除数据服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as=None
            )
            
            # 业务断言
            self.assert_util.assert_response_success(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
