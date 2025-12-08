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
@allure.feature("检查规则管理")
class TestCheckRuleManagement(ErpAccBaseTest):
    """检查规则管理测试类 - 覆盖检查规则CRUD和标准导入导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.check_rule_id = None
        cls.logger.info("检查规则管理测试类初始化完成")
        
        # 初始化依赖数据（检查规则依赖档案和基础数据）
        if cls.acc_cache_data:
            cls.acc_archive_id = cls.acc_cache_data.get("archive_info", [])[0].get("id") if cls.acc_cache_data.get("archive_info") else None
            cls.cust_id = cls.acc_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id") if cls.acc_cache_data.get("partner_info") else None
            cls.amount_config_id = cls.acc_cache_data.get("amount_info", [])[0].get("id") if cls.acc_cache_data.get("amount_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理检查规则主表
            cls.db.delete(
                table="adv_cm_cr_head",  # 检查规则抬头表，实际表名需确认
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("检查规则测试数据清理完成")
            
            # 清理规则条件明细表（如果存在）
            # cls.db.delete(table="adv_cm_cr_condition", where="rule_id like %s", params=["AT_%"])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    def _build_rule_conditions(self, rule_type="CREDIT_LIMIT"):
        """辅助方法：构建检查规则条件"""
        # 根据规则类型构建不同的条件配置
        if rule_type == "CREDIT_LIMIT":
            conditions = {
                "conditionItems": [
                    {
                        "field": "credit_limit",
                        "operator": "GT",  # 大于
                        "value": 50000.00,
                        "logic": "AND"
                    },
                    {
                        "field": "temp_limit", 
                        "operator": "LT",  # 小于
                        "value": 100000.00,
                        "logic": "AND"
                    },
                    {
                        "field": "status",
                        "operator": "EQ",
                        "value": "ACTIVE",
                        "logic": "AND"
                    }
                ],
                "action": "WARNING",  # 触发动作：警告
                "priority": 1,         # 优先级
                "description": "信用额度超过5万且临时额度小于10万时发出警告"
            }
        elif rule_type == "OVERDUE_DAYS":
            conditions = {
                "conditionItems": [
                    {
                        "field": "overdue_days",
                        "operator": "GT",
                        "value": 30,
                        "logic": "OR"
                    },
                    {
                        "field": "overdue_amount", 
                        "operator": "GT",
                        "value": 1000.00,
                        "logic": "OR"
                    }
                ],
                "action": "FROZEN",    # 触发动作：冻结
                "priority": 2,
                "description": "逾期天数超过30天或逾期金额超过1000元时冻结账户"
            }
        else:
            conditions = {
                "conditionItems": [],
                "action": "NONE",
                "priority": 0,
                "description": "默认规则"
            }
        
        return conditions
    
    @case_decorator(
        story="检查规则管理",
        title="测试创建检查规则",
        description="验证检查规则创建功能，包括规则条件和触发动作配置",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "check_rule", "create"]
    )
    def test_save_check_rule(self):
        """测试创建检查规则"""
        try:
            # 1. 检查依赖数据（需要账户档案或额度配置）
            if not self.acc_archive_id and not self.amount_config_id:
                self.logger.warning("缺少档案或额度配置依赖，跳过创建测试")
                pytest.skip("缺少基础依赖数据")
            
            # 2. 准备测试数据
            rule_code = self.mock_util.generate_unique_code(tag="CHK_RULE")
            rule_name = f"自动化测试检查规则_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 构建规则条件（信用额度检查）
            rule_conditions = self._build_rule_conditions("CREDIT_LIMIT")
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_SAVE")  # 假设创建API键名
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "archive_id", "amount_config_id", "rule_type", 
                              "conditions", "action", "priority", "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            create_data = {
                "code": rule_code,
                "name": rule_name,
                "archive_id": self.acc_archive_id or None,
                "amount_config_id": self.amount_config_id or None,
                "rule_type": "CREDIT_LIMIT_CHECK",  # 规则类型
                "conditions": rule_conditions["conditionItems"],  # 条件数组
                "action": rule_conditions["action"],
                "priority": rule_conditions["priority"],
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
            
            self.check_rule_id = data.get("id")
            assert self.check_rule_id, "未获取到规则ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", rule_code, "规则编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", rule_name, "规则名称验证失败")
            self.assert_util.assert_by_operator(data.get("action"), "=", rule_conditions["action"], "触发动作验证失败")
            self.assert_util.assert_by_operator(data.get("priority"), "=", rule_conditions["priority"], "优先级验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "启用状态验证失败")
            
            # 验证条件数量
            conditions_returned = data.get("conditions", [])
            assert len(conditions_returned) >= len(rule_conditions["conditionItems"]), "规则条件数量不匹配"
            
            # 7. Allure报告
            a.json(filtered_params, "创建检查规则请求参数")
            a.json(response, "创建检查规则响应结果")
            a.text(rule_conditions["description"], "规则描述")
            self.logger.info(f"检查规则创建成功，ID: {self.check_rule_id}, 类型: CREDIT_LIMIT_CHECK")
            
        except Exception as e:
            a.text(str(e), "创建检查规则失败原因")
            self.logger.error(f"创建检查规则失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试查询检查规则列表",
        description="验证检查规则分页查询功能，支持条件过滤",
        severity="normal",
        order=4,
        tags=["erp_acc", "check_rule", "query"]
    )
    def test_query_check_rule(self):
        """测试查询检查规则"""
        try:
            # 确保有测试数据
            if not self.check_rule_id:
                self.test_save_check_rule()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_QUERY")  # 假设查询API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [{"field": "priority", "direction": "ASC"}],
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.check_rule_id},
                        {"field": "enabled", "operator": "eq", "value": True}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "rule_type", "type": "TEXT"},
                    {"name": "action", "type": "TEXT"},
                    {"name": "priority", "type": "NUMBER"},
                    {"name": "enabled", "type": "BOOLEAN"},
                    {"name": "conditions_count", "type": "NUMBER"}  # 条件数量
                ],
                "systemParams": None,
                "expand": ["conditions"]  # 展开条件明细
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
            
            assert total >= 1, "未查询到检查规则记录"
            assert len(records) >= 1, "查询记录列表为空"
            
            # 验证具体记录
            rule_info = records[0]
            self.assert_util.assert_by_operator(rule_info.get("id"), "=", self.check_rule_id, "规则ID不匹配")
            self.assert_util.assert_by_operator(rule_info.get("action"), "=", "WARNING", "触发动作不匹配")
            self.assert_util.assert_by_operator(rule_info.get("priority"), "=", 1, "优先级不匹配")
            self.assert_util.assert_by_operator(rule_info.get("enabled"), "=", True, "启用状态不匹配")
            
            # 验证条件展开
            conditions = rule_info.get("conditions", [])
            assert len(conditions) >= 2, "规则条件展开失败"
            # 验证第一个条件
            first_condition = conditions[0]
            self.assert_util.assert_by_operator(first_condition.get("field"), "=", "credit_limit", "条件字段不匹配")
            self.assert_util.assert_by_operator(first_condition.get("operator"), "=", "GT", "条件操作符不匹配")
            
            # 5. Allure报告
            a.json(filtered_params, "查询检查规则参数")
            a.json(response, "查询检查规则结果")
            self.logger.info(f"检查规则查询成功，共{total}条记录，条件数量: {len(conditions)}")
            
        except Exception as e:
            a.text(str(e), "查询检查规则失败原因")
            self.logger.error(f"查询检查规则失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试更新检查规则",
        description="验证检查规则更新功能，修改条件配置和优先级",
        severity="normal",
        order=7,
        tags=["erp_acc", "check_rule", "update"]
    )
    def test_update_check_rule(self):
        """测试更新检查规则"""
        try:
            # 确保有测试数据
            if not self.check_rule_id:
                self.test_save_check_rule()
            
            # 1. 准备更新数据 - 修改为逾期检查规则
            new_rule_name = f"更新后逾期检查规则_{self.mock_util.get_timestamp()}"
            new_remark = self.mock_util.get_mock_remark()
            
            # 构建新的逾期规则条件
            new_conditions = self._build_rule_conditions("OVERDUE_DAYS")
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_UPDATE")  # 假设更新API键名
            params, url = self.get_api_params(api_path)
            
            # 3. 参数设置
            update_data = {
                "id": self.check_rule_id,
                "name": new_rule_name,
                "rule_type": "OVERDUE_CHECK",
                "conditions": new_conditions["conditionItems"],
                "action": new_conditions["action"],  # 改为FROZEN
                "priority": new_conditions["priority"],  # 改为2
                "enabled": True,
                "remark": new_remark
            }
            
            fields_to_filter = ["id", "name", "rule_type", "conditions", "action", "priority", "enabled", "remark"]
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
            self.test_query_check_rule()  # 重新查询验证
            
            # 额外验证更新内容
            updated_rule = self._get_current_rule_info()
            self.assert_util.assert_by_operator(updated_rule.get("name"), "=", new_rule_name, "规则名称更新失败")
            self.assert_util.assert_by_operator(updated_rule.get("rule_type"), "=", "OVERDUE_CHECK", "规则类型更新失败")
            self.assert_util.assert_by_operator(updated_rule.get("action"), "=", "FROZEN", "触发动作更新失败")
            self.assert_util.assert_by_operator(updated_rule.get("priority"), "=", 2, "优先级更新失败")
            
            # 验证新条件
            updated_conditions = updated_rule.get("conditions", [])
            overdue_condition = next((c for c in updated_conditions if c.get("field") == "overdue_days"), None)
            assert overdue_condition, "逾期天数条件未更新"
            self.assert_util.assert_by_operator(overdue_condition.get("operator"), "=", "GT", "逾期条件操作符不匹配")
            self.assert_util.assert_by_operator(overdue_condition.get("value"), "=", 30, "逾期天数阈值不匹配")
            
            # 7. Allure报告
            a.json(filtered_params, "更新检查规则参数")
            a.json(response, "更新检查规则结果")
            a.text(f"规则类型变更: CREDIT_LIMIT_CHECK -> OVERDUE_CHECK", "规则变更记录")
            a.text(new_conditions["description"], "更新后规则描述")
            self.logger.info(f"检查规则更新成功，ID: {self.check_rule_id}, 新类型: OVERDUE_CHECK")
            
        except Exception as e:
            a.text(str(e), "更新检查规则失败原因")
            self.logger.error(f"更新检查规则失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试删除检查规则",
        description="验证单个检查规则删除功能",
        severity="critical",
        order=16,
        tags=["erp_acc", "check_rule", "delete"]
    )
    def test_delete_check_rule(self):
        """测试删除检查规则"""
        try:
            # 确保有测试数据
            if not self.check_rule_id:
                self.test_save_check_rule()
            
            # 1. 获取删除API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_DELETE")  # 假设删除API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 单个ID删除参数
            delete_data = {"id": self.check_rule_id}
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
            saved_id = self.check_rule_id
            self.check_rule_id = None
            
            # 尝试查询已删除的规则
            api_path_query = self.get_api_path("ADV_CM_CR_HEAD_QUERY")
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
            
            assert len(query_records) == 0, f"删除后仍能查询到规则 ID: {saved_id}"
            
            # 6. Allure报告
            a.json(filtered_params, "删除检查规则参数")
            a.json(response, "删除检查规则结果")
            self.logger.info(f"检查规则删除成功，ID: {saved_id}")
            
        except Exception as e:
            a.text(str(e), "删除检查规则失败原因")
            self.logger.error(f"删除检查规则失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试检查规则抬头标准导入",
        description="验证ADV_CM_CR_HEAD_CF_GEI_IMPOR...标准导入服务",
        severity="normal",
        order=13,
        tags=["erp_acc", "check_rule", "import"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import_cr_head(self):
        """测试检查规则抬头标准导入服务"""
        try:
            # 1. 获取导入API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_CF_GEI_IMPOR")  # 标准导入服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导入参数
            import_data = {
                "serviceKey": "ADV_CM_CR_HEAD_CF_GEI_IMPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"CR_RULE_IMPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "filePath": "/tmp/check_rule_template.xlsx",
                    "modelKey": "ADV_CM_CR_HEAD",
                    "importConfig": {
                        "headerRow": 1,
                        "dataStartRow": 2,
                        "fieldMapping": {
                            "code": "A",
                            "name": "B",
                            "rule_type": "C",
                            "action": "D",
                            "priority": "E",
                            "conditions": "F"  # 条件JSON列
                        },
                        "validationRules": {
                            "priority": {"type": "NUMBER", "min": 1, "max": 10, "required": True},
                            "action": {"type": "ENUM", "values": ["WARNING", "FROZEN", "BLOCK"], "required": True}
                        }
                    }
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
            
            # 5. Allure报告
            a.json(filtered_params, "标准导入请求参数")
            a.json(response, "标准导入响应结果")
            self.logger.info(f"检查规则标准导入任务创建成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "标准导入检查规则失败原因")
            self.logger.error(f"标准导入失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试提交检查规则导入任务",
        description="验证ADV_CM_CR_HEAD_CF_API_GEI_TA...导入任务提交服务",
        severity="normal",
        order=14,
        tags=["erp_acc", "check_rule", "import_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_import_task_cr(self):
        """测试提交检查规则导入任务"""
        try:
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_CF_API_GEI_TA_IMPORT")  # 导入任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "IMPORT",
                "taskName": f"CR_RULE_IMPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_CR_HEAD",
                "fileInfo": {
                    "fileName": "check_rules_data.xlsx",
                    "fileSize": 20480,
                    "filePath": "/oss/check_rule_import/xxx.xlsx"
                },
                "importFields": ["code", "name", "rule_type", "action", "priority", "conditions"],
                "validationRules": {
                    "conditions": {"type": "JSON", "required": True},
                    "priority": {"type": "NUMBER", "min": 1, "required": True},
                    "action": {"type": "ENUM", "values": ["WARNING", "FROZEN"], "required": True}
                },
                "batchSize": 100,  # 批次大小
                "errorHandle": "CONTINUE"  # 错误处理策略
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
            self.logger.info(f"检查规则导入任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导入任务失败原因")
            self.logger.error(f"提交导入任务失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试检查规则抬头标准导出",
        description="验证ADV_CM_CR_HEAD_CF_GEI_EXPOR...标准导出服务",
        severity="normal",
        order=10,
        tags=["erp_acc", "check_rule", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export_cr_head(self):
        """测试检查规则抬头标准导出服务"""
        try:
            # 确保有测试数据
            if not self.check_rule_id:
                self.test_save_check_rule()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_CF_GEI_EXPOR")  # 标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数
            export_data = {
                "serviceKey": "ADV_CM_CR_HEAD_CF_GEI_EXPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"CR_RULE_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_CR_HEAD",
                            "modelName": "检查规则抬头",
                            "sheetNo": 0,
                            "sheetName": "规则列表",
                            "headerConfigList": [
                                {"name": "规则ID", "type": "TEXT", "field": "id"},
                                {"name": "规则编码", "type": "TEXT", "field": "code"},
                                {"name": "规则名称", "type": "TEXT", "field": "name"},
                                {"name": "规则类型", "type": "TEXT", "field": "rule_type"},
                                {"name": "触发动作", "type": "TEXT", "field": "action"},
                                {"name": "优先级", "type": "NUMBER", "field": "priority"},
                                {"name": "条件数量", "type": "NUMBER", "field": "conditions_count"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "enabled"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_CR_CONDITION",
                            "modelName": "规则条件明细",
                            "sheetNo": 1,
                            "sheetName": "条件配置",
                            "headerConfigList": [
                                {"name": "条件ID", "type": "TEXT", "field": "id"},
                                {"name": "规则ID", "type": "NUMBER", "field": "rule_id"},
                                {"name": "字段名", "type": "TEXT", "field": "field"},
                                {"name": "操作符", "type": "TEXT", "field": "operator"},
                                {"name": "比较值", "type": "TEXT", "field": "value"},
                                {"name": "逻辑连接", "type": "TEXT", "field": "logic"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_CR",
                        "viewKey": "ADV_CM_CR_HEAD:list",
                        "sceneKey": "ADV_CM_CR_HEAD",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 100,
                                    "needTotal": True,
                                    "sortOrders": [{"field": "priority", "direction": "ASC"}],
                                    "conditionItems": [
                                        {"field": "id", "operator": "eq", "value": self.check_rule_id},
                                        {"field": "enabled", "operator": "eq", "value": True}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "rule_type"}, {"field": "action"}, {"field": "priority"},
                                {"field": "enabled"}, {"field": "conditions_count"}
                            ],
                            "modelKey": "ADV_CM_CR_HEAD",
                            "expand": ["conditions"]  # 展开条件明细
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_CR_HEAD",
                        "modelName": "检查规则抬头",
                        "containerKey": "ADV_CM_CR",
                        "viewKey": "ADV_CM_CR_HEAD:list",
                        "sceneKey": "ADV_CM_CR_HEAD"
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
            
            # 5. Allure报告
            a.json(filtered_params, "标准导出请求参数")
            a.json(response, "标准导出响应结果")
            self.logger.info(f"检查规则标准导出任务创建成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "标准导出检查规则失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查规则管理",
        title="测试提交检查规则导出任务",
        description="验证ADV_CM_CR_HEAD_CF_API_GEI_TA...导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "check_rule", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task_cr(self):
        """测试提交检查规则导出任务"""
        try:
            # 确保有测试数据
            if not self.check_rule_id:
                self.test_save_check_rule()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_CR_HEAD_CF_API_GEI_TA_EXPORT")  # 导出任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"CR_RULE_EXPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_CR_HEAD",
                "filterCondition": {
                    "enabled": True,
                    "priority": {"min": 1, "max": 5}
                },
                "exportFields": [
                    "id", "code", "name", "rule_type", "action", "priority", "enabled"
                ],
                "expandFields": ["conditions"],  # 导出时展开条件
                "exportFormat": "EXCEL",
                "includeHeader": True,
                "separateSheets": True  # 条件明细单独工作表
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
            
            # 5. Allure报告
            a.json(filtered_params, "导出任务提交参数")
            a.json(response, "导出任务提交结果")
            self.logger.info(f"检查规则导出任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    def _get_current_rule_info(self):
        """辅助方法：获取当前检查规则信息"""
        try:
            api_path = self.get_api_path("ADV_CM_CR_HEAD_QUERY")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.check_rule_id}]
                },
                "fields": [
                    {"name": "name", "type": "TEXT"},
                    {"name": "rule_type", "type": "TEXT"},
                    {"name": "action", "type": "TEXT"},
                    {"name": "priority", "type": "NUMBER"},
                    {"name": "conditions", "type": "ARRAY"}
                ],
                "expand": ["conditions"]
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
            self.logger.error(f"获取规则信息失败: {str(e)}")
            return {}
