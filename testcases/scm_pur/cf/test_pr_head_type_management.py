import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_pur import ScmPurBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("采购管理")
@allure.feature("采购申请类型定义表管理")
class TestPrHeadTypeManagement(ScmPurBaseTest):
    """采购申请类型定义表管理测试类"""
    
    # 常量定义
    MODEL_KEY = "SCM_PUR$pur_pr_head_type_cf"
    MODULE_NAME = "SCM_PUR"
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.pr_head_type_id = None
        cls.pr_head_type_code = None
        cls.logger.info("采购申请类型定义表管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="pur_pr_head_type_cf",
                where="pr_type_code like %s",
                params=["AUTOTEST_PR_%"]
            )
            cls.logger.info("采购申请类型定义表测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    @case_decorator(
        story="采购申请类型定义表新建",
        title="测试创建采购申请类型",
        description="验证采购申请类型创建功能",
        severity="critical",
        file_level_order=1,  # 使用新的文件级排序
        tags=["采购申请类型定义表", "创建", "SYS_SaveDataService"]
    )
    def test_create_pr_head_type(self):
        """创建采购申请类型用例"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("(系统)保存数据服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 生成测试数据
            timestamp = self.mock_util.get_timestamp()
            test_code = f"AUTOTEST_PR_{timestamp}"
            test_name = f"自动化测试申请类型_{timestamp}"
            
            # 3. 过滤参数 - 只保留业务字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["prTypeCode", "prTypeName"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数
            ParamUtil.set_request_params(filtered_params, {
                "prTypeCode": test_code,
                "prTypeName": test_name
            })
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            # 5. 执行请求
            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            self.assert_util.assert_response_data(response)
            
            # 6. 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert "id" in result_data and "prTypeCode" in result_data, "创建结果缺少必需字段"
            assert result_data.get("prTypeCode") == test_code, "申请类型编码不匹配"
            
            # 7. 保存测试数据
            self.__class__.pr_head_type_id = result_data.get("id")
            self.__class__.pr_head_type_code = result_data.get("prTypeCode")
            
            self.logger.info(f"✅ 采购申请类型创建成功，ID: {self.__class__.pr_head_type_id}, 编码: {self.__class__.pr_head_type_code}")
            
            # 8. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请类型定义表分页查询",
        title="采购申请类型定义表分页数据服务",
        description="验证采购申请类型定义表分页数据服务功能",
        severity="blocker",
        file_level_order=2,  # 使用新的文件级排序
        tags=["采购申请类型定义表", "分页查询", "SYS_PagingDataService"]
    )
    def test_paging_pr_head_type(self):
        """采购申请类型定义表分页查询测试"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("PR-申请类型定义分页查询服务")
            params, url = self.get_api_params(api_path)
            
            # 2. 过滤参数 - 只过滤pageable
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["pageable"],
                ["params", "request"]
            )
            
            # 3. 设置请求参数 - 设置整个pageable对象
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "sortOrders": None,
                    "conditionItems": None
                }
            })
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            # 4. 执行请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            # 5. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
            # 6. 验证响应数据
            response_data = response.get("data", {}).get("data", {})
            data_list = response_data.get("data", [])
            total = response_data.get("total", 0)
            
            self.logger.info(f"✅ 分页查询成功，总数: {total}, 当前页数据: {len(data_list)} 条")
            
                
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请类型定义表导出任务",
        title="采购申请类型定义表导出任务接口",
        description="验证采购申请类型定义表导出任务接口功能",
        severity="normal",
        file_level_order=3,  # 使用新的文件级排序
        tags=["采购申请类型定义表", "导出任务"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_export_task_pr_head_type(self):
        """采购申请类型定义表导出任务测试"""
        try:
            # 1. 获取API配置
            api_path = self.get_api_path("采购申请类型定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)
            
            # 2. 生成任务名称
            timestamp = self.mock_util.get_timestamp()
            task_name = f"申请类型-自动化测试-{timestamp}-导出"
            
            # 3. 获取导出的ID列表
            condition_value = [self.__class__.pr_head_type_id] if self.__class__.pr_head_type_id else []
            
            # 4. 过滤参数 - 只过滤业务字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["serviceKey", "teamId", "taskName", "multiSheetConfig", "queryData", "processConfig"],
                ["params"]
            )
            
            # 5. 构建导出配置
            export_config = {
                "serviceKey": "SCM_PUR$PUR_PR_HEAD_TYPE_CF_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "taskName": task_name,
                "multiSheetConfig": [{
                    "modelKey": self.MODEL_KEY,
                    "modelName": "采购申请类型定义表",
                    "sheetNo": 0,
                    "sheetName": "采购申请类型定义表",
                    "headerConfigList": [
                        {"name": "类型编号", "type": "TEXT", "field": "prTypeCode"},
                        {"name": "类型名称", "type": "TEXT", "field": "prTypeName"}
                    ]
                }],
                "queryData": {
                    "appId": 0,
                    "teamId": 22,
                    "containerKey": f"{self.MODULE_NAME}$PUR_PR_TYPE_VIEW-list-{self.MODEL_KEY}",
                    "viewKey": f"{self.MODULE_NAME}$PUR_PR_TYPE_VIEW:list",
                    "sceneKey": f"{self.MODULE_NAME}$PUR_PR_TYPE_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
                                "conditionItems": {
                                    "type": "ConditionItems",
                                    "logicOperator": "AND",
                                    "conditions": {
                                        "id": {
                                            "operator": "IN",
                                            "value": condition_value
                                        }
                                    } if condition_value else {}
                                },
                                "pageNo": 1,
                                "pageSize": 20
                            }
                        },
                        "selectFields": [
                            {"field": "prTypeCode"},
                            {"field": "prTypeName"}
                        ],
                        "modelKey": self.MODEL_KEY
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR",
                    "appId": 0,
                    "teamId": 22,
                    "model": self.MODEL_KEY,
                    "modelName": "采购申请类型定义表",
                    "containerKey": f"{self.MODULE_NAME}$PUR_PR_TYPE_VIEW-list-{self.MODEL_KEY}",
                    "viewKey": f"{self.MODULE_NAME}$PUR_PR_TYPE_VIEW:list",
                    "sceneKey": f"{self.MODULE_NAME}$PUR_PR_TYPE_VIEW"
                }
            }
            
            # 6. 设置参数
            filtered_params["serviceKey"] = export_config["serviceKey"]
            filtered_params["teamId"] = export_config["teamId"]
            for key in ["taskName", "multiSheetConfig", "queryData", "processConfig"]:
                filtered_params["params"][key] = export_config[key]
            
            # 7. 执行请求
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.logger.info(f"✅ 导出任务创建成功，任务名称: {task_name}")
            
            # 8. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="采购申请类型定义表删除",
        title="测试删除采购申请类型",
        description="验证采购申请类型删除功能",
        severity="critical",
        file_level_order=4,  # 使用新的文件级排序
        tags=["采购申请类型定义表", "删除", "SYS_DeleteDataByIdService"]
    )
    def test_delete_pr_head_type(self):
        """删除采购申请类型用例"""
        try:
            # 1. 检查是否有可用的ID
            if not self.__class__.pr_head_type_id:
                pytest.skip("没有可用的采购申请类型ID，跳过删除测试")
            
            # 2. 获取API配置
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 3. 过滤参数 - 只保留id字段
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["id"],
                ["params", "request"]
            )
            
            # 4. 设置请求参数
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.pr_head_type_id})
            filtered_params["params"]["modelKey"] = self.MODEL_KEY
            
            # 5. 执行请求
            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": self.MODULE_NAME, "modelKey": self.MODEL_KEY}
            )
            
            # 6. 验证删除结果
            assert response.get("success") is True, "删除请求失败"
            
            self.logger.info(f"✅ 采购申请类型删除成功，ID: {self.__class__.pr_head_type_id}")
            
            # 7. 清空类变量
            self.__class__.pr_head_type_id = None
            self.__class__.pr_head_type_code = None
            
            # 8. 记录报告
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
