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
@allure.feature("账户状态管理")
class TestAccStatusManagement(ErpAccBaseTest):
    """账户状态管理测试类 - 覆盖停用/启用服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.acc_archive_id = None
        cls.logger.info("账户状态管理测试类初始化完成")
        
        # 初始化依赖数据（账户档案需要的基础数据）
        if cls.acc_cache_data:
            # 获取组织、客户等基础ID
            cls.com_org_id = cls.acc_cache_data.get("org_info", {}).get("gr_come_org_info", [])[0].get("id") if cls.acc_cache_data.get("org_info") else None
            cls.cust_id = cls.acc_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id") if cls.acc_cache_data.get("partner_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理账户档案测试数据
            if cls.acc_archive_id:
                cls.db.delete(
                    table="adv_cm_acc_archive",  # 账户档案表，实际表名需确认
                    where="code like %s",
                    params=["AT_%"]
                )
                cls.logger.info("账户档案测试数据清理完成")
            
            # 清理相关状态记录表（如果存在）
            # cls.db.delete(table="adv_cm_status_log", where="archive_id = %s", params=[cls.acc_archive_id])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="账户状态管理",
        title="测试创建信用账户档案",
        description="验证信用账户档案创建功能，为状态操作准备测试数据",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "status", "create", "archive"]
    )
    def test_save_acc_archive(self):
        """测试创建信用账户档案"""
        try:
            # 1. 检查依赖数据是否存在
            if not self.cust_id or not self.com_org_id:
                self.logger.warning("缺少客户或组织基础数据，跳过创建")
                pytest.skip("缺少基础依赖数据")
            
            # 2. 准备测试数据
            archive_code = self.mock_util.generate_unique_code(tag="ACC_ARC")
            archive_name = f"自动化测试账户档案_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 3. 获取API配置（使用实际YAML中的服务名）
            api_path = self.get_api_path("ACC_MD_SAVE_EVENT_SERVICE")  # 账户-档案保存服务
            params, url = self.get_api_params(api_path)
            
            # 4. 参数处理
            fields_to_filter = ["code", "name", "cust_id", "org_id", "status", "remark", "enabled"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            # 设置测试数据
            test_data = {
                "code": archive_code,
                "name": archive_name,
                "cust_id": self.cust_id,
                "org_id": self.com_org_id,
                "status": "ACTIVE",  # 初始状态为启用
                "enabled": True,
                "remark": remark
            }
            ParamUtil.set_request_params(filtered_params, test_data)
            
            # 5. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 6. 断言验证
            self.assert_util.assert_response_data(response)
            data = response.get("data", {}).get("data", {})
            assert data, "创建返回数据为空"
            
            # 7. 保存ID用于后续状态测试
            self.acc_archive_id = data.get("id")
            assert self.acc_archive_id, "未获取到档案ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", archive_code, "档案编码不匹配")
            self.assert_util.assert_by_operator(data.get("status"), "=", "ACTIVE", "初始状态不正确")
            
            # 8. 记录报告
            a.json(filtered_params, "创建账户档案请求参数")
            a.json(response, "创建账户档案响应结果")
            self.logger.info(f"信用账户档案创建成功，ID: {self.acc_archive_id}, Code: {archive_code}")
            
        except Exception as e:
            a.text(str(e), "创建账户档案失败原因")
            self.logger.error(f"测试创建账户档案失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户状态管理",
        title="测试查询账户档案状态",
        description="验证账户档案状态查询功能，确认创建的数据状态正确",
        severity="normal",
        order=4,
        tags=["erp_acc", "status", "query", "archive"]
    )
    def test_query_acc_archive_status(self):
        """测试查询账户档案状态"""
        try:
            # 确保有测试数据
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("account_profile_query_customer_info")  # 账户档案查询客户信息
            params, url = self.get_api_params(api_path)
            
            # 2. 设置查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.acc_archive_id}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"},
                    {"name": "enabled", "type": "BOOLEAN"}
                ],
                "systemParams": None
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 3. 发送查询请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 断言验证
            self.assert_util.assert_response_success(response)
            data_list = response.get("data", {}).get("data", {}).get("records", [])
            total = response.get("data", {}).get("data", {}).get("total", 0)
            
            assert total >= 1, "未查询到账户档案数据"
            assert len(data_list) >= 1, "返回记录列表为空"
            
            # 验证测试数据
            archive_data = data_list[0]
            self.assert_util.assert_by_operator(archive_data.get("id"), "=", self.acc_archive_id, "档案ID不匹配")
            self.assert_util.assert_by_operator(archive_data.get("status"), "=", "ACTIVE", "档案状态不正确")
            self.assert_util.assert_by_operator(archive_data.get("enabled"), "=", True, "启用状态不正确")
            
            # 5. 记录报告
            a.json(filtered_params, "查询账户档案状态参数")
            a.json(response, "查询账户档案状态结果")
            self.logger.info(f"账户档案状态查询成功，状态: ACTIVE, ID: {self.acc_archive_id}")
            
        except Exception as e:
            a.text(str(e), "查询账户档案状态失败原因")
            self.logger.error(f"测试查询账户档案状态失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户状态管理",
        title="测试停用信用账户档案",
        description="验证信用账户档案停用功能，将ACTIVE状态改为FROZEN",
        severity="critical",
        order=7,
        smoke=True,
        tags=["erp_acc", "status", "freeze", "archive"]
    )
    def test_freeze_acc_archive(self):
        """测试停用信用账户档案"""
        try:
            # 确保有测试数据且当前为启用状态
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 验证当前状态为ACTIVE
            current_status = self._get_current_archive_status()
            if current_status != "ACTIVE":
                self.logger.warning(f"当前状态为 {current_status}，不是ACTIVE，跳过停用测试")
                pytest.skip(f"当前状态 {current_status} 不适合停用测试")
            
            # 1. 获取停用API配置
            api_path = self.get_api_path("ADV_CM_ARCHIVES_FREEZE_ACTION_SERVICE")  # 信用管理-信用账户档案停用服务
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理 - 单个ID操作
            freeze_data = {
                "id": self.acc_archive_id,
                "operation": "FREEZE",  # 停用操作
                "reason": f"自动化测试停用_{self.mock_util.get_timestamp()}"
            }
            
            fields_to_filter = ["id", "operation", "reason"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, freeze_data)
            
            # 3. 发送停用请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 断言验证
            self.assert_util.assert_response_success(response)
            result_data = response.get("data", {})
            assert result_data.get("success"), "停用操作未成功"
            assert result_data.get("message", "").find("停用") != -1, "响应消息未包含停用关键字"
            
            # 5. 验证停用结果
            new_status = self._get_current_archive_status()
            assert new_status == "FROZEN", f"停用后状态应为FROZEN，实际为: {new_status}"
            
            # 6. 记录报告
            a.json(filtered_params, "停用账户档案请求参数")
            a.json(response, "停用账户档案响应结果")
            a.text(f"状态变更: ACTIVE -> FROZEN", "状态变更记录")
            self.logger.info(f"信用账户档案停用成功，ID: {self.acc_archive_id}，新状态: FROZEN")
            
        except Exception as e:
            a.text(str(e), "停用账户档案失败原因")
            self.logger.error(f"测试停用账户档案失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户状态管理",
        title="测试启用信用账户档案",
        description="验证信用账户档案启用功能，将FROZEN状态恢复为ACTIVE",
        severity="critical",
        order=8,
        tags=["erp_acc", "status", "unfreeze", "archive"]
    )
    def test_unfreeze_acc_archive(self):
        """测试启用信用账户档案"""
        try:
            # 确保有测试数据且当前为停用状态
            if not self.acc_archive_id:
                self.test_save_acc_archive()
                self.test_freeze_acc_archive()  # 先停用再启用
            
            # 验证当前状态为FROZEN
            current_status = self._get_current_archive_status()
            if current_status != "FROZEN":
                self.logger.warning(f"当前状态为 {current_status}，不是FROZEN，执行停用后再测试")
                self.test_freeze_acc_archive()
                current_status = self._get_current_archive_status()
                assert current_status == "FROZEN", "准备状态失败"
            
            # 1. 获取启用API配置
            api_path = self.get_api_path("ADV_CM_ARCHIVES_UN_FREEZE_ACTION_SERVICE")  # 信用管理-信用账户档案启用服务
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理 - 单个ID操作
            unfreeze_data = {
                "id": self.acc_archive_id,
                "operation": "UNFREEZE",  # 启用操作
                "reason": f"自动化测试启用_{self.mock_util.get_timestamp()}"
            }
            
            fields_to_filter = ["id", "operation", "reason"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, unfreeze_data)
            
            # 3. 发送启用请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 断言验证
            self.assert_util.assert_response_success(response)
            result_data = response.get("data", {})
            assert result_data.get("success"), "启用操作未成功"
            assert result_data.get("message", "").find("启用") != -1, "响应消息未包含启用关键字"
            
            # 5. 验证启用结果
            new_status = self._get_current_archive_status()
            assert new_status == "ACTIVE", f"启用后状态应为ACTIVE，实际为: {new_status}"
            
            # 6. 记录报告
            a.json(filtered_params, "启用账户档案请求参数")
            a.json(response, "启用账户档案响应结果")
            a.text(f"状态变更: FROZEN -> ACTIVE", "状态变更记录")
            self.logger.info(f"信用账户档案启用成功，ID: {self.acc_archive_id}，新状态: ACTIVE")
            
        except Exception as e:
            a.text(str(e), "启用账户档案失败原因")
            self.logger.error(f"测试启用账户档案失败: {str(e)}")
            raise
    
    def _get_current_archive_status(self):
        """辅助方法：获取当前账户档案状态"""
        try:
            api_path = self.get_api_path("account_profile_query_customer_info")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.acc_archive_id}]
                },
                "fields": [{"name": "status", "type": "TEXT"}]
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["pageable", "fields"], ["params", "request"])
            ParamUtil.set_request_params(filtered_params, query_params)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            data_list = response.get("data", {}).get("data", {}).get("records", [])
            if data_list:
                return data_list[0].get("status", "UNKNOWN")
            return "NOT_FOUND"
            
        except Exception as e:
            self.logger.error(f"获取档案状态失败: {str(e)}")
            return "ERROR"
