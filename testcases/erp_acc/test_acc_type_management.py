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
@allure.feature("账户类型管理")
class TestAccTypeManagement(ErpAccBaseTest):
    """账户类型管理测试类 - 覆盖账户类型抬头CRUD和标准导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.acc_type_id = None
        cls.acc_head_cf_id = None  # 信用账户类型抬头ID（用于详情查询）
        cls.logger.info("账户类型管理测试类初始化完成")
        
        # 初始化依赖数据（账户类型依赖组织等基础数据）
        if cls.acc_cache_data:
            cls.com_org_id = cls.acc_cache_data.get("org_info", {}).get("gr_come_org_info", [])[0].get("id") if cls.acc_cache_data.get("org_info") else None
            cls.acc_archive_id = cls.acc_cache_data.get("archive_info", [])[0].get("id") if cls.acc_cache_data.get("archive_info") else None
            cls.amount_config_id = cls.acc_cache_data.get("amount_info", [])[0].get("id") if cls.acc_cache_data.get("amount_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理账户类型抬头主表
            if cls.acc_type_id:
                cls.db.delete(
                    table="adv_cm_acc_head",  # 账户类型抬头表，实际表名需确认
                    where="id = %s",
                    params=[cls.acc_type_id]
                )
                cls.logger.info(f"账户类型ID {cls.acc_type_id} 测试数据清理完成")
            
            # 清理所有AT_前缀的类型（兜底清理）
            cls.db.delete(
                table="adv_cm_acc_head",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("账户类型测试数据清理完成")
            
            # 清理类型属性关联表（如果存在）
            # cls.db.delete(table="adv_cm_acc_type_attr", where="type_id like %s", params=["AT_%"])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    def _build_type_attributes(self, type_category="GENERAL"):
        """辅助方法：构建账户类型属性配置"""
        # 根据类型类别构建不同的属性配置
        if type_category == "GENERAL":
            attributes = {
                "type_category": "GENERAL_CREDIT",
                "risk_level": 2,  # 风险等级：低
                "approval_flow": "STANDARD",  # 审批流程：标准
                "default_amount_limits": {
                    "credit_limit_min": 10000.00,
                    "credit_limit_max": 500000.00,
                    "temp_limit_ratio": 0.5  # 临时额度比例50%
                },
                "associated_services": [
                    "BASIC_CREDIT_CHECK",
                    "STANDARD_APPROVAL",
                    "MONTHLY_REVIEW"
                ],
                "type_features": {
                    "allow_overdraft": False,  # 不允许透支
                    "auto_renewal": True,  # 自动续期
                    "credit_period_days": 90,  # 信用期90天
                    "interest_rate": 0.05  # 年化利率5%
                },
                "compliance_requirements": [
                    "KYC_VERIFIED",  # 客户身份验证
                    "AML_CHECK",     # 反洗钱检查
                    "REGULATORY_APPROVAL"  # 监管审批
                ],
                "description": "通用信用账户类型，适用于中小型企业，风险等级低，标准审批流程"
            }
        elif type_category == "HIGH_RISK":
            attributes = {
                "type_category": "HIGH_RISK_CREDIT",
                "risk_level": 4,  # 风险等级：高
                "approval_flow": "STRICT",  # 审批流程：严格
                "default_amount_limits": {
                    "credit_limit_min": 5000.00,
                    "credit_limit_max": 100000.00,
                    "temp_limit_ratio": 0.3  # 临时额度比例30%
                },
                "associated_services": [
                    "ADVANCED_CREDIT_CHECK",
                    "MULTI_LEVEL_APPROVAL",
                    "DAILY_MONITORING",
                    "RISK_ALERT_SERVICE"
                ],
                "type_features": {
                    "allow_overdraft": False,  # 不允许透支
                    "auto_renewal": False,  # 手动续期
                    "credit_period_days": 30,  # 信用期30天
                    "interest_rate": 0.08,  # 年化利率8%
                    "guarantee_required": True  # 需要担保
                },
                "compliance_requirements": [
                    "KYC_VERIFIED",
                    "AML_CHECK", 
                    "REGULATORY_APPROVAL",
                    "THIRD_PARTY_AUDIT",  # 第三方审计
                    "LEGAL_REVIEW"  # 法律审查
                ],
                "description": "高风险信用账户类型，适用于特殊行业或高风险客户，严格审批，多重监控"
            }
        else:
            attributes = {
                "type_category": "BASIC",
                "risk_level": 1,
                "approval_flow": "SIMPLE",
                "default_amount_limits": {},
                "associated_services": [],
                "type_features": {},
                "compliance_requirements": [],
                "description": "默认账户类型配置"
            }
        
        return attributes
    
    @case_decorator(
        story="账户类型管理",
        title="测试创建通用账户类型",
        description="验证账户类型创建功能，包括风险等级、审批流程和额度限制",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "account_type", "create", "general"]
    )
    def test_save_acc_type(self):
        """测试创建通用账户类型"""
        try:
            # 1. 检查基础依赖数据
            if not self.com_org_id:
                self.logger.warning("缺少组织ID依赖，跳过创建测试")
                pytest.skip("缺少组织基础数据")
            
            # 2. 准备测试数据
            type_code = self.mock_util.generate_unique_code(tag="ACC_TYP")
            type_name = f"自动化测试通用账户类型_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 构建类型属性（通用信用类型）
            type_attributes = self._build_type_attributes("GENERAL")
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_SAVE")  # 假设创建API键名
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "org_id", "archive_id", "amount_config_id",
                              "type_category", "risk_level", "approval_flow",
                              "default_amount_limits", "associated_services",
                              "type_features", "compliance_requirements",
                              "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            create_data = {
                "code": type_code,
                "name": type_name,
                "org_id": self.com_org_id,
                "archive_id": self.acc_archive_id or None,
                "amount_config_id": self.amount_config_id or None,
                "type_category": type_attributes["type_category"],
                "risk_level": type_attributes["risk_level"],
                "approval_flow": type_attributes["approval_flow"],
                "default_amount_limits": type_attributes["default_amount_limits"],
                "associated_services": type_attributes["associated_services"],
                "type_features": type_attributes["type_features"],
                "compliance_requirements": type_attributes["compliance_requirements"],
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
            
            self.acc_type_id = data.get("id")
            assert self.acc_type_id, "未获取到账户类型ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", type_code, "类型编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", type_name, "类型名称验证失败")
            self.assert_util.assert_by_operator(data.get("type_category"), "=", type_attributes["type_category"], "类型类别验证失败")
            self.assert_util.assert_by_operator(data.get("risk_level"), "=", type_attributes["risk_level"], "风险等级验证失败")
            self.assert_util.assert_by_operator(data.get("approval_flow"), "=", type_attributes["approval_flow"], "审批流程验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "启用状态验证失败")
            
            # 验证额度限制
            limits_returned = data.get("default_amount_limits", {})
            self.assert_util.assert_by_operator(limits_returned.get("credit_limit_min"), "=", 10000.00, "最小信用额度验证失败")
            self.assert_util.assert_by_operator(limits_returned.get("credit_limit_max"), "=", 500000.00, "最大信用额度验证失败")
            self.assert_util.assert_by_operator(limits_returned.get("temp_limit_ratio"), "=", 0.5, "临时额度比例验证失败")
            
            # 验证关联服务数量
            services_returned = data.get("associated_services", [])
            assert len(services_returned) >= 3, "关联服务数量不匹配"
            self.assert_util.assert_all_in(["BASIC_CREDIT_CHECK", "STANDARD_APPROVAL", "MONTHLY_REVIEW"], services_returned, "关联服务不匹配")
            
            # 验证合规要求
            compliance_returned = data.get("compliance_requirements", [])
            assert len(compliance_returned) >= 3, "合规要求数量不匹配"
            self.assert_util.assert_all_in(["KYC_VERIFIED", "AML_CHECK", "REGULATORY_APPROVAL"], compliance_returned, "合规要求不匹配")
            
            # 验证类型特性
            features_returned = data.get("type_features", {})
            self.assert_util.assert_by_operator(features_returned.get("allow_overdraft"), "=", False, "透支权限验证失败")
            self.assert_util.assert_by_operator(features_returned.get("auto_renewal"), "=", True, "自动续期验证失败")
            self.assert_util.assert_by_operator(features_returned.get("credit_period_days"), "=", 90, "信用期验证失败")
            self.assert_util.assert_by_operator(features_returned.get("interest_rate"), "=", 0.05, "利率验证失败")
            
            # 7. Allure报告
            a.json(filtered_params, "创建账户类型请求参数")
            a.json(response, "创建账户类型响应结果")
            a.text(type_attributes["description"], "类型描述")
            a.text(f"额度范围: {limits_returned.get('credit_limit_min')} - {limits_returned.get('credit_limit_max')}, 临时额度比例: {limits_returned.get('temp_limit_ratio')*100}%", "额度配置")
            a.text(f"关联服务: {', '.join(services_returned[:3])}{'...' if len(services_returned) > 3 else ''}", "服务配置")
            self.logger.info(f"账户类型创建成功，ID: {self.acc_type_id}, 类别: {type_attributes['type_category']}, 风险等级: {type_attributes['risk_level']}")
            
        except Exception as e:
            a.text(str(e), "创建账户类型失败原因")
            self.logger.error(f"创建账户类型失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试查询信用账户类型抬头分页列表",
        description="验证使用SYS_PagingDataService查询adv_cm_acc_head_cf模型的分页数据",
        severity="critical",
        file_level_order=4,
        smoke=True,
        tags=["erp_acc", "account_type", "query", "paging", "adv_cm_acc_head_cf"]
    )
    def test_query_acc_head_cf_paging(self):
        """测试查询信用账户类型抬头分页列表 - 使用standard_api_call"""
        try:
            # 1. 准备分页查询参数
            pageable_params = {
                "pageNo": 1,
                "pageSize": 20,
                "needTotal": True,
                "sortOrders": None,
                "conditionItems": None
            }
            
            # 2. 获取API路径和基础参数
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path, with_query_params="tmodule=ERP_ACC&modelKey=ERP_ACC%24adv_cm_acc_head_cf")
            
            # 3. 构建完整参数结构
            # modelKey在params层级，需要手动添加到请求参数中
            filtered_params = params.copy() if params else {}
            if "params" not in filtered_params:
                filtered_params["params"] = {}
            if "request" not in filtered_params["params"]:
                filtered_params["params"]["request"] = {}
            
            # 设置pageable参数
            filtered_params["params"]["request"]["pageable"] = pageable_params
            # 设置modelKey（在params层级，不在request下）
            filtered_params["params"]["modelKey"] = "ERP_ACC$adv_cm_acc_head_cf"
            
            # 4. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 5. 业务断言
            self.assert_util.assert_response_success(response)
            query_data = response.get("data", {}).get("data", {})
            records = query_data.get("records", [])
            total = query_data.get("total", 0)
            
            # 验证分页结果
            self.assert_util.assert_by_operator(total, ">=", 0, "总记录数异常")
            self.assert_util.assert_by_operator(len(records), ">=", 0, "记录列表异常")
            
            # 如果有记录，验证记录结构
            if records:
                first_record = records[0]
                self.assert_util.assert_by_operator(first_record.get("id"), "not_empty", None, "记录ID为空")
                self.logger.info(f"查询到{total}条信用账户类型抬头记录，第一条记录ID: {first_record.get('id')}")
            
            # 6. Allure报告
            request_params = {
                "pageable": pageable_params,
                "modelKey": "ERP_ACC$adv_cm_acc_head_cf"
            }
            a.json(request_params, "查询信用账户类型抬头参数")
            a.json(response, "查询信用账户类型抬头结果")
            a.text(f"查询结果: 共{total}条记录，当前页{len(records)}条", "查询统计")
            self.logger.info(f"信用账户类型抬头分页查询成功，共{total}条记录")
            
        except Exception as e:
            a.text(str(e), "查询信用账户类型抬头失败原因")
            self.logger.error(f"查询信用账户类型抬头失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试查询信用账户类型抬头详情",
        description="验证使用SYS_FindDataByIdService查询adv_cm_acc_head_cf模型的详情数据",
        severity="critical",
        file_level_order=5,
        smoke=True,
        tags=["erp_acc", "account_type", "query", "detail", "adv_cm_acc_head_cf"]
    )
    def test_query_acc_head_cf_detail(self):
        """测试查询信用账户类型抬头详情"""
        try:
            # 1. 先查询分页列表获取一个ID（如果没有测试数据）
            if not hasattr(self, 'acc_head_cf_id') or not self.acc_head_cf_id:
                # 先执行分页查询获取一个ID
                api_path = self.get_api_path("(系统)查询分页数据服务")
                params, url = self.get_api_params(api_path, with_query_params="tmodule=ERP_ACC&modelKey=ERP_ACC%24adv_cm_acc_head_cf")
                pageable_params = {
                    "pageNo": 1,
                    "pageSize": 1,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": None
                }
                filtered_params = params.copy() if params else {}
                if "params" not in filtered_params:
                    filtered_params["params"] = {}
                if "request" not in filtered_params["params"]:
                    filtered_params["params"]["request"] = {}
                filtered_params["params"]["request"]["pageable"] = pageable_params
                filtered_params["params"]["modelKey"] = "ERP_ACC$adv_cm_acc_head_cf"
                query_response = self.http.post(url, json=filtered_params)
                query_data = query_response.get("data", {}).get("data", {})
                records = query_data.get("records", [])
                if records and records[0].get("id"):
                    self.acc_head_cf_id = records[0].get("id")
                else:
                    pytest.skip("未找到可用的信用账户类型抬头记录，跳过详情查询测试")
            
            # 2. 准备详情查询参数
            detail_id = self.acc_head_cf_id
            
            # 3. 获取API路径和基础参数
            api_path = self.get_api_path("(系统)查询数据详情服务")
            params, url = self.get_api_params(api_path, with_query_params="tmodule=ERP_ACC&modelKey=ERP_ACC%24adv_cm_acc_head_cf")
            
            # 4. 构建完整参数结构
            # id在params.request.id，modelKey在params.modelKey
            filtered_params = params.copy() if params else {}
            if "params" not in filtered_params:
                filtered_params["params"] = {}
            if "request" not in filtered_params["params"]:
                filtered_params["params"]["request"] = {}
            
            # 设置id参数
            filtered_params["params"]["request"]["id"] = detail_id
            # 设置modelKey（在params层级，不在request下）
            filtered_params["params"]["modelKey"] = "ERP_ACC$adv_cm_acc_head_cf"
            
            # 5. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 6. 业务断言
            self.assert_util.assert_response_success(response)
            detail_data = response.get("data", {}).get("data", {})
            
            # 验证详情数据
            self.assert_util.assert_by_operator(detail_data, "not_empty", None, "详情数据为空")
            self.assert_util.assert_by_operator(detail_data.get("id"), "=", detail_id, "详情ID不匹配")
            
            # 验证关键字段存在（根据实际业务字段调整）
            if detail_data.get("id"):
                self.logger.info(f"查询到信用账户类型抬头详情，ID: {detail_data.get('id')}")
            
            # 7. Allure报告
            request_params = {
                "id": detail_id,
                "modelKey": "ERP_ACC$adv_cm_acc_head_cf"
            }
            a.json(request_params, "查询信用账户类型抬头详情参数")
            a.json(response, "查询信用账户类型抬头详情结果")
            a.text(f"查询详情成功，ID: {detail_id}", "查询结果")
            self.logger.info(f"信用账户类型抬头详情查询成功，ID: {detail_id}")
            
        except Exception as e:
            a.text(str(e), "查询信用账户类型抬头详情失败原因")
            self.logger.error(f"查询信用账户类型抬头详情失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试查询账户类型列表",
        description="验证账户类型分页查询功能，支持风险等级和组织过滤",
        severity="normal",
        order=4,
        tags=["erp_acc", "account_type", "query"]
    )
    def test_query_acc_type(self):
        """测试查询账户类型列表"""
        try:
            # 确保有测试数据
            if not self.acc_type_id:
                self.test_save_acc_type()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_QUERY")  # 假设查询API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": [
                        {"field": "risk_level", "direction": "ASC"},
                        {"field": "create_time", "direction": "DESC"}
                    ],
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.acc_type_id},
                        {"field": "org_id", "operator": "eq", "value": self.com_org_id},
                        {"field": "enabled", "operator": "eq", "value": True},
                        {"field": "risk_level", "operator": "lte", "value": 3}  # 低风险类型
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "type_category", "type": "TEXT"},
                    {"name": "risk_level", "type": "NUMBER"},
                    {"name": "approval_flow", "type": "TEXT"},
                    {"name": "enabled", "type": "BOOLEAN"},
                    {"name": "org_id", "type": "NUMBER"},
                    {"name": "services_count", "type": "NUMBER"},  # 关联服务数量
                    {"name": "compliance_count", "type": "NUMBER"}  # 合规要求数量
                ],
                "systemParams": None,
                "expand": ["associated_services", "compliance_requirements"]  # 展开关联数据
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
            
            assert total >= 1, "未查询到账户类型记录"
            assert len(records) >= 1, "查询记录列表为空"
            
            # 验证具体记录
            type_info = records[0]
            self.assert_util.assert_by_operator(type_info.get("id"), "=", self.acc_type_id, "类型ID不匹配")
            self.assert_util.assert_by_operator(type_info.get("type_category"), "=", "GENERAL_CREDIT", "类型类别不匹配")
            self.assert_util.assert_by_operator(type_info.get("risk_level"), "=", 2, "风险等级不匹配")
            self.assert_util.assert_by_operator(type_info.get("approval_flow"), "=", "STANDARD", "审批流程不匹配")
            self.assert_util.assert_by_operator(type_info.get("enabled"), "=", True, "启用状态不匹配")
            self.assert_util.assert_by_operator(type_info.get("org_id"), "=", self.com_org_id, "组织ID不匹配")
            
            # 验证展开数据
            services = type_info.get("associated_services", [])
            assert len(services) >= 3, "关联服务展开失败"
            self.assert_util.assert_all_in(["BASIC_CREDIT_CHECK", "STANDARD_APPROVAL", "MONTHLY_REVIEW"], services, "关联服务不匹配")
            
            compliance = type_info.get("compliance_requirements", [])
            assert len(compliance) >= 3, "合规要求展开失败"
            self.assert_util.assert_all_in(["KYC_VERIFIED", "AML_CHECK", "REGULATORY_APPROVAL"], compliance, "合规要求不匹配")
            
            # 验证统计字段
            self.assert_util.assert_by_operator(type_info.get("services_count", 0), ">=", 3, "服务数量统计失败")
            self.assert_util.assert_by_operator(type_info.get("compliance_count", 0), ">=", 3, "合规数量统计失败")
            
            # 5. Allure报告
            a.json(filtered_params, "查询账户类型参数")
            a.json(response, "查询账户类型结果")
            a.text(f"账户类型查询: 风险等级≤3, 共{total}条记录, 服务{len(services)}个, 合规{len(compliance)}项", "查询统计")
            self.logger.info(f"账户类型查询成功，共{total}条记录，风险等级: {type_info.get('risk_level')}")
            
        except Exception as e:
            a.text(str(e), "查询账户类型失败原因")
            self.logger.error(f"查询账户类型失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试更新账户类型",
        description="验证账户类型更新功能，升级为高风险类型，修改审批流程和额度限制",
        severity="normal",
        order=7,
        tags=["erp_acc", "account_type", "update", "high_risk"]
    )
    def test_update_acc_type(self):
        """测试更新账户类型"""
        try:
            # 确保有测试数据
            if not self.acc_type_id:
                self.test_save_acc_type()
            
            # 1. 准备更新数据 - 升级为高风险类型
            new_type_name = f"更新后高风险账户类型_{self.mock_util.get_timestamp()}"
            new_remark = self.mock_util.get_mock_remark()
            
            # 构建高风险类型属性
            new_attributes = self._build_type_attributes("HIGH_RISK")
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_UPDATE")  # 假设更新API键名
            params, url = self.get_api_params(api_path)
            
            # 3. 参数设置
            update_data = {
                "id": self.acc_type_id,
                "name": new_type_name,
                "type_category": new_attributes["type_category"],  # 改为HIGH_RISK_CREDIT
                "risk_level": new_attributes["risk_level"],  # 改为4
                "approval_flow": new_attributes["approval_flow"],  # 改为STRICT
                "default_amount_limits": new_attributes["default_amount_limits"],
                "associated_services": new_attributes["associated_services"],
                "type_features": new_attributes["type_features"],
                "compliance_requirements": new_attributes["compliance_requirements"],
                "enabled": True,
                "remark": new_remark
            }
            
            fields_to_filter = ["id", "name", "type_category", "risk_level", "approval_flow",
                              "default_amount_limits", "associated_services", "type_features",
                              "compliance_requirements", "enabled", "remark"]
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
            self.test_query_acc_type()  # 重新查询验证
            
            # 额外验证更新内容
            updated_type = self._get_current_type_info()
            self.assert_util.assert_by_operator(updated_type.get("name"), "=", new_type_name, "类型名称更新失败")
            self.assert_util.assert_by_operator(updated_type.get("type_category"), "=", "HIGH_RISK_CREDIT", "类型类别更新失败")
            self.assert_util.assert_by_operator(updated_type.get("risk_level"), "=", 4, "风险等级更新失败")
            self.assert_util.assert_by_operator(updated_type.get("approval_flow"), "=", "STRICT", "审批流程更新失败")
            
            # 验证新额度限制（更严格）
            new_limits = updated_type.get("default_amount_limits", {})
            self.assert_util.assert_by_operator(new_limits.get("credit_limit_min"), "=", 5000.00, "更新后最小信用额度不匹配")
            self.assert_util.assert_by_operator(new_limits.get("credit_limit_max"), "=", 100000.00, "更新后最大信用额度不匹配")
            self.assert_util.assert_by_operator(new_limits.get("temp_limit_ratio"), "=", 0.3, "更新后临时额度比例不匹配")
            
            # 验证新增关联服务
            new_services = updated_type.get("associated_services", [])
            assert len(new_services) >= 4, "高风险服务数量不足"
            self.assert_util.assert_all_in(["ADVANCED_CREDIT_CHECK", "MULTI_LEVEL_APPROVAL", "DAILY_MONITORING"], new_services, "高风险服务不匹配")
            
            # 验证新增合规要求
            new_compliance = updated_type.get("compliance_requirements", [])
            assert len(new_compliance) >= 5, "高风险合规要求不足"
            self.assert_util.assert_all_in(["THIRD_PARTY_AUDIT", "LEGAL_REVIEW"], new_compliance, "新增合规要求不匹配")
            
            # 验证类型特性变更
            new_features = updated_type.get("type_features", {})
            self.assert_util.assert_by_operator(new_features.get("auto_renewal"), "=", False, "自动续期更新失败")
            self.assert_util.assert_by_operator(new_features.get("credit_period_days"), "=", 30, "信用期更新失败")
            self.assert_util.assert_by_operator(new_features.get("interest_rate"), "=", 0.08, "利率更新失败")
            self.assert_util.assert_by_operator(new_features.get("guarantee_required"), "=", True, "担保要求更新失败")
            
            # 7. Allure报告
            a.json(filtered_params, "更新账户类型参数")
            a.json(response, "更新账户类型结果")
            a.text(f"风险升级: 等级2(GENERAL) -> 4(HIGH_RISK), 审批: STANDARD -> STRICT", "风险升级记录")
            a.text(f"额度收紧: 10-50万 -> 0.5-10万, 临时比例: 50% -> 30%", "额度调整记录")
            a.text(f"新增服务: {', '.join(new_services[-2:])} (共{len(new_services)}项)", "服务扩展")
            a.text(new_attributes["description"], "更新后类型描述")
            self.logger.info(f"账户类型更新成功，ID: {self.acc_type_id}, 新风险等级: {new_attributes['risk_level']}")
            
        except Exception as e:
            a.text(str(e), "更新账户类型失败原因")
            self.logger.error(f"更新账户类型失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试删除账户类型",
        description="验证单个账户类型删除功能，检查关联数据清理",
        severity="critical",
        order=16,
        tags=["erp_acc", "account_type", "delete"]
    )
    def test_delete_acc_type(self):
        """测试删除账户类型"""
        try:
            # 确保有测试数据
            if not self.acc_type_id:
                self.test_save_acc_type()
            
            # 1. 获取删除API配置
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_DELETE")  # 假设删除API键名
            params, url = self.get_api_params(api_path)
            
            # 2. 单个ID删除参数
            delete_data = {
                "id": self.acc_type_id,
                "cascade_delete": True,  # 级联删除关联数据
                "check_dependencies": True  # 检查依赖关系
            }
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "cascade_delete", "check_dependencies"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, delete_data)
            
            # 3. 发送删除请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证删除结果
            self.assert_util.assert_response_success(response)
            delete_result = response.get("data", {})
            assert delete_result.get("success"), "删除操作失败"
            deleted_count = delete_result.get("deleted_count", 0)
            cascade_deleted = delete_result.get("cascade_deleted", 0)
            dependency_check = delete_result.get("dependency_check", True)
            
            assert deleted_count >= 1, "主记录删除数量异常"
            assert dependency_check, "依赖检查失败"
            
            # 5. 查询验证删除效果
            saved_id = self.acc_type_id
            self.acc_type_id = None
            
            # 尝试查询已删除的账户类型
            api_path_query = self.get_api_path("ADV_CM_ACC_HEAD_QUERY")
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
            
            assert len(query_records) == 0, f"删除后仍能查询到类型 ID: {saved_id}"
            
            # 6. Allure报告
            a.json(filtered_params, "删除账户类型参数")
            a.json(response, "删除账户类型结果")
            a.text(f"删除统计: 主记录{deleted_count}条, 级联删除{cascade_deleted}条, 依赖检查: {dependency_check}", "删除详情")
            self.logger.info(f"账户类型删除成功，ID: {saved_id}, 级联: {cascade_deleted}")
            
        except Exception as e:
            a.text(str(e), "删除账户类型失败原因")
            self.logger.error(f"删除账户类型失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试账户类型标准导出",
        description="验证ADV_CM_ACC_HEAD_CF_GEI_EXPO...标准导出服务",
        severity="normal",
        order=10,
        tags=["erp_acc", "account_type", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export_acc_head(self):
        """测试账户类型标准导出服务"""
        try:
            # 确保有测试数据
            if not self.acc_type_id:
                self.test_save_acc_type()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_CF_GEI_EXPO")  # 标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数
            export_data = {
                "serviceKey": "ADV_CM_ACC_HEAD_CF_GEI_EXPORT",
                "teamId": 22,
                "params": {
                    "taskName": f"ACC_TYPE_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_ACC_HEAD",
                            "modelName": "账户类型配置",
                            "sheetNo": 0,
                            "sheetName": "类型基本信息",
                            "headerConfigList": [
                                {"name": "类型ID", "type": "TEXT", "field": "id"},
                                {"name": "类型编码", "type": "TEXT", "field": "code"},
                                {"name": "类型名称", "type": "TEXT", "field": "name"},
                                {"name": "类型类别", "type": "TEXT", "field": "type_category"},
                                {"name": "风险等级", "type": "NUMBER", "field": "risk_level"},
                                {"name": "审批流程", "type": "TEXT", "field": "approval_flow"},
                                {"name": "组织ID", "type": "NUMBER", "field": "org_id"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "enabled"},
                                {"name": "创建时间", "type": "DATETIME", "field": "create_time"},
                                {"name": "更新时间", "type": "DATETIME", "field": "update_time"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_AMOUNT_LIMITS",
                            "modelName": "额度限制配置",
                            "sheetNo": 1,
                            "sheetName": "额度配置",
                            "headerConfigList": [
                                {"name": "类型ID", "type": "NUMBER", "field": "type_id"},
                                {"name": "最小信用额度", "type": "NUMBER", "field": "credit_limit_min"},
                                {"name": "最大信用额度", "type": "NUMBER", "field": "credit_limit_max"},
                                {"name": "临时额度比例", "type": "NUMBER", "field": "temp_limit_ratio"},
                                {"name": "调整步长", "type": "NUMBER", "field": "adjustment_step"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_SERVICES",
                            "modelName": "关联服务配置",
                            "sheetNo": 2,
                            "sheetName": "服务配置",
                            "headerConfigList": [
                                {"name": "类型ID", "type": "NUMBER", "field": "type_id"},
                                {"name": "服务编码", "type": "TEXT", "field": "service_code"},
                                {"name": "服务名称", "type": "TEXT", "field": "service_name"},
                                {"name": "服务类型", "type": "TEXT", "field": "service_type"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "service_enabled"},
                                {"name": "优先级", "type": "NUMBER", "field": "priority"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_COMPLIANCE",
                            "modelName": "合规要求配置",
                            "sheetNo": 3,
                            "sheetName": "合规配置",
                            "headerConfigList": [
                                {"name": "类型ID", "type": "NUMBER", "field": "type_id"},
                                {"name": "合规要求编码", "type": "TEXT", "field": "compliance_code"},
                                {"name": "合规要求名称", "type": "TEXT", "field": "compliance_name"},
                                {"name": "要求类型", "type": "TEXT", "field": "requirement_type"},
                                {"name": "严重程度", "type": "TEXT", "field": "severity"},
                                {"name": "是否必选", "type": "BOOLEAN", "field": "mandatory"}
                            ]
                        },
                        {
                            "modelKey": "ADV_CM_ACC_FEATURES",
                            "modelName": "类型特性配置",
                            "sheetNo": 4,
                            "sheetName": "特性配置",
                            "headerConfigList": [
                                {"name": "类型ID", "type": "NUMBER", "field": "type_id"},
                                {"name": "特性键", "type": "TEXT", "field": "feature_key"},
                                {"name": "特性值", "type": "TEXT", "field": "feature_value"},
                                {"name": "特性类型", "type": "TEXT", "field": "feature_type"},
                                {"name": "描述", "type": "TEXT", "field": "description"},
                                {"name": "启用状态", "type": "BOOLEAN", "field": "feature_enabled"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_ACC_HEAD",
                        "viewKey": "ADV_CM_ACC_HEAD:list",
                        "sceneKey": "ADV_CM_ACC_HEAD",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 500,  # 导出较多数据
                                    "needTotal": True,
                                    "sortOrders": [
                                        {"field": "risk_level", "direction": "ASC"},
                                        {"field": "type_category", "direction": "ASC"},
                                        {"field": "code", "direction": "ASC"}
                                    ],
                                    "conditionItems": [
                                        {"field": "org_id", "operator": "eq", "value": self.com_org_id},
                                        {"field": "enabled", "operator": "eq", "value": True}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "type_category"}, {"field": "risk_level"}, {"field": "approval_flow"},
                                {"field": "org_id"}, {"field": "enabled"}, {"field": "create_time"},
                                {"field": "update_time"}, {"field": "remark"}
                            ],
                            "modelKey": "ADV_CM_ACC_HEAD",
                            "expand": [
                                "default_amount_limits",
                                "associated_services", 
                                "compliance_requirements",
                                "type_features"
                            ]  # 展开所有关联配置
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_ACC_HEAD",
                        "modelName": "账户类型配置",
                        "containerKey": "ADV_CM_ACC_HEAD",
                        "viewKey": "ADV_CM_ACC_HEAD:list",
                        "sceneKey": "ADV_CM_ACC_HEAD",
                        "dataTransform": {
                            "default_amount_limits": "format_currency_ranges",  # 格式化额度范围
                            "associated_services": "array_to_detailed_list",  # 服务详细列表
                            "compliance_requirements": "array_to_compliance_table",  # 合规表格
                            "type_features": "flatten_json_features",  # 扁平化特性
                            "risk_level": "risk_level_to_color",  # 风险等级着色
                            "approval_flow": "flow_type_to_description"  # 流程描述化
                        },
                        "exportOptions": {
                            "include_configuration_details": True,  # 包含配置详情
                            "group_by_risk_level": True,  # 按风险等级分组
                            "include_type_hierarchy": False,  # 类型无层级
                            "format_for_compliance": True,  # 合规格式
                            "add_summary_statistics": True  # 添加统计摘要
                        },
                        "summaryConfig": {  # 汇总配置
                            "risk_distribution": True,  # 风险分布
                            "service_usage": True,  # 服务使用情况
                            "compliance_coverage": True,  # 合规覆盖率
                            "amount_limit_summary": True  # 额度限制汇总
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
            
            # 验证导出预估
            estimated_types = export_result.get("data", {}).get("estimated_types", 0)
            estimated_sheets = export_result.get("data", {}).get("expected_sheets", 0)
            config_complexity = export_result.get("data", {}).get("config_complexity", "MEDIUM")
            summary_stats = export_result.get("data", {}).get("summary_stats", {})
            
            self.assert_util.assert_by_operator(estimated_types, ">=", 0, "预估类型数量异常")
            self.assert_util.assert_by_operator(estimated_sheets, ">=", 5, "预期工作表数量异常")
            self.assert_util.assert_by_operator(config_complexity, "in", ["LOW", "MEDIUM", "HIGH"], "配置复杂度异常")
            
            if summary_stats:
                total_risk_levels = summary_stats.get("total_risk_levels", 0)
                avg_risk_level = summary_stats.get("avg_risk_level", 0)
                total_services = summary_stats.get("total_services", 0)
                compliance_coverage = summary_stats.get("compliance_coverage", 0)
                
                self.assert_util.assert_by_operator(total_risk_levels, ">=", 1, "风险等级总数异常")
                self.assert_util.assert_by_operator(avg_risk_level, ">=", 0, "平均风险等级异常")
                self.assert_util.assert_by_operator(total_services, ">=", 0, "总服务数异常")
                self.assert_util.assert_by_operator(compliance_coverage, ">=", 0, "合规覆盖率异常")
            
            # 5. Allure报告
            a.json(filtered_params, "标准导出请求参数")
            a.json(response, "标准导出响应结果")
            a.text(f"账户类型导出: 预估{estimated_types}种类型, {estimated_sheets}个工作表, 复杂度: {config_complexity}", "导出预估")
            if summary_stats:
                a.text(f"统计摘要: 风险等级总数{total_risk_levels}, 平均{avg_risk_level}, 服务{total_services}个, 合规覆盖{compliance_coverage}%", "配置统计")
            self.logger.info(f"账户类型标准导出任务创建成功，Task ID: {task_id}, 预估{estimated_types}种类型")
            
        except Exception as e:
            a.text(str(e), "标准导出账户类型失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户类型管理",
        title="测试提交账户类型导出任务",
        description="验证ADV_CM_ACC_HEAD_CF_API_GEI_T...导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "account_type", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task_type(self):
        """测试提交账户类型导出任务"""
        try:
            # 确保有测试数据
            if not self.acc_type_id:
                self.test_save_acc_type()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_CF_API_GEI_T_EXPORT")  # 导出任务提交API
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"ACC_TYPE_EXPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_HEAD",
                "filterCondition": {
                    "org_id": {"operator": "eq", "value": self.com_org_id},
                    "enabled": {"operator": "eq", "value": True},
                    "risk_level": {"operator": "between", "value": [1, 4]},
                    "type_category": {"operator": "in", "value": ["GENERAL_CREDIT", "HIGH_RISK_CREDIT"]},
                    "approval_flow": {"operator": "neq", "value": "SIMPLE"}  # 排除简单流程
                },
                "exportFields": [
                    "id", "code", "name", "type_category", "risk_level", "approval_flow",
                    "org_id", "enabled", "create_time", "update_time", "remark"
                ],
                "expandFields": [
                    "default_amount_limits",  # 额度限制
                    "associated_services",    # 关联服务
                    "compliance_requirements",  # 合规要求
                    "type_features"           # 类型特性
                ],
                "exportFormat": "EXCEL",
                "includeHeader": True,
                "separateSheets": {
                    "basic_info": True,  # 基本信息
                    "amount_limits": True,  # 额度配置
                    "services": True,  # 服务配置
                    "compliance": True,  # 合规配置
                    "features": True  # 特性配置
                },
                "dataTransform": {
                    "default_amount_limits": "currency_format_with_ranges",  # 货币格式化+范围
                    "associated_services": "service_detailed_with_priority",  # 服务详情+优先级
                    "compliance_requirements": "compliance_matrix_format",  # 合规矩阵
                    "type_features": "feature_key_value_pairs",  # 特性键值对
                    "risk_level": "risk_color_coding",  # 风险等级颜色编码
                    "approval_flow": "flow_visualization",  # 流程可视化
                    "create_time": "standard_datetime",  # 标准日期时间
                    "type_category": "category_with_description"  # 类别+描述
                },
                "groupingOptions": {  # 分组选项
                    "by_risk_level": True,  # 按风险等级分组
                    "by_approval_flow": True,  # 按审批流程分组
                    "by_type_category": True  # 按类型类别分组
                },
                "summaryFields": [  # 汇总字段
                    "total_types_by_risk",  # 按风险分类总数
                    "avg_credit_limit_range",  # 平均信用额度范围
                    "total_associated_services",  # 总关联服务数
                    "compliance_coverage_percentage",  # 合规覆盖率
                    "high_risk_types_count",  # 高风险类型数量
                    "approval_flow_distribution"  # 审批流程分布
                ],
                "filterEnhancements": {  # 过滤增强
                    "exclude_simple_flows": True,  # 排除简单流程
                    "include_only_active": True,  # 只包含启用类型
                    "risk_threshold": 4,  # 风险阈值
                    "recently_updated": {"days": 30}  # 最近30天更新
                },
                "exportOptions": {
                    "include_detailed_config": True,  # 包含详细配置
                    "preserve_relationships": True,  # 保持关系完整性
                    "format_for_audit": True,  # 审计格式
                    "add_metadata": True,  # 添加元数据
                    "version_control": True  # 版本控制
                },
                "progressTracking": {  # 进度跟踪
                    "enable": True,
                    "interval": 25,  # 每25%报告
                    "metrics": [
                        "exported_types", 
                        "processed_configs", 
                        "validation_errors", 
                        "hierarchy_complete"
                    ]
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
            
            # 验证预估信息
            export_estimate = task_result.get("data", {}).get("export_estimate", {})
            total_types = export_estimate.get("total_types", 0)
            config_sheets = export_estimate.get("config_sheets", 0)
            estimated_size = export_estimate.get("estimated_size_mb", 0)
            complexity_level = export_estimate.get("complexity_level", "MEDIUM")
            validation_status = export_estimate.get("validation_status", "PASS")
            
            self.assert_util.assert_by_operator(total_types, ">=", 0, "预估类型数量异常")
            self.assert_util.assert_by_operator(config_sheets, ">=", 5, "配置工作表数量异常")
            self.assert_util.assert_by_operator(complexity_level, "in", ["LOW", "MEDIUM", "HIGH", "COMPLEX"], "复杂度级别异常")
            self.assert_util.assert_by_operator(validation_status, "=", "PASS", "预验证状态异常")
            
            # 5. Allure报告
            a.json(filtered_params, "导出任务提交参数")
            a.json(response, "导出任务提交结果")
            a.text(f"账户类型导出预估: {total_types}种类型, {config_sheets}个配置表, 大小{estimated_size}MB, 复杂度{complexity_level}, 验证{validation_status}", "导出预估详情")
            self.logger.info(f"账户类型导出任务提交成功，Task ID: {task_id}, 预估{total_types}种类型, 复杂度: {complexity_level}")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    def _get_current_type_info(self):
        """辅助方法：获取当前账户类型信息"""
        try:
            api_path = self.get_api_path("ADV_CM_ACC_HEAD_QUERY")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.acc_type_id}]
                },
                "fields": [
                    {"name": "name", "type": "TEXT"},
                    {"name": "type_category", "type": "TEXT"},
                    {"name": "risk_level", "type": "NUMBER"},
                    {"name": "approval_flow", "type": "TEXT"},
                    {"name": "default_amount_limits", "type": "OBJECT"},
                    {"name": "associated_services", "type": "ARRAY"},
                    {"name": "compliance_requirements", "type": "ARRAY"},
                    {"name": "type_features", "type": "OBJECT"}
                ],
                "expand": [
                    "default_amount_limits",
                    "associated_services", 
                    "compliance_requirements",
                    "type_features"
                ]
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
            self.logger.error(f"获取类型信息失败: {str(e)}")
            return {}
