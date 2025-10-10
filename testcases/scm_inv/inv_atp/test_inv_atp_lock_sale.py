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
@allure.feature("ATP库存占量-销售")
class TestInvAtpLockSale(ScmInvBaseTest):
    """ATP库存占量-销售单测试类
    
    测试流程：
    1. 创建销售单，验证响应中confirmQty为-5
    2. 查询数据库保存ATP记录ID
    """
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.atp_record_id = None
        cls.plan_qty = 5
        
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
        order=3,
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
                "planQty": self.__class__.plan_qty,
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
            doc_i_code = result_data.get("docICode")
            item_list = result_data.get("itemList", [])
            
            self.logger.info(f"✅ 销售单创建成功，docICode: {doc_i_code}")
            
            # 验证响应数据中的confirmQty
            assert item_list and len(item_list) > 0, "响应中未返回itemList"
            confirm_qty = item_list[0].get("confirmQty")
            expected_qty = -self.__class__.plan_qty
            
            self.logger.info(f"📊 响应数据验证: confirmQty={confirm_qty}, 期望值={expected_qty}")
            assert confirm_qty == expected_qty, f"confirmQty应该为{expected_qty}，实际为{confirm_qty}"
            
            # 查询数据库保存ID
            query_id_sql = f"""
                SELECT id
                FROM inv_atp_lock_tr
                WHERE doc_i_code = '{doc_i_code}'
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


 
