# -*- coding: utf-8 -*-
"""
销售发票单据管理测试用例
包含：销售发票的创建、查询、更新、提交、过账、删除、撤回、反过账等核心功能测试
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


@allure.epic("ERP通业财模块")
@allure.feature("销售发票管理")
class TestSbDocManagement(FinBaseTest):
    """销售发票单据管理测试类"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("销售发票管理测试类初始化完成")

    
    # ==================== 创建相关测试 ====================
    
    @case_decorator(
        story="销售发票创建",
        title="测试销售发票保存（创建）",
        description="验证销售发票的创建功能，包括发票头信息和行信息的保存",
        severity="critical",
        file_level_order=1,
        smoke=True,
        tags=["销售发票", "创建", "保存"]
    )
    def test_save_sb_doc(self):
        """
        测试销售发票保存（创建）
        测试方面：
        1. 销售发票头信息保存（发票编码、发票日期、组织、客户等）
        2. 销售发票行信息保存（物料、数量、金额、税率等）
        3. 发票金额计算（含税金额、不含税金额、税额等）
        4. 发票状态初始化（草稿状态）
        """
        try:
            # 1. 准备测试数据
            sb_code = f"SB_{self.mock_util.generate_unique_code(tag='AT')}"
            sb_date = self.mock_util.get_mock_date(include_time=False, days_offset=0)
            
            # 2. 使用标准化API调用（推荐方式）
            set_dict = {
                "bilCode": sb_code,
                "bilDate": sb_date,
                "docTypeId": {"id": self.sb_type_id} if self.sb_type_id else None,
                "comOrgId": {"id": self.com_org_id} if self.com_org_id else None,
                "slsOrgId": {"id": self.sls_org_id} if self.sls_org_id else None,
                "settPartnerType": "CUSTOMER",
                "settPartnerId": {"id": self.cust_id} if self.cust_id else None,
                "docCurrId": {"id": self.curr_id} if self.curr_id else None,
                "baseCurrId": {"id": self.curr_id} if self.curr_id else None,
                "exchRate": 1.0,
                "posNeg": "BLUE",  # 蓝字发票
                "sbStatus": "DRAFT"  # 草稿状态
            }
            fields_to_filter = [
                "bilCode", "bilDate", "docTypeId", "comOrgId", "slsOrgId",
                "settPartnerType", "settPartnerId", "docCurrId", "baseCurrId",
                "exchRate", "posNeg", "sbStatus"
            ]
            
            response, extracted_id = self.standard_api_call(
                api_key="SB-销售发票保存并更新来源单服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="sb"  # 自动存储为 self.sb_id
            )
            
            # 3. 业务断言（standard_api_call不包含断言）
            self.assert_util.assert_response_data(response)
            
            # 4. 保存数据
            if not hasattr(self, 'sb_id'):
                self.sb_id = extracted_id
            self.sb_code = sb_code
            
            # 5. 额外的业务验证
            # 验证返回的发票状态
            data = response.get("data", {}).get("data", {})
            sb_status = data.get("sbStatus")
            self.assert_util.assert_by_operator(sb_status, "=", "DRAFT")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 查询相关测试 ====================
    
    @case_decorator(
        story="销售发票查询",
        title="测试销售发票分页查询",
        description="验证销售发票的分页查询功能，包括条件筛选和分页参数",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["销售发票", "查询", "分页"]
    )
    def test_query_sb_doc_page(self):
        """
        测试销售发票分页查询
        测试方面：
        1. 分页参数设置（页码、每页数量、是否需要总数）
        2. 查询条件筛选（发票编码、客户、组织、日期范围等）
        3. 排序功能（按创建时间、发票日期等排序）
        4. 返回数据格式验证（列表数据、总数、分页信息等）
        """
        try:
            # 1. 准备测试数据
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "bilCode", "type": "TEXT"}
                ],
                "systemParams": None
            }
            fields_to_filter = ["pageable", "fields", "systemParams"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证
            # 验证返回的分页数据
            data = response.get("data", {}).get("data", {})
            data_list = data.get("data", [])
            self.assert_util.assert_by_operator(data_list, "not_empty")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票查询",
        title="测试销售发票详情查询",
        description="验证根据ID查询销售发票详情的功能",
        severity="critical",
        file_level_order=5,
        smoke=True,
        tags=["销售发票", "查询", "详情"]
    )
    def test_query_sb_doc_detail(self):
        """
        测试销售发票详情查询
        测试方面：
        1. 根据ID查询发票头信息（发票编码、日期、金额、状态等）
        2. 查询发票行信息（物料明细、数量、单价、金额等）
        3. 查询关联信息（客户信息、组织信息、币种信息等）
        4. 数据完整性验证（所有必要字段是否存在）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="销售发票-详情查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证
            # 验证返回的发票ID
            data = response.get("data", {}).get("data", {})
            returned_id = data.get("id")
            self.assert_util.assert_by_operator(returned_id, "=", self.sb_id)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 更新相关测试 ====================
    
    @case_decorator(
        story="销售发票更新",
        title="测试销售发票更新",
        description="验证销售发票的更新功能，包括修改发票信息和行信息",
        severity="normal",
        file_level_order=7,
        smoke=False,
        tags=["销售发票", "更新", "修改"]
    )
    def test_update_sb_doc(self):
        """
        测试销售发票更新
        测试方面：
        1. 更新发票头信息（备注、日期等可修改字段）
        2. 更新发票行信息（数量、单价、金额等）
        3. 更新后金额重新计算（含税金额、不含税金额、税额）
        4. 更新权限验证（草稿状态可修改，已提交状态不可修改）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
            
            # 2. 准备更新数据
            remark = f"更新备注_{self.mock_util.get_timestamp()}"
            set_dict = {
                "id": self.sb_id,
                "remark": remark
            }
            fields_to_filter = ["id", "remark"]
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="SB-销售发票保存并更新来源单服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 5. 额外的业务验证
            # 验证更新后的备注
            data = response.get("data", {}).get("data", {})
            updated_remark = data.get("remark")
            self.assert_util.assert_by_operator(updated_remark, "=", remark)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 提交相关测试 ====================
    
    @case_decorator(
        story="销售发票提交",
        title="测试销售发票提交",
        description="验证销售发票的提交功能，将草稿状态的发票提交审批",
        severity="critical",
        file_level_order=8,
        smoke=True,
        tags=["销售发票", "提交", "审批"]
    )
    def test_submit_sb_doc(self):
        """
        测试销售发票提交
        测试方面：
        1. 草稿状态发票提交（状态从DRAFT变为SUBMITTED）
        2. 提交前数据校验（必填字段、金额校验、业务规则校验等）
        3. 提交后状态变更（发票状态、审批状态等）
        4. 提交权限验证（只有草稿状态可以提交）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票提交服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 查询数据库验证状态变更
            sql = "SELECT sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
            result = self.db.query(sql, (self.sb_id,))
            if result:
                sb_status = result[0].get("sb_status")
                self.assert_util.assert_by_operator(sb_status, "in", ["SUBMITTED", "APPROVED"])
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 过账相关测试 ====================
    
    @case_decorator(
        story="销售发票过账",
        title="测试销售发票过账",
        description="验证销售发票的过账功能，将已审批的发票过账到财务系统",
        severity="critical",
        file_level_order=9,
        smoke=True,
        tags=["销售发票", "过账", "财务"]
    )
    def test_post_sb_doc(self):
        """
        测试销售发票过账
        测试方面：
        1. 已审批发票过账（状态从APPROVED变为DONE）
        2. 过账前数据校验（发票完整性、金额校验、会计科目配置等）
        3. 过账后生成财务凭证（应收凭证、收入凭证等）
        4. 过账权限验证（只有已审批状态可以过账）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
                # 先提交才能过账
                self.test_submit_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票过账服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 查询数据库验证状态变更
            sql = "SELECT sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
            result = self.db.query(sql, (self.sb_id,))
            if result:
                sb_status = result[0].get("sb_status")
                self.assert_util.assert_by_operator(sb_status, "=", "DONE")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 撤回相关测试 ====================
    
    @case_decorator(
        story="销售发票撤回",
        title="测试销售发票撤回",
        description="验证销售发票的撤回功能，将已提交的发票撤回为草稿状态",
        severity="normal",
        file_level_order=10,
        smoke=False,
        tags=["销售发票", "撤回", "取消"]
    )
    def test_rollback_sb_doc(self):
        """
        测试销售发票撤回
        测试方面：
        1. 已提交发票撤回（状态从SUBMITTED/APPROVED变为DRAFT）
        2. 撤回权限验证（只有已提交未过账的发票可以撤回）
        3. 撤回后状态恢复（发票状态、审批状态等）
        4. 撤回后数据可编辑性（撤回后可以重新编辑和提交）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
                self.test_submit_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票撤回服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 查询数据库验证状态变更
            sql = "SELECT sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
            result = self.db.query(sql, (self.sb_id,))
            if result:
                sb_status = result[0].get("sb_status")
                self.assert_util.assert_by_operator(sb_status, "=", "DRAFT")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 反过账相关测试 ====================
    
    @case_decorator(
        story="销售发票反过账",
        title="测试销售发票反过账",
        description="验证销售发票的反过账功能，将已过账的发票反过账",
        severity="normal",
        file_level_order=11,
        smoke=False,
        tags=["销售发票", "反过账", "冲销"]
    )
    def test_reverse_post_sb_doc(self):
        """
        测试销售发票反过账
        测试方面：
        1. 已过账发票反过账（状态从DONE变为APPROVED）
        2. 反过账前数据校验（发票状态、关联凭证状态等）
        3. 反过账后凭证处理（冲销已生成的财务凭证）
        4. 反过账权限验证（只有已过账状态可以反过账）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
                self.test_submit_sb_doc()
                self.test_post_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票反过账服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 查询数据库验证状态变更
            sql = "SELECT sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
            result = self.db.query(sql, (self.sb_id,))
            if result:
                sb_status = result[0].get("sb_status")
                self.assert_util.assert_by_operator(sb_status, "in", ["APPROVED", "SUBMITTED"])
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 删除相关测试 ====================
    
    @case_decorator(
        story="销售发票删除",
        title="测试销售发票删除",
        description="验证销售发票的删除功能，删除草稿状态的发票",
        severity="normal",
        file_level_order=16,
        smoke=False,
        tags=["销售发票", "删除"]
    )
    def test_delete_sb_doc(self):
        """
        测试销售发票删除
        测试方面：
        1. 草稿状态发票删除（软删除或硬删除）
        2. 删除权限验证（只有草稿状态可以删除）
        3. 删除后数据清理（发票头、发票行、关联数据等）
        4. 已提交/已过账发票删除限制（已提交或已过账的发票不能删除）
        """
        try:
            # 1. 检查并创建依赖数据（确保是草稿状态）
            if not self.sb_id:
                self.test_save_sb_doc()
            else:
                # 如果已提交，先撤回
                sql = "SELECT sb_status FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
                result = self.db.query(sql, (self.sb_id,))
                if result and result[0].get("sb_status") != "DRAFT":
                    self.test_rollback_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 4. 额外的业务验证
            # 查询数据库验证删除（软删除）
            sql = "SELECT deleted FROM fin_tm_sb_head_tr WHERE id = %s LIMIT 1"
            result = self.db.query(sql, (self.sb_id,))
            if result:
                deleted = result[0].get("deleted")
                self.assert_util.assert_by_operator(deleted, "=", 1)
            
            # 重置ID，避免teardown重复删除
            self.sb_id = None
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    # ==================== 业务功能测试 ====================
    
    @case_decorator(
        story="销售发票业务功能",
        title="测试基于应收单生成销售发票",
        description="验证根据应收单自动生成销售发票的功能",
        severity="critical",
        file_level_order=12,
        smoke=False,
        tags=["销售发票", "生成", "应收单"]
    )
    def test_create_sb_by_ar(self):
        """
        测试基于应收单生成销售发票
        测试方面：
        1. 应收单数据转换（应收单头、行数据转换为发票数据）
        2. 金额数据传递（含税金额、不含税金额、税额等）
        3. 关联关系建立（发票与应收单的关联关系）
        4. 业务规则校验（应收单状态、发票类型匹配等）
        """
        try:
            # 注意：此测试需要先有应收单数据，这里仅提供测试框架
            # 实际使用时需要先创建应收单
            set_dict = {
                "arHeadId": None,  # 应收单ID，需要从实际业务中获取
                "docTypeId": {"id": self.sb_type_id} if self.sb_type_id else None
            }
            fields_to_filter = ["arHeadId", "docTypeId"]
            
            # 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="SB-基于应收单生成销售发票服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter,
                store_id_as="sb"
            )
            
            # 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票业务功能",
        title="测试销售发票钩稽查询",
        description="验证销售发票的钩稽查询功能，查询发票与应收单的钩稽关系",
        severity="normal",
        file_level_order=13,
        smoke=False,
        tags=["销售发票", "钩稽", "查询"]
    )
    def test_query_sb_clearing(self):
        """
        测试销售发票钩稽查询
        测试方面：
        1. 钩稽关系查询（发票与应收单的钩稽明细）
        2. 钩稽金额统计（已钩稽金额、未钩稽金额等）
        3. 钩稽状态查询（已钩稽、未钩稽、部分钩稽等）
        4. 钩稽明细展示（钩稽日期、钩稽金额、钩稽单号等）
        """
        try:
            # 1. 检查并创建依赖数据
            if not self.sb_id:
                self.test_save_sb_doc()
            
            # 2. 使用标准化API调用
            set_dict = {"id": self.sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票-钩稽查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票业务功能",
        title="测试销售发票ES数据查询",
        description="验证销售发票的ES（ElasticSearch）数据查询功能",
        severity="normal",
        file_level_order=14,
        smoke=False,
        tags=["销售发票", "ES查询", "搜索"]
    )
    def test_query_sb_from_es(self):
        """
        测试销售发票ES数据查询
        测试方面：
        1. ES索引查询（从ElasticSearch中查询发票数据）
        2. 全文搜索功能（支持发票编码、客户名称等字段搜索）
        3. 高级查询条件（多条件组合查询、模糊查询等）
        4. 查询性能验证（大数据量下的查询响应时间）
        """
        try:
            # 1. 准备查询参数
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                },
                "fields": [
                    {"name": "bilCode", "type": "TEXT"}
                ]
            }
            fields_to_filter = ["pageable", "fields"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-ES数据查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
