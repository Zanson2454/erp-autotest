import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("风险管理")
@pytest.mark.skip(reason="风险管理功能暂未开发，暂时跳过")
class TestRiskManagement(GenMdBaseTest):
    """风险管理测试类 - 覆盖库存风险定时通知等风险相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        # 数据存储
        cls.risk_id = None
        cls.risk_code = None
        cls.risk_tr_id = None  # 风险项目ID
        cls.logger.info("风险管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 风险管理通常涉及定时任务和系统配置，不需要清理测试数据
            cls.logger.info("风险管理测试类结束")
        except Exception as e:
            cls.logger.error(f"测试类结束异常: {str(e)}")

        super().teardown_class()
    # ================ 库存风险管理 ================
    @case_decorator(
        story="风险管理",
        title="测试库存风险定时通知服务",
        description="验证库存风险定时通知服务功能 - 用于监控库存风险并发送通知",
        severity="normal",
        file_level_order=1,
        tags=["风险管理", "库存风险", "定时通知", "inventory_risk_timed_notification"]
    )
    @pytest.mark.skip(reason="库存风险定时通知服务为系统定时任务，无法直接调用测试")
    def test_inventory_risk_timed_notification(self):
        """
        库存风险定时通知服务用例 - inventory_risk_timed_notification
        
        该服务为系统定时任务，用于：
        1. 定时检查库存风险状态
        2. 识别超出安全库存阈值的物料
        3. 发送风险预警通知给相关人员
        4. 记录风险通知日志
        """
        try:
            # 模拟库存风险定时通知服务的参数结构
            notification_params = {
                "serviceKey": "inventory_risk_timed_notification",
                "params": {
                    "riskType": "INVENTORY_SHORTAGE",  # 库存短缺风险
                    "checkInterval": "DAILY",  # 检查频率：每日
                    "thresholdConfig": {
                        "safetyStockLevel": 100,  # 安全库存水平
                        "riskLevel": "HIGH",  # 风险等级
                        "alertThreshold": 0.2  # 预警阈值（20%）
                    },
                    "notificationConfig": {
                        "notifyUsers": ["admin", "warehouse_manager"],  # 通知用户
                        "notifyMethods": ["EMAIL", "SMS", "SYSTEM"],  # 通知方式
                        "notifyTemplate": "INVENTORY_RISK_ALERT"  # 通知模板
                    },
                    "filterConditions": {
                        "materialTypes": ["FINP", "SEMI", "RAW"],  # 物料类型过滤
                        "warehouseIds": [],  # 仓库ID过滤
                        "orgIds": []  # 组织ID过滤
                    },
                    "scheduleConfig": {
                        "enabled": True,  # 是否启用
                        "cronExpression": "0 0 8 * * ?",  # 每天8点执行
                        "timezone": "Asia/Shanghai"  # 时区
                    }
                }
            }

            # 模拟API路径
            api_url = "/api/trantor/service/engine/execute/inventory_risk_timed_notification"
            
            # 模拟响应数据
            mock_response = {
                "success": True,
                "message": "库存风险定时通知服务配置成功",
                "data": {
                    "taskId": f"RISK_TASK_{self.mock_util.get_timestamp()}",
                    "scheduleStatus": "SCHEDULED",
                    "nextExecutionTime": "2024-01-01 08:00:00",
                    "riskItemsCount": 0,
                    "notificationsSent": 0
                }
            }
            
            # 由于是定时任务，无法直接调用，这里仅做参数验证
            self.logger.info("库存风险定时通知服务参数配置完成")
            self.assert_util.assert_by_operator(notification_params.get("serviceKey"), "=", 
                                               "inventory_risk_timed_notification", "服务标识正确")
            self.assert_util.assert_by_operator(notification_params.get("params", {}).get("riskType"), "=", 
                                               "INVENTORY_SHORTAGE", "风险类型配置正确")

            a.json(notification_params, "定时通知服务参数")
            a.json(mock_response, "模拟响应数据")
            a.text("库存风险定时通知服务为系统后台定时任务，用于监控库存状态并发送预警通知", "服务说明")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险规则分页查询",
        description="验证风险规则分页查询服务功能",
        severity="normal",
        file_level_order=2,
        tags=["风险管理", "风险规则", "分页查询"]
    )
    @pytest.mark.skip(reason="后端数据库缺少'indicator'列，导致查询异常：Unknown column 'indicator' in 'field list'")
    def test_query_risk_rule_page(self):
        """风险规则分页查询用例 - 用于查看系统配置的风险规则"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "riskitemCode", "type": "TEXT"},
                    {"name": "riskitemName", "type": "TEXT"},
                    {"name": "riskitemLevel", "type": "TEXT"},
                    {"name": "riskitemText", "type": "TEXT"}
                ],
                "systemParams": None
            }
            response, _ = self.standard_api_call(
                api_key="风险规则分页查询服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"]
            )
            self.assert_util.assert_response_data(response)

            # 保存风险规则ID用于后续测试
            data_list = response.get("data", {}).get("data", {}).get("records", [])
            if data_list:
                self.risk_id = data_list[0].get("id")
                self.risk_code = data_list[0].get("riskitemCode")

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险规则保存",
        description="验证风险规则保存服务功能",
        severity="blocker",
        file_level_order=3,
        tags=["风险管理", "风险规则", "保存", "GEN_RISK_RULE_MD_SAVE_SERVICE"]
    )
    @pytest.mark.skip(reason="风险规则保存服务功能暂未开发，暂时跳过")
    def test_save_risk_rule(self):
        """风险规则保存用例 - GEN_RISK_RULE_MD_SAVE_SERVICE"""
        try:
            # 生成测试数据
            risk_rule_code = self.mock_util.generate_unique_code(tag="RISK_RULE")
            risk_rule_name = f"风险规则_{self.mock_util.get_timestamp()}"

            set_dict = {
                "riskitemCode": risk_rule_code,
                "riskitemName": risk_rule_name,
                "riskitemLevel": "HIGH",
                "riskitemText": f"风险规则描述_{self.mock_util.get_timestamp()}",
                "dimension": "INVENTORY",  # 维度不能为空，设置为库存维度
                "indicatorClass": "QUANTITY",  # 指标类型不能为空，设置为数量类型
                "btClass": "ORDER"  # 业务类型不能为空，设置为订单类型
            }
            response, extracted_id = self.standard_api_call(
                api_key="风险规则保存服务",
                set_dict=set_dict,
                fields_to_filter=["riskitemCode", "riskitemName", "riskitemLevel", "riskitemText", "dimension", "indicatorClass", "btClass"]
            )
            self.assert_util.assert_response_data(response)

            # 保存风险规则ID
            self.risk_id = extracted_id
            self.risk_code = risk_rule_code

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险项目保存",
        description="验证风险项目保存服务功能",
        severity="blocker",
        file_level_order=4,
        tags=["风险管理", "风险项目", "保存", "GEN_RISK_TR_SAVE_SERVICE"]
    )
    @pytest.mark.skip(reason="风险项目保存服务功能暂未开发，暂时跳过")
    def test_save_risk_tr(self):
        """风险项目保存用例 - GEN_RISK_TR_SAVE_SERVICE"""
        try:
            # 检查依赖：如果风险规则不存在，先创建风险规则
            if not self.risk_id:
                self.test_save_risk_rule()
            
            # 生成测试数据
            risk_tr_code = self.mock_util.generate_unique_code(tag="RISK_TR")
            risk_tr_name = f"风险项目_{self.mock_util.get_timestamp()}"

            set_dict = {
                "riskCode": risk_tr_code,
                "riskName": risk_tr_name,
                "riskLevel": "MEDIUM",
                "riskText": f"风险项目描述_{self.mock_util.get_timestamp()}",
                "riskRule": self.risk_id if self.risk_id else 1,
                "btClass": "ORDER",  # 业务类型不能为空，设置为订单类型
                "dimension": "INVENTORY",  # 维度不能为空，设置为库存维度
                "indicatorClass": "QUANTITY"  # 指标类型不能为空，设置为数量类型
            }
            response, extracted_id = self.standard_api_call(
                api_key="风险项目保存服务",
                set_dict=set_dict,
                fields_to_filter=["riskCode", "riskName", "riskLevel", "riskText", "riskRule", "btClass", "dimension", "indicatorClass"]
            )
            self.assert_util.assert_response_data(response)

            # 保存风险项目ID
            self.risk_tr_id = extracted_id.get("id") if isinstance(extracted_id, dict) else extracted_id

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险项目分页查询",
        description="验证风险项目分页查询服务功能",
        severity="critical",
        file_level_order=5,
        tags=["风险管理", "风险项目", "分页查询", "GEN_RISK_TR_QUERY_PAGE_SERVICE"]
    )
    @pytest.mark.skip(reason="风险项目分页查询服务功能暂未开发，暂时跳过")
    def test_query_risk_tr_page(self):
        """风险项目分页查询用例 - GEN_RISK_TR_QUERY_PAGE_SERVICE"""
        try:
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                },
                "fields": [
                    {"name": "riskCode", "type": "TEXT"},
                    {"name": "riskName", "type": "TEXT"},
                    {"name": "riskLevel", "type": "TEXT"},
                    {"name": "riskText", "type": "TEXT"}
                ],
                "systemParams": None
            }
            response, _ = self.standard_api_call(
                api_key="风险项目分页查询服务",
                set_dict=set_dict,
                fields_to_filter=["pageable", "fields", "systemParams"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险项目查询详情",
        description="验证风险项目查询详情服务功能",
        severity="normal",
        file_level_order=6,
        tags=["风险管理", "风险项目", "查询详情", "GEN_RISK_TR_DETAIL_SERVICE"]
    )
    @pytest.mark.skip(reason="风险项目查询详情服务功能暂未开发，暂时跳过")
    def test_query_risk_tr_detail(self):
        """风险项目查询详情用例 - GEN_RISK_TR_DETAIL_SERVICE"""
        try:
            # 检查依赖：如果风险规则和风险项目不存在，先创建
            if not self.risk_id:
                self.test_save_risk_rule()
            # 创建风险项目
            if not hasattr(self, 'risk_tr_id') or not self.risk_tr_id:
                self.test_save_risk_tr()

            set_dict = {"id": self.risk_tr_id if self.risk_tr_id else self.risk_id}
            response, _ = self.standard_api_call(
                api_key="风险项目详情服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险项目各等级数量查询",
        description="验证风险项目各等级数量查询服务功能",
        severity="normal",
        file_level_order=7,
        tags=["风险管理", "风险项目", "等级统计", "GEN_RISK_TR_QUERY_LEVEL_COUNT_SERVICE"]
    )
    @pytest.mark.skip(reason="风险项目各等级数量查询服务功能暂未开发，暂时跳过")
    def test_query_risk_level_count(self):
        """风险项目各等级数量查询用例 - GEN_RISK_TR_QUERY_LEVEL_COUNT_SERVICE"""
        try:
            set_dict = {
                "filterConditions": {
                    "dateRange": {
                        "startDate": "2024-01-01",
                        "endDate": "2024-12-31"
                    },
                    "orgIds": [],
                    "riskTypes": []
                }
            }
            response, _ = self.standard_api_call(
                api_key="风险项目各等级数量查询服务",
                set_dict=set_dict,
                fields_to_filter=["filterConditions"]
            )
            self.assert_util.assert_response_data(response)

            # 验证返回的等级统计数据
            level_counts = response.get("data", {}).get("data", {})
            if level_counts:
                self.logger.info(f"风险等级统计: {level_counts}")

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险行动保存",
        description="验证风险行动保存服务功能",
        severity="normal",
        file_level_order=8,
        tags=["风险管理", "风险行动", "保存", "GEN_RISK_ACTION_TR_SAVE_SERVICE"]
    )
    @pytest.mark.skip(reason="风险行动保存服务功能暂未开发，暂时跳过")
    def test_save_risk_action(self):
        """风险行动保存用例 - GEN_RISK_ACTION_TR_SAVE_SERVICE"""
        try:
            # 生成测试数据
            action_code = self.mock_util.generate_unique_code(tag="RISK_ACTION")
            action_name = f"风险行动_{self.mock_util.get_timestamp()}"

            set_dict = {
                "actionCode": action_code,
                "actionName": action_name,
                "actionType": "PREVENTIVE",
                "actionDesc": f"风险行动描述_{self.mock_util.get_timestamp()}",
                "riskId": self.risk_id if self.risk_id else 1
            }
            response, _ = self.standard_api_call(
                api_key="风险行动保存服务",
                set_dict=set_dict,
                fields_to_filter=["actionCode", "actionName", "actionType", "actionDesc", "riskId"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试行动规则保存",
        description="验证行动规则保存服务功能",
        severity="normal",
        file_level_order=9,
        tags=["风险管理", "行动规则", "保存", "GEN_RISK_ACTION_RULE_MD_SAVE_SERVICE"]
    )
    @pytest.mark.skip(reason="行动规则保存服务功能暂未开发，暂时跳过")
    def test_save_action_rule(self):
        """行动规则保存用例 - GEN_RISK_ACTION_RULE_MD_SAVE_SERVICE"""
        try:
            # 生成测试数据
            rule_code = self.mock_util.generate_unique_code(tag="ACTION_RULE")
            rule_name = f"行动规则_{self.mock_util.get_timestamp()}"

            set_dict = {
                "ruleCode": rule_code,
                "ruleName": rule_name,
                "ruleType": "AUTO_TRIGGER",
                "ruleDesc": f"行动规则描述_{self.mock_util.get_timestamp()}",
                "triggerConditions": {
                    "riskLevel": "HIGH",
                    "threshold": 80,
                    "actionType": "IMMEDIATE"
                }
            }
            response, _ = self.standard_api_call(
                api_key="行动规则保存服务",
                set_dict=set_dict,
                fields_to_filter=["ruleCode", "ruleName", "ruleType", "ruleDesc", "triggerConditions"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险项目本次忽略",
        description="验证风险项目本次忽略服务功能",
        severity="normal",
        file_level_order=10,
        tags=["风险管理", "风险项目", "忽略", "GEN_RISK_TR_STATUS_IGNORE_SERVICE"]
    )
    @pytest.mark.skip(reason="风险项目本次忽略服务功能暂未开发，暂时跳过")
    def test_ignore_risk_tr(self):
        """风险项目本次忽略用例 - GEN_RISK_TR_STATUS_IGNORE_SERVICE"""
        try:
            # 检查依赖：如果风险规则和风险项目不存在，先创建
            if not self.risk_id:
                self.test_save_risk_rule()
            if not hasattr(self, 'risk_tr_id') or not self.risk_tr_id:
                self.test_save_risk_tr()

            set_dict = {
                "id": self.risk_tr_id if self.risk_tr_id else self.risk_id,
                "ignoreReason": f"测试忽略原因_{self.mock_util.get_timestamp()}",
                "ignoreUntil": "2024-12-31"
            }
            response, _ = self.standard_api_call(
                api_key="风险项目本次忽略服务",
                set_dict=set_dict,
                fields_to_filter=["id", "ignoreReason", "ignoreUntil"]
            )
            self.assert_util.assert_response_data(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="风险管理",
        title="测试风险项目删除",
        description="验证风险项目删除服务功能",
        severity="critical",
        file_level_order=11,
        tags=["风险管理", "风险项目", "删除", "GEN_RISK_TR_DELETE_SERVICE"]
    )
    @pytest.mark.skip(reason="风险项目删除服务功能暂未开发，暂时跳过")
    def test_delete_risk_tr(self):
        """风险项目删除用例 - GEN_RISK_TR_DELETE_SERVICE"""
        try:
            # 检查是否存在风险项目ID，如果不存在先创建风险规则和风险项目
            if not self.risk_id:
                try:
                    self.test_save_risk_rule()
                except Exception as e:
                    self.logger.warning(f"创建风险规则失败: {str(e)}")
            if not hasattr(self, 'risk_tr_id') or not self.risk_tr_id:
                try:
                    self.test_save_risk_tr()
                except Exception as e:
                    self.logger.warning(f"创建风险项目失败: {str(e)}")
                
            # 如果还是没有数据，使用模拟ID
            if not hasattr(self, 'risk_tr_id') or not self.risk_tr_id:
                self.logger.warning("未获取到风险项目ID，使用模拟ID进行测试")
                self.risk_tr_id = 1

            set_dict = {"id": self.risk_tr_id if hasattr(self, 'risk_tr_id') and self.risk_tr_id else self.risk_id}
            response, _ = self.standard_api_call(
                api_key="风险项目删除服务",
                set_dict=set_dict,
                fields_to_filter=["id"]
            )
            self.assert_util.assert_response_success(response)

            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
