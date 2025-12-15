import allure
import pytest
import sys
from pathlib import Path

# 项目根目录添加路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from testcases.erp_acc import ErpAccBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("财务模块 - 信用管理")
@allure.feature("账户事务管理")
class TestAccTransactionManagement(ErpAccBaseTest):
    """账户事务管理测试类 - 覆盖事务抬头CRUD、流水分页查询和标准导入导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.trans_head_id = None
        cls.logger.info("账户事务管理测试类初始化完成")
        
        # 初始化依赖数据（事务依赖档案、额度等基础数据）
        if cls.acc_cache_data:
            cls.acc_archive_id = cls.acc_cache_data.get("archive_info", [])[0].get("id") if cls.acc_cache_data.get("archive_info") else None
            cls.amount_config_id = cls.acc_cache_data.get("amount_info", [])[0].get("id") if cls.acc_cache_data.get("amount_info") else None
            cls.check_rule_id = cls.acc_cache_data.get("rule_info", [])[0].get("id") if cls.acc_cache_data.get("rule_info") else None
            cls.cust_id = cls.acc_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id") if cls.acc_cache_data.get("partner_info") else None
            cls.com_org_id = cls.acc_cache_data.get("org_info", {}).get("gr_come_org_info", [])[0].get("id") if cls.acc_cache_data.get("org_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理事务抬头主表
            cls.db.delete(
                table="adv_cm_acc_trans_head",  # 事务抬头表，实际表名需确认
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("事务抬头测试数据清理完成")
            
            # 清理事务流水记录表（如果创建了测试流水）
            # cls.db.delete(table="adv_cm_acc_trans_record", where="trans_head_id like %s", params=["AT_%"])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    def _build_trans_config(self, trans_type="CREDIT_ADJUST"):
        """辅助方法：构建事务配置"""
        # 根据事务类型构建不同的配置
        if trans_type == "CREDIT_ADJUST":
            config = {
                "trans_type": "CREDIT_ADJUSTMENT",
                "flow_type": "APPROVAL",  # 审批流程
                "trigger_events": ["AMOUNT_CHANGE", "STATUS_UPDATE"],  # 触发事件
                "amount_limits": {
                    "min_adjust": -50000.00,  # 最小调整额度
                    "max_adjust": 100000.00,  # 最大调整额度
                    "step_amount": 1000.00    # 调整步长
                },
                "validation_rules": [
                    {
                        "rule": "AMOUNT_RANGE",
                        "params": {"min": -50000, "max": 100000},
                        "severity": "WARNING"
                    },
                    {
                        "rule": "BALANCE_CHECK", 
                        "params": {"min_balance": 0},
                        "severity": "ERROR"
                    }
                ],
                "audit_required": True,     # 需要审计
                "auto_approve_limit": 10000.00,  # 自动审批限额
                "description": "信用额度调整事务配置，支持正负调整，超过1万需要审批"
            }
        elif trans_type == "PAYMENT_SETTLE":
            config = {
                "trans_type": "PAYMENT_SETTLEMENT",
                "flow_type": "DIRECT",     # 直通流程
                "trigger_events": ["PAYMENT_RECEIVED", "INVOICE_SETTLED"],
                "amount_limits": {
                    "min_amount": 100.00,    # 最小交易额
                    "max_amount": 500000.00, # 最大交易额
                    "fee_rate": 0.01         # 手续费率
                },
                "validation_rules": [
                    {
                        "rule": "AMOUNT_POSITIVE",
                        "severity": "ERROR"
                    },
                    {
                        "rule": "CUSTOMER_ACTIVE", 
                        "severity": "ERROR"
                    },
                    {
                        "rule": "RISK_LEVEL_CHECK",
                        "params": {"max_risk": 3},
                        "severity": "WARNING"
                    }
                ],
                "audit_required": False,    # 无需审计
                "auto_approve_limit": None, # 无自动审批
                "description": "付款结算事务配置，支持收款和发票结算，风险等级≤3可直通"
            }
        else:
            config = {
                "trans_type": "BASIC",
                "flow_type": "MANUAL",
                "trigger_events": [],
                "amount_limits": {},
                "validation_rules": [],
                "audit_required": False,
                "auto_approve_limit": None,
                "description": "默认事务配置"
            }
        
        return config
    
    @case_decorator(
        story="账户事务管理",
        title="测试创建事务抬头配置",
        description="验证事务抬头创建功能，包括流程类型、触发事件和额度限制",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "transaction", "create", "head"]
    )
    def test_save_trans_head(self):
        """测试创建事务抬头配置"""
        try:
            # 1. 检查依赖数据（需要账户档案）
            if not self.acc_archive_id:
                self.logger.warning("缺少账户档案依赖，跳过创建测试")
                pytest.skip("缺少账户档案依赖数据")
            
            # 2. 准备测试数据
            head_code = self.mock_util.generate_unique_code(tag="TRANS_H")
            head_name = f"自动化测试事务配置_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 构建事务配置（信用调整）
            trans_config = self._build_trans_config("CREDIT_ADJUST")
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_SAVE")  # 假设创建API键名
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "archive_id", "amount_config_id", "cust_id", "org_id",
                              "trans_type", "flow_type", "trigger_events", "amount_limits",
                              "validation_rules", "audit_required", "auto_approve_limit",
                              "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            create_data = {
                "code": head_code,
                "name": head_name,
                "archive_id": self.acc_archive_id,
                "amount_config_id": self.amount_config_id or None,
                "cust_id": self.cust_id,
                "org_id": self.com_org_id,
                "trans_type": trans_config["trans_type"],
                "flow_type": trans_config["flow_type"],
                "trigger_events": trans_config["trigger_events"],
                "amount_limits": trans_config["amount_limits"],
                "validation_rules": trans_config["validation_rules"],
                "audit_required": trans_config["audit_required"],
                "auto_approve_limit": trans_config["auto_approve_limit"],
                "enabled": True,
                "remark": remark
            }
            ParamUtil.set_request_params(filtered_params, create_data)
            
            # 5. 发送创建请求
            response = self.http.post(url, json=filtered_params)
            
            # 6. 断言和验证
            self.assert_util.assert_response_data(response)
            data = response.get("data", {}).get("data", {})
            assert data, "创建响应数据为空"
            
            self.trans_head_id = data.get("id")
            assert self.trans_head_id, "未获取到事务抬头ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", head_code, "事务编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", head_name, "事务名称验证失败")
            self.assert_util.assert_by_operator(data.get("trans_type"), "=", trans_config["trans_type"], "事务类型验证失败")
            self.assert_util.assert_by_operator(data.get("flow_type"), "=", trans_config["flow_type"], "流程类型验证失败")
            self.assert_util.assert_by_operator(data.get("audit_required"), "=", trans_config["audit_required"], "审计要求验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "启用状态验证失败")
            
            # 验证额度限制
            limits_returned = data.get("amount_limits", {})
            self.assert_util.assert_by_operator(limits_returned.get("min_adjust"), "=", -50000.00, "最小调整额度验证失败")
            self.assert_util.assert_by_operator(limits_returned.get("max_adjust"), "=", 100000.00, "最大调整额度验证失败")
            
            # 验证触发事件数量
            events_returned = data.get("trigger_events", [])
            assert len(events_returned) >= 2, "触发事件数量不匹配"
            self.assert_util.assert_all_in(["AMOUNT_CHANGE", "STATUS_UPDATE"], events_returned, "触发事件不匹配")
            
            # 验证规则数量
            rules_returned = data.get("validation_rules", [])
            assert len(rules_returned) >= 2, "验证规则数量不匹配"
            
            # 7. Allure报告
            a.json(filtered_params, "创建事务抬头请求参数")
            a.json(response, "创建事务抬头响应结果")
            a.text(trans_config["description"], "事务配置描述")
            self.logger.info(f"事务抬头创建成功，ID: {self.trans_head_id}, 类型: {trans_config['trans_type']}")
            
        except Exception as e:
            a.text(str(e), "创建事务抬头失败原因")
            self.logger.error(f"创建事务抬头失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试查询事务抬头配置列表",
        description="验证事务抬头分页查询功能，支持类型和状态过滤",
        severity="normal",
        order=4,
        tags=["erp_acc", "transaction", "query", "head"]
    )
    def test_query_trans_head(self):
        """测试查询事务抬头配置"""
        try:
            # 确保有测试数据
            if not self.trans_head_id:
                self.test_save_trans_head()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_QUERY")  # 假设查询API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [{"field": "create_time", "direction": "DESC"}],
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.trans_head_id},
                        {"field": "enabled", "operator": "eq", "value": True},
                        {"field": "trans_type", "operator": "eq", "value": "CREDIT_ADJUSTMENT"}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "trans_type", "type": "TEXT"},
                    {"name": "flow_type", "type": "TEXT"},
                    {"name": "audit_required", "type": "BOOLEAN"},
                    {"name": "enabled", "type": "BOOLEAN"},
                    {"name": "events_count", "type": "NUMBER"},  # 触发事件数量
                    {"name": "rules_count", "type": "NUMBER"}    # 验证规则数量
                ],
                "systemParams": None,
                "expand": ["trigger_events", "validation_rules"]  # 展开关联数据
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 3. 发送查询请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证查询结果
            self.assert_util.assert_response_success(response)
            query_data = response.get("data", {}).get("data", {})
            records = query_data.get("records", [])
            total = query_data.get("total", 0)
            
            assert total >= 1, "未查询到事务抬头记录"
            assert len(records) >= 1, "查询记录列表为空"
            
            # 验证具体记录
            trans_info = records[0]
            self.assert_util.assert_by_operator(trans_info.get("id"), "=", self.trans_head_id, "事务ID不匹配")
            self.assert_util.assert_by_operator(trans_info.get("trans_type"), "=", "CREDIT_ADJUSTMENT", "事务类型不匹配")
            self.assert_util.assert_by_operator(trans_info.get("flow_type"), "=", "APPROVAL", "流程类型不匹配")
            self.assert_util.assert_by_operator(trans_info.get("audit_required"), "=", True, "审计要求不匹配")
            self.assert_util.assert_by_operator(trans_info.get("enabled"), "=", True, "启用状态不匹配")
            
            # 验证展开数据
            events = trans_info.get("trigger_events", [])
            assert len(events) >= 2, "触发事件展开失败"
            self.assert_util.assert_all_in(["AMOUNT_CHANGE", "STATUS_UPDATE"], events, "触发事件不匹配")
            
            rules = trans_info.get("validation_rules", [])
            assert len(rules) >= 2, "验证规则展开失败"
            # 验证额度范围规则
            amount_rule = next((r for r in rules if r.get("rule") == "AMOUNT_RANGE"), None)
            assert amount_rule, "额度范围规则未找到"
            self.assert_util.assert_by_operator(amount_rule.get("params", {}).get("min"), "=", -50000, "最小额度参数不匹配")
            self.assert_util.assert_by_operator(amount_rule.get("params", {}).get("max"), "=", 100000, "最大额度参数不匹配")
            
            # 5. Allure报告
            a.json(filtered_params, "查询事务抬头参数")
            a.json(response, "查询事务抬头结果")
            self.logger.info(f"事务抬头查询成功，共{total}条记录，事件数量: {len(events)}, 规则数量: {len(rules)}")
            
        except Exception as e:
            a.text(str(e), "查询事务抬头失败原因")
            self.logger.error(f"查询事务抬头失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试账户流水分页查询",
        description="验证acc_trans_record_page_service分页查询功能，支持多条件过滤",
        severity="critical",
        order=5,
        tags=["erp_acc", "transaction", "query", "record", "page"]
    )
    def test_query_trans_record_page(self):
        """测试账户流水分页查询"""
        try:
            # 确保有测试数据（事务抬头）
            if not self.trans_head_id:
                self.test_save_trans_head()
            
            # 1. 获取流水查询API配置
            api_path = self.get_api_path("acc_trans_record_page_service")
            params, url = self.get_api_params(api_path)
            
            # 2. 构建复杂查询参数（模拟真实流水查询场景）
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 50,
                    "needTotal": True,
                    "sortOrders": [
                        {"field": "trans_time", "direction": "DESC"},
                        {"field": "amount", "direction": "DESC"}
                    ],
                    "conditionItems": [
                        {"field": "cust_id", "operator": "eq", "value": self.cust_id},
                        {"field": "trans_head_id", "operator": "eq", "value": self.trans_head_id},
                        {"field": "trans_status", "operator": "in", "value": ["SUCCESS", "PROCESSING"]},
                        {"field": "trans_time", "operator": "between", "value": ["2025-01-01", "2025-12-31"]},
                        {"field": "amount", "operator": "gt", "value": 1000.00},
                        {"field": "risk_level", "operator": "lte", "value": 3}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "trans_code", "type": "TEXT"},
                    {"name": "trans_time", "type": "DATETIME"},
                    {"name": "cust_id", "type": "NUMBER"},
                    {"name": "trans_head_id", "type": "NUMBER"},
                    {"name": "amount", "type": "NUMBER"},
                    {"name": "trans_type", "type": "TEXT"},
                    {"name": "trans_status", "type": "TEXT"},
                    {"name": "risk_level", "type": "NUMBER"},
                    {"name": "operator_id", "type": "NUMBER"},
                    {"name": "remark", "type": "TEXT"}
                ],
                "systemParams": {
                    "need_audit_log": True,  # 需要审计日志
                    "include_related": True  # 包含关联数据
                },
                "summary": {  # 汇总统计
                    "total_amount": True,
                    "success_count": True,
                    "risky_count": True
                }
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(query_params.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 3. 发送流水查询请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证查询结果
            self.assert_util.assert_response_success(response)
            query_data = response.get("data", {}).get("data", {})
            records = query_data.get("records", [])
            total = query_data.get("total", 0)
            summary = query_data.get("summary", {})
            
            # 基础验证
            self.assert_util.assert_by_operator(total, ">=", 0, "总记录数异常")
            self.assert_util.assert_by_operator(len(records), ">=", 0, "记录列表异常")
            
            # 如果有数据，进行详细验证
            if total > 0 and len(records) > 0:
                first_record = records[0]
                self.assert_util.assert_by_operator(first_record.get("cust_id"), "=", self.cust_id, "客户ID不匹配")
                self.assert_util.assert_by_operator(first_record.get("trans_head_id"), "=", self.trans_head_id, "事务抬头ID不匹配")
                self.assert_util.assert_by_operator(first_record.get("amount"), ">=", 1000.00, "金额过滤不生效")
                self.assert_util.assert_by_operator(first_record.get("risk_level"), "<=", 3, "风险等级过滤不生效")
                self.assert_util.assert_all_in(["SUCCESS", "PROCESSING"], [r.get("trans_status") for r in records], "交易状态过滤不生效")
                
                # 验证汇总统计
                if summary:
                    self.assert_util.assert_by_operator(summary.get("total_amount", 0), ">=", 0, "总额汇总异常")
                    self.assert_util.assert_by_operator(summary.get("success_count", 0), ">=", 0, "成功计数异常")
                    self.assert_util.assert_by_operator(summary.get("risky_count", 0), ">=", 0, "风险计数异常")
            
            # 5. Allure报告
            a.json(filtered_params, "查询账户流水参数")
            a.json(response, "查询账户流水结果")
            a.text(f"流水查询结果: 共{total}条记录，第{query_params['pageable']['pageNo']}页，每页{query_params['pageable']['pageSize']}条", "查询统计")
            if summary:
                a.text(f"汇总统计: 总额{summary.get('total_amount', 0)}, 成功{summary.get('success_count', 0)}条, 风险{summary.get('risky_count', 0)}条", "流水汇总")
            self.logger.info(f"账户流水分页查询成功，共{total}条记录，风险等级≤3，金额≥1000")
            
        except Exception as e:
            a.text(str(e), "查询账户流水失败原因")
            self.logger.error(f"查询账户流水失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试更新事务抬头配置",
        description="验证事务抬头更新功能，修改流程类型和额度限制",
        severity="normal",
        order=7,
        tags=["erp_acc", "transaction", "update", "head"]
    )
    def test_update_trans_head(self):
        """测试更新事务抬头配置"""
        try:
            # 确保有测试数据
            if not self.trans_head_id:
                self.test_save_trans_head()
            
            # 1. 准备更新数据 - 修改为付款结算配置
            new_head_name = f"更新后付款结算配置_{self.mock_util.get_timestamp()}"
            new_remark = self.mock_util.get_mock_remark()
            
            # 构建新的付款结算配置
            new_config = self._build_trans_config("PAYMENT_SETTLE")
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_UPDATE")  # 假设更新API键名
            params, url = self.get_api_params(api_path)
            
            # 3. 参数设置
            update_data = {
                "id": self.trans_head_id,
                "name": new_head_name,
                "trans_type": new_config["trans_type"],  # 改为PAYMENT_SETTLEMENT
                "flow_type": new_config["flow_type"],    # 改为DIRECT
                "trigger_events": new_config["trigger_events"],
                "amount_limits": new_config["amount_limits"],
                "validation_rules": new_config["validation_rules"],
                "audit_required": new_config["audit_required"],  # 改为False
                "auto_approve_limit": new_config["auto_approve_limit"],  # 改为None
                "enabled": True,
                "remark": new_remark
            }
            
            fields_to_filter = ["id", "name", "trans_type", "flow_type", "trigger_events", 
                              "amount_limits", "validation_rules", "audit_required", 
                              "auto_approve_limit", "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, update_data)
            
            # 4. 发送更新请求
            response = self.http.post(url, json=filtered_params)
            
            # 5. 验证更新结果
            self.assert_util.assert_response_success(response)
            update_result = response.get("data", {})
            assert update_result.get("success"), "更新操作失败"
            
            # 6. 查询验证更新效果
            self.test_query_trans_head()  # 重新查询验证
            
            # 额外验证更新内容
            updated_trans = self._get_current_trans_info()
            self.assert_util.assert_by_operator(updated_trans.get("name"), "=", new_head_name, "事务名称更新失败")
            self.assert_util.assert_by_operator(updated_trans.get("trans_type"), "=", "PAYMENT_SETTLEMENT", "事务类型更新失败")
            self.assert_util.assert_by_operator(updated_trans.get("flow_type"), "=", "DIRECT", "流程类型更新失败")
            self.assert_util.assert_by_operator(updated_trans.get("audit_required"), "=", False, "审计要求更新失败")
            
            # 验证新额度限制
            new_limits = updated_trans.get("amount_limits", {})
            self.assert_util.assert_by_operator(new_limits.get("min_amount"), "=", 100.00, "最小交易额更新失败")
            self.assert_util.assert_by_operator(new_limits.get("max_amount"), "=", 500000.00, "最大交易额更新失败")
            self.assert_util.assert_by_operator(new_limits.get("fee_rate"), "=", 0.01, "手续费率更新失败")
            
            # 验证触发事件变更
            new_events = updated_trans.get("trigger_events", [])
            self.assert_util.assert_all_in(["PAYMENT_RECEIVED", "INVOICE_SETTLED"], new_events, "新触发事件不匹配")
            
            # 验证规则变更
            new_rules = updated_trans.get("validation_rules", [])
            positive_rule = next((r for r in new_rules if r.get("rule") == "AMOUNT_POSITIVE"), None)
            assert positive_rule, "金额正数规则未更新"
            self.assert_util.assert_by_operator(positive_rule.get("severity"), "=", "ERROR", "金额正数规则严重度不匹配")
            
            # 7. Allure报告
            a.json(filtered_params, "更新事务抬头参数")
            a.json(response, "更新事务抬头结果")
            a.text(f"事务类型变更: CREDIT_ADJUSTMENT -> PAYMENT_SETTLEMENT", "类型变更记录")
            a.text(f"流程变更: APPROVAL -> DIRECT, 审计: True -> False", "流程变更记录")
            a.text(new_config["description"], "更新后事务描述")
            self.logger.info(f"事务抬头更新成功，ID: {self.trans_head_id}, 新类型: {new_config['trans_type']}")
            
        except Exception as e:
            a.text(str(e), "更新事务抬头失败原因")
            self.logger.error(f"更新事务抬头失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试删除事务抬头配置",
        description="验证单个事务抬头配置删除功能",
        severity="critical",
        order=16,
        tags=["erp_acc", "transaction", "delete", "head"]
    )
    def test_delete_trans_head(self):
        """测试删除事务抬头配置"""
        try:
            # 确保有测试数据
            if not self.trans_head_id:
                self.test_save_trans_head()
            
            # 1. 获取删除API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_DELETE")  # 假设删除API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 单个ID删除参数
            delete_data = {"id": self.trans_head_id}
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, delete_data)
            
            # 3. 发送删除请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证删除结果
            self.assert_util.assert_response_success(response)
            delete_result = response.get("data", {})
            assert delete_result.get("success"), "删除操作失败"
            
            # 5. 查询验证删除效果
            saved_id = self.trans_head_id
            self.trans_head_id = None
            
            # 尝试查询已删除的事务抬头
            api_path_query = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_QUERY")
            query_params, query_url = self.get_api_params(api_path_query)
            
            verify_query = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": saved_id}]
                }
            }
            
            filtered_query = ParamUtil.filter_post_body_fields(query_params, ["pageable"], ["params", "request"])
            ParamUtil.set_request_params(filtered_query, verify_query)
            
            query_response = self.http.post(query_url, json=filtered_query)
            query_records = query_response.get("data", {}).get("data", {}).get("records", [])
            
            assert len(query_records) == 0, f"删除后仍能查询到事务 ID: {saved_id}"
            
            # 6. Allure报告
            a.json(filtered_params, "删除事务抬头参数")
            a.json(response, "删除事务抬头结果")
            self.logger.info(f"事务抬头删除成功，ID: {saved_id}")
            
        except Exception as e:
            a.text(str(e), "删除事务抬头失败原因")
            self.logger.error(f"删除事务抬头失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试事务抬头标准导入",
        description="验证ADV_CM_ACC_TRANS_HEAD_CF_GEI_IMPOR...标准导入服务",
        severity="normal",
        order=13,
        tags=["erp_acc", "transaction", "import"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import_trans_head(self):
        """测试事务抬头标准导入服务"""
        try:
            # 1. 获取导入API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_CF_GEI_IMPOR")  # 标准导入服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导入参数
            import_data = {
                "serviceKey": "ADV_CM_ACC_TRANS_HEAD_CF_GEI_IMPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"TRANS_HEAD_IMPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "filePath": "/tmp/trans_head_template.xlsx",
                    "modelKey": "ADV_CM_ACC_TRANS_HEAD",
                    "importConfig": {
                        "headerRow": 1,
                        "dataStartRow": 2,
                        "fieldMapping": {
                            "code": "A",
                            "name": "B",
                            "trans_type": "C",
                            "flow_type": "D",
                            "audit_required": "E",
                            "amount_limits": "F",  # JSON列
                            "trigger_events": "G",  # JSON数组列
                            "validation_rules": "H"  # JSON数组列
                        },
                        "validationRules": {
                            "trans_type": {"type": "ENUM", "values": ["CREDIT_ADJUSTMENT", "PAYMENT_SETTLEMENT"], "required": True},
                            "flow_type": {"type": "ENUM", "values": ["APPROVAL", "DIRECT", "MANUAL"], "required": True},
                            "audit_required": {"type": "BOOLEAN", "required": True},
                            "amount_limits": {"type": "JSON_OBJECT", "required": True, "schema": {"min_adjust": "NUMBER", "max_adjust": "NUMBER"}},
                            "trigger_events": {"type": "JSON_ARRAY", "min_length": 1, "required": True}
                        },
                        "defaultValues": {
                            "enabled": True,
                            "org_id": self.com_org_id,
                            "remark": "系统批量导入"
                        },
                        "relatedValidation": {  # 关联验证
                            "archive_id": {"required": True, "foreign_key": "adv_cm_acc_archive.id"},
                            "amount_config_id": {"required": False, "foreign_key": "adv_cm_acc_amount_config.id"}
                        }
                    },
                    "batchSize": 200,  # 批次大小
                    "errorHandle": "LOG_CONTINUE",  # 记录错误但继续导入
                    "duplicateHandle": "SKIP"  # 重复记录跳过
                }
            }
            
            filtered_params = params.copy()
            ParamUtil.set_request_params(filtered_params, import_data)
            
            # 3. 发送导入请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证导入任务
            self.assert_util.assert_response_data(response)
            import_result = response.get("data", {})
            assert import_result.get("success"), "导入任务创建失败"
            task_id = import_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导入任务ID"
            expected_count = import_result.get("data", {}).get("expected_count", 0)
            processed_count = import_result.get("data", {}).get("processed_count", 0)
            success_count = import_result.get("data", {}).get("success_count", 0)
            error_count = import_result.get("data", {}).get("error_count", 0)
            
            self.assert_util.assert_by_operator(processed_count, ">=", 0, "处理数量异常")
            self.assert_util.assert_by_operator(success_count, ">=", 0, "成功数量异常")
            self.assert_util.assert_by_operator(error_count, ">=", 0, "错误数量异常")
            
            # 5. Allure报告
            a.json(filtered_params, "标准导入请求参数")
            a.json(response, "标准导入响应结果")
            a.text(f"导入统计: 预期{expected_count}条, 处理{processed_count}条, 成功{success_count}条, 错误{error_count}条", "导入结果统计")
            self.logger.info(f"事务抬头标准导入任务创建成功，Task ID: {task_id}, 成功: {success_count}/{processed_count}")
            
        except Exception as e:
            a.text(str(e), "标准导入事务抬头失败原因")
            self.logger.error(f"标准导入失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试提交事务抬头导入任务",
        description="验证ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TA...导入任务提交服务",
        severity="normal",
        order=14,
        tags=["erp_acc", "transaction", "import_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_import_task_trans(self):
        """测试提交事务抬头导入任务"""
        try:
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TA_IMPORT")  # 导入任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "IMPORT",
                "taskName": f"TRANS_HEAD_IMPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_TRANS_HEAD",
                "fileInfo": {
                    "fileName": "trans_head_config.xlsx",
                    "fileSize": 51200,
                    "filePath": "/oss/trans_head_import/batch_config.xlsx",
                    "fileType": "EXCEL",
                    "charset": "UTF-8"
                },
                "importFields": [
                    "code", "name", "trans_type", "flow_type", "audit_required", 
                    "amount_limits", "trigger_events", "validation_rules"
                ],
                "validationRules": {
                    "amount_limits": {
                        "type": "JSON_OBJECT", 
                        "required": True, 
                        "schema": {
                            "min_adjust": {"type": "NUMBER", "required": True},
                            "max_adjust": {"type": "NUMBER", "required": True},
                            "step_amount": {"type": "NUMBER", "required": False}
                        }
                    },
                    "trigger_events": {
                        "type": "JSON_ARRAY", 
                        "min_length": 1, 
                        "required": True,
                        "item_type": "ENUM",
                        "allowed_values": ["AMOUNT_CHANGE", "STATUS_UPDATE", "PAYMENT_RECEIVED", "INVOICE_SETTLED"]
                    },
                    "validation_rules": {
                        "type": "JSON_ARRAY", 
                        "min_length": 1, 
                        "required": True,
                        "item_schema": {
                            "rule": "ENUM[AMOUNT_RANGE,BALANCE_CHECK,AMOUNT_POSITIVE]",
                            "severity": "ENUM[ERROR,WARNING]"
                        }
                    },
                    "trans_type": {
                        "type": "ENUM", 
                        "values": ["CREDIT_ADJUSTMENT", "PAYMENT_SETTLEMENT", "RISK_REVIEW"],
                        "required": True
                    },
                    "flow_type": {
                        "type": "ENUM", 
                        "values": ["APPROVAL", "DIRECT", "MANUAL"],
                        "required": True
                    }
                },
                "batchSize": 100,
                "errorHandle": "DETAILED_LOG",  # 详细错误日志
                "duplicateHandle": "UPDATE",  # 重复记录更新
                "importMode": "MERGE",  # 合并模式
                "preValidation": {  # 预验证
                    "check_dependencies": True,  # 检查依赖关系
                    "validate_amount_limits": True  # 验证额度限制
                },
                "postProcessing": {  # 后处理
                    "auto_enable": True,  # 自动启用
                    "notify_admins": True  # 通知管理员
                }
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(task_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, task_data)
            
            # 3. 提交任务
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证任务提交
            self.assert_util.assert_response_success(response)
            task_result = response.get("data", {})
            assert task_result.get("success"), "导入任务提交失败"
            task_id = task_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导入任务ID"
            
            # 5. Allure报告
            a.json(filtered_params, "导入任务提交参数")
            a.json(response, "导入任务提交结果")
            self.logger.info(f"事务抬头导入任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导入任务失败原因")
            self.logger.error(f"提交导入任务失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试事务抬头标准导出",
        description="验证ADV_CM_ACC_TRANS_HEAD_CF_GEI_EXPOR...标准导出服务",
        severity="normal",
        order=10,
        tags=["erp_acc", "transaction", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export_trans_head(self):
        """测试事务抬头标准导出服务"""
        try:
            # 确保有测试数据
            if not self.trans_head_id:
                self.test_save_trans_head()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_CF_GEI_EXPOR")  # 标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数
            export_data = {
                "serviceKey": "ADV_CM_ACC_TRANS_HEAD_CF_GEI_EXPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"TRANS_HEAD_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_ACC_TRANS_HEAD",
                            "modelName": "事务抬头配置",
                            "sheetNo": 0,
                            "sheetName": "事务配置列表",
                            "headerConfigList": [
                                {"name": "事务ID", "type": "TEXT", "field": "id"},
                                {"name": "事务编码", "type": "TEXT", "field": "code"},
                                {"name": "事务名称", "type": "TEXT", "field": "name"},
                                {"name": "事务类型", "type": "TEXT", "field": "trans_type"},
                                {"name": "流程类型", "type": "TEXT", "field": "flow_type"},
                                {"name": "审计要求", "type": "BOOLEAN", "field": "audit_required"},
                                {"name": "自动审批限额", "type": "NUMBER", "field": "auto_approve_limit"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "enabled"},
                                {"name": "事件数量", "type": "NUMBER", "field": "events_count"},
                                {"name": "规则数量", "type": "NUMBER", "field": "rules_count"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_TRANS_RULE",
                            "modelName": "验证规则明细",
                            "sheetNo": 1,
                            "sheetName": "规则配置",
                            "headerConfigList": [
                                {"name": "规则ID", "type": "TEXT", "field": "id"},
                                {"name": "事务ID", "type": "NUMBER", "field": "trans_head_id"},
                                {"name": "规则类型", "type": "TEXT", "field": "rule"},
                                {"name": "参数配置", "type": "TEXT", "field": "params"},
                                {"name": "严重程度", "type": "TEXT", "field": "severity"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_TRANS_EVENT",
                            "modelName": "触发事件明细",
                            "sheetNo": 2,
                            "sheetName": "事件配置",
                            "headerConfigList": [
                                {"name": "事件ID", "type": "TEXT", "field": "id"},
                                {"name": "事务ID", "type": "NUMBER", "field": "trans_head_id"},
                                {"name": "事件类型", "type": "TEXT", "field": "event_type"},
                                {"name": "触发条件", "type": "TEXT", "field": "trigger_condition"},
                                {"name": "处理动作", "type": "TEXT", "field": "action"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_ACC_TRANS",
                        "viewKey": "ADV_CM_ACC_TRANS_HEAD:list",
                        "sceneKey": "ADV_CM_ACC_TRANS_HEAD",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 200,
                                    "needTotal": True,
                                    "sortOrders": [{"field": "create_time", "direction": "DESC"}],
                                    "conditionItems": [
                                        {"field": "id", "operator": "eq", "value": self.trans_head_id},
                                        {"field": "enabled", "operator": "eq", "value": True}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "trans_type"}, {"field": "flow_type"}, {"field": "audit_required"},
                                {"field": "auto_approve_limit"}, {"field": "enabled"},
                                {"field": "events_count"}, {"field": "rules_count"}
                            ],
                            "modelKey": "ADV_CM_ACC_TRANS_HEAD",
                            "expand": ["trigger_events", "validation_rules"]  # 展开关联数据
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_ACC_TRANS_HEAD",
                        "modelName": "事务抬头配置",
                        "containerKey": "ADV_CM_ACC_TRANS",
                        "viewKey": "ADV_CM_ACC_TRANS_HEAD:list",
                        "sceneKey": "ADV_CM_ACC_TRANS_HEAD",
                        "dataTransform": {  # 数据转换
                            "amount_limits": "format_currency",  # 格式化货币
                            "trigger_events": "array_to_string"   # 数组转字符串
                        }
                    }
                }
            }
            
            filtered_params = params.copy()
            ParamUtil.set_request_params(filtered_params, export_data)
            
            # 3. 发送导出请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证导出任务
            self.assert_util.assert_response_data(response)
            export_result = response.get("data", {})
            assert export_result.get("success"), "导出任务创建失败"
            task_id = export_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导出任务ID"
            expected_sheets = export_result.get("data", {}).get("expected_sheets", 0)
            assert expected_sheets >= 3, "预期工作表数量异常"
            
            # 5. Allure报告
            a.json(filtered_params, "标准导出请求参数")
            a.json(response, "标准导出响应结果")
            a.text(f"导出配置: {expected_sheets}个工作表 (抬头+规则+事件)", "导出结构")
            self.logger.info(f"事务抬头标准导出任务创建成功，Task ID: {task_id}, 工作表: {expected_sheets}")
            
        except Exception as e:
            a.text(str(e), "标准导出事务抬头失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户事务管理",
        title="测试提交事务抬头导出任务",
        description="验证ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TA...导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "transaction", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task_trans(self):
        """测试提交事务抬头导出任务"""
        try:
            # 确保有测试数据
            if not self.trans_head_id:
                self.test_save_trans_head()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_CF_API_GEI_TA_EXPORT")  # 导出任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"TRANS_HEAD_EXPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_TRANS_HEAD",
                "filterCondition": {
                    "enabled": True,
                    "trans_type": "in", 
                    "value": ["CREDIT_ADJUSTMENT", "PAYMENT_SETTLEMENT"],
                    "flow_type": "eq",
                    "value": "APPROVAL",
                    "audit_required": "eq",
                    "value": True,
                    "create_time": "between",
                    "value": ["2025-01-01", "2025-12-31"]
                },
                "exportFields": [
                    "id", "code", "name", "trans_type", "flow_type", "audit_required", 
                    "auto_approve_limit", "enabled", "cust_id", "org_id", "create_time"
                ],
                "expandFields": ["trigger_events", "validation_rules"],  # 展开关联字段
                "exportFormat": "EXCEL",
                "includeHeader": True,
                "separateSheets": True,  # 关联数据单独工作表
                "dataTransform": {
                    "amount_limits": "format_json_pretty",  # 格式化JSON
                    "trigger_events": "array_to_comma_separated",  # 数组转逗号分隔
                    "validation_rules": "array_to_table"  # 数组转表格
                },
                "summaryFields": [  # 汇总字段
                    "total_config_count",
                    "approval_flow_count", 
                    "direct_flow_count",
                    "audit_required_count"
                ],
                "customFilters": {  # 自定义过滤
                    "high_value_configs": {"amount_limits.max_adjust": "gt", "value": 50000}
                },
                "exportOptions": {
                    "include_empty": False,  # 排除空值
                    "remove_duplicates": True,  # 去重
                    "sort_by_priority": True  # 按优先级排序
                }
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(task_data.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, task_data)
            
            # 3. 提交任务
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证任务提交
            self.assert_util.assert_response_success(response)
            task_result = response.get("data", {})
            assert task_result.get("success"), "导出任务提交失败"
            task_id = task_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导出任务ID"
            estimated_rows = task_result.get("data", {}).get("estimated_rows", 0)
            estimated_sheets = task_result.get("data", {}).get("estimated_sheets", 0)
            
            # 5. Allure报告
            a.json(filtered_params, "导出任务提交参数")
            a.json(response, "导出任务提交结果")
            a.text(f"导出预估: {estimated_rows}行数据, {estimated_sheets}个工作表", "导出预估")
            self.logger.info(f"事务抬头导出任务提交成功，Task ID: {task_id}, 预估{estimated_rows}行")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    def _get_current_trans_info(self):
        """辅助方法：获取当前事务抬头信息"""
        try:
            api_path = self.get_api_path("ADV_CM_ACC_TRANS_HEAD_QUERY")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.trans_head_id}]
                },
                "fields": [
                    {"name": "name", "type": "TEXT"},
                    {"name": "trans_type", "type": "TEXT"},
                    {"name": "flow_type", "type": "TEXT"},
                    {"name": "audit_required", "type": "BOOLEAN"},
                    {"name": "amount_limits", "type": "OBJECT"},
                    {"name": "trigger_events", "type": "ARRAY"},
                    {"name": "validation_rules", "type": "ARRAY"}
                ],
                "expand": ["trigger_events", "validation_rules"]
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["pageable", "fields"], ["params", "request"])
            ParamUtil.set_request_params(filtered_params, query_params)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            records = response.get("data", {}).get("data", {}).get("records", [])
            if records:
                return records[0]
            return {}
            
        except Exception as e:
            self.logger.error(f"获取事务信息失败: {str(e)}")
            return {}
