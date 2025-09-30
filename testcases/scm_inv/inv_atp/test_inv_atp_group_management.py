import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))
from testcases.scm_inv import ScmInvBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("库存管理")
@allure.feature("ATP检查组管理")
class TestInvAtpGroupManagement(ScmInvBaseTest):
    """ATP检查组管理测试类 - 覆盖ATP检查组的增删改查功能"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 测试数据变量（使用类变量）
        cls.atp_group_id = None
        cls.atp_group_code = None
        cls.test_atp_group_code = None  # 从查询结果中提取的ATP组编码
        cls.test_atp_group_id = None    # 从查询结果中提取的ATP组ID
        
        cls.logger.info("ATP检查组管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="inv_atp_group_md",
                where="code like %s",
                params=["AUTOTEST_ATP_%"]
            )
            cls.logger.info("ATP检查组测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    #@pytest.mark.run(order=1)
    @case_decorator(
        story="ATP检查组管理",
        title="测试创建ATP检查组",
        description="验证ATP检查组创建功能",
        severity="critical",
        order=1,
        tags=["ATP检查组", "创建", "SYS_SaveDataService"]
    )
    def test_create_atp_group(self):
        """创建ATP检查组用例"""
        try:
            api_path = self.get_api_path("(系统)保存数据服务")
            params, url = self.get_api_params(api_path)
            
            # 生成测试数据
            timestamp = self.mock_util.get_timestamp()
            test_code = f"AUTOTEST_ATP_{timestamp}"
            test_name = f"自动化测试ATP组_{timestamp}"
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "code": test_code,
                "name": test_name
            })
            filtered_params["params"]["modelKey"] = "SCM_INV$inv_atp_group_md"

            # 执行请求
            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": "SCM_INV", "modelKey": "SCM_INV$inv_atp_group_md"}
            )
            self.assert_util.assert_response_data(response)
            
            # 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert "id" in result_data and "code" in result_data, "创建结果缺少必需字段"
            assert result_data.get("code") == test_code, "ATP组编码不匹配"
            
            # 保存测试数据
            self.__class__.atp_group_id = result_data.get("id")
            self.__class__.atp_group_code = result_data.get("code")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.run(order=2)
    @case_decorator(
        story="ATP检查组管理",
        title="测试查询ATP检查组导出",
        description="验证ATP检查组导出查询功能",
        severity="normal",
        order=2,
        tags=["ATP检查组", "导出查询"]
    )
    def test_query_atp_group_export(self):
        """查询ATP检查组导出用例"""
        try:
            api_path = self.get_api_path("ATP检查组-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            timestamp = self.mock_util.get_timestamp()
            task_name = f"ATP检查组-自动化测试-{timestamp}-导出"
            condition_value = [self.__class__.atp_group_id] if self.__class__.atp_group_id else []

            # 构建导出参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params,
                ["serviceKey", "teamId", "taskName", "multiSheetConfig", "queryData", "processConfig"],
                ["params"]
            )
            
            # 设置导出配置
            export_config = {
                "serviceKey": "SCM_INV$INV_ATP_GROUP_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "taskName": task_name,
                "multiSheetConfig": [{
                    "modelKey": "SCM_INV$inv_atp_group_md",
                    "modelName": "ATP检查组",
                    "sheetNo": 0,
                    "sheetName": "ATP检查组",
                    "headerConfigList": [
                        {"name": "编码", "type": "TEXT", "field": "code"},
                        {"name": "名称", "type": "TEXT", "field": "name"}
                    ]
                }],
                "queryData": {
                    "appId": 0, "teamId": 22,
                    "containerKey": "SCM_INV$INV_ATP_GROUP_VIEW-table-container-SCM_INV$inv_atp_group_md",
                    "viewKey": "SCM_INV$INV_ATP_GROUP_VIEW:list",
                    "sceneKey": "SCM_INV$INV_ATP_GROUP_VIEW",
                    "params": {
                        "request": {
                            "pageable": {
                                "conditionItems": {
                                    "type": "ConditionItems",
                                    "logicOperator": "AND",
                                    "conditions": {"id": {"operator": "IN", "value": condition_value}} if condition_value else {}
                                },
                                "pageNo": 1, "pageSize": 20
                            }
                        },
                        "selectFields": [{"field": "code"}, {"field": "name"}],
                        "modelKey": "SCM_INV$inv_atp_group_md"
                    }
                },
                "processConfig": {
                    "processType": "TRANTOR", "appId": 0, "teamId": 22,
                    "model": "SCM_INV$inv_atp_group_md", "modelName": "ATP检查组",
                    "containerKey": "SCM_INV$INV_ATP_GROUP_VIEW-table-container-SCM_INV$inv_atp_group_md",
                    "viewKey": "SCM_INV$INV_ATP_GROUP_VIEW:list",
                    "sceneKey": "SCM_INV$INV_ATP_GROUP_VIEW"
                }
            }
            
            # 应用配置
            filtered_params["serviceKey"] = export_config["serviceKey"]
            filtered_params["teamId"] = export_config["teamId"]
            for key in ["taskName", "multiSheetConfig", "queryData", "processConfig"]:
                filtered_params["params"][key] = export_config[key]

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.run(order=3)
    @case_decorator(
        story="ATP检查组管理",
        title="测试查询ATP检查组详情",
        description="验证ATP检查组详情查询功能",
        severity="normal",
        order=3,
        tags=["ATP检查组", "详情查询", "SYS_FindDataByIdService"]
    )
    def test_query_atp_group_detail(self):
        """查询ATP检查组详情用例"""
        try:
            if not self.__class__.atp_group_id:
                pytest.skip("没有可用的ATP组ID，跳过详情查询测试")
            
            api_path = self.get_api_path("(系统)查询数据详情服务")
            params, url = self.get_api_params(api_path)
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.atp_group_id})
            filtered_params["params"]["modelKey"] = "SCM_INV$inv_atp_group_md"
            
            # 处理selectFields
            if "selectFields" in filtered_params["params"]:
                filtered_params["selectFields"] = filtered_params["params"]["selectFields"]
                del filtered_params["params"]["selectFields"]
            
            if "selectFields" not in filtered_params or not filtered_params["selectFields"]:
                filtered_params["selectFields"] = [
                    {"field": "id"}, {"field": "code"}, {"field": "name"}
                ]

            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": "SCM_INV", "modelKey": "SCM_INV$inv_atp_group_md"}
            )
            self.assert_util.assert_response_data(response)
            
            # 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert "id" in result_data and "code" in result_data, "详情查询结果缺少必需字段"
            assert result_data.get("id") == self.__class__.atp_group_id, "ATP组ID不匹配"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.run(order=4)
    @case_decorator(
        story="ATP检查组管理",
        title="测试分页查询ATP检查组列表",
        description="验证ATP检查组分页查询功能，根据编码进行模糊搜索",
        severity="normal",
        order=4,
        tags=["ATP检查组", "分页查询", "SYS_PagingDataService"]
    )
    def test_query_atp_group_paging(self):
        """分页查询ATP检查组列表用例"""
        try:
            api_path = self.get_api_path("(系统)查询分页数据服务")
            params, url = self.get_api_params(api_path)
            
            search_code = self.__class__.atp_group_code if self.__class__.atp_group_code else "AUTOTEST_ATP"
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {
                "pageable": {
                    "pageNo": 1, "pageSize": 20, "needTotal": True,
                    "conditionItems": {
                        "type": "ConditionItems",
                        "conditions": {"code": {"operator": "CONTAINS", "value": search_code}},
                        "logicOperator": "AND"
                    }
                }
            })
            filtered_params["params"]["modelKey"] = "SCM_INV$inv_atp_group_md"
            
            # 处理selectFields
            if "selectFields" in filtered_params["params"]:
                filtered_params["selectFields"] = filtered_params["params"]["selectFields"]
                del filtered_params["params"]["selectFields"]
            
            if "selectFields" not in filtered_params or not filtered_params["selectFields"]:
                filtered_params["selectFields"] = [
                    {"field": "id"}, {"field": "code"}, {"field": "name"}
                ]

            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": "SCM_INV", "modelKey": "SCM_INV$inv_atp_group_md"}
            )
            self.assert_util.assert_response_data(response)
            
            # 验证结果
            result_data = response.get("data", {}).get("data", {})
            assert "data" in result_data and "total" in result_data, "分页查询结果缺少必需字段"
            
            content = result_data.get("data", [])
            if content:
                assert "id" in content[0] and "code" in content[0], "查询结果项缺少必需字段"
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    #@pytest.mark.run(order=5)
    @case_decorator(
        story="ATP检查组管理",
        title="测试删除ATP检查组",
        description="验证ATP检查组删除功能",
        severity="critical",
        order=5,
        tags=["ATP检查组", "删除", "SYS_DeleteDataByIdService"]
    )
    def test_delete_atp_group(self):
        """删除ATP检查组用例"""
        try:
            if not self.__class__.atp_group_id:
                pytest.skip("没有可用的ATP组ID，跳过删除测试")
            
            api_path = self.get_api_path("(系统)删除数据服务")
            params, url = self.get_api_params(api_path)
            
            # 构建请求参数
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            ParamUtil.set_request_params(filtered_params, {"id": self.__class__.atp_group_id})
            filtered_params["params"]["modelKey"] = "SCM_INV$inv_atp_group_md"

            response = self.http.post(
                url, json=filtered_params,
                params={"tmodule": "SCM_INV", "modelKey": "SCM_INV$inv_atp_group_md"}
            )
            
            # 验证删除结果
            assert response.get("success") is True, "删除请求失败"
            
            # 清空类变量
            self.__class__.atp_group_id = None
            self.__class__.atp_group_code = None
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise


