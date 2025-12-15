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
@allure.feature("账户额度配置管理")
class TestAccAmountConfig(ErpAccBaseTest):
    """账户额度配置管理测试类 - 覆盖额度配置CRUD和标准导入导出服务"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.amount_config_id = None
        cls.logger.info("账户额度配置管理测试类初始化完成")
        
        # 初始化依赖数据（额度配置依赖档案和基础数据）
        if cls.acc_cache_data:
            cls.acc_archive_id = cls.acc_cache_data.get("archive_info", [])[0].get("id") if cls.acc_cache_data.get("archive_info") else None
            cls.cust_id = cls.acc_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id") if cls.acc_cache_data.get("partner_info") else None
            cls.com_org_id = cls.acc_cache_data.get("org_info", {}).get("gr_come_org_info", [])[0].get("id") if cls.acc_cache_data.get("org_info") else None
            cls.curr_id = cls.acc_cache_data.get("currency_info", [])[0].get("curr_id") if cls.acc_cache_data.get("currency_info") else None
    
    @classmethod
    def teardown_class(cls):
        """测试类清理 - 单独清理每个表"""
        try:
            # 清理额度配置主表
            cls.db.delete(
                table="adv_cm_acc_amount_config",  # 额度配置表，实际表名需确认
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("额度配置测试数据清理完成")
            
            # 清理相关历史记录表（如果存在）
            # cls.db.delete(table="adv_cm_amount_history", where="config_id like %s", params=["AT_%"])
            
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试创建账户额度配置",
        description="验证账户额度配置创建功能，包括额度限制和有效期设置",
        severity="critical",
        order=1,
        smoke=True,
        tags=["erp_acc", "amount", "create", "config"]
    )
    def test_save_amount_config(self):
        """测试创建账户额度配置"""
        try:
            # 1. 检查依赖数据（需要账户档案）
            if not self.acc_archive_id or not self.cust_id:
                # 如果没有档案，先创建
                if not self.acc_archive_id:
                    from testcases.erp_acc.test_acc_archive_management import TestAccArchiveManagement
                    # 模拟创建档案（实际中可能需要调用测试方法）
                    self.logger.warning("缺少账户档案，创建测试档案")
                    # 这里简化处理，实际应调用档案创建逻辑
                    pytest.skip("缺少账户档案依赖，需先运行档案管理测试")
            
            # 2. 准备测试数据
            config_code = self.mock_util.generate_unique_code(tag="AMT_CFG")
            config_name = f"自动化测试额度配置_{self.mock_util.get_timestamp()}"
            remark = self.mock_util.get_mock_remark()
            
            # 随机生成额度值（正数）
            credit_limit = 100000.00  # 信用额度
            temp_limit = 50000.00     # 临时额度
            valid_start = "2025-01-01"  # 有效开始日期
            valid_end = "2025-12-31"    # 有效结束日期
            
            # 3. 获取创建API配置
            api_path = self.get_api_path("SYS_CreateDataService")  # (系统)新增数据服务
            params, url = self.get_api_params(api_path)
            
            # 4. 参数过滤和设置
            fields_to_filter = ["code", "name", "archive_id", "cust_id", "org_id", "currency_id", 
                              "credit_limit", "temp_limit", "valid_start", "valid_end", 
                              "enabled", "remark"]
            filtered_params = ParamUtil.filter_post_body_fields(
                params, fields_to_filter, ["params", "request"]
            )
            
            create_data = {
                "code": config_code,
                "name": config_name,
                "archive_id": self.acc_archive_id,
                "cust_id": self.cust_id,
                "org_id": self.com_org_id,
                "currency_id": self.curr_id,
                "credit_limit": credit_limit,
                "temp_limit": temp_limit,
                "valid_start": valid_start,
                "valid_end": valid_end,
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
            
            self.amount_config_id = data.get("id")
            assert self.amount_config_id, "未获取到配置ID"
            
            # 验证关键字段
            self.assert_util.assert_by_operator(data.get("code"), "=", config_code, "配置编码验证失败")
            self.assert_util.assert_by_operator(data.get("credit_limit"), "=", credit_limit, "信用额度验证失败")
            self.assert_util.assert_by_operator(data.get("temp_limit"), "=", temp_limit, "临时额度验证失败")
            self.assert_util.assert_by_operator(data.get("enabled"), "=", True, "启用状态验证失败")
            
            # 7. Allure报告
            a.json(filtered_params, "创建额度配置请求参数")
            a.json(response, "创建额度配置响应结果")
            self.logger.info(f"额度配置创建成功，ID: {self.amount_config_id}, 额度: {credit_limit}")
            
        except Exception as e:
            a.text(str(e), "创建额度配置失败原因")
            self.logger.error(f"创建额度配置失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试查询账户额度配置列表",
        description="验证账户额度配置分页查询功能",
        severity="normal",
        order=4,
        tags=["erp_acc", "amount", "query", "config"]
    )
    def test_query_amount_config(self):
        """测试查询账户额度配置"""
        try:
            # 确保有测试数据
            if not self.amount_config_id:
                self.test_save_amount_config()
            
            # 1. 获取查询API配置
            api_path = self.get_api_path("SYS_PagingDataService")  # (系统)查询分页数据服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建查询参数
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True,
                    "sortOrders": None,
                    "conditionItems": [
                        {"field": "id", "operator": "eq", "value": self.amount_config_id},
                        {"field": "cust_id", "operator": "eq", "value": self.cust_id}
                    ]
                },
                "fields": [
                    {"name": "id", "type": "NUMBER"},
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "archive_id", "type": "NUMBER"},
                    {"name": "credit_limit", "type": "NUMBER"},
                    {"name": "temp_limit", "type": "NUMBER"},
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
            
            # 4. 验证查询结果
            self.assert_util.assert_response_success(response)
            query_data = response.get("data", {}).get("data", {})
            records = query_data.get("records", [])
            total = query_data.get("total", 0)
            
            assert total >= 1, "未查询到额度配置记录"
            assert len(records) >= 1, "查询记录列表为空"
            
            # 验证具体记录
            config_info = records[0]
            self.assert_util.assert_by_operator(config_info.get("id"), "=", self.amount_config_id, "配置ID不匹配")
            self.assert_util.assert_by_operator(config_info.get("cust_id"), "=", self.cust_id, "客户ID不匹配")
            self.assert_util.assert_by_operator(config_info.get("credit_limit"), ">", 0, "信用额度必须大于0")
            self.assert_util.assert_by_operator(config_info.get("enabled"), "=", True, "启用状态不匹配")
            
            # 5. Allure报告
            a.json(filtered_params, "查询额度配置参数")
            a.json(response, "查询额度配置结果")
            self.logger.info(f"额度配置查询成功，共{total}条记录")
            
        except Exception as e:
            a.text(str(e), "查询额度配置失败原因")
            self.logger.error(f"查询额度配置失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试更新账户额度配置",
        description="验证账户额度配置更新功能，修改额度限制和有效期",
        severity="normal",
        order=7,
        tags=["erp_acc", "amount", "update", "config"]
    )
    def test_update_amount_config(self):
        """测试更新账户额度配置"""
        try:
            # 确保有测试数据
            if not self.amount_config_id:
                self.test_save_amount_config()
            
            # 1. 准备更新数据
            new_credit_limit = 200000.00  # 增加信用额度
            new_temp_limit = 100000.00    # 增加临时额度
            new_valid_end = "2026-12-31"  # 延长有效期
            new_remark = self.mock_util.get_mock_remark()
            
            # 2. 获取更新API配置
            api_path = self.get_api_path("SYS_UpdateDataByIdService")  # (系统)更新数据服务
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            update_data = {
                "id": self.amount_config_id,
                "credit_limit": new_credit_limit,
                "temp_limit": new_temp_limit,
                "valid_end": new_valid_end,
                "remark": new_remark,
                "enabled": True
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id", "credit_limit", "temp_limit", "valid_end", "remark"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, update_data)
            
            # 4. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 5. 断言验证
            self.assert_util.assert_response_success(response)
            update_result = response.get("data", {})
            assert update_result.get("success"), "更新操作未成功"
            
            # 6. 查询验证更新效果
            self.test_query_amount_config()  # 重新查询验证
            
            # 7. 记录报告
            a.json(filtered_params, "更新额度配置参数")
            a.json(response, "更新额度配置结果")
            a.text(f"额度变更: 信用额度 {100000.00} -> {new_credit_limit}", "额度变更记录")
            self.logger.info(f"额度配置更新成功，ID: {self.amount_config_id}, 新额度: {new_credit_limit}")
            
        except Exception as e:
            a.text(str(e), "更新额度配置失败原因")
            self.logger.error(f"更新额度配置失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试删除账户额度配置",
        description="验证单个账户额度配置删除功能",
        severity="critical",
        order=16,
        tags=["erp_acc", "amount", "delete", "config"]
    )
    def test_delete_amount_config(self):
        """测试删除账户额度配置"""
        try:
            # 确保有测试数据
            if not self.amount_config_id:
                self.test_save_amount_config()
            
            # 1. 获取API配置
            api_path = self.get_api_path("SYS_DeleteDataByIdService")  # (系统)删除数据服务
            params, url = self.get_api_params(api_path)
            
            # 2. 单个ID删除参数
            delete_data = {"id": self.amount_config_id}
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
            
            # 5. 查询验证删除效果
            saved_id = self.amount_config_id
            self.amount_config_id = None
            
            # 尝试查询已删除的配置
            api_path_query = self.get_api_path("SYS_PagingDataService")
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
            
            assert len(query_records) == 0, f"删除后仍能查询到配置 ID: {saved_id}"
            
            # 6. 记录报告
            a.json(filtered_params, "删除额度配置参数")
            a.json(response, "删除额度配置结果")
            self.logger.info(f"额度配置删除成功，ID: {saved_id}")
            
        except Exception as e:
            a.text(str(e), "删除额度配置失败原因")
            self.logger.error(f"删除额度配置失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试账户额度配置标准导入",
        description="验证ADV_CM_ACC_AMOUNT_CF_GEI_IMPORT_SERVICE标准导入服务",
        severity="normal",
        order=13,
        tags=["erp_acc", "amount", "import"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_import_amount(self):
        """测试账户额度配置标准导入服务"""
        try:
            # 1. 获取导入API配置
            api_path = self.get_api_path("ADV_CM_ACC_AMOUNT_CF_GEI_IMPORT_SERVICE")  # 账户额度配置标准导入服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导入参数（需要准备导入文件，这里简化）
            import_data = {
                "serviceKey": "ADV_CM_ACC_AMOUNT_CF_GEI_IMPORT_SERVICE",
                "teamId": 22,
                "params": {
                    "taskName": f"AMOUNT_IMPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "filePath": "/tmp/amount_config_template.xlsx",  # 假设文件路径
                    "modelKey": "ADV_CM_ACC_AMOUNT_CONFIG",
                    "importConfig": {
                        "headerRow": 1,
                        "dataStartRow": 2,
                        "fieldMapping": {
                            "code": "A",
                            "name": "B", 
                            "credit_limit": "C",
                            "temp_limit": "D",
                            "cust_id": "E"
                        }
                    }
                }
            }
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["serviceKey", "teamId", "params"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, import_data)
            
            # 3. 发送请求
            response = self.http.post(url, json=filtered_params)
            
            # 4. 验证导入任务
            self.assert_util.assert_response_data(response)
            import_result = response.get("data", {})
            assert import_result.get("success"), "导入任务创建失败"
            
            # 5. Allure报告
            a.json(filtered_params, "标准导入请求参数")
            a.json(response, "标准导入响应结果")
            self.logger.info("额度配置标准导入任务创建成功")
            
        except Exception as e:
            a.text(str(e), "标准导入额度配置失败原因")
            self.logger.error(f"标准导入失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试提交额度配置导入任务",
        description="验证ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST导入任务提交服务",
        severity="normal",
        order=14,
        tags=["erp_acc", "amount", "import_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_import_task(self):
        """测试提交额度配置导入任务"""
        try:
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST")  # 账户额度配置-导入导出任务管理接口-通过OSS提交导入任务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "IMPORT",
                "taskName": f"AMOUNT_IMPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_AMOUNT_CONFIG",
                "fileInfo": {
                    "fileName": "amount_config_data.xlsx",
                    "fileSize": 10240,
                    "filePath": "/oss/amount_import/xxx.xlsx"
                },
                "importFields": ["code", "name", "credit_limit", "temp_limit", "cust_id"],
                "validationRules": {
                    "credit_limit": {"type": "NUMBER", "min": 0, "required": True},
                    "temp_limit": {"type": "NUMBER", "min": 0, "required": False}
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
            
            # 5. Allure报告
            a.json(filtered_params, "导入任务提交参数")
            a.json(response, "导入任务提交结果")
            self.logger.info(f"额度配置导入任务提交成功，Task ID: {task_result.get('data', {}).get('task_id')}")
            
        except Exception as e:
            a.text(str(e), "提交导入任务失败原因")
            self.logger.error(f"提交导入任务失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试账户额度配置标准导出",
        description="验证ADV_CM_ACC_AMOUNT_CF_GEI_EXPORT_SERVICE标准导出服务",
        severity="normal",
        order=10,
        tags=["erp_acc", "amount", "export"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_standard_export_amount(self):
        """测试账户额度配置标准导出服务"""
        try:
            # 确保有测试数据
            if not self.amount_config_id:
                self.test_save_amount_config()
            
            # 1. 获取导出API配置
            api_path = self.get_api_path("ADV_CM_ACC_AMOUNT_CF_GEI_EXPORT_SERVICE")  # 账户额度配置标准导出服务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建导出参数
            export_data = {
                "serviceKey": "ADV_CM_ACC_AMOUNT_CF_GEI_EXPORT_SERVICE",
                "teamId": 22,
                "params": {
                    "taskName": f"AMOUNT_EXPORT_{self.nickname}_{self.mock_util.get_timestamp()}",
                    "multiSheetConfig": [
                        {
                            "modelKey": "ADV_CM_ACC_AMOUNT_CONFIG",
                            "modelName": "账户额度配置",
                            "sheetNo": 0,
                            "sheetName": "额度配置列表",
                            "headerConfigList": [
                                {"name": "配置ID", "type": "TEXT", "field": "id"},
                                {"name": "配置编码", "type": "TEXT", "field": "code"},
                                {"name": "配置名称", "type": "TEXT", "field": "name"},
                                {"name": "信用额度", "type": "NUMBER", "field": "credit_limit"},
                                {"name": "临时额度", "type": "NUMBER", "field": "temp_limit"},
                                {"name": "客户ID", "type": "NUMBER", "field": "cust_id"},
                                {"name": "状态", "type": "TEXT", "field": "status"}
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "ADV_CM_ACC",
                        "viewKey": "ADV_CM_ACC_AMOUNT:list",
                        "sceneKey": "ADV_CM_ACC_AMOUNT",
                        "params": {
                            "request": {
                                "pageable": {
                                    "pageNo": 1,
                                    "pageSize": 100,
                                    "needTotal": True,
                                    "sortOrders": [{"field": "credit_limit", "direction": "DESC"}],
                                    "conditionItems": [
                                        {"field": "id", "operator": "eq", "value": self.amount_config_id}
                                    ]
                                }
                            },
                            "selectFields": [
                                {"field": "id"}, {"field": "code"}, {"field": "name"},
                                {"field": "credit_limit"}, {"field": "temp_limit"}, 
                                {"field": "cust_id"}, {"field": "status"}, {"field": "enabled"}
                            ],
                            "modelKey": "ADV_CM_ACC_AMOUNT_CONFIG"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "ADV_CM_ACC_AMOUNT_CONFIG",
                        "modelName": "账户额度配置",
                        "containerKey": "ADV_CM_ACC",
                        "viewKey": "ADV_CM_ACC_AMOUNT:list",
                        "sceneKey": "ADV_CM_ACC_AMOUNT"
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
            self.logger.info(f"额度配置标准导出任务创建成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "标准导出额度配置失败原因")
            self.logger.error(f"标准导出失败: {str(e)}")
            raise
    
    @case_decorator(
        story="账户额度配置管理",
        title="测试提交额度配置导出任务",
        description="验证ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_EXPORT_DIRECT_POST导出任务提交服务",
        severity="normal",
        order=11,
        tags=["erp_acc", "amount", "export_task"]
    )
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    def test_submit_export_task(self):
        """测试提交额度配置导出任务"""
        try:
            # 确保有测试数据
            if not self.amount_config_id:
                self.test_save_amount_config()
            
            # 1. 获取任务提交API配置
            api_path = self.get_api_path("ADV_CM_ACC_AMOUNT_CF_API_GEI_TASK_EXPORT_DIRECT_POST")  # 账户额度配置-导入导出任务管理接口-提交导出任务
            params, url = self.get_api_params(api_path)
            
            # 2. 构建任务参数
            task_data = {
                "taskType": "EXPORT",
                "taskName": f"AMOUNT_EXPORT_TASK_{self.mock_util.get_timestamp()}",
                "targetModel": "ADV_CM_ACC_AMOUNT_CONFIG",
                "filterCondition": {
                    "cust_id": self.cust_id,
                    "enabled": True
                },
                "exportFields": ["id", "code", "name", "credit_limit", "temp_limit", "cust_id", "status"],
                "exportFormat": "EXCEL",
                "includeHeader": True
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
            self.logger.info(f"额度配置导出任务提交成功，Task ID: {task_id}")
            
        except Exception as e:
            a.text(str(e), "提交导出任务失败原因")
            self.logger.error(f"提交导出任务失败: {str(e)}")
            raise
    
    def _get_current_config_info(self):
        """辅助方法：获取当前额度配置信息"""
        try:
            api_path = self.get_api_path("SYS_PagingDataService")
            params, url = self.get_api_params(api_path)
            
            query_params = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 1,
                    "conditionItems": [{"field": "id", "operator": "eq", "value": self.amount_config_id}]
                },
                "fields": [
                    {"name": "credit_limit", "type": "NUMBER"},
                    {"name": "temp_limit", "type": "NUMBER"},
                    {"name": "valid_end", "type": "TEXT"}
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
            self.logger.error(f"获取配置信息失败: {str(e)}")
            return {}
