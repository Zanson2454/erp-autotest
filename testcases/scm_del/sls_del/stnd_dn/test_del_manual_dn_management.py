"""
手动标准销售交货单测试（不依赖销售订单）
"""
import sys
from datetime import datetime
from pathlib import Path

import allure

project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_del import ScmDelBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("交货管理")
@allure.feature("手动标准销售交货单")
class TestDelManualDnManagement(ScmDelBaseTest):
    """手动标准销售交货单测试类（不依赖销售订单）"""
    
    TEST_REMARK = "自动化测试sqw"
    PLAN_DEL_QTY = 22  # 计划交货数量
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.dn_id = None
        cls.dn_code = None
        
        if cls.md_cache_data:
            mat_info = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0]
            org_info = cls.md_cache_data.get("org_info", {})
            partner_info = cls.md_cache_data.get("partner_info", {})
            
            cls.mat_id = mat_info.get("id")
            cls.mat_code = mat_info.get("mat_code")
            cls.inv_org_id = org_info.get("inv_org_info", [{}])[0].get("id")
            cls.inv_loc_id = org_info.get("inv_loc_info", [{}])[0].get("id")
            cls.com_org_id = org_info.get("gr_come_org_info", [{}])[0].get("id")
            cls.sls_org_id = org_info.get("sls_org_info", [{}])[0].get("id")
            cls.cust_id = partner_info.get("cust_info", [{}])[0].get("id")
        
        if cls.init_data:
            cls.uom_id = cls.init_data.get("uom_info", {}).get("qty_uom_info", [{}])[0].get("uom_id")
            cls.default_addr_id = cls.init_data.get("address_info", {}).get("default_addr_id", 70035597)
        
        # 从交货缓存数据获取交货类型配置（销售交货单）
        # 注意：交货单类型配置在 del_config（del_init_sql.yaml）中
        cls.dn_type_id = None
        cls.dn_item_type_id = None
        
        if cls.del_cache_data:
            del_sql = cls.del_cache_data.get("del_config", {})
            dn_types = del_sql.get("dn_type_info", [])
            
            # 销售交货单类型是 STND_OUBN（标准出库），注意是 OUBN 不是 OUTBN
            cls.dn_type_id = next(
                (item.get("id") for item in dn_types if item.get("dn_type_code") == "STND_OUBN"),
                None
            )
            
            dn_item_types = del_sql.get("dn_item_type_info", [])
            cls.dn_item_type_id = next(
                (item.get("id") for item in dn_item_types if item.get("dn_item_type_code") == "s_revi"),
                None
            )
        
        if not cls.dn_type_id:
            cls.logger.warning("未找到交货单类型 STND_OUBN，请检查缓存数据")
        if not cls.dn_item_type_id:
            cls.logger.warning("未找到交货单行类型 s_revi，请检查缓存数据")
        
        cls.logger.info(f"手动标准销售交货单测试类初始化完成: dn_type_id={cls.dn_type_id}, dn_item_type_id={cls.dn_item_type_id}")
    
    

    @case_decorator(
        story="手动标准销售交货单",
        title="手动创建标准销售交货单",
        description="手动创建标准销售交货单（不依赖销售订单），验证创建成功，状态为草稿",
        severity="critical",
        file_level_order=1,
        tags=["交货", "销售交货单", "手动创建"]
    )
    def test_create_manual_dn(self):
        """手动创建标准销售交货单"""
        try:
            current_ts = int(datetime.now().timestamp() * 1000)
            
            api_path = self.get_api_path("DEL-交货单公共-创建交货单服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["dnType", "delClass", "invOrgId", "invLocId", "btClass", "planRecvDate", 
                 "delStatus", "dnItemList", "vendPrtnId", "sendContactInfo", "sendContactPhone",
                 "sendAddrId", "sendAddrDesc", "custPrtnId", "recvContactInfo", "recvContactPhone",
                 "recvAddrId", "recvAddrDesc", "remark"],
                ["params", "request"]
            )
            
            # 确保交货单类型ID存在
            if not self.dn_type_id:
                raise ValueError("交货单类型ID为空，无法创建交货单")
            
            set_dict = {
                "dnType": {"id": self.dn_type_id},
                "delClass": "SEND",  # 销售交货单是发货（SEND），采购交货单是收货（RECV）
                "invOrgId": {"id": self.inv_org_id},
                "invLocId": {"id": self.inv_loc_id},
                "btClass": "SLS",  # 销售交货单业务类型
                "planSendDate": current_ts,  # 销售交货单关注发货日期
                "planRecvDate": None,
                "delStatus": "DRAFT",
                "dnItemList": [
                    {
                        "dnItemTypeId": {"id": self.dn_item_type_id},
                        "matId": {"id": self.mat_id},
                        "baseUnit": {"id": self.uom_id},
                        "dnDelUnit": {"id": self.uom_id},
                        "planDelQty": self.PLAN_DEL_QTY,
                        "batchInfo": None
                    }
                ],
                "custPrtnId": {"id": self.cust_id},  # 销售交货单主要关联客户
                "sendContactInfo": "自动化测试发货联系人",
                "sendContactPhone": "18808080808",
                "sendAddrId": {"id": self.default_addr_id},
                "sendAddrDesc": "自动化测试发货地址",
                "recvContactInfo": "自动化测试收货联系人",
                "recvContactPhone": "18808080808",
                "recvAddrId": {"id": self.default_addr_id},
                "recvAddrDesc": "自动化测试收货地址",
                "expressList": None,
                "remark": self.TEST_REMARK,
                "delPartnerList": None,
                "delAttachmentList": None,
                "delTextList": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="DEL-交货单公共-创建交货单服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 从数据库查询刚创建的交货单
            query_sql = """
                SELECT id, dn_code, del_status 
                FROM del_dn_head_tr 
                WHERE remark = %s 
                ORDER BY created_at DESC 
                LIMIT 1
            """
            db_result = self.query_service.query(query_sql, [self.TEST_REMARK])
            
            if not db_result:
                raise ValueError("未在数据库中找到刚创建的交货单")
            
            result = db_result[0]
            self.__class__.dn_id = result.get("id")
            self.__class__.dn_code = result.get("dn_code")
            del_status = result.get("del_status")
            
            assert self.__class__.dn_id, "交货单ID不能为空"
            assert self.__class__.dn_code, "交货单编码不能为空"
            assert del_status == "DRAFT", f"交货单状态不符合预期: 期望=DRAFT, 实际={del_status}"
            
            a.text(
                f"交货单ID: {self.__class__.dn_id}\n"
                f"交货单编码: {self.__class__.dn_code}\n"
                f"交货状态: {del_status}\n"
                f"计划交货数量: {self.PLAN_DEL_QTY}",
                "交货单信息"
            )
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="手动标准销售交货单",
        title="提交销售交货单",
        description="提交草稿态的销售交货单，验证状态变更为生效态",
        severity="critical",
        file_level_order=2,
        tags=["交货", "销售交货单", "提交"]
    )
    def test_submit_manual_dn(self):
        """提交销售交货单"""
        try:
            if not self.__class__.dn_id:
                self._ensure_create_manual_dn()
            
            api_path = self.get_api_path("DEL-交货单公共-交货单提交业务处理服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_id})
            
            response, _ = self.standard_api_call(
                api_key="DEL-交货单公共-交货单提交业务处理服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 从数据库验证状态
            query_sql = """
                SELECT del_status, dn_code 
                FROM del_dn_head_tr 
                WHERE id = %s
            """
            db_result = self.query_service.query(query_sql, [self.__class__.dn_id])
            
            if not db_result:
                raise ValueError(f"未在数据库中找到交货单: id={self.__class__.dn_id}")
            
            result = db_result[0]
            actual_status = result.get("del_status")
            actual_dn_code = result.get("dn_code")
            
            assert actual_status == "INEFFECT", f"交货单状态应为生效态: {actual_status}"
            assert actual_dn_code == self.__class__.dn_code, \
                f"交货单编码不匹配: 期望={self.__class__.dn_code}, 实际={actual_dn_code}"
            
            a.text(
                f"交货单ID: {self.__class__.dn_id}\n"
                f"交货单编码: {self.__class__.dn_code}\n"
                f"数据库状态: {actual_status}",
                "提交结果"
            )
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="手动标准销售交货单",
        title="作废销售交货单",
        description="作废生效态的销售交货单，验证状态变更为作废态",
        severity="critical",
        file_level_order=3,
        tags=["交货", "销售交货单", "作废"]
    )
    def test_discard_manual_dn(self):
        """作废销售交货单"""
        try:
            if not self.__class__.dn_id:
                self._ensure_create_manual_dn()
                self._ensure_submit_manual_dn()
            
            api_path = self.get_api_path("DEL-交货单作废服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.dn_id})
            
            response, _ = self.standard_api_call(
                api_key="DEL-交货单作废服务",
                set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 从数据库验证状态
            query_sql = """
                SELECT del_status, dn_code 
                FROM del_dn_head_tr 
                WHERE id = %s
            """
            db_result = self.query_service.query(query_sql, [self.__class__.dn_id])
            
            if not db_result:
                raise ValueError(f"未在数据库中找到交货单: id={self.__class__.dn_id}")
            
            result = db_result[0]
            actual_status = result.get("del_status")
            actual_dn_code = result.get("dn_code")
            
            assert actual_status == "DISCARDED", f"交货单状态应为作废态: {actual_status}"
            assert actual_dn_code == self.__class__.dn_code, \
                f"交货单编码不匹配: 期望={self.__class__.dn_code}, 实际={actual_dn_code}"
            
            a.text(
                f"交货单ID: {self.__class__.dn_id}\n"
                f"交货单编码: {self.__class__.dn_code}\n"
                f"数据库状态: {actual_status}",
                "作废结果"
            )
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
