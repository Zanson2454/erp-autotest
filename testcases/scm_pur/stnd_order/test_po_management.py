import allure
import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_pur import ScmPurBaseTest
from utils.report_util import a, case_decorator
from data_factory.pur_po_factory import PurPoFactory
from utils.param_util import ParamUtil


@allure.epic("采购管理")
@allure.feature("标准采购订单")
class TestPoManagement(ScmPurBaseTest):
    """标准采购订单测试类"""
    
    # 测试数据标识常量
    TEST_REMARK = "执行自动化测试备注"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.po_id = None
        cls.po_code = None
        cls.pur_remark = None
        
        if cls.md_cache_data:
            mat_info = cls.md_cache_data.get("mat_info", {}).get("mat_md", {}).get("FINP", [{}])[0]
            org_info = cls.md_cache_data.get("org_info", {})
            partner_info = cls.md_cache_data.get("partner_info", {})
            
            cls.mat_id = mat_info.get("id")
            cls.mat_code = mat_info.get("mat_code")
            cls.inv_org_id = org_info.get("inv_org_info", [{}])[0].get("id")
            cls.inv_loc_id = org_info.get("inv_loc_info", [{}])[0].get("id")
            cls.pur_org_id = org_info.get("pur_org_info", [{}])[0].get("id")
            cls.com_org_id = org_info.get("gr_come_org_info", [{}])[0].get("id")
            cls.vend_id = partner_info.get("vend_info", [{}])[0].get("id")
            cls.pur_employee_id = org_info.get("employee_info", [{}])[0].get("id")
        
        if cls.init_data:
            cls.pur_curr_id = cls.init_data.get("currency_info", [{}])[0].get("curr_id")
            cls.uom_pur_id = cls.init_data.get("uom_info", {}).get("qty_uom_info", [{}])[0].get("uom_id")
            cls.tax_rate_id = cls.init_data.get("tax_info", [{}])[0].get("id")
        
        if cls.pur_cache_data:
            pur_config = cls.pur_cache_data.get("pur_config", {})
            cls.po_type_id = pur_config.get("po_type_info", [{}])[0].get("id")
            
            po_item_types = pur_config.get("po_item_type_info", [])
            cls.po_item_type_id = next(
                (item.get("id") for item in po_item_types if item.get("po_item_type") == "STND"),
                None
            )
        
        cls.logger.info("标准采购订单测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="pur_po_head_tr",
                where="pur_remark like %s",
                params=[f"%{cls.TEST_REMARK}%"]
            )
            cls.db.delete(
                table="pur_po_item_tr",
                where="note like %s",
                params=[f"%{cls.TEST_REMARK}%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    def _get_po_detail_by_id(self, po_id):
        """根据订单ID获取完整订单详情对象"""
        api_path = self.get_api_path("(系统)查询数据详情服务")
        _, url = self.get_api_params(api_path)
        
        params = {
            "serviceKey": "SCM_PUR$SYS_FindDataByIdService",
            "params": {
                "request": {"id": po_id},
                "modelKey": "SCM_PUR$pur_po_head_tr"
            }
        }
        
        response = self.http.post(
            url,
            json=params,
            params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$pur_po_head_tr"}
        )
        self.assert_util.assert_response_data(response)
        
        po_detail = response.get("data", {}).get("data", {})
        if not po_detail:
            raise ValueError(f"未获取到订单详情数据: po_id={po_id}")
        
        return po_detail
    
    def _verify_po_status(self, expected_status, status_desc):
        """验证订单状态的公共方法"""
        query_sql = "SELECT id, document_status, deleted FROM pur_po_head_tr WHERE id = %s"
        result = self.db.query(query_sql, [self.__class__.po_id])
        
        assert result, "数据库未查询到订单数据"
        
        document_status = result[0].get("document_status")
        assert document_status == expected_status, \
            f"订单状态不符合预期: 期望={expected_status}, 实际={document_status}"
        
        self.logger.info(f"订单{status_desc}成功: po_id={self.__class__.po_id}, status={document_status}")
        return result
    
    @case_decorator(
        story="标准采购订单",
        title="创建标准采购订单",
        description="创建标准采购订单,验证创建成功",
        severity="critical",
        file_level_order=1,
        tags=["采购", "标准订单", "创建"]
    )
    def test_create_standard_po(self):
        """测试创建标准采购订单"""
        try:
            current_ts = int(datetime.now().timestamp() * 1000)
            
            mat_items = [{
                "mat_id": str(self.mat_id),
                "mat_code": self.mat_code,
                "inv_org_id": str(self.inv_org_id),
                "inv_loc_id": str(self.inv_loc_id),
                "uom_pur_id": str(self.uom_pur_id),
                "qty": 12,
                "price": 11,
                "po_item_type_id": str(self.po_item_type_id),
                "tax_rate_id": str(self.tax_rate_id),
                "delivery_date": current_ts,
                "note": self.TEST_REMARK
            }]
            
            po_factory = PurPoFactory(
                http_client=self.http,
                apis=self.apis,
                api_params=self.api_params,
                mock_util=self.mock_util,
                logger=self.logger,
                init_data=self.init_data,
                md_cache_data=self.md_cache_data,
                pur_cache_data=self.pur_cache_data
            )
            
            result = po_factory.create_standard_po(
                mat_items=mat_items,
                business_date=current_ts,
                pur_remark=self.TEST_REMARK
            )
            
            self.__class__.pur_remark = self.TEST_REMARK
            self.logger.info(f"采购订单创建成功，备注: {self.TEST_REMARK}")
            a.json(result.get("response", {}), "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="查询采购订单列表",
        description="查询采购订单列表,获取第一条数据的ID和编码",
        severity="critical",
        file_level_order=2,
        tags=["采购", "标准订单", "查询"]
    )
    def test_query_po_list(self):
        """测试查询采购订单列表"""
        try:
            api_path = self.get_api_path("采购订单分页查询ACTION服务")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable", "fields", "systemParams"],
                ["params", "request"]
            )
            
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {"fieldAlias": "updatedAt", "sortType": "DESC"},
                        {"fieldAlias": "createdAt", "sortType": "DESC"}
                    ],
                    "conditionItems": None
                },
                "fields": [
                    {"name": "poCode", "type": "TEXT"},
                    {"name": "poType", "type": "OBJECT"},
                    {"name": "vendId", "type": "OBJECT"},
                    {"name": "documentStatus", "type": "SELECT"},
                    {"name": "businessStatus", "type": "SELECT"},
                    {"name": "comOrgId", "type": "OBJECT"},
                    {"name": "purOrgId", "type": "OBJECT"},
                    {"name": "invOrgId", "type": "OBJECT"},
                    {"name": "poStatusDel", "type": "SELECT"},
                    {"name": "createdBy", "type": "OBJECT"},
                    {"name": "updatedBy", "type": "OBJECT"}
                ],
                "systemParams": None
            })
            
            response = self.http.post(
                url,
                json=filtered_params,
                params={"tmodule": "SCM_PUR"}
            )
            self.assert_util.assert_response_data(response)
            
            records = response.get("data", {}).get("data", {}).get("data", [])
            assert records, "未查询到采购订单数据"
            
            first_record = records[0]
            self.__class__.po_id = first_record.get("id")
            self.__class__.po_code = first_record.get("poCode")
            pur_remark = first_record.get("purRemark")
            document_status = first_record.get("documentStatus")
            
            assert document_status == "EFFECT", \
                f"单据状态不符合预期: 期望=EFFECT, 实际={document_status}"
            
            if self.__class__.pur_remark:
                assert pur_remark == self.__class__.pur_remark, \
                    f"采购备注不匹配: 期望={self.__class__.pur_remark}, 实际={pur_remark}"
            
            self.logger.info(
                f"查询列表成功: po_id={self.__class__.po_id}, "
                f"po_code={self.__class__.po_code}, status={document_status}"
            )
            
            a.text(
                f"订单ID: {self.__class__.po_id}\n"
                f"订单编码: {self.__class__.po_code}\n"
                f"备注: {pur_remark}\n"
                f"单据状态: {document_status}",
                "订单信息"
            )
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="查询采购订单详情",
        description="根据订单ID查询采购订单详情",
        severity="critical",
        file_level_order=3,
        tags=["采购", "标准订单", "查询"]
    )
    def test_query_po_detail(self):
        """测试查询采购订单详情"""
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            api_path = self.get_api_path("(系统)查询数据详情服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$SYS_FindDataByIdService",
                "params": {
                    "request": {"id": self.__class__.po_id},
                    "modelKey": "SCM_PUR$pur_po_head_tr"
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR", "modelKey": "SCM_PUR$pur_po_head_tr"}
            )
            
            self.assert_util.assert_response_data(response)
            
            result_data = response.get("data", {}).get("data", {})
            assert result_data, "详情数据为空"
            
            document_status = result_data.get("documentStatus")
            assert document_status == "EFFECT", \
                f"单据状态不符合预期: 期望=EFFECT, 实际={document_status}"
            
            self.logger.info(
                f"订单详情查询成功: po_id={self.__class__.po_id}, "
                f"po_code={result_data.get('poCode')}, status={document_status}"
            )
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="作废采购订单",
        description="作废采购订单并验证状态",
        severity="critical",
        file_level_order=4,
        tags=["采购", "标准订单", "作废"]
    )
    def test_abolish_po(self):
        """测试作废采购订单"""
        try:
            if not self.__class__.po_id:
                self.test_query_po_list()
            
            api_path = self.get_api_path("PO-订单-作废服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_ABOLISHED_SERVICE",
                "params": {
                    "request": {"id": self.__class__.po_id}
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            result = self._verify_po_status("ABOLISH", "作废")
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="取消提交采购订单",
        description="创建新订单后取消提交并验证状态为草稿",
        severity="critical",
        file_level_order=5,
        tags=["采购", "标准订单", "取消提交"]
    )
    def test_cancel_submit_po(self):
        """测试取消提交采购订单"""
        try:
            self.test_create_standard_po()
            self.test_query_po_list()
            
            if not self.__class__.po_id:
                raise ValueError("创建订单后未获取到po_id")
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("PO-取消提交服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PUR_PO_CANCEL_SUBMIT_EVENT_SERVICE",
                "params": {
                    "request": po_detail
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            result = self._verify_po_status("DRAFT", "取消提交")
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="标准采购订单",
        title="删除采购订单",
        description="删除草稿状态的采购订单并验证deleted字段",
        severity="critical",
        file_level_order=6,
        tags=["采购", "标准订单", "删除"]
    )
    def test_delete_po(self):
        """测试删除采购订单"""
        try:
            if not self.__class__.po_id:
                raise ValueError("未找到可删除的订单ID")
            
            po_detail = self._get_po_detail_by_id(self.__class__.po_id)
            
            api_path = self.get_api_path("PO-删除订单服务")
            _, url = self.get_api_params(api_path)
            
            request_params = {
                "serviceKey": "SCM_PUR$PO_DELETE_DRAFT_PO_BY_ID_EVENT_SERVICE",
                "params": {
                    "request": po_detail
                }
            }
            
            response = self.http.post(
                url,
                json=request_params,
                params={"tmodule": "SCM_PUR"}
            )
            
            self.assert_util.assert_response_success(response)
            
            query_sql = "SELECT id, document_status, deleted FROM pur_po_head_tr WHERE id = %s"
            result = self.db.query(query_sql, [self.__class__.po_id])
            
            assert result, "数据库未查询到订单数据"
            
            deleted_value = result[0].get("deleted")
            assert deleted_value != 0, \
                f"订单删除标记不符合预期: 期望 deleted != 0, 实际 deleted={deleted_value}"
            
            self.logger.info(f"订单删除成功: po_id={self.__class__.po_id}, deleted={deleted_value}")
            
            a.json(request_params, "请求数据")
            a.json(response, "响应数据")
            a.text(f"数据库查询结果: {result}", "数据库验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise


 