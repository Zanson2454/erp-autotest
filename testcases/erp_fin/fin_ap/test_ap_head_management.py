# -*- coding: utf-8 -*-
"""
应付单管理测试用例
包含：应付单分页查询、应付单详情查询、应付单新建等
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_fin.fin_ap import ApBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP业财集成-应付单")
@allure.feature("应付单管理")
class TestApHeadManagement(ApBaseTest):
    """应付单管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.ap_head_id = None
        cls.ap_head_detail = None
        cls.ap_head_save_body = None
        cls.logger.info("应付单管理测试类初始化完成")
        
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 应付单数据通常不需要清理，因为它们是业务单据
            # 如果需要清理，请根据实际业务需求添加清理逻辑
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单分页查询",
        description="验证应付单分页查询功能",
        severity="critical",
        file_level_order=3,
        smoke=True,
        tags=["应付单", "分页查询"]
    )
    def test_query_ap_head_page(self):
        """测试应付单分页查询"""
        try:
            # 1. 准备分页查询参数
            # 根据curl请求，params.request中包含pageableDTO和pageable两个字段
            # 根据规范，提取params.request内部的字段作为set_dict的根
            # 根据API配置，还需要包含enableUserPartner字段
            set_dict = {
                "enableUserPartner": False,
                "pageableDTO": {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": None,
                        "conditionGroup": None,
                        "keyword": None
                    }
                },
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
            }
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="应付单分页查询服务",
                set_dict=set_dict
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 验证分页结果
            data_list = response.get("data", {}).get("data", {}).get("data", [])
            total_count = response.get("data", {}).get("data", {}).get("total", 0)
            
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            self.assert_util.assert_by_operator(len(data_list), "<=", 20, "每页记录数不应超过20")
            
            # 5. 记录关键数据
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            a.text(f"✅ 分页查询成功，共 {total_count} 条记录，当前页 {len(data_list)} 条", "查询结果")
            
            # 6. 保存第一个ID供详情查询使用
            if data_list and len(data_list) > 0:
                self.ap_head_id = data_list[0].get("id")
                a.text(f"保存应付单ID: {self.ap_head_id}", "数据准备")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单详情查询",
        description="验证应付单详情查询功能",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["应付单", "详情查询"]
    )
    def test_query_ap_head_detail(self):
        """测试应付单详情查询"""
        try:
            # 1. 确保有数据ID（从分页查询获取）
            if not self.ap_head_id:
                self.test_create_ap_head()
            
            # 2. 准备详情查询参数
            set_dict = {"id": self.ap_head_id}
            self.logger.debug(f"set_dict: {set_dict}")
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="应付单详情查询服务",
                set_dict=set_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 5. 验证返回的数据
            self.ap_head_detail = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(self.ap_head_detail, "not_empty", "详情数据不应为空")
            
            # 6. 记录关键数据
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            a.text(f"✅ 详情查询成功，应付单ID: {self.ap_head_id}", "查询结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    
    def _build_ap_head_base(self):
        """
        构建应付单头基础数据
        """
        ap_date = self.mock_util.get_timestamp(timestamp=True)
        return {
            "docTypeId": {"id":self.ap_type_stnd_id},
            "comOrgId": {"id":self.gr_com_org_id},
            "purOrgId": {"id":self.pur_org_id},
            "payOrgId": {"id":self.gr_com_org_id},
            "apDate": ap_date,
            "settPartnerId": {"id":self.vend_id},
            "remark": f"自动化创建_{self.mock_util.get_timestamp(timestamp=True)}",
            "extPoId": None,
            "extPoSoCode": None,
            "apHeadCode": None,
            "settPartnerType": "SUPPLIER",
            "apStatus": None,
            "createType": None,
            "payClearingStatus": "UNCLEARED",
            "invClearingStatus": "UNCLEARED",
            "headOffsetStatus": "UNOFFSET",
            "purEmployeeId": None,
            "apItems": [],
            "apSchls": [],
            "netBaseAmt": None,
            "grossBaseAmt": None,
            "netDocAmt": None,
            "docCurrId": {"id":self.curr_id},
            "baseCurrId": {"id":self.curr_id},
            "grossDocAmt": None,
            "exchRate": 1
        }
    
    def _build_ap_item(self):
        """
        构建应付单行数据（apItem）
        注意：金额计算必须使用round()控制精度，避免浮点数精度误差导致系统校验失败
        """
        apQty = self.mock_util.get_mock_qty()
        grossDocPrice = self.mock_util.get_mock_price()
        # 含税金额 = 数量 × 含税单价（保留2位小数）
        grossDocAmt = round(apQty * grossDocPrice, 2)
        taxRate = 13
        # 税额 = 含税金额 × 税率 / (100 + 税率)（保留2位小数）
        taxAmt = round(grossDocAmt * taxRate / (100 + taxRate), 2)
        # 不含税金额 = 含税金额 - 税额（保留2位小数）
        netDocAmt = round(grossDocAmt - taxAmt, 2)
        # 本位币金额：如果汇率=1，本位币金额等于单据金额；否则需要换算
        # 由于exchRate=1，本位币金额等于单据金额（保留2位小数）
        netBaseAmt = round(netDocAmt, 2)
        grossBaseAmt = round(grossDocAmt, 2)
        return {
            "matId": {"id": self.mat_id},
            "apQty": apQty,
            "grossDocPrice": grossDocPrice,
            "taxRate": taxRate,
            "grossDocAmt": grossDocAmt,
            "netDocAmt": netDocAmt,
            "netBaseAmt": netBaseAmt,
            "grossBaseAmt": grossBaseAmt,
            "taxAmt": taxAmt,
            "settItemTypeId": {"id": self.sett_item_type_E_PUR_GOODS_id},
            "taxCodeId": {"id": self.tax_code_id}
        }
    
    def _build_ap_head_for_init(self):
        """
        构建用于初始化应付计划行的应付单头数据
        
        Args:
            base_data: 基础数据字典（包含vend_id, mat_id, curr_id）
            ap_date: 应付单日期（时间戳）
            remark: 备注
            ap_items: 应付单行数据列表
        
        Returns:
            dict: 应付单头数据
        """
        ap_base_body = self._build_ap_head_base()
        ap_items= [self._build_ap_item()]
        init_body = {
            **ap_base_body,
            "apItems": ap_items,
            "apSchls": [],
        }
        return init_body
    
    def _extract_id_from_obj(self, obj):
        """
        从嵌套对象中提取id，如果对象不存在则返回None
        
        Args:
            obj: 可能是字典对象，包含id字段
        
        Returns:
            dict: {"id": id} 或 None
        """
        if obj and isinstance(obj, dict) and obj.get("id"):
            return {"id": obj.get("id")}
        return None
    
    

    @case_decorator(
        story="应付单管理",
        title="测试应付单新建过程，应付计划行初始化并回填应付单头",
        description="验证应付单新建过程，应付计划行初始化并回填应付单头",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["应付单", "新建", "创建", "初始化"]
    )
    def test_ap_schls_init(self):
        """
        测试应付计划行初始化并回填应付单头
        """
        try:
            ap_head_for_init = self._build_ap_head_for_init()
            ap_schls_init_response, _ = self.standard_api_call(
                api_key="AP-应付计划行初始化服务",
                set_dict=ap_head_for_init
                )
            self.assert_util.assert_response_data(ap_schls_init_response)
            self.logger.debug(f"ap_schls_init_response: {ap_schls_init_response}")
            ap_schls = ap_schls_init_response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(ap_schls, "not_empty", "应付计划行初始化失败，未返回apSchls数据")
            init_body = ap_head_for_init.copy()
            init_body["apSchls"] = ap_schls
            self.ap_head_save_body = init_body
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单新建",
        description="验证应付单新建功能",
        severity="critical",
        file_level_order=2,
        smoke=True,
        tags=["应付单", "新建", "创建"]
    )
    def test_create_ap_head(self):
        """测试应付单新建"""
        try:
            if not self.ap_head_save_body:
                self.test_ap_schls_init()
            
            # 调用保存接口
            save_response, saved_id = self.standard_api_call(
                api_key="AP-应付保存服务",
                set_dict=self.ap_head_save_body,
                store_id_as="ap_head"
            )
            
            # 业务断言
            self.assert_util.assert_response_data(save_response)
            
            # 10. 验证保存的数据
            self.ap_head_id = save_response.get("data", {}).get("data", {}).get("id")
            self.assert_util.assert_by_operator(self.ap_head_id, "not_empty", "保存的应付单数据不应为空")      
            # 11. 记录关键数据
            a.json(self.ap_head_save_body, "保存请求数据")
            a.json(save_response, "保存响应数据")
            a.text(f"✅ 应付单新建成功，应付单ID: {self.ap_head_id}", "创建结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单提交",
        description="验证应付单提交功能",
        severity="critical",
        file_level_order=5,
        smoke=True,
        tags=["应付单", "提交"]
    )
    def test_submit_ap_head(self):
        """测试应付单提交"""
        try:
            # 1. 确保有数据（先创建，再查询详情）
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            # 2. 准备提交参数
            # 从详情数据中提取必要字段，移除系统字段，简化嵌套对象
            submit_dict =self.ap_head_detail
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="AP-应付单-列表提交服务",
                set_dict=submit_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            
            
            # 5. 记录关键数据
            a.json(submit_dict, "提交请求数据")
            a.json(response, "提交响应数据")
            a.text(f"✅ 应付单提交成功，应付单ID: {self.ap_head_id}, 应付单编号: {submit_dict.get('apHeadCode')}", "提交结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单提交撤回",
        description="验证应付单提交撤回功能",
        severity="critical",
        file_level_order=6,
        smoke=True,
        tags=["应付单", "提交撤回", "撤回"]
    )
    def test_submit_rollback_ap_head(self):
        """测试应付单提交撤回"""
        try:
            # 1. 确保有已提交的应付单（先创建、查询详情、提交）
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            current_status = self.ap_head_detail.get("apStatus")
            if current_status != "CONFIRM":
                # 如果状态不是已提交，先执行提交
                self.test_submit_ap_head()
                # 提交后重新查询详情
                self.test_query_ap_head_detail()
            
            # 2. 准备撤回参数
            # 从详情数据中提取必要字段，移除系统字段，简化嵌套对象
            rollback_dict = self.ap_head_detail.copy()
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="AP-应付撤回服务",
                set_dict=rollback_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证撤回后状态（可选：重新查询详情验证状态变为DRAFT）
            # 重新查询详情验证状态
            detail_response, _ = self.standard_api_call(
                api_key="应付单详情查询服务",
                set_dict={"id": self.ap_head_id}
            )
            self.assert_util.assert_response_data(detail_response)
            updated_detail = detail_response.get("data", {}).get("data", {})
            updated_status = updated_detail.get("apStatus")
            
            # 6. 记录关键数据
            a.json(rollback_dict, "撤回请求数据")
            a.json(response, "撤回响应数据")
            a.text(
                f"✅ 应付单提交撤回成功，应付单ID: {self.ap_head_id}, "
                f"应付单编号: {rollback_dict.get('apHeadCode')}, "
                f"撤回前状态: CONFIRM, 撤回后状态: {updated_status}",
                "撤回结果"
            )
            
            # 更新详情数据
            self.ap_head_detail = updated_detail
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单删除",
        description="验证应付单删除功能",
        severity="critical",
        file_level_order=16,
        tags=["应付单", "删除"]
    )
    def test_delete_ap_head(self):
        """测试应付单删除"""
        try:
            # 1. 确保有数据ID（如果没有则先创建）
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            # 2. 准备删除参数
            set_dict = self.ap_head_detail
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="AP-应付单删除服务",
                set_dict=set_dict
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 记录关键数据
            a.json(set_dict, "删除请求数据")
            a.json(response, "删除响应数据")
            a.text(f"✅ 应付单删除成功，应付单ID: {self.ap_head_id}", "删除结果")
            
            # 6. 清空ID，避免后续测试使用已删除的数据
            self.ap_head_id = None
            self.ap_head_detail = None
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="应付单管理",
        title="测试应付单批量删除",
        description="验证应付单批量删除功能",
        severity="critical",
        file_level_order=17,
        tags=["应付单", "批量删除"]
    )
    def test_batch_delete_ap_head(self):
        """测试应付单批量删除"""
        try:
            if not self.ap_head_id:
                self.test_create_ap_head()
                self.test_query_ap_head_detail()
            
            set_dict = {"request": [self.ap_head_detail]}
          
            # 3. 使用标准化API调用
            # 注意：对于数组类型的set_dict，standard_api_call会自动处理
            response, _ = self.standard_api_call(
                api_key="AP-应付单批量删除服务",
                set_dict=set_dict,
                param_path=["params"]
                
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 记录关键数据
            a.json(set_dict, "批量删除请求数据")
            a.json(response, "批量删除响应数据")
            a.text(
                f"✅ 应付单批量删除成功，共删除 1 条应付单，ID: {self.ap_head_id}",
                "批量删除结果"
            )
            
            # 6. 清空ID列表，避免后续测试使用已删除的数据
            self.ap_head_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise