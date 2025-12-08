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
@allure.feature("检查项管理")
class TestCheckItemManagement(ErpAccBaseTest):
    """检查项管理测试类 - 覆盖检查项CRUD和标准导入导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.check_item_id = None
        cls.logger.info("检查项管理测试类初始化完成")
        
        # 初始化依赖数据（检查项依赖规则和基础数据）
        if cls.acc_cache_data:
            cls.check_rule_id = cls.acc_cache_data.get("rule_info", [])[0].get("id") if cls.acc_cache_data.get("rule_info") else None
            cls.acc_archive_id = cls.acc_cache_data.get("archive_info", [])[0].get("id") if cls.acc_cache_data.get("archive_info") else None
            cls.amount_config_id = cls.acc_cache_data.get("amount_info", [])[0].get("id") if cls.acc_cache_data.get("amount_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理检查项主表
            cls.db.delete(
                table="adv_cm_cs_type",  # 检查项表，实际表名需确认
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("检查项测试数据清理完成")
            
            # 清理检查项规则关联表（如果存在）
            # cls.db.delete(table="adv_cm_cs_rule_assoc", where="item_id like %s", params=["AT_%"])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    def _build_check_item_config(self, item_type="AMOUNT_CHECK"):
        """辅助方法：构建检查项配置"""
        # 根据检查项类型构建不同的配置
        if item_type == "AMOUNT_CHECK":
            config = {
                "item_type": "AMOUNT_VALIDATION",
                "check_fields": ["credit_limit", "temp_limit", "available_limit"],
                "validation_rules": [
                    {
                        "field": "credit_limit",
                        "rule": "REQUIRED",
                        "message": "信用额度不能为空",
                        "severity": "ERROR"
                    },
                    {
                        "field": "temp_limit", 
                        "rule": "RANGE",
                        "params": {"min": 0, "max": 1000000},
                        "message": "临时额度必须在0-100万之间",
                        "severity": "WARNING"
                    },
                    {
                        "field": "available_limit",
                        "rule": "GREATER_THAN",
                        "compare_field": "credit_limit",
                        "message": "可用额度不能大于信用额度",
                        "severity": "ERROR"
                    }
                ],
                "execution_order": 1,
                "description": "额度信息完整性检查，包括必填、范围和逻辑验证"
            }
        elif item_type == "STATUS_CHECK":
            config = {
                "item_type": "STATUS_VALIDATION",
                "check_fields": ["account_status", "risk_level", "enabled"],
                "validation_rules": [
                    {
                        "field": "account_status",
                        "rule": "IN_LIST",
                        "params": {"values": ["ACTIVE", "FROZEN", "BLOCKED"]},
                        "message": "账户状态必须是有效的枚举值",
                        "severity": "ERROR"
                    },
                    {
                        "field": "risk_level",
                        "rule": "RANGE",
                        "params": {"min": 1, "max": 5},
                        "message": "风险等级必须在1-5之间",
                        "severity": "WARNING"
                    },
                    {
                        "field": "enabled",
                        "rule": "BOOLEAN_TRUE",
                        "message": "检查项必须启用",
                        "severity": "ERROR"
                    }
                ],
                "execution_order": 2,
                "description": "账户状态和风险等级的有效性检查"
            }
        else:
            config = {
                "item_type": "BASIC",
                "check_fields": [],
                "validation_rules": [],
                "execution_order": 0,
                "description": "默认检查项配置"
            }
        
        return config
    
    @case_decorator(
        story="检查项管理",
        title="测试创建检查项",
        description="验证检查项创建功能，包括验证规则和字段配置",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "check_item", "create"]
    )
    def test_save_check_item(self):
        """测试创建检查项"""
        try:
            # 1. 检查依赖数据（需要检查规则）
            if not self.check_rule_id:
                self.logger.warning("缺少检查规则依赖，跳过创建测试")
                pytest.skip("缺少检查规则依赖数据")
            
            # 2. 准备测试数据
            item_code = self.mock_util.generate_unique_code(tag="CHK_ITEM")
            item_name = f"自动化测试检查项_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 构建检查项配置（额度检查）
            item_config = self._build_check_item_config("AMOUNT_CHECK")
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_SAVE")  # 假设创建API键名
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "rule_id", "archive_id", "amount_config_id",
                              "item_type", "check_fields", "validation_rules", 
                              "execution_order", "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            create_data = {
                "code": item_code,
                "name": item_name,
                "rule_id": self.check_rule_id,  # 关联检查规则
                "archive_id": self.acc_archive_id or None,
                "amount_config_id": self.amount_config_id or None,
                "item_type": item_config["item_type"],
                "check_fields": item_config["check_fields"],
                "validation_rules": item_config["validation_rules"],
                "execution_order": item_config["execution_order"],
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
            
            self.check_item_id = data.get("id")
            assert self.check_item_id, "未获取到检查项ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", item_code, "检查项编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", item_name, "检查项名称验证失败")
            self.assert_util.assert_by_operator(data.get("item_type"), "=", item_config["item_type"], "检查项类型验证失败")
            self.assert_util.assert_by_operator(data.get("execution_order"), "=", item_config["execution_order"], "执行顺序验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "启用状态验证失败")
            
            # 验证规则数量
            rules_returned = data.get("validation_rules", [])
            assert len(rules_returned) >= len(item_config["validation_rules"]), "验证规则数量不匹配"
            
            # 验证第一个规则
            first_rule = rules_returned[0]
            self.assert_util.assert_by_operator(first_rule.get("field"), "=", "credit_limit", "规则字段不匹配")
            self.assert_util.assert_by_operator(first_rule.get("rule"), "=", "REQUIRED", "规则类型不匹配")
            self.assert_util.assert_by_operator(first_rule.get("severity"), "=", "ERROR", "严重程度不匹配")
            
            # 7. Allure报告
            a.json(filtered_params, "创建检查项请求参数")
            a.json(response, "创建检查项响应结果")
            a.text(item_config["description"], "检查项描述")
            self.logger.info(f"检查项创建成功，ID: {self.check_item_id}, 类型: {item_config['item_type']}")
            
        except Exception as e:
            a.text(str(e), "创建检查项失败原因")
            self.logger.error(f"创建检查项失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试查询检查项列表",
        description="验证检查项分页查询功能，支持规则关联过滤",
        severity="normal",
        order=4,
        tags=["erp_acc", "check_item", "query"]
    )
    def test_query_check_item(self):
        """测试查询检查项"""
        try:
            # 确保有测试数据
            if not self.check_item_id:
                self.test_save_check_item()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_QUERY")  # 假设查询API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [{"field": "execution_order", "direction": "ASC"}],
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.check_item_id},
                        {"field": "enabled", "operator": "eq", "value": True},
                        {"field": "rule_id", "operator": "eq", "value": self.check_rule_id}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "item_type", "type": "TEXT"},
                    {"name": "execution_order", "type": "NUMBER"},
                    {"name": "enabled", "type": "BOOLEAN"},
                    {"name": "rule_id", "type": "NUMBER"},
                    {"name": "rules_count", "type": "NUMBER"}  # 验证规则数量
                ],
                "systemParams": None,
                "expand": ["validation_rules"]  # 展开验证规则明细
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
            
            assert total >= 1, "未查询到检查项记录"
            assert len(records) >= 1, "查询记录列表为空"
            
            # 验证具体记录
            item_info = records[0]
            self.assert_util.assert_by_operator(item_info.get("id"), "=", self.check_item_id, "检查项ID不匹配")
            self.assert_util.assert_by_operator(item_info.get("item_type"), "=", "AMOUNT_VALIDATION", "检查项类型不匹配")
            self.assert_util.assert_by_operator(item_info.get("execution_order"), "=", 1, "执行顺序不匹配")
            self.assert_util.assert_by_operator(item_info.get("enabled"), "=", True, "启用状态不匹配")
            self.assert_util.assert_by_operator(item_info.get("rule_id"), "=", self.check_rule_id, "关联规则ID不匹配")
            
            # 验证规则展开
            rules = item_info.get("validation_rules", [])
            assert len(rules) >= 3, "验证规则展开失败"
            # 验证第一个规则（信用额度必填）
            first_rule = rules[0]
            self.assert_util.assert_by_operator(first_rule.get("field"), "=", "credit_limit", "规则字段不匹配")
            self.assert_util.assert_by_operator(first_rule.get("rule"), "=", "REQUIRED", "规则类型不匹配")
            self.assert_util.assert_by_operator(first_rule.get("severity"), "=", "ERROR", "严重程度不匹配")
            self.assert_util.assert_by_operator(first_rule.get("message"), "contains", "不能为空", "错误消息不匹配")
            
            # 5. Allure报告
            a.json(filtered_params, "查询检查项参数")
            a.json(response, "查询检查项结果")
            self.logger.info(f"检查项查询成功，共{total}条记录，规则数量: {len(rules)}")
            
        except Exception as e:
            a.text(str(e), "查询检查项失败原因")
            self.logger.error(f"查询检查项失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试更新检查项",
        description="验证检查项更新功能，修改类型和验证规则配置",
        severity="normal",
        order=7,
        tags=["erp_acc", "check_item", "update"]
    )
    def test_update_check_item(self):
        """测试更新检查项"""
        try:
            # 确保有测试数据
            if not self.check_item_id:
                self.test_save_check_item()
            
            # 1. 准备更新数据 - 修改为状态检查项
            new_item_name = f"更新后状态检查项_{self.mock_util.get_timestamp()}"
            new_remark = self.mock_util.get_mock_remark()
            
            # 构建新的状态检查配置
            new_config = self._build_check_item_config("STATUS_CHECK")
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_UPDATE")  # 假设更新API键名
            params, url = self.get_api_params(api_path)
            
            # 3. 参数设置
            update_data = {
                "id": self.check_item_id,
                "name": new_item_name,
                "item_type": new_config["item_type"],  # 改为STATUS_VALIDATION
                "check_fields": new_config["check_fields"],
                "validation_rules": new_config["validation_rules"],
                "execution_order": new_config["execution_order"],  # 改为2
                "enabled": True,
                "remark": new_remark
            }
            
            fields_to_filter = ["id", "name", "item_type", "check_fields", "validation_rules", 
                              "execution_order", "enabled", "remark"]
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
            self.test_query_check_item()  # 重新查询验证
            
            # 额外验证更新内容
            updated_item = self._get_current_item_info()
            self.assert_util.assert_by_operator(updated_item.get("name"), "=", new_item_name, "检查项名称更新失败")
            self.assert_util.assert_by_operator(updated_item.get("item_type"), "=", "STATUS_VALIDATION", "检查项类型更新失败")
            self.assert_util.assert_by_operator(updated_item.get("execution_order"), "=", 2, "执行顺序更新失败")
            
            # 验证新规则
            updated_rules = updated_item.get("validation_rules", [])
            status_rule = next((r for r in updated_rules if r.get("field") == "account_status"), None)
            assert status_rule, "账户状态规则未更新"
            self.assert_util.assert_by_operator(status_rule.get("rule"), "=", "IN_LIST", "状态规则类型不匹配")
            self.assert_util.assert_by_operator(status_rule.get("params", {}).get("values"), "contains", "ACTIVE", "状态枚举值不匹配")
            self.assert_util.assert_by_operator(status_rule.get("severity"), "=", "ERROR", "严重程度不匹配")
            
            # 7. Allure报告
            a.json(filtered_params, "更新检查项参数")
            a.json(response, "更新检查项结果")
            a.text(f"检查项类型变更: AMOUNT_VALIDATION -> STATUS_VALIDATION", "类型变更记录")
            a.text(new_config["description"], "更新后检查项描述")
            self.logger.info(f"检查项更新成功，ID: {self.check_item_id}, 新类型: {new_config['item_type']}")
            
        except Exception as e:
            a.text(str(e), "更新检查项失败原因")
            self.logger.error(f"更新检查项失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试删除检查项",
        description="验证单个检查项删除功能",
        severity="critical",
        order=16,
        tags=["erp_acc", "check_item", "delete"]
    )
    def test_delete_check_item(self):
        """测试删除检查项"""
        try:
            # 确保有测试数据
            if not self.check_item_id:
                self.test_save_check_item()
            
            # 1. 获取删除API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_DELETE")  # 假设删除API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 单个ID删除参数
            delete_data = {"id": self.check_item_id}
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
            saved_id = self.check_item_id
            self.check_item_id = None
            
            # 尝试查询已删除的检查项
            api_path_query = self.get_api_path("ADV_CM_CS_TYPE_QUERY")
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
            
            assert len(query_records) == 0, f"删除后仍能查询到检查项 ID: {saved_id}"
            
            # 6. Allure报告
            a.json(filtered_params, "删除检查项参数")
            a.json(response, "删除检查项结果")
            self.logger.info(f"检查项删除成功，ID: {saved_id}")
            
        except Exception as e:
            a.text(str(e), "删除检查项失败原因")
            self.logger.error(f"删除检查项失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试检查项标准导出",
        description="验证ADV_CM_CS_TYPE_CF_GEI_EXPOR...标准导出服务",
        severity="normal",
        order=10,
        tags=["erp_acc", "check_item", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export_cs_type(self):
        """测试检查项标准导出服务"""
        try:
            # 确保有测试数据
            if not self.check_item_id:
                self.test_save_check_item()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_CF_GEI_EXPOR")  # 标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数
            export_data = {
                "serviceKey": "ADV_CM_CS_TYPE_CF_GEI_EXPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"CS_ITEM_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_CS_TYPE",
                            "modelName": "检查项配置",
                            "sheetNo": 0,
                            "sheetName": "检查项列表",
                            "headerConfigList": [
                                {"name": "检查项ID", "type": "TEXT", "field": "id"},
                                {"name": "检查项编码", "type": "TEXT", "field": "code"},
                                {"name": "检查项名称", "type": "TEXT", "field": "name"},
                                {"name": "检查类型", "type": "TEXT", "field": "item_type"},
                                {"name": "执行顺序", "type": "NUMBER", "field": "execution_order"},
                                {"name": "关联规则ID", "type": "NUMBER", "field": "rule_id"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "enabled"},
                                {"name": "规则数量", "type": "NUMBER", "field": "rules_count"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_CS_RULE",
                            "modelName": "验证规则明细",
                            "sheetNo": 1,
                            "sheetName": "规则配置",
                            "headerConfigList": [
                                {"name": "规则ID", "type": "TEXT", "field": "id"},
                                {"name": "检查项ID", "type": "NUMBER", "field": "item_id"},
                                {"name": "检查字段", "type": "TEXT", "field": "field"},
                                {"name": "验证规则", "type": "TEXT", "field": "rule"},
                                {"name": "参数配置", "type": "TEXT", "field": "params"},
                                {"name": "错误消息", "type": "TEXT", "field": "message"},
                                {"name": "严重程度", "type": "TEXT", "field": "severity"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_CS",
                        "viewKey": "ADV_CM_CS_TYPE:list",
                        "sceneKey": "ADV_CM_CS_TYPE",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 100,
                                    "needTotal": True,
                                    "sortOrders": [{"field": "execution_order", "direction": "ASC"}],
                                    "conditionItems": [
                                        {"field": "id", "operator": "eq", "value": self.check_item_id},
                                        {"field": "enabled", "operator": "eq", "value": True}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "item_type"}, {"field": "execution_order"}, 
                                {"field": "rule_id"}, {"field": "enabled"}, {"field": "rules_count"}
                            ],
                            "modelKey": "ADV_CM_CS_TYPE",
                            "expand": ["validation_rules"]  # 展开验证规则
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_CS_TYPE",
                        "modelName": "检查项配置",
                        "containerKey": "ADV_CM_CS",
                        "viewKey": "ADV_CM_CS_TYPE:list",
                        "sceneKey": "ADV_CM_CS_TYPE"
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
            self.logger.info(f"检查项标准导出任务创建成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "标准导出检查项失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试提交检查项导出任务",
        description="验证ADV_CM_CS_TYPE_CF_API_GEI_TA...导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "check_item", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task_cs(self):
        """测试提交检查项导出任务"""
        try:
            # 确保有测试数据
            if not self.check_item_id:
                self.test_save_check_item()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_CF_API_GEI_TA_EXPORT")  # 导出任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"CS_ITEM_EXPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_CS_TYPE",
                "filterCondition": {
                    "enabled": True,
                    "execution_order": {"min": 1, "max": 5}
                },
                "exportFields": [
                    "id", "code", "name", "item_type", "execution_order", "enabled", "rule_id"
                ],
                "expandFields": ["validation_rules"],  # 导出时展开规则
                "exportFormat": "EXCEL",
                "includeHeader": True,
                "separateSheets": True,  # 规则明细单独工作表
                "dataTransform": {  # 数据转换规则
                    "severity": {
                        "ERROR": "严重错误",
                        "WARNING": "警告",
                        "INFO": "信息"
                    }
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
            
            # 5. Allure报告
            a.json(filtered_params, "导出任务提交参数")
            a.json(response, "导出任务提交结果")
            self.logger.info(f"检查项导出任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试检查项标准导入",
        description="验证ADV_CM_CS_TYPE_CF_GEI_IMPORT...标准导入服务",
        severity="normal",
        order=13,
        tags=["erp_acc", "check_item", "import"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import_cs_type(self):
        """测试检查项标准导入服务"""
        try:
            # 1. 获取导入API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_CF_GEI_IMPORT")  # 标准导入服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导入参数
            import_data = {
                "serviceKey": "ADV_CM_CS_TYPE_CF_GEI_IMPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"CS_ITEM_IMPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "filePath": "/tmp/check_item_template.xlsx",
                    "modelKey": "ADV_CM_CS_TYPE",
                    "importConfig": {
                        "headerRow": 1,
                        "dataStartRow": 2,
                        "fieldMapping": {
                            "code": "A",
                            "name": "B",
                            "item_type": "C",
                            "execution_order": "D",
                            "rule_id": "E",
                            "validation_rules": "F"  # 规则JSON列
                        },
                        "validationRules": {
                            "execution_order": {"type": "NUMBER", "min": 1, "max": 10, "required": True},
                            "item_type": {"type": "ENUM", "values": ["AMOUNT_VALIDATION", "STATUS_VALIDATION"], "required": True},
                            "validation_rules": {"type": "JSON_ARRAY", "required": True, "min_length": 1}
                        },
                        "defaultValues": {
                            "enabled": True,
                            "remark": "系统导入"
                        }
                    },
                    "batchSize": 50,  # 批次导入
                    "errorHandle": "LOG"  # 记录错误但继续
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
            success_count = import_result.get("data", {}).get("success_count", 0)
            error_count = import_result.get("data", {}).get("error_count", 0)
            assert success_count >= 0, "成功导入数量异常"
            
            # 5. Allure报告
            a.json(filtered_params, "标准导入请求参数")
            a.json(response, "标准导入响应结果")
            a.text(f"导入结果: 成功{success_count}条, 错误{error_count}条", "导入统计")
            self.logger.info(f"检查项标准导入任务创建成功，Task ID: {task_id}, 成功: {success_count}")
            
        except Exception as e:
            a.text(str(e), "标准导入检查项失败原因")
            self.logger.error(f"标准导入失败: {str(e)}")
            raise
    
    @case_decorator(
        story="检查项管理",
        title="测试提交检查项导入任务",
        description="验证ADV_CM_CS_TYPE_CF_API_GEI_TA...导入任务提交服务",
        severity="normal",
        order=14,
        tags=["erp_acc", "check_item", "import_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_import_task_cs(self):
        """测试提交检查项导入任务"""
        try:
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_CS_TYPE_CF_API_GEI_TA_IMPORT")  # 导入任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "IMPORT",
                "taskName": f"CS_ITEM_IMPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_CS_TYPE",
                "fileInfo": {
                    "fileName": "check_items_data.xlsx",
                    "fileSize": 30720,
                    "filePath": "/oss/check_item_import/xxx.xlsx",
                    "fileType": "EXCEL"
                },
                "importFields": [
                    "code", "name", "item_type", "execution_order", "rule_id", 
                    "check_fields", "validation_rules"
                ],
                "validationRules": {
                    "validation_rules": {
                        "type": "JSON_ARRAY", 
                        "required": True, 
                        "schema": {
                            "field": "STRING",
                            "rule": "ENUM[REQUIRED,RANGE,GREATER_THAN]",
                            "severity": "ENUM[ERROR,WARNING,INFO]"
                        }
                    },
                    "execution_order": {"type": "NUMBER", "min": 1, "required": True},
                    "item_type": {"type": "ENUM", "values": ["AMOUNT_VALIDATION", "STATUS_VALIDATION"], "required": True}
                },
                "batchSize": 100,
                "errorHandle": "CONTINUE",  # 继续处理错误记录
                "duplicateHandle": "UPDATE",  # 重复记录更新
                "importMode": "APPEND"  # 追加模式
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
            self.logger.info(f"检查项导入任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导入任务失败原因")
            self.logger.error(f"提交导入任务失败: {str(e)}")
            raise
    
    def _get_current_item_info(self):
        """辅助方法：获取当前检查项信息"""
        try:
            api_path = self.get_api_path("ADV_CM_CS_TYPE_QUERY")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.check_item_id}]
                },
                "fields": [
                    {"name": "name", "type": "TEXT"},
                    {"name": "item_type", "type": "TEXT"},
                    {"name": "execution_order", "type": "NUMBER"},
                    {"name": "validation_rules", "type": "ARRAY"}
                ],
                "expand": ["validation_rules"]
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
            self.logger.error(f"获取检查项信息失败: {str(e)}")
            return {}
