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
@allure.feature("账户档案管理")
class TestAccArchiveManagement(ErpAccBaseTest):
    """账户档案管理测试类 - 覆盖档案查询、CRUD和标准导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.acc_archive_id = None
        cls.logger.info("账户档案管理测试类初始化完成")
        
        # 初始化依赖数据
        if cls.acc_cache_data:
            cls.cust_id = cls.acc_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id") if cls.acc_cache_data.get("partner_info") else None
            cls.com_org_id = cls.acc_cache_data.get("org_info", {}).get("gr_come_org_info", [])[0].get("id") if cls.acc_cache_data.get("org_info") else None
            cls.curr_id = cls.acc_cache_data.get("currency_info", [])[0].get("curr_id") if cls.acc_cache_data.get("currency_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理账户档案主表
            cls.db.delete(
                table="adv_cm_acc_archive",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("账户档案主表测试数据清理完成")
            
            # 清理相关日志或扩展表（如果存在）
            # cls.db.delete(table="adv_cm_acc_archive_log", where="archive_id like %s", params=["AT_%"])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="账户档案管理",
        title="测试创建信用账户档案",
        description="验证信用账户档案创建功能，包括基本信息和客户关联",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "archive", "create"]
    )
    def test_save_acc_archive(self):
        """测试创建信用账户档案"""
        try:
            # 1. 检查基础依赖数据
            if not all([self.cust_id, self.com_org_id]):
                self.logger.warning("缺少客户或组织ID，跳过创建测试")
                pytest.skip("缺少基础依赖数据")
            
            # 2. 准备测试数据
            archive_code = self.mock_util.generate_unique_code(tag="ACC_ARC")
            archive_name = f"自动化测试档案_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("ACC_MD_SAVE_EVENT_SERVICE")  # 账户-档案保存服务
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "cust_id", "org_id", "currency_id", "status", "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            create_data = {
                "code": archive_code,
                "name": archive_name,
                "cust_id": self.cust_id,
                "org_id": self.com_org_id,
                "currency_id": self.curr_id,
                "status": "ACTIVE",
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
            
            self.acc_archive_id = data.get("id")
            assert self.acc_archive_id, "未获取到档案ID"
            
            # 验证返回数据
            self.assert_util.assert_by_operator(data.get("code"), "=", archive_code, "档案编码验证失败")
            self.assert_util.assert_by_operator(data.get("name"), "=", archive_name, "档案名称验证失败")
            self.assert_util.assert_by_operator(data.get("status"), "=", "ACTIVE", "初始状态验证失败")
            
            # 7. Allure报告
            a.json(filtered_params, "创建账户档案请求参数")
            a.json(response, "创建账户档案响应结果")
            self.logger.info(f"账户档案创建成功，ID: {self.acc_archive_id}")
            
        except Exception as e:
            a.text(str(e), "创建账户档案失败原因")
            self.logger.error(f"创建账户档案失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户档案管理",
        title="测试查询客户账户档案信息",
        description="使用account_profile_query_customer_info接口查询档案详情",
        severity="normal",
        order=4,
        tags=["erp_acc", "archive", "query"]
    )
    def test_query_customer_info(self):
        """测试查询客户账户档案信息"""
        try:
            # 确保有测试数据
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("account_profile_query_customer_info")  # 账户档案查询客户信息
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数
            query_params = {
                "cust_id": self.cust_id,  # 查询指定客户
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True,
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.acc_archive_id}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "cust_id", "type": "NUMBER"},
                    {"name": "status", "type": "TEXT"},
                    {"name": "enabled", "type": "BOOLEAN"}
                ]
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, list(query_params.keys()), ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, query_params)
            
            # 3. 发送查询请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证查询结果
            self.assert_util.assert_response_success(response)
            query_data = response.get("data", {}).get("data", {})
            records = query_data.get("records", [])
            total = query_data.get("total", 0)
            
            assert total >= 1, "未查询到账户档案记录"
            assert len(records) >= 1, "查询记录列表为空"
            
            # 验证具体记录
            archive_info = records[0]
            self.assert_util.assert_by_operator(archive_info.get("id"), "=", self.acc_archive_id, "档案ID不匹配")
            self.assert_util.assert_by_operator(archive_info.get("cust_id"), "=", self.cust_id, "客户ID不匹配")
            self.assert_util.assert_by_operator(archive_info.get("status"), "=", "ACTIVE", "档案状态不匹配")
            
            # 5. Allure报告
            a.json(filtered_params, "查询客户档案参数")
            a.json(response, "查询客户档案结果")
            self.logger.info(f"客户档案查询成功，共{total}条记录")
            
        except Exception as e:
            a.text(str(e), "查询客户档案信息失败原因")
            self.logger.error(f"查询客户档案失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户档案管理",
        title="测试更新信用账户档案",
        description="验证账户档案信息更新功能，修改名称和备注",
        severity="normal",
        order=7,
        tags=["erp_acc", "archive", "update"]
    )
    def test_update_acc_archive(self):
        """测试更新信用账户档案"""
        try:
            # 确保有测试数据
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 1. 准备更新数据
            new_name = f"更新后档案名称_{self.mock_util.get_timestamp()}"
            new_remark = self.mock_util.get_mock_remark()
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("SYS_MasterData_UpdateDataService")  # (系统)更新主数据服务
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            update_data = {
                "id": self.acc_archive_id,
                "name": new_name,
                "remark": new_remark,
                "enabled": True  # 保持启用状态
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "name", "remark"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, update_data)
            
            # 4. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 5. 断言验证
            self.assert_util.assert_response_success(response)
            assert response.get("data", {}).get("success"), "更新操作未成功"
            
            # 6. 验证更新结果（通过查询验证）
            self.test_query_customer_info()  # 重新查询验证
            
            # 7. 记录报告
            a.json(filtered_params, "更新账户档案参数")
            a.json(response, "更新账户档案结果")
            self.logger.info(f"账户档案更新成功，ID: {self.acc_archive_id}")
            
        except Exception as e:
            a.text(str(e), "更新账户档案失败原因")
            self.logger.error(f"测试更新账户档案失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户档案管理",
        title="测试删除信用账户档案",
        description="验证单个账户档案删除功能",
        severity="critical",
        order=16,
        tags=["erp_acc", "archive", "delete"]
    )
    def test_delete_acc_archive(self):
        """测试删除信用账户档案"""
        try:
            # 确保有测试数据
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 1. 获取API配置
            api_path = self.get_api_path("ADV_CM_ACC_MD_DELETE_EVENT_SERVICE")  # 账户-档案删除服务
            params, url = self.get_api_params(api_path)
            
            # 2. 参数处理 - 单个ID
            delete_data = {"id": self.acc_archive_id}
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, delete_data)
            
            # 3. 发送删除请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 断言验证
            self.assert_util.assert_response_success(response)
            delete_result = response.get("data", {})
            assert delete_result.get("success"), "删除操作未成功"
            
            # 5. 验证删除结果（查询不应存在）
            # 临时保存ID用于验证
            saved_id = self.acc_archive_id
            self.acc_archive_id = None
            
            # 查询验证
            api_path_query = self.get_api_path("account_profile_query_customer_info")
            query_params, query_url = self.get_api_params(api_path_query)
            
            query_data = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 10,
                    "needTotal": True,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": saved_id}]
                }
            }
            
            filtered_query = ParamUtil.filter_post_body_fields(
                query_params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_query, query_data)
            
            query_response = self.http.post(query_url, json=filtered_query)
            query_data_list = query_response.get("data", {}).get("data", {}).get("records", [])
            
            assert len(query_data_list) == 0, f"删除后仍能查询到档案 ID: {saved_id}"
            self.logger.info(f"账户档案删除验证成功，ID: {saved_id} 已不存在")
            
            # 6. 记录报告
            a.json(filtered_params, "删除账户档案参数")
            a.json(response, "删除账户档案结果")
            
        except Exception as e:
            a.text(str(e), "删除账户档案失败原因")
            self.logger.error(f"测试删除账户档案失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户档案管理",
        title="测试信用账户档案标准导出",
        description="验证ADV_CM_ACC_MD_GEI_EXPORT_SERVICE标准导出服务",
        severity="normal",
        order=10,
        tags=["erp_acc", "archive", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_export_acc_archive_standard(self):
        """测试信用账户档案标准导出服务"""
        try:
            # 确保有测试数据
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_ACC_MD_GEI_EXPORT_SERVICE")  # 信用账户档案标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数
            export_data = {
                "serviceKey": "ADV_CM_ACC_MD_GEI_EXPORT_SERVICE",
                "teamId": 22,  # 固定团队ID
                "params": {
                    "taskName": f"ACC_ARCHIVE_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_ACC_ARCHIVE",
                            "modelName": "信用账户档案",
                            "sheetNo": 0,
                            "sheetName": "账户档案列表",
                            "headerConfigList": [
                                {"name": "档案ID", "type": "TEXT", "field": "id"},
                                {"name": "档案编码", "type": "TEXT", "field": "code"},
                                {"name": "档案名称", "type": "TEXT", "field": "name"},
                                {"name": "客户ID", "type": "NUMBER", "field": "cust_id"},
                                {"name": "状态", "type": "TEXT", "field": "status"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_ACC",
                        "viewKey": "ADV_CM_ACC_ARCHIVE:list",
                        "sceneKey": "ADV_CM_ACC_ARCHIVE",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 100,
                                    "needTotal": True,
                                    "sortOrders": [],
                                    "conditionItems": [
                                        {"field": "id", "operator": "eq", "value": self.acc_archive_id}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "cust_id"}, {"field": "status"}, {"field": "enabled"}
                            ],
                            "modelKey": "ADV_CM_ACC_ARCHIVE"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_ACC_ARCHIVE",
                        "modelName": "信用账户档案",
                        "containerKey": "ADV_CM_ACC",
                        "viewKey": "ADV_CM_ACC_ARCHIVE:list",
                        "sceneKey": "ADV_CM_ACC_ARCHIVE"
                    }
                }
            }
            
            # 简化参数设置（实际可能需要ParamUtil处理复杂结构）
            filtered_params = params.copy()
            ParamUtil.set_request_params(filtered_params, export_data)
            
            # 3. 发送导出请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证导出任务创建
            self.assert_util.assert_response_data(response)
            export_result = response.get("data", {})
            assert export_result.get("success"), "导出任务创建失败"
            task_id = export_result.get("data", {}).get("task_id")
            assert task_id, "未获取到导出任务ID"
            
            # 5. Allure报告
            a.json(filtered_params, "标准导出请求参数")
            a.json(response, "标准导出响应结果")
            self.logger.info(f"账户档案标准导出任务创建成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "标准导出账户档案失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户档案管理",
        title="测试提交账户档案导出任务",
        description="验证ADV_CM_ACC_MD_API_GEI_TASK_EXPORT_DIRECT_POST导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "archive", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task(self):
        """测试提交账户档案导出任务"""
        try:
            # 确保有测试数据
            if not self.acc_archive_id:
                self.test_save_acc_archive()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_MD_API_GEI_TASK_EXPORT_DIRECT_POST")  # 信用账户档案-导入导出任务管理接口-提交导出任务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务提交参数（简化版）
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"ACC_ARCHIVE_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_ARCHIVE",
                "filterCondition": {
                    "id": self.acc_archive_id
                },
                "exportFields": ["id", "code", "name", "cust_id", "status"]
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
            assert task_result.get("success"), "任务提交失败"
            
            # 5. Allure报告
            a.json(filtered_params, "导出任务提交参数")
            a.json(response, "导出任务提交结果")
            self.logger.info("账户档案导出任务提交成功")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户档案管理",
        title="测试账户档案导入任务提交(OSS)",
        description="验证通过OSS提交导入任务（复杂度较高，暂时标记跳过）",
        severity="minor",
        order=13,
        tags=["erp_acc", "archive", "import_oss"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_submit_import_task_oss(self):
        """测试账户档案OSS导入任务提交"""
        # 此测试涉及OSS配置，暂时跳过
        # 实现逻辑类似导出任务，但需要准备导入文件和OSS凭证
        pass
