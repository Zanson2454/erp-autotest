import allure
import pytest
import sys
from pathlib import Path
import datetime
import time

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("ATP库存占量-销售")
@pytest.mark.run(order=2)
class TestInvAtpLockSale(ScmInvBaseTest):
    """ATP库存占量-销售单测试类
    
    测试流程：
    1. 创建销售单，验证响应中confirmQty为-5
    2. 创建销售交货单，验证相关字段
    3. 查询销售单数据库数据，验证confirm_qty=-2（轮询等待异步更新）
    4. 查询交货单数据库数据
    """
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.atp_record_id = None
        cls.so_doc_i_code = None  # 销售单docICode
        cls.dn_doc_i_code = None  # 交货单docICode
        cls.so_plan_qty = 5  # 销售单数量
        cls.dn_plan_qty = 3  # 交货单数量
        
        if cls.inv_cache_data:
            cls.mat_id = cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [])[0].get("id")
            cls.mat_code = cls.inv_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [])[0].get("matCode")
            cls.inv_org_id = cls.inv_cache_data.get("org_info", {}).get("inv_org_info", [])[0].get("id")
            cls.inv_loc_id = cls.inv_cache_data.get("org_info", {}).get("inv_loc_info", [])[0].get("id")
        
        cls.logger.info("ATP销售单测试类初始化完成")

    @case_decorator(
        story="ATP销售单",
        title="创建销售单验证confirmQty为-5",
        description="创建销售单，验证响应中confirmQty为-5（销售为负数）",
        severity="critical",
        order=6,
        tags=["ATP", "销售", "创建"]
    )
    def test_create_sale_order(self):
        """创建销售单"""
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
                "docClass": "SO",
                "docPosneg": "NEG",
                "docHId": None,
                "docIId": None,
                "srcDocClass": None,
                "srcDocIId": None,
                "srcDocICode": None,
                "planDate": plan_date,
                "planQty": self.__class__.so_plan_qty,
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
            
            result_data = response.get("data", {}).get("data", {})
            self.__class__.so_doc_i_code = result_data.get("docICode")
            item_list = result_data.get("itemList", [])
            
            self.logger.info(f"✅ 销售单创建成功，docICode: {self.__class__.so_doc_i_code}")
            
            # 验证响应数据中的confirmQty
            assert item_list and len(item_list) > 0, "响应中未返回itemList"
            confirm_qty = item_list[0].get("confirmQty")
            expected_qty = -self.__class__.so_plan_qty
            
            self.logger.info(f"📊 响应数据验证: confirmQty={confirm_qty}, 期望值={expected_qty}")
            assert confirm_qty == expected_qty, f"confirmQty应该为{expected_qty}，实际为{confirm_qty}"
            
            # 查询数据库保存ID
            query_id_sql = f"""
                SELECT id
                FROM inv_atp_lock_tr
                WHERE doc_i_code = '{self.__class__.so_doc_i_code}'
                  AND deleted = 0
            """
            
            id_result = self.db.query(query_id_sql)
            assert id_result and len(id_result) > 0, "未查询到ATP记录"
            
            self.__class__.atp_record_id = id_result[0].get("id")
            self.logger.info(f"📋 查询到ATP记录ID: {self.__class__.atp_record_id}")
            self.logger.info(f"✅ 验证通过: confirmQty={confirm_qty}")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP销售单",
        title="创建销售交货单",
        description="创建销售交货单，验证srcDocICode、planQty、postingQty",
        severity="critical",
        order=7,
        tags=["ATP", "销售", "交货单"]
    )
    def test_create_delivery_note(self):
        """创建销售交货单"""
        try:
            # 确保已创建销售单
            if not self.__class__.so_doc_i_code:
                self.test_create_sale_order()
            
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
                "docPosneg": "NEG",
                "docHId": None,
                "docIId": None,
                "srcDocClass": "SO",
                "srcDocIId": None,
                "srcDocICode": self.__class__.so_doc_i_code,
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
            
            self.logger.info(f"✅ 销售交货单创建成功，docICode: {self.__class__.dn_doc_i_code}")
            self.logger.info(f"📊 验证数据: srcDocICode={src_doc_i_code}, planQty={plan_qty}, postingQty={posting_qty}")
            
            # 断言验证
            assert src_doc_i_code == self.__class__.so_doc_i_code, f"srcDocICode应该为{self.__class__.so_doc_i_code}，实际为{src_doc_i_code}"
            assert plan_qty == self.__class__.dn_plan_qty, f"planQty应该为{self.__class__.dn_plan_qty}，实际为{plan_qty}"
            assert posting_qty == self.__class__.dn_plan_qty, f"postingQty应该为{self.__class__.dn_plan_qty}，实际为{posting_qty}"
            
            self.logger.info(f"✅ 验证通过: srcDocICode={src_doc_i_code}, planQty={plan_qty}, postingQty={posting_qty}")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP销售单",
        title="查询销售单数据库数据",
        description="查询销售单数据库，验证confirm_qty=-2, unclose_qty=2, plan_qty=5",
        severity="critical",
        order=8,
        tags=["ATP", "销售", "数据库验证"]
    )
    def test_verify_sale_order_db(self):
        """查询销售单数据库数据"""
        try:
            # 确保已创建交货单
            if not self.__class__.dn_doc_i_code:
                self.test_create_delivery_note()
            
            query_sql = f"""
                SELECT doc_s_code, confirm_qty, unclose_qty, plan_qty
                FROM inv_atp_lock_tr
                WHERE doc_s_code = '{self.__class__.so_doc_i_code}'
                  AND deleted = 0
            """
            
            # 轮询等待confirm_qty更新（销售单的confirm_qty通过后台任务异步更新）
            expected_confirm_qty = -(self.__class__.so_plan_qty - self.__class__.dn_plan_qty)
            expected_unclose_qty = self.__class__.so_plan_qty - self.__class__.dn_plan_qty
            
            # 轮询查询，最多等待10秒
            for i in range(10):
                db_result = self.db.query(query_sql)
                if db_result and len(db_result) > 0:
                    record = db_result[0]
                    confirm_qty = float(record.get("confirm_qty"))
                    unclose_qty = float(record.get("unclose_qty"))
                    plan_qty = float(record.get("plan_qty"))
                    
                    if confirm_qty == expected_confirm_qty:
                        if i > 0:
                            self.logger.info(f"✅ 第{i+1}次查询成功，confirm_qty已更新")
                        break
                    elif i < 9:  # 不是最后一次才等待
                        time.sleep(1)
            
            self.logger.info(f"📊 数据库查询结果: confirm_qty={confirm_qty}, unclose_qty={unclose_qty}, plan_qty={plan_qty}")
            
            # 断言验证
            assert confirm_qty == expected_confirm_qty, f"confirm_qty应该为{expected_confirm_qty}，实际为{confirm_qty}"
            assert unclose_qty == expected_unclose_qty, f"unclose_qty应该为{expected_unclose_qty}，实际为{unclose_qty}"
            assert plan_qty == self.__class__.so_plan_qty, f"plan_qty应该为{self.__class__.so_plan_qty}，实际为{plan_qty}"
            
            self.logger.info(f"✅ 销售单数据库验证通过")
            
            a.text(
                f"doc_s_code: {self.__class__.so_doc_i_code}\n"
                f"confirm_qty: {confirm_qty}\n"
                f"unclose_qty: {unclose_qty}\n"
                f"plan_qty: {plan_qty}",
                "销售单数据库数据"
            )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="ATP销售单",
        title="查询交货单数据库数据",
        description="查询交货单数据库，验证confirm_qty=0, unclose_qty=0, plan_qty=3",
        severity="critical",
        order=9,
        tags=["ATP", "销售", "数据库验证"]
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
