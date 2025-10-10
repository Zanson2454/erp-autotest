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
@pytest.mark.run(order=1)
class TestInvAtpLockPur(ScmInvBaseTest):
    """ATP库存占量-采购单测试类
    
    测试流程：
    1. 查询ATP库存占量表，记录初始数量
    2. 创建采购单，验证在途数量增加
    3. 创建采购交货单
    4. 查询采购单数据库数据验证
    5. 查询交货单数据库数据验证
    """
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_doc_i_code = None  # 采购单docICode
        cls.dn_doc_i_code = None  # 交货单docICode
        cls.po_plan_qty = 11  # 采购单数量
        cls.dn_plan_qty = 2  # 交货单数量
        
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
                self.logger.info(f"✅ ATP库存占量查询成功 (共{len(content)}条数据)")
            else:
                self.logger.warning("⚠️ 未查询到ATP库存占量数据")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP采购单",
        title="创建采购单",
        description="创建采购单，保存docICode",
        severity="critical",
        order=2,
        tags=["ATP", "采购", "创建"]
    )
    def test_create_atp_supply_order(self):
        """创建ATP供给订单（采购单）"""
        try:
            
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
                "planQty": self.__class__.po_plan_qty,
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
            
            # 保存采购单docICode
            result_data = response.get("data", {}).get("data", {})
            self.__class__.po_doc_i_code = result_data.get("docICode")
            self.logger.info(f"✅ ATP采购单创建成功，docICode: {self.__class__.po_doc_i_code}")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP采购单",
        title="创建采购交货单",
        description="创建采购交货单，验证srcDocICode、planQty、postingQty",
        severity="critical",
        order=3,
        tags=["ATP", "采购", "交货单"]
    )
    def test_create_delivery_note(self):
        """创建采购交货单"""
        try:
            # 确保已创建采购单
            if not self.__class__.po_doc_i_code:
                self.test_create_atp_supply_order()
            
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
                "docClass": "DN",
                "docPosneg": "POS",
                "docHId": None,
                "docIId": None,
                "srcDocClass": "PO",
                "srcDocIId": None,
                "srcDocICode": self.__class__.po_doc_i_code,
                "planDate": plan_date,
                "planQty": self.__class__.dn_plan_qty,
                "postingQty": self.__class__.dn_plan_qty,
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
            
            result_data = response.get("data", {}).get("data", {})
            self.__class__.dn_doc_i_code = result_data.get("docICode")
            src_doc_i_code = result_data.get("srcDocICode")
            plan_qty = result_data.get("planQty")
            posting_qty = result_data.get("postingQty")
            
            self.logger.info(f"✅ 采购交货单创建成功，docICode: {self.__class__.dn_doc_i_code}")
            self.logger.info(f"📊 验证数据: srcDocICode={src_doc_i_code}, planQty={plan_qty}, postingQty={posting_qty}")
            
            # 断言验证
            assert src_doc_i_code == self.__class__.po_doc_i_code, f"srcDocICode应该为{self.__class__.po_doc_i_code}，实际为{src_doc_i_code}"
            assert plan_qty == self.__class__.dn_plan_qty, f"planQty应该为{self.__class__.dn_plan_qty}，实际为{plan_qty}"
            assert posting_qty == self.__class__.dn_plan_qty, f"postingQty应该为{self.__class__.dn_plan_qty}，实际为{posting_qty}"
            
            self.logger.info(f"✅ 验证通过: srcDocICode={src_doc_i_code}, planQty={plan_qty}, postingQty={posting_qty}")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP采购单",
        title="查询采购单数据库数据",
        description="查询采购单数据库，验证confirm_qty=9, unclose_qty=9, plan_qty=11",
        severity="critical",
        order=4,
        tags=["ATP", "采购", "数据库验证"]
    )
    def test_verify_purchase_order_db(self):
        """查询采购单数据库数据"""
        try:
            # 确保已创建交货单（因为需要验证confirm_qty=9，即11-2）
            if not self.__class__.dn_doc_i_code:
                self.test_create_delivery_note()
            
            query_sql = f"""
                SELECT doc_i_code, confirm_qty, unclose_qty, plan_qty
                FROM inv_atp_lock_tr
                WHERE doc_i_code = '{self.__class__.po_doc_i_code}'
                  AND deleted = 0
            """
            
            db_result = self.db.query(query_sql)
            assert db_result and len(db_result) > 0, f"未查询到采购单数据: {self.__class__.po_doc_i_code}"
            
            record = db_result[0]
            confirm_qty = float(record.get("confirm_qty"))
            unclose_qty = float(record.get("unclose_qty"))
            plan_qty = float(record.get("plan_qty"))
            
            self.logger.info(f"📊 数据库查询结果: confirm_qty={confirm_qty}, unclose_qty={unclose_qty}, plan_qty={plan_qty}")
            
            # 断言验证
            assert confirm_qty == 9, f"confirm_qty应该为9，实际为{confirm_qty}"
            assert unclose_qty == 9, f"unclose_qty应该为9，实际为{unclose_qty}"
            assert plan_qty == self.__class__.po_plan_qty, f"plan_qty应该为{self.__class__.po_plan_qty}，实际为{plan_qty}"
            
            self.logger.info(f"✅ 采购单数据库验证通过")
            
            a.text(
                f"doc_i_code: {self.__class__.po_doc_i_code}\n"
                f"confirm_qty: {confirm_qty}\n"
                f"unclose_qty: {unclose_qty}\n"
                f"plan_qty: {plan_qty}",
                "采购单数据库数据"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP采购单",
        title="查询交货单数据库数据",
        description="查询交货单数据库，验证confirm_qty=0, unclose_qty=0, plan_qty=2",
        severity="critical",
        order=5,
        tags=["ATP", "交货单", "数据库验证"]
    )
    def test_verify_delivery_note_db(self):
        """查询交货单数据库数据"""
        try:
            # 确保已创建交货单
            if not self.__class__.dn_doc_i_code:
                self.test_create_delivery_note()
            
            query_sql = f"""
                SELECT doc_s_code, confirm_qty, unclose_qty, plan_qty
                FROM inv_atp_lock_tr
                WHERE doc_s_code = '{self.__class__.dn_doc_i_code}'
            """
            
            db_result = self.db.query(query_sql)
            assert db_result and len(db_result) > 0, f"未查询到交货单数据: {self.__class__.dn_doc_i_code}"
            
            record = db_result[0]
            confirm_qty = float(record.get("confirm_qty"))
            unclose_qty = float(record.get("unclose_qty"))
            plan_qty = float(record.get("plan_qty"))
            
            self.logger.info(f"📊 数据库查询结果: confirm_qty={confirm_qty}, unclose_qty={unclose_qty}, plan_qty={plan_qty}")
            
            # 断言验证
            assert confirm_qty == 0, f"confirm_qty应该为0，实际为{confirm_qty}"
            assert unclose_qty == 0, f"unclose_qty应该为0，实际为{unclose_qty}"
            assert plan_qty == self.__class__.dn_plan_qty, f"plan_qty应该为{self.__class__.dn_plan_qty}，实际为{plan_qty}"
            
            self.logger.info(f"✅ 交货单数据库验证通过")
            
            a.text(
                f"doc_s_code: {self.__class__.dn_doc_i_code}\n"
                f"confirm_qty: {confirm_qty}\n"
                f"unclose_qty: {unclose_qty}\n"
                f"plan_qty: {plan_qty}",
                "交货单数据库数据"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

