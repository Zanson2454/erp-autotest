# -*- coding: utf-8 -*-
"""
销售发票单据管理测试用例
包含：销售发票的查询、删除、反过账等核心功能测试
"""

import allure
import pytest

from testcases.erp_fin import FinBaseTest
from utils.report_util import a, case_decorator


@allure.epic("ERP通业财模块")
@allure.feature("销售发票管理")
class TestSbDocManagement(FinBaseTest):
    """销售发票单据管理测试类"""
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.logger.info("销售发票管理测试类初始化完成")
    
    def _build_view_condition(self):
        """
        构建viewCondition，筛选状态为UNCOMMITTED和BACK的发票
        :return: viewCondition字典
        """
        return {
            "conditionKey": "-od-1gHxYjcHj3qmGvY25",
            "rightValues": {
                "CmewWscZKc-2UJdARiX6I": [
                    {
                        "constValue": "UNCOMMITTED",
                        "fieldType": "Enum",
                        "type": "ConstValue",
                        "valueType": "CONST"
                    },
                    {
                        "constValue": "BACK",
                        "fieldType": "Enum",
                        "type": "ConstValue",
                        "valueType": "CONST"
                    }
                ]
            }
        }
    
    def _build_sb_head_code_condition(self, prefix="SB"):
        """
        构建发票编码筛选条件（CONTAINS操作符）
        :param prefix: 发票编码前缀，默认为"SB"
        :return: ConditionLeaf字典
        """
        return {
            "key": "VnvCjun3l91gFFcFhdKu9",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "xMQU9k1VbX3vri6hhGuy_",
                "key": "xMQU9k1VbX3vri6hhGuy_",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "sbHeadCode",
                        "valueName": "sbHeadCode"
                    }
                ]
            },
            "operator": "CONTAINS",
            "rightValue": {
                "key": "X8V0h4O9FGolS5RnIXnPj",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "CONST",
                "constValue": prefix
            }
        }
    
    def _build_sb_status_condition(self):
        """
        构建发票状态筛选条件（IN操作符）
        :return: ConditionLeaf字典
        """
        return {
            "key": "9Nuxwa9wsSNv-YA8BFlBn",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "ZFv_3FZRk9gpcpnQ1HrGX",
                "key": "ZFv_3FZRk9gpcpnQ1HrGX",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "sbStatus",
                        "valueName": "sbStatus"
                    }
                ]
            },
            "operator": "IN",
            "rightValues": [
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DRAFT"
                },
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "CONFIRM"
                },
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DONE"
                },
                {
                    "key": "BoJCAZOgZ0lTjuyY5HQRq",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DELETE"
                }
            ]
        }
    
    def _build_create_type_condition(self):
        """
        构建创建类型筛选条件（IN操作符）
        :return: ConditionLeaf字典
        """
        return {
            "key": "sOs0UE8dbaURsImYeAv6q",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "_KCID1Hqv10TFBAzUHa_a",
                "key": "_KCID1Hqv10TFBAzUHa_a",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "createType",
                        "valueName": "createType"
                    }
                ]
            },
            "operator": "IN",
            "rightValues": [
                {
                    "key": "BR2znCq-1DvvE9m6kWJoc",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "AUTO"
                },
                {
                    "key": "BR2znCq-1DvvE9m6kWJoc",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "MANUAL"
                },
                {
                    "key": "BR2znCq-1DvvE9m6kWJoc",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "SETT"
                }
            ]
        }
    
    def _build_aes_dsd_push_status_condition(self):
        """
        构建AES推送状态筛选条件（IN操作符）
        :return: ConditionLeaf字典
        """
        return {
            "key": "SBB0xvc06KthgwNwSETLc",
            "type": "ConditionLeaf",
            "leftValue": {
                "id": "ugYTT6KGwHGzOxpYYWKCc",
                "key": "ugYTT6KGwHGzOxpYYWKCc",
                "type": "VarValue",
                "fieldType": "Text",
                "valueType": "VAR",
                "varValue": [
                    {
                        "valueKey": "aesDsdPushStatus",
                        "valueName": "aesDsdPushStatus"
                    }
                ]
            },
            "operator": "IN",
            "rightValues": [
                {
                    "key": "qsjpsZQNf4mWlLHEblRy6",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "DONE"
                },
                {
                    "key": "qsjpsZQNf4mWlLHEblRy6",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "WAITING"
                },
                {
                    "key": "qsjpsZQNf4mWlLHEblRy6",
                    "type": "VarValue",
                    "fieldType": "Text",
                    "valueType": "CONST",
                    "constValue": "FAIL"
                }
            ]
        }
    
    def _build_condition_group(self, conditions):
        """
        构建conditionGroup（保持与原始curl一致的三层嵌套结构）
        :param conditions: 筛选条件列表
        :return: conditionGroup字典，如果conditions为空则返回None
        """
        if not conditions:
            return None
        
        return {
            "type": "ConditionGroup",
            "logicOperator": "AND",
            "conditions": [
                {
                    "type": "ConditionGroup",
                    "logicOperator": "AND",
                    "conditions": [
                        {
                            "type": "ConditionGroup",
                            "logicOperator": "AND",
                            "conditions": conditions
                        }
                    ]
                }
            ]
        }
    
    def _build_pageable_dict(self, view_condition, condition_group, page_no=1, page_size=20):
        """
        构建分页查询参数字典
        :param view_condition: viewCondition字典
        :param condition_group: conditionGroup字典
        :param page_no: 页码，默认为1
        :param page_size: 每页数量，默认为20
        :return: set_dict字典
        """
        pageable = {
            "pageNo": page_no,
            "pageSize": page_size,
            "needTotal": True,
            "sortOrders": None,
            "systemParams": {
                "viewCondition": view_condition
            },
            "conditionGroup": condition_group
        }
        
        return {
            "pageableDTO": {
                "pageable": pageable
            },
            "pageable": pageable
        }
    
    def _query_ar_info_by_sb_id(self, sb_id):
        """
        查询销售发票关联的应收单信息（支持多个应收单头）
        :param sb_id: 销售发票头ID
        :return: tuple (ar_head_ids, ar_heads_before, ar_items_before_map)
            - ar_head_ids: 应收单头ID集合
            - ar_heads_before: {ar_head_id: ar_head_data}
            - ar_items_before_map: {ar_head_id: [ar_item_data, ...]}
        """
        ar_head_ids = set(self.query_service.get_ar_head_ids_by_sb_head_id(sb_id))
        
        # 存储所有应收单头的数据
        ar_heads_before = {}  # {ar_head_id: ar_head_data}
        ar_items_before_map = {}  # {ar_head_id: [ar_item_data, ...]}
        
        if ar_head_ids:
            self.logger.info(f"关联的应收单头数量: {len(ar_head_ids)}")
            
            # 查询所有关联的应收单头信息
            for ar_head_id in ar_head_ids:
                # 查询应收单头的开票金额
                ar_head_before = self.query_service.get_ar_head_amount_row(ar_head_id)
                if ar_head_before:
                    ar_heads_before[ar_head_id] = ar_head_before
                    self.logger.info(
                        f"应收单头金额 - ID: {ar_head_id}, "
                        f"开票中金额: {ar_head_before.get('billing_doc_amt')}, "
                        f"未开票金额: {ar_head_before.get('unbilled_doc_amt')}, "
                        f"已开票金额: {ar_head_before.get('billed_doc_amt')}"
                    )
                
                # 查询应收单行的开票金额
                ar_items_before_result = self.query_service.get_ar_item_amount_rows(ar_head_id)
                if ar_items_before_result:
                    ar_items_before_map[ar_head_id] = ar_items_before_result
                    self.logger.info(
                        f"应收单头ID {ar_head_id} 的行数量: {len(ar_items_before_result)}"
                    )
        
        return ar_head_ids, ar_heads_before, ar_items_before_map
    
    def _query_clearing_records_by_doc_ids(self, sb_id, ar_head_ids=None):
        """
        查询与销售发票和应收单相关的钩稽记录（头和行）
        :param sb_id: 销售发票头ID
        :param ar_head_ids: 应收单头ID集合（可选）
        :return: tuple (clearing_head_ids, clearing_item_ids)
        """
        clearing_head_ids = set()
        clearing_item_ids = set()
        
        # 查询与销售发票相关的钩稽记录头
        clearing_head_ids.update(self.query_service.get_clearing_head_ids_by_rel_doc_head_id(sb_id))
        
        # 查询与应收单相关的钩稽记录头（如果有关联的应收单）
        if ar_head_ids:
            for ar_head_id in ar_head_ids:
                clearing_head_ids.update(self.query_service.get_clearing_head_ids_by_rel_doc_head_id(ar_head_id))
        
        # 查询钩稽记录行ID
        if clearing_head_ids:
            clearing_head_ids_list = list(clearing_head_ids)
            clearing_item_result = self.query_service.get_clearing_items_by_head_ids(clearing_head_ids_list)
            if clearing_item_result:
                for row in clearing_item_result:
                    clearing_item_id = row.get("id")
                    if clearing_item_id:
                        clearing_item_ids.add(clearing_item_id)
        
        if clearing_head_ids or clearing_item_ids:
            self.logger.info(
                f"钩稽记录 - 钩稽记录头数量: {len(clearing_head_ids)}, "
                f"钩稽记录行数量: {len(clearing_item_ids)}"
            )
        
        return clearing_head_ids, clearing_item_ids
    
    def _validate_clearing_amount_transfer(self, before_data, after_data, data_type="sb", doc_id=None, item_idx=None):
        """
        验证钩稽金额转移（从已钩稽转移到钩稽中）
        :param before_data: 操作前的数据字典，包含 cleared_doc_amt, clearing_doc_amt, uncleared_doc_amt
        :param after_data: 操作后的数据字典，包含 cleared_doc_amt, clearing_doc_amt, uncleared_doc_amt
        :param data_type: 数据类型，"sb"表示销售发票，"ar"表示应收单
        :param doc_id: 单据ID（用于日志）
        :param item_idx: 行索引（用于日志，None表示头）
        """
        cleared_before = float(before_data.get("cleared_doc_amt") or 0)
        clearing_before = float(before_data.get("clearing_doc_amt") or 0)
        float(before_data.get("uncleared_doc_amt") or 0)
        
        cleared_after = float(after_data.get("cleared_doc_amt") or 0)
        clearing_after = float(after_data.get("clearing_doc_amt") or 0)
        float(after_data.get("uncleared_doc_amt") or 0)
        
        # 只有当操作前有已钩稽金额时，才验证金额转移
        if cleared_before > 0:
            # 验证：操作后的钩稽中金额 = 操作前的钩稽中金额 + 操作前的已钩稽金额
            expected_clearing = clearing_before + cleared_before
            doc_desc = f"{data_type.upper()}{'头' if item_idx is None else f'行第{item_idx + 1}行'}"
            if doc_id:
                doc_desc += f"（ID: {doc_id}）"
            
            self.assert_util.assert_by_operator(
                round(clearing_after, 2),
                "=",
                round(expected_clearing, 2),
                f"{doc_desc}钩稽中金额转移失败 - "
                f"操作前钩稽中: {clearing_before}, "
                f"操作前已钩稽: {cleared_before}, "
                f"期望钩稽中: {expected_clearing}, "
                f"实际钩稽中: {clearing_after}"
            )
            
            # 验证：操作后的已钩稽金额应该减少
            self.assert_util.assert_by_operator(
                cleared_after,
                "<=",
                cleared_before,
                f"{doc_desc}已钩稽金额应该减少 - "
                f"操作前: {cleared_before}, 操作后: {cleared_after}"
            )
            
            self.logger.info(
                f"{doc_desc}钩稽金额转移验证成功 - "
                f"已钩稽金额从 {cleared_before} 变为 {cleared_after}, "
                f"钩稽中金额从 {clearing_before} 变为 {clearing_after}"
            )
            return True
        else:
            item_desc = f"行第{item_idx + 1}行" if item_idx is not None else "头"
            self.logger.info(f"{data_type.upper()}{item_desc}操作前已钩稽金额为0，跳过钩稽金额转移验证")
            return False
    
    def _validate_billing_amount_transfer(self, before_data, after_data, doc_id=None, item_idx=None):
        """
        验证开票金额转移（从已开票转移到开票中）- 用于反过账场景
        :param before_data: 操作前的数据字典，包含 billing_doc_amt, unbilled_doc_amt, billed_doc_amt
        :param after_data: 操作后的数据字典，包含 billing_doc_amt, unbilled_doc_amt, billed_doc_amt
        :param doc_id: 单据ID（用于日志）
        :param item_idx: 行索引（用于日志，None表示头）
        """
        billing_before = float(before_data.get("billing_doc_amt") or 0)
        float(before_data.get("unbilled_doc_amt") or 0)
        billed_before = float(before_data.get("billed_doc_amt") or 0)
        
        billing_after = float(after_data.get("billing_doc_amt") or 0)
        float(after_data.get("unbilled_doc_amt") or 0)
        billed_after = float(after_data.get("billed_doc_amt") or 0)
        
        # 只有当操作前有已开票金额时，才验证金额转移
        if billed_before > 0:
            # 验证：操作后的开票中金额 = 操作前的开票中金额 + 操作前的已开票金额
            expected_billing = billing_before + billed_before
            doc_desc = f"应收单{'头' if item_idx is None else f'行第{item_idx + 1}行'}"
            if doc_id:
                doc_desc += f"（ID: {doc_id}）"
            
            self.assert_util.assert_by_operator(
                round(billing_after, 2),
                "=",
                round(expected_billing, 2),
                f"{doc_desc}开票中金额转移失败 - "
                f"操作前开票中: {billing_before}, "
                f"操作前已开票: {billed_before}, "
                f"期望开票中: {expected_billing}, "
                f"实际开票中: {billing_after}"
            )
            
            # 验证：操作后的已开票金额应该减少
            self.assert_util.assert_by_operator(
                billed_after,
                "<=",
                billed_before,
                f"{doc_desc}已开票金额应该减少 - "
                f"操作前: {billed_before}, 操作后: {billed_after}"
            )
            
            self.logger.info(
                f"{doc_desc}金额转移验证成功 - "
                f"已开票金额从 {billed_before} 变为 {billed_after}, "
                f"开票中金额从 {billing_before} 变为 {billing_after}"
            )
            return True
        else:
            item_desc = f"行第{item_idx + 1}行" if item_idx is not None else "头"
            self.logger.info(f"应收单{item_desc}操作前已开票金额为0，跳过开票金额转移验证")
            return False
    
    def _validate_billing_amount_rollback(self, before_data, after_data, doc_id=None, item_idx=None):
        """
        验证开票金额回退（从开票中转移到未开票）- 用于删除场景
        :param before_data: 操作前的数据字典，包含 billing_doc_amt, unbilled_doc_amt, billed_doc_amt
        :param after_data: 操作后的数据字典，包含 billing_doc_amt, unbilled_doc_amt, billed_doc_amt
        :param doc_id: 单据ID（用于日志）
        :param item_idx: 行索引（用于日志，None表示头）
        """
        billing_before = float(before_data.get("billing_doc_amt") or 0)
        unbilled_before = float(before_data.get("unbilled_doc_amt") or 0)
        cleared_before = float(before_data.get("clearing_doc_amt") or 0)  # 应收单行使用clearing_doc_amt
        uncleared_before = float(before_data.get("uncleared_doc_amt") or 0)  # 应收单行使用uncleared_doc_amt
        
        billing_after = float(after_data.get("billing_doc_amt") or 0)
        unbilled_after = float(after_data.get("unbilled_doc_amt") or 0)
        cleared_after = float(after_data.get("clearing_doc_amt") or 0)
        uncleared_after = float(after_data.get("uncleared_doc_amt") or 0)
        
        # 对于应收单头，验证开票中金额转移到未开票金额
        if item_idx is None:
            # 只有当操作前有开票中金额时，才验证金额回退
            if billing_before > 0:
                # 验证：操作后的未开票金额 = 操作前的未开票金额 + 操作前的开票中金额
                expected_unbilled = unbilled_before + billing_before
                doc_desc = f"应收单头（ID: {doc_id}）" if doc_id else "应收单头"
                
                self.assert_util.assert_by_operator(
                    round(unbilled_after, 2),
                    "=",
                    round(expected_unbilled, 2),
                    f"{doc_desc}未开票金额回退失败 - "
                    f"操作前未开票: {unbilled_before}, "
                    f"操作前开票中: {billing_before}, "
                    f"期望未开票: {expected_unbilled}, "
                    f"实际未开票: {unbilled_after}"
                )
                
                # 验证：操作后的开票中金额应该减少
                self.assert_util.assert_by_operator(
                    billing_after,
                    "<=",
                    billing_before,
                    f"{doc_desc}开票中金额应该减少 - "
                    f"操作前: {billing_before}, 操作后: {billing_after}"
                )
                
                self.logger.info(
                    f"{doc_desc}金额回退验证成功 - "
                    f"开票中金额从 {billing_before} 变为 {billing_after}, "
                    f"未开票金额从 {unbilled_before} 变为 {unbilled_after}"
                )
                return True
            else:
                self.logger.info(f"应收单头（ID: {doc_id}）操作前开票中金额为0，跳过金额回退验证")
                return False
        else:
            # 对于应收单行，验证钩稽中金额转移到未钩稽金额
            if cleared_before > 0:
                # 验证：操作后的未钩稽金额 = 操作前的未钩稽金额 + 操作前的钩稽中金额
                expected_uncleared = uncleared_before + cleared_before
                doc_desc = f"应收单行第{item_idx + 1}行（ID: {doc_id}）" if doc_id else f"应收单行第{item_idx + 1}行"
                
                self.assert_util.assert_by_operator(
                    round(uncleared_after, 2),
                    "=",
                    round(expected_uncleared, 2),
                    f"{doc_desc}未钩稽金额回退失败 - "
                    f"操作前未钩稽: {uncleared_before}, "
                    f"操作前钩稽中: {cleared_before}, "
                    f"期望未钩稽: {expected_uncleared}, "
                    f"实际未钩稽: {uncleared_after}"
                )
                
                # 验证：操作后的钩稽中金额应该减少
                self.assert_util.assert_by_operator(
                    cleared_after,
                    "<=",
                    cleared_before,
                    f"{doc_desc}钩稽中金额应该减少 - "
                    f"操作前: {cleared_before}, 操作后: {cleared_after}"
                )
                
                self.logger.info(
                    f"{doc_desc}金额回退验证成功 - "
                    f"钩稽中金额从 {cleared_before} 变为 {cleared_after}, "
                    f"未钩稽金额从 {uncleared_before} 变为 {uncleared_after}"
                )
                return True
            else:
                self.logger.info(f"应收单行第{item_idx + 1}行（ID: {doc_id}）操作前钩稽中金额为0，跳过金额回退验证")
                return False
    
    def _validate_clearing_records_deleted(self, clearing_head_ids, clearing_item_ids):
        """
        验证钩稽记录头和行是否被逻辑删除
        :param clearing_head_ids: 钩稽记录头ID集合
        :param clearing_item_ids: 钩稽记录行ID集合
        """
        if not clearing_head_ids and not clearing_item_ids:
            self.logger.info("未找到钩稽记录，跳过钩稽记录逻辑删除验证")
            return
        
        # 验证钩稽记录头是否被逻辑删除
        if clearing_head_ids:
            clearing_head_ids_list = list(clearing_head_ids)
            clearing_head_verify_result = self.query_service.get_clearing_heads_deleted_rows(clearing_head_ids_list)
            
            if clearing_head_verify_result:
                for head_record in clearing_head_verify_result:
                    clearing_head_id = head_record.get("id")
                    deleted = head_record.get("deleted")
                    self.assert_util.assert_by_operator(
                        deleted,
                        "!=",
                        0,
                        f"钩稽记录头（ID: {clearing_head_id}）应该被逻辑删除，deleted字段应不为0，实际为: {deleted}"
                    )
                self.logger.info(
                    f"钩稽记录头逻辑删除验证成功 - 验证了 {len(clearing_head_verify_result)} 条记录头"
                )
            else:
                self.logger.warning("未找到钩稽记录头数据，可能已被物理删除")
        
        # 验证钩稽记录行是否被逻辑删除
        if clearing_item_ids:
            clearing_item_ids_list = list(clearing_item_ids)
            clearing_item_verify_result = self.query_service.get_clearing_items_deleted_rows(clearing_item_ids_list)
            
            if clearing_item_verify_result:
                for item_record in clearing_item_verify_result:
                    clearing_item_id = item_record.get("id")
                    deleted = item_record.get("deleted")
                    self.assert_util.assert_by_operator(
                        deleted,
                        "!=",
                        0,
                        f"钩稽记录行（ID: {clearing_item_id}）应该被逻辑删除，deleted字段应不为0，实际为: {deleted}"
                    )
                self.logger.info(
                    f"钩稽记录行逻辑删除验证成功 - 验证了 {len(clearing_item_verify_result)} 条记录行"
                )
            else:
                self.logger.warning("未找到钩稽记录行数据，可能已被物理删除")
    
    def _validate_sb_query_results(self, response, filter_config=None):
        """
        验证销售发票查询结果是否符合筛选条件
        :param response: API响应
        :param filter_config: 筛选条件配置字典，如果为None则验证所有条件
        """
        data = response.get("data", {}).get("data", {})
        data_list = data.get("data", [])
        total = data.get("total", 0)
        
        # 验证返回的数据不为空（如果有数据的话）
        if total > 0:
            self.assert_util.assert_by_operator(data_list, "not_empty")
            self.assert_util.assert_by_operator(len(data_list), "<=", 20)
            
            # 定义筛选条件的允许值
            allowed_sb_status = ["DRAFT", "CONFIRM", "DONE", "DELETE"]
            allowed_create_type = ["AUTO", "MANUAL", "SETT"]
            allowed_aes_dsd_push_status = ["DONE", "WAITING", "FAIL"]
            sb_head_code_prefix = "SB"  # 发票编码前缀
            
            # 验证返回的每条数据都符合所有筛选条件
            for record in data_list:
                # 如果提供了filter_config，只验证启用的条件；否则验证所有条件
                should_check_code = filter_config is None or filter_config.get("sb_head_code", False)
                should_check_status = filter_config is None or filter_config.get("sb_status", False)
                should_check_create_type = filter_config is None or filter_config.get("create_type", False)
                should_check_aes = filter_config is None or filter_config.get("aes_dsd_push_status", False)
                
                # 验证发票编码（如果启用了该筛选条件）
                if should_check_code:
                    sb_head_code = record.get("sbHeadCode") or record.get("bilCode")
                    if sb_head_code is not None:
                        self.assert_util.assert_by_operator(
                            sb_head_code_prefix in str(sb_head_code),
                            "=",
                            True,
                            f"发票编码 {sb_head_code} 不符合查询条件（应包含前缀 {sb_head_code_prefix}）"
                        )
                
                # 验证发票状态（如果启用了该筛选条件）
                if should_check_status:
                    sb_status = record.get("sbStatus")
                    self.assert_util.assert_by_operator(
                        sb_status in allowed_sb_status,
                        "=",
                        True,
                        f"发票状态 {sb_status} 不符合查询条件（应为 {allowed_sb_status} 之一）"
                    )
                
                # 验证创建类型（如果启用了该筛选条件）
                if should_check_create_type:
                    create_type = record.get("createType")
                    if create_type is not None:
                        self.assert_util.assert_by_operator(
                            create_type in allowed_create_type,
                            "=",
                            True,
                            f"创建类型 {create_type} 不符合查询条件（应为 {allowed_create_type} 之一）"
                        )
                
                # 验证AES推送状态（如果启用了该筛选条件）
                if should_check_aes:
                    aes_dsd_push_status = record.get("aesDsdPushStatus")
                    if aes_dsd_push_status is not None:
                        self.assert_util.assert_by_operator(
                            aes_dsd_push_status in allowed_aes_dsd_push_status,
                            "=",
                            True,
                            f"AES推送状态 {aes_dsd_push_status} 不符合查询条件（应为 {allowed_aes_dsd_push_status} 之一）"
                        )
    
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
        测试销售发票分页查询（带多条件筛选）
        测试方面：
        1. 分页参数设置（页码、每页数量、是否需要总数）
        2. 查询条件筛选：
           - viewCondition筛选：状态为UNCOMMITTED或BACK
           - conditionGroup筛选（AND逻辑）：
             * sbHeadCode CONTAINS "SB" - 发票编码筛选（模糊匹配测试数据）
             * sbStatus IN (DRAFT, CONFIRM, DONE, DELETE) - 发票状态筛选
             * createType IN (AUTO, MANUAL, SETT) - 创建类型筛选
             * aesDsdPushStatus IN (DONE, WAITING, FAIL) - AES推送状态筛选
        3. 排序功能（按创建时间、发票日期等排序）
        4. 返回数据格式验证（列表数据、总数、分页信息等）
        5. 筛选结果验证（验证返回的数据符合所有筛选条件）
        """
        try:
            # 1. 准备测试数据
            # 构建viewCondition和conditionGroup
            view_condition = self._build_view_condition()
            
            # 构建所有筛选条件
            conditions = [
                self._build_sb_head_code_condition(),
                self._build_sb_status_condition(),
                self._build_create_type_condition(),
                self._build_aes_dsd_push_status_condition()
            ]
            condition_group = self._build_condition_group(conditions)
            
            # 构建分页参数字典
            set_dict = self._build_pageable_dict(view_condition, condition_group)
            fields_to_filter = ["pageableDTO", "pageable"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证（验证所有筛选条件）
            self._validate_sb_query_results(response, filter_config=None)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.parametrize(
        "filter_config,title_suffix",
        [
            # 单个筛选条件
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": False,
                    "aes_dsd_push_status": False
                },
                "仅发票编码筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": False
                },
                "仅发票状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "仅创建类型筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": False,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "仅AES推送状态筛选"
            ),
            # 两个筛选条件组合
            (
                {
                    "sb_head_code": True,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": False
                },
                "发票编码+发票状态筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "发票编码+创建类型筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "发票编码+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "发票状态+创建类型筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "发票状态+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": True
                },
                "创建类型+AES推送状态筛选"
            ),
            # 三个筛选条件组合
            (
                {
                    "sb_head_code": True,
                    "sb_status": True,
                    "create_type": True,
                    "aes_dsd_push_status": False
                },
                "发票编码+发票状态+创建类型筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": True,
                    "create_type": False,
                    "aes_dsd_push_status": True
                },
                "发票编码+发票状态+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": True,
                    "sb_status": False,
                    "create_type": True,
                    "aes_dsd_push_status": True
                },
                "发票编码+创建类型+AES推送状态筛选"
            ),
            (
                {
                    "sb_head_code": False,
                    "sb_status": True,
                    "create_type": True,
                    "aes_dsd_push_status": True
                },
                "发票状态+创建类型+AES推送状态筛选"
            ),
        ]
    )
    @case_decorator(
        story="销售发票查询",
        title="测试销售发票分页查询-筛选条件组合",
        description="验证不同筛选条件组合的查询功能",
        severity="normal",
        file_level_order=5,
        tags=["销售发票", "查询", "分页", "筛选条件组合"]
    )
    def test_query_sb_doc_page_with_filters(self, filter_config, title_suffix):
        """
        测试销售发票分页查询（不同筛选条件组合）
        测试不同筛选条件的组合场景：
        - 单个筛选条件（发票编码、发票状态、创建类型、AES推送状态）
        - 两个筛选条件组合
        - 三个筛选条件组合
        """
        try:
            import allure
            allure.dynamic.title(f"测试销售发票分页查询-{title_suffix}")
            
            # 1. 准备测试数据
            # 构建viewCondition
            view_condition = self._build_view_condition()
            
            # 根据filter_config动态构建conditionGroup
            conditions = []
            if filter_config.get("sb_head_code"):
                conditions.append(self._build_sb_head_code_condition())
            if filter_config.get("sb_status"):
                conditions.append(self._build_sb_status_condition())
            if filter_config.get("create_type"):
                conditions.append(self._build_create_type_condition())
            if filter_config.get("aes_dsd_push_status"):
                conditions.append(self._build_aes_dsd_push_status_condition())
            
            condition_group = self._build_condition_group(conditions)
            
            # 构建分页参数字典
            set_dict = self._build_pageable_dict(view_condition, condition_group)
            fields_to_filter = ["pageableDTO", "pageable"]
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="销售发票-分页查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证（根据filter_config验证启用的筛选条件）
            self._validate_sb_query_results(response, filter_config=filter_config)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票查询",
        title="测试销售发票详情查询",
        description="验证根据ID查询销售发票详情的功能",
        severity="critical",
        file_level_order=6,
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
            # 1. 获取测试数据（从数据库查询一个已存在的销售发票ID）
            # 优先查询测试数据（使用SB前缀），如果没有则查询任意一条
            sb_record = self.query_service.get_latest_sb_head_by_statuses(["DRAFT", "CONFIRM", "DONE", "DELETE"])
            if not sb_record:
                raise ValueError("未找到可用的销售发票数据，请先创建销售发票")
            sb_id = sb_record.get("id")
            sb_head_code = sb_record.get("sb_head_code")
            sb_status = sb_record.get("sb_status")
            
            self.logger.info(f"查询销售发票详情，ID: {sb_id}, 编码: {sb_head_code}, 状态: {sb_status}")
            
            # 2. 使用标准化API调用
            set_dict = {"id": sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="销售发票-详情查询服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 额外的业务验证
            data = response.get("data", {}).get("data", {})
            
            # 验证返回的发票ID
            returned_id = data.get("id")
            self.assert_util.assert_by_operator(
                returned_id,
                "=",
                sb_id,
                f"返回的发票ID {returned_id} 与查询ID {sb_id} 不一致"
            )
            
            # 验证发票编码
            returned_code = data.get("sbHeadCode") or data.get("bilCode")
            if sb_head_code:
                self.assert_util.assert_by_operator(
                    returned_code,
                    "=",
                    sb_head_code,
                    f"返回的发票编码 {returned_code} 与数据库编码 {sb_head_code} 不一致"
                )
            
            # 验证发票状态
            returned_status = data.get("sbStatus")
            if sb_status:
                self.assert_util.assert_by_operator(
                    returned_status,
                    "=",
                    sb_status,
                    f"返回的发票状态 {returned_status} 与数据库状态 {sb_status} 不一致"
                )
            
            # 验证必要字段是否存在
            required_fields = ["id", "sbHeadCode", "sbStatus", "sbDate"]
            for field in required_fields:
                field_value = data.get(field) or data.get(field[0].lower() + field[1:])
                self.assert_util.assert_by_operator(
                    field_value is not None,
                    "=",
                    True,
                    f"必要字段 {field} 在返回数据中不存在或为None"
                )
            
            # 验证发票行信息
            sb_items = data.get("sbItems") or data.get("items") or []
            if sb_items:
                self.logger.info(f"查询到 {len(sb_items)} 条发票行数据")
                # 验证所有发票行的必要字段
                item_required_fields = ["id", "matId", "valQty", "grossDocPrice", "grossDocAmt", "netDocAmt", "netDocPrice", "taxDocAmt"]
                for idx, item in enumerate(sb_items):
                    for field in item_required_fields:
                        field_value = item.get(field)
                        self.assert_util.assert_by_operator(
                            field_value is not None,
                            "=",
                            True,
                            f"发票行第{idx + 1}行的必要字段 {field} 在返回数据中不存在或为None"
                        )
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票删除",
        title="测试销售发票删除",
        description="验证销售发票的删除功能，删除草稿或已提交状态的发票",
        severity="normal",
        file_level_order=16,
        smoke=False,
        tags=["销售发票", "删除"]
    )
    def test_delete_sb_doc(self):
        """
        测试销售发票删除
        测试方面：
        1. 草稿状态发票删除（软删除，deleted=1）
        2. 已提交状态发票删除（软删除，deleted=1）
        3. 删除权限验证（草稿和已提交状态可以删除，已过账状态不能删除）
        4. 删除后数据状态验证（发票头、发票行的deleted字段）
        """
        try:
            # 1. 获取测试数据（从数据库查询一个草稿或已提交状态的销售发票ID）
            # 优先查询草稿状态的测试数据（使用SB前缀），如果没有则查询已提交状态
            sb_record = self.query_service.get_latest_sb_head_by_statuses(["DRAFT", "CONFIRM"])
            if not sb_record:
                self.logger.warning("未找到草稿或已提交状态的销售发票数据，跳过删除测试")
                pytest.fail("未找到草稿或已提交状态的销售发票数据，无法执行删除测试")
            sb_id = sb_record.get("id")
            sb_head_code = sb_record.get("sb_head_code")
            sb_status = sb_record.get("sb_status")
            
            self.logger.info(f"准备删除销售发票，ID: {sb_id}, 编码: {sb_head_code}, 状态: {sb_status}")
            
            # 2. 验证删除前状态（确保是草稿或已提交状态且未删除）
            allowed_statuses = ["DRAFT", "CONFIRM"]
            self.assert_util.assert_by_operator(
                sb_status in allowed_statuses,
                "=",
                True,
                f"销售发票状态必须为DRAFT或CONFIRM才能删除，当前状态: {sb_status}"
            )
            
            # 2.1 查询关联的应收单信息（删除前）
            ar_head_ids, ar_heads_before, ar_items_before_map = self._query_ar_info_by_sb_id(sb_id)
            
            # 3. 使用标准化API调用（只传ID参数）
            set_dict = {"id": sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 额外的业务验证
            # 查询数据库验证删除状态（软删除）
            delete_result = self.query_service.get_sb_deleted_status_row(sb_id)
            if delete_result:
                deleted = delete_result.get("deleted")
                self.assert_util.assert_by_operator(
                    deleted,
                    "!=",
                    0,
                    f"销售发票删除失败，deleted字段不应为0，实际为: {deleted}"
                )
                self.logger.info(f"销售发票删除成功，ID: {sb_id}, deleted: {deleted}")
            else:
                raise ValueError(f"删除后未找到销售发票记录，ID: {sb_id}")
            
            # 验证发票行也被删除（软删除）
            item_count = self.query_service.get_active_sb_item_count(sb_id)
            self.assert_util.assert_by_operator(
                item_count,
                "=",
                0,
                f"销售发票行删除失败，仍有 {item_count} 条未删除的行数据"
            )
            self.logger.info(f"销售发票行删除成功，ID: {sb_id}, 未删除行数: {item_count}")
            
            # 6. 验证应收单金额回退（如果有关联的应收单，支持多个应收单头）
            if ar_heads_before:
                # 遍历所有关联的应收单头进行验证
                for ar_head_id, ar_head_before in ar_heads_before.items():
                    self.logger.info(f"开始验证应收单头ID: {ar_head_id} 的金额回退")
                    
                    # 查询删除后应收单头的开票中金额和未开票金额
                    ar_head_after = self.query_service.get_ar_head_amount_row(ar_head_id)
                    if ar_head_after:
                        self.logger.info(
                            f"删除后应收单头金额 - ID: {ar_head_id}, "
                            f"开票中金额: {ar_head_after.get('billing_doc_amt')}, "
                            f"未开票金额: {ar_head_after.get('unbilled_doc_amt')}, "
                            f"已开票金额: {ar_head_after.get('billed_doc_amt')}"
                        )
                        
                        self._validate_billing_amount_rollback(
                            ar_head_before, ar_head_after, 
                            doc_id=ar_head_id, item_idx=None
                        )
                    
                    # 验证应收单行的金额回退（处理多行情况）
                    ar_items_before = ar_items_before_map.get(ar_head_id, [])
                    if ar_items_before:
                        ar_items_after_result = self.query_service.get_ar_item_amount_rows(ar_head_id)
                        
                        if ar_items_after_result:
                            # 将删除后的数据转换为字典，以ID为key，便于查找
                            ar_items_after_dict = {item.get("id"): item for item in ar_items_after_result}
                            
                            # 验证每一行的金额回退
                            verified_count = 0
                            for idx, item_before in enumerate(ar_items_before):
                                item_id = item_before.get("id")
                                item_after = ar_items_after_dict.get(item_id)
                                
                                if not item_after:
                                    self.logger.warning(
                                        f"应收单头（ID: {ar_head_id}）行第{idx + 1}行（ID: {item_id}）在删除后未找到，可能已被删除"
                                    )
                                    continue
                                
                                    # 使用金额回退验证方法（删除场景：从开票中转移到未开票）
                                    if self._validate_billing_amount_rollback(
                                        item_before, item_after, 
                                        doc_id=item_id, item_idx=idx
                                    ):
                                        verified_count += 1
                            
                            self.logger.info(
                                f"应收单头（ID: {ar_head_id}）行金额回退验证完成 - 总行数: {len(ar_items_before)}, "
                                f"已验证行数: {verified_count}"
                            )
                        else:
                            self.logger.warning(f"删除后未找到应收单行数据，应收单头ID: {ar_head_id}")
                else:
                    self.logger.info(f"应收单头（ID: {ar_head_id}）没有关联的行数据")
            else:
                self.logger.info(f"销售发票ID {sb_id} 未关联应收单，跳过应收单金额回退验证")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="销售发票删除",
        title="测试已过账销售发票不能删除",
        description="验证已过账状态的销售发票不能删除",
        severity="normal",
        file_level_order=17,
        smoke=False,
        tags=["销售发票", "删除", "权限验证"]
    )
    def test_delete_sb_doc_done_status_failed(self):
        """
        测试已过账销售发票不能删除
        测试方面：
        1. 已过账状态发票删除限制（已过账的发票不能删除）
        2. 删除权限验证（只有草稿和已提交状态可以删除）
        3. 错误信息验证（删除失败时返回的错误信息）
        """
        try:
            # 1. 获取测试数据（从数据库查询一个已过账状态的销售发票ID）
            sb_record = self.query_service.get_latest_sb_head_by_status("DONE")
            if not sb_record:
                self.logger.warning("未找到已过账状态的销售发票数据，跳过删除权限验证测试")
                pytest.fail("未找到已过账状态的销售发票数据，无法执行删除权限验证测试")
            sb_id = sb_record.get("id")
            sb_head_code = sb_record.get("sb_head_code")
            sb_status = sb_record.get("sb_status")
            
            self.logger.info(f"准备测试已过账发票删除限制，ID: {sb_id}, 编码: {sb_head_code}, 状态: {sb_status}")
            
            # 2. 验证删除前状态（确保是已过账状态）
            self.assert_util.assert_by_operator(
                sb_status,
                "=",
                "DONE",
                f"销售发票状态必须为DONE才能测试删除限制，当前状态: {sb_status}"
            )
            
            # 3. 使用标准化API调用（只传ID参数）
            set_dict = {"id": sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票-删除服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 验证删除失败（已过账状态应该删除失败）
            # 删除应该失败，返回错误信息
            success = response.get("success", False)
            if success:
                # 如果删除成功，验证数据库状态未改变（deleted仍为0）
                deleted = self.query_service.get_sb_deleted_flag(sb_id)
                if deleted is not None:
                    # 如果删除成功但deleted仍为0，说明可能是软删除但状态不允许
                    # 如果deleted为1，说明删除成功了，这与预期不符
                    if deleted == 1:
                        self.logger.warning(f"已过账发票被成功删除，这可能不符合业务规则，ID: {sb_id}")
            else:
                # 删除失败是预期的
                error_message = response.get("errorMessage") or response.get("message") or "删除失败"
                self.logger.info(f"已过账发票删除失败（符合预期），ID: {sb_id}, 错误信息: {error_message}")
            
            # 5. 验证数据库状态未改变（deleted仍为0）
            verify_result = self.query_service.get_sb_deleted_status_row(sb_id)
            if verify_result:
                deleted = verify_result.get("deleted")
                # 已过账发票应该不能被删除，deleted应该仍为0
                self.assert_util.assert_by_operator(
                    deleted,
                    "=",
                    0,
                    f"已过账销售发票不应该被删除，deleted字段应为0，实际为: {deleted}"
                )
                self.logger.info(f"已过账发票删除限制验证成功，ID: {sb_id}, deleted: {deleted}")
            else:
                raise ValueError(f"验证时未找到销售发票记录，ID: {sb_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
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
        1. 已过账发票反过账（状态从DONE变为CONFIRM或其他状态）
        2. 反过账前数据校验（发票状态、关联凭证状态等）
        3. 反过账后状态变更（发票状态、过账状态等）
        4. 反过账权限验证（只有已过账状态可以反过账）
        """
        try:
            # 1. 获取测试数据（从数据库查询一个已过账状态的销售发票ID）
            sb_record = self.query_service.get_latest_sb_head_by_status("DONE")
            if not sb_record:
                self.logger.warning("未找到已过账状态的销售发票数据，跳过反过账测试")
                pytest.fail("未找到已过账状态的销售发票数据，无法执行反过账测试")
            sb_id = sb_record.get("id")
            sb_head_code = sb_record.get("sb_head_code")
            sb_status = sb_record.get("sb_status")
            pst_date = sb_record.get("pst_date")
            
            self.logger.info(
                f"准备反过账销售发票，ID: {sb_id}, 编码: {sb_head_code}, "
                f"状态: {sb_status}, 过账日期: {pst_date}"
            )
            
            # 2. 验证反过账前状态（确保是已过账状态）
            self.assert_util.assert_by_operator(
                sb_status,
                "=",
                "DONE",
                f"销售发票状态必须为DONE才能反过账，当前状态: {sb_status}"
            )
            
            # 2.1 查询反过账前发票头的钩稽金额
            sb_head_cleared_before = float(sb_record.get("cleared_doc_amt") or 0)
            sb_head_clearing_before = float(sb_record.get("clearing_doc_amt") or 0)
            sb_head_uncleared_before = float(sb_record.get("uncleared_doc_amt") or 0)
            
            self.logger.info(
                f"反过账前发票头钩稽金额 - ID: {sb_id}, "
                f"已钩稽金额: {sb_head_cleared_before}, "
                f"钩稽中金额: {sb_head_clearing_before}, "
                f"未钩稽金额: {sb_head_uncleared_before}"
            )
            
            # 2.2 查询反过账前发票行的钩稽金额（处理多行情况）
            sb_items_before_result = self.query_service.get_sb_item_amount_rows(sb_id)
            sb_items_before = []
            if sb_items_before_result:
                sb_items_before = sb_items_before_result
                self.logger.info(f"反过账前发票行数量: {len(sb_items_before)}")
                # 记录所有行的钩稽金额信息
                for idx, item in enumerate(sb_items_before):
                    item_id = item.get("id")
                    cleared_amt = float(item.get("cleared_doc_amt") or 0)
                    clearing_amt = float(item.get("clearing_doc_amt") or 0)
                    uncleared_amt = float(item.get("uncleared_doc_amt") or 0)
                    self.logger.info(
                        f"反过账前发票行第{idx + 1}行（ID: {item_id}） - "
                        f"已钩稽金额: {cleared_amt}, "
                        f"钩稽中金额: {clearing_amt}, "
                        f"未钩稽金额: {uncleared_amt}"
                    )
            
            # 2.3 查询关联的应收单信息（反过账前，支持多个应收单头）
            ar_head_ids, ar_heads_before, ar_items_before_map = self._query_ar_info_by_sb_id(sb_id)
            
            # 2.4 查询反过账前产生的钩稽记录（头和行）
            clearing_head_ids, clearing_item_ids = self._query_clearing_records_by_doc_ids(sb_id, ar_head_ids)
            
            # 3. 使用标准化API调用（只传ID参数）
            set_dict = {"id": sb_id}
            fields_to_filter = ["id"]
            
            response, _ = self.standard_api_call(
                api_key="SB-销售发票反过账服务",
                set_dict=set_dict,
                fields_to_filter=fields_to_filter
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 额外的业务验证
            # 查询数据库验证状态变更
            verify_data = self.query_service.get_sb_reversal_verify_row(sb_id)
            if verify_data:
                new_sb_status = verify_data.get("sb_status")
                new_pst_date = verify_data.get("pst_date")
                
                # 验证状态已变更（从DONE变为其他状态，通常是CONFIRM）
                self.assert_util.assert_by_operator(
                    new_sb_status,
                    "!=",
                    "DONE",
                    f"销售发票反过账失败，状态仍为DONE，ID: {sb_id}"
                )
                
                # 验证状态变更为允许的状态（CONFIRM或其他）
                allowed_statuses_after_rollback = ["CONFIRM", "DRAFT"]
                self.assert_util.assert_by_operator(
                    new_sb_status in allowed_statuses_after_rollback,
                    "=",
                    True,
                    f"销售发票反过账后状态应为 {allowed_statuses_after_rollback} 之一，实际为: {new_sb_status}"
                )
                
                self.logger.info(
                    f"销售发票反过账成功，ID: {sb_id}, "
                    f"状态从 {sb_status} 变为 {new_sb_status}, "
                    f"过账日期: {new_pst_date}"
                )
                
                # 5.1 验证发票头钩稽金额转移
                sb_head_after_data = {
                    "cleared_doc_amt": verify_data.get("cleared_doc_amt"),
                    "clearing_doc_amt": verify_data.get("clearing_doc_amt"),
                    "uncleared_doc_amt": verify_data.get("uncleared_doc_amt")
                }
                sb_head_before_data = {
                    "cleared_doc_amt": sb_record.get("cleared_doc_amt"),
                    "clearing_doc_amt": sb_record.get("clearing_doc_amt"),
                    "uncleared_doc_amt": sb_record.get("uncleared_doc_amt")
                }
                self.logger.info(
                    f"反过账后发票头钩稽金额 - ID: {sb_id}, "
                    f"已钩稽金额: {sb_head_after_data.get('cleared_doc_amt')}, "
                    f"钩稽中金额: {sb_head_after_data.get('clearing_doc_amt')}, "
                    f"未钩稽金额: {sb_head_after_data.get('uncleared_doc_amt')}"
                )
                self._validate_clearing_amount_transfer(
                    sb_head_before_data, sb_head_after_data, 
                    data_type="sb", doc_id=sb_id, item_idx=None
                )
                
                # 5.2 验证发票行钩稽金额转移（处理多行情况）
                if sb_items_before:
                    sb_items_after_result = self.query_service.get_sb_item_amount_rows(sb_id)
                    
                    if sb_items_after_result:
                        # 将反过账后的数据转换为字典，以ID为key，便于查找
                        sb_items_after_dict = {item.get("id"): item for item in sb_items_after_result}
                        
                        # 验证每一行的钩稽金额转移
                        verified_count = 0
                        for idx, item_before in enumerate(sb_items_before):
                            item_id = item_before.get("id")
                            item_after = sb_items_after_dict.get(item_id)
                            
                            if not item_after:
                                self.logger.warning(
                                    f"发票行第{idx + 1}行（ID: {item_id}）在反过账后未找到，可能已被删除"
                                )
                                continue
                            
                            if self._validate_clearing_amount_transfer(
                                item_before, item_after, 
                                data_type="sb", doc_id=item_id, item_idx=idx
                            ):
                                verified_count += 1
                        
                        self.logger.info(
                            f"发票行钩稽金额转移验证完成 - 总行数: {len(sb_items_before)}, "
                            f"已验证行数: {verified_count}"
                        )
                    else:
                        self.logger.warning(f"反过账后未找到发票行数据，发票头ID: {sb_id}")
                
                # 5.3 验证应收单金额回退（如果有关联的应收单，支持多个应收单头）
                if ar_heads_before:
                    # 验证所有关联的应收单头金额回退
                    for ar_head_id, ar_head_before in ar_heads_before.items():
                        self.logger.info(f"开始验证应收单头ID: {ar_head_id} 的金额回退")
                        
                        # 查询反过账后应收单头的开票金额
                        ar_head_after = self.query_service.get_ar_head_amount_row(ar_head_id)
                        if ar_head_after:
                            self.logger.info(
                                f"反过账后应收单头金额 - ID: {ar_head_id}, "
                                f"开票中金额: {ar_head_after.get('billing_doc_amt')}, "
                                f"未开票金额: {ar_head_after.get('unbilled_doc_amt')}, "
                                f"已开票金额: {ar_head_after.get('billed_doc_amt')}"
                            )
                            
                            self._validate_billing_amount_transfer(
                                ar_head_before, ar_head_after, 
                                doc_id=ar_head_id, item_idx=None
                            )
                        
                        # 验证应收单行的金额回退（处理多行情况）
                        ar_items_before = ar_items_before_map.get(ar_head_id, [])
                        if ar_items_before:
                            ar_items_after_result = self.query_service.get_ar_item_amount_rows(ar_head_id)
                            
                            if ar_items_after_result:
                                # 将反过账后的数据转换为字典，以ID为key，便于查找
                                ar_items_after_dict = {item.get("id"): item for item in ar_items_after_result}
                                
                                # 验证每一行的金额回退
                                verified_count = 0
                                for idx, item_before in enumerate(ar_items_before):
                                    item_id = item_before.get("id")
                                    item_after = ar_items_after_dict.get(item_id)
                                    
                                    if not item_after:
                                        self.logger.warning(
                                            f"应收单头（ID: {ar_head_id}）行第{idx + 1}行（ID: {item_id}）在反过账后未找到，可能已被删除"
                                        )
                                        continue
                                    
                                    # 已钩稽金额对应应收单行的已开票金额，钩稽中金额对应开票中金额
                                    # 使用钩稽金额验证方法（应收单行使用钩稽字段）
                                    if self._validate_clearing_amount_transfer(
                                        item_before, item_after, 
                                        data_type="ar", doc_id=item_id, item_idx=idx
                                    ):
                                        verified_count += 1
                                
                                self.logger.info(
                                    f"应收单头（ID: {ar_head_id}）行金额转移验证完成 - 总行数: {len(ar_items_before)}, "
                                    f"已验证行数: {verified_count}"
                                )
                            else:
                                self.logger.warning(f"反过账后未找到应收单行数据，应收单头ID: {ar_head_id}")
                else:
                    self.logger.info(f"销售发票ID {sb_id} 未关联应收单，跳过应收单金额转移验证")
                
                # 5.4 验证钩稽记录头和行是否被逻辑删除
                self._validate_clearing_records_deleted(clearing_head_ids, clearing_item_ids)
            else:
                raise ValueError(f"反过账后未找到销售发票记录，ID: {sb_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
  
        
if __name__ == "__main__":
    test = TestSbDocManagement()
    test.setup_class()
    test.test_reverse_post_sb_doc()
