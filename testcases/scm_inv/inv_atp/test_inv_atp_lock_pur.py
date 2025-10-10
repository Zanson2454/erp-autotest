import allure
import pytest
import sys
from pathlib import Path
import datetime

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("ATP库存占量-采购")
class TestInvAtpLockPur(ScmInvBaseTest):
    """ATP库存占量-采购单测试类
    
    测试流程：
    1. 查询ATP库存占量表
    2. 创建采购单，验证在途可用数量增加
    """
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.atp_available_qty = None
        cls.atp_spot_available_qty = None
        cls.atp_future_available_qty = None
        
        if cls.inv_cache_data:
            cls.mat_id = cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [])[0].get("id")
            cls.mat_code = cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [])[0].get("matCode")
            cls.inv_org_id = cls.inv_cache_data.get("org_info", {}).get("inv_org_info", [])[0].get("id")
            cls.inv_loc_id = cls.inv_cache_data.get("org_info", {}).get("inv_loc_info", [])[0].get("id")
        
        cls.logger.info("ATP采购单测试类初始化完成")

    @case_decorator(
        story="ATP采购单",
        title="查询ATP库存占量表",
        description="查询ATP库存占量表，记录在途可用数量",
        severity="critical",
        order=1,
        tags=["ATP", "采购", "查询"]
    )
    def test_query_atp_overview(self):
        """查询ATP库存占量表"""
        try:
            api_path = self.get_api_path("INV-ATP总览-分页查询")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1000,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {
                            "matId": {
                                "operator": "EQ",
                                "value": {"id": self.__class__.mat_id, "matCode": self.__class__.mat_code}
                            },
                            "docClass": {
                                "operator": "EQ",
                                "value": "SO"
                            },
                            "invOrgId": {
                                "operator": "EQ",
                                "value": {"id": self.__class__.inv_org_id}
                            },
                            "invLocId": {
                                "operator": "EQ",
                                "value": {"id": self.__class__.inv_loc_id}
                            }
                        },
                        "logicOperator": "AND"
                    }
                },
                "fields": [
                    {"name": "matId", "type": "OBJECT"},
                    {"name": "docClass", "type": "SELECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "invLocId", "type": "OBJECT"},
                    {"name": "spcStkTypeId", "type": "OBJECT"},
                    {"name": "spcStkTypeClass", "type": "TEXT"}
                ],
                "systemParams": None
            })
            
            response = self.http.post(
                url, 
                json=filtered_params,
                params={"tmodule": "SCM_INV"}
            )
            self.assert_util.assert_response_data(response)
            
            result_data = response.get("data", {}).get("data", {})
            content = result_data.get("data", [])
            
            if content and len(content) > 0:
                last_item = content[-1]
                self.__class__.atp_available_qty = last_item.get("availableQty", 0)
                self.__class__.atp_spot_available_qty = last_item.get("stkAvailableQty", 0)
                self.__class__.atp_future_available_qty = last_item.get("futAvailableQty", 0)
                self.__class__.atp_record_id = last_item.get("id")
                self.__class__.atp_doc_code = last_item.get("docCode")
                
                self.logger.info(f"✅ ATP库存占量查询成功 (共{len(content)}条数据)")
                self.logger.info(f"  - 记录ID: {self.__class__.atp_record_id}")
                self.logger.info(f"  - 在途可用数量: {self.__class__.atp_future_available_qty}")
            else:
                self.logger.warning("⚠️ 未查询到ATP库存占量数据")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP采购单",
        title="创建采购单验证在途数量增加",
        description="创建采购单，验证在途可用数量增加11",
        severity="critical",
        order=2,
        tags=["ATP", "采购", "创建"]
    )
    def test_create_atp_supply_order(self):
        """创建ATP供给订单（采购单）"""
        try:
            if not self.__class__.atp_available_qty:
                self.test_query_atp_overview()
            
            old_future_qty = self.__class__.atp_future_available_qty
            
            api_path = self.get_api_path("INV-ATP-手动创建单据")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, [
                    "id", "docHCode", "docICode", "docClass", "docPosneg", "docHId", 
                    "docIId", "srcDocClass", "srcDocIId", "srcDocICode", "planDate", 
                    "planQty", "postingQty", "matId", "invOrgId", "invLocId", "docTime"
                ], 
                ["params", "request"]
            )
            
            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            plan_date = int(today.timestamp() * 1000)
            doc_time = int(datetime.datetime.now().timestamp() * 1000)
            
            ParamUtil.set_request_params(filtered_params, {
                "id": None,
                "docHCode": None,
                "docICode": None,
                "docClass": "PO",
                "docPosneg": "POS",
                "docHId": None,
                "docIId": None,
                "srcDocClass": None,
                "srcDocIId": None,
                "srcDocICode": None,
                "planDate": plan_date,
                "planQty": 11,
                "postingQty": None,
                "matId": {"id": self.__class__.mat_id, "matCode": self.__class__.mat_code},
                "invOrgId": {"id": self.__class__.inv_org_id},
                "invLocId": {"id": self.__class__.inv_loc_id},
                "docTime": doc_time
            })
            
            response = self.http.post(
                url, 
                json=filtered_params,
                params={"tmodule": "SCM_INV"}
            )
            self.assert_util.assert_response_data(response)
            self.logger.info("✅ ATP供给订单创建成功")
            
            self.test_query_atp_overview()
            
            new_future_qty = self.__class__.atp_future_available_qty
            future_qty_diff = new_future_qty - old_future_qty
            
            self.logger.info(f"📊 在途可用数量变化: {old_future_qty} -> {new_future_qty} (+{future_qty_diff})")
            
            assert future_qty_diff == 11, f"在途可用数量应该增加11，实际增加{future_qty_diff}"
            self.logger.info(f"✅ 验证通过: 在途数量增加{future_qty_diff}")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            a.text(
                f"创建前: {old_future_qty}\n"
                f"创建后: {new_future_qty}\n"
                f"变化: +{future_qty_diff}",
                "在途可用数量变化"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

