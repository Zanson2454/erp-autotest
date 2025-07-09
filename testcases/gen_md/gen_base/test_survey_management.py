import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("评分管理")
class TestSurveyManagement(GenMdBaseTest):
    """评分管理测试类 - 覆盖评分任务和评分详情相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.survey_mission_id = None
        cls.survey_mission_code = None
        cls.survey_detail_id = None
        cls.survey_detail_code = None
        cls.logger.info("评分管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            tables = ["gen_survey_mission_md", "gen_survey_detail_md"]
            for table in tables:
                try:
                    cls.db.delete(
                        table=table,
                        where="code like %s",
                        params=["AT_%"]
                    )
                except Exception:
                    pass
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 评分任务管理 ================
    @case_decorator(
        story="评分任务管理",
        title="测试创建评分任务",
        description="验证GEN-评分任务-创建评分任务服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["评分任务", "创建", "GEN_SURVEY_MISSION_SAVE_UPDATE_ACTION_SERVICE"]
    )
    def test_create_survey_mission(self):
        """创建评分任务用例 - GEN_SURVEY_MISSION_SAVE_UPDATE_ACTION_SERVICE"""
        try:
            mission_code = self.mock_util.generate_unique_code(tag="MISSION")
            mission_name = f"测试评分任务_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-评分任务-创建评分任务服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "description", "status"], ["params", "request"]
            )
            set_dict = {
                "code": mission_code,
                "name": mission_name,
                "description": f"测试评分任务描述_{self.mock_util.get_timestamp()}",
                "status": "DRAFT"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.survey_mission_id = response.get("data", {}).get("data", {})
            self.survey_mission_code = mission_code

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务管理",
        title="测试发布评分任务",
        description="验证GEN-评分任务-发布评分任务服务功能",
        severity="critical",
        order=2,
        tags=["评分任务", "发布", "GEN_SURVEY_MISSION_RELEASE_ACTION_SERVICE"]
    )
    def test_release_survey_mission(self):
        """发布评分任务用例 - GEN_SURVEY_MISSION_RELEASE_ACTION_SERVICE"""
        try:
            if not self.survey_mission_id:
                self.test_create_survey_mission()

            api_path = self.get_api_path("GEN-评分任务-发布评分任务服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.survey_mission_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务管理",
        title="测试业务人员进行评分",
        description="验证GEN-评分任务-业务人员进行评分服务功能",
        severity="critical",
        order=3,
        tags=["评分任务", "评分", "GEN_SURVEY_SCORE_ACTION_SERVICE"]
    )
    def test_survey_score(self):
        """业务人员进行评分用例 - GEN_SURVEY_SCORE_ACTION_SERVICE"""
        try:
            if not self.survey_mission_id:
                self.test_create_survey_mission()

            api_path = self.get_api_path("GEN-评分任务-业务人员进行评分服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["missionId", "score", "comment"], ["params", "request"]
            )
            set_dict = {
                "missionId": self.survey_mission_id,
                "score": 85,
                "comment": f"测试评分评价_{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 保存评分详情ID
            self.survey_detail_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分详情管理",
        title="测试查询评分详情",
        description="验证GEN-评分详情-查询评分详情服务功能",
        severity="critical",
        order=4,
        tags=["评分详情", "查询", "GEN_SURVEY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_survey_detail(self):
        """查询评分详情用例 - GEN_SURVEY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.survey_detail_id:
                self.test_survey_score()

            api_path = self.get_api_path("GEN-评分详情-查询评分详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.survey_detail_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 评分任务导入导出管理 ================
    @case_decorator(
        story="评分任务导入导出管理",
        title="测试评分任务标准导入",
        description="验证评分任务标准导入服务功能",
        severity="normal",
        order=5,
        tags=["评分任务", "导入", "GEN_SURVEY_MISSION_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_import_survey_mission(self):
        """评分任务标准导入用例 - GEN_SURVEY_MISSION_MD_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("评分任务标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_MISSION"),
                    "name": f"导入测试评分任务_{self.mock_util.get_timestamp()}",
                    "description": "导入测试评分任务描述",
                    "status": "DRAFT"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sliceData"], ["params", "request"]
            )
            set_dict = {"sliceData": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务导入导出管理",
        title="测试评分任务标准导出",
        description="验证评分任务标准导出服务功能",
        severity="normal",
        order=6,
        tags=["评分任务", "导出", "GEN_SURVEY_MISSION_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导出需要复杂配置，暂时跳过")
    def test_export_survey_mission(self):
        """评分任务标准导出用例 - GEN_SURVEY_MISSION_MD_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("评分任务标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务任务管理",
        title="测试评分任务导出任务",
        description="验证评分任务-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=7,
        tags=["评分任务", "任务管理", "GEN_SURVEY_MISSION_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="任务管理接口配置复杂，暂时跳过")
    def test_survey_mission_export_task(self):
        """评分任务导出任务用例 - GEN_SURVEY_MISSION_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("评分任务-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            # 构造导出任务参数
            params = {
                "serviceKey": "GEN_SURVEY_MISSION_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": f"评分任务_{self.nickname}_{self.mock_util.get_timestamp()}_导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_survey_mission_md",
                            "modelName": "评分任务",
                            "sheetNo": 0,
                            "sheetName": "评分任务",
                            "headerConfigList": [
                                {
                                    "name": "任务编码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "任务名称",
                                    "type": "TEXT",
                                    "field": "name"
                                },
                                {
                                    "name": "任务状态",
                                    "type": "TEXT",
                                    "field": "status"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$gen_survey_mission_md",
                        "viewKey": "GEN_MD$gen_survey_mission_md:list",
                        "sceneKey": "GEN_MD$gen_survey_mission_md",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "name"},
                                {"field": "status"}
                            ],
                            "modelKey": "GEN_MD$gen_survey_mission_md"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_survey_mission_md",
                        "modelName": "评分任务",
                        "containerKey": "GEN_MD$gen_survey_mission_md",
                        "viewKey": "GEN_MD$gen_survey_mission_md:list",
                        "sceneKey": "GEN_MD$gen_survey_mission_md"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分任务任务管理",
        title="测试评分任务OSS导入任务",
        description="验证评分任务-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=8,
        tags=["评分任务", "任务管理", "GEN_SURVEY_MISSION_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_survey_mission_oss_import_task(self):
        """评分任务OSS导入任务用例 - GEN_SURVEY_MISSION_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("评分任务-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 构造OSS导入任务参数
            params = {
                "serviceKey": "GEN_SURVEY_MISSION_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "params": {
                    "taskName": f"评分任务_{self.nickname}_{self.mock_util.get_timestamp()}_OSS导入",
                    "fileKey": "test_survey_mission_import.xlsx",
                    "fileName": "评分任务导入模板.xlsx",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_survey_mission_md",
                            "modelName": "评分任务",
                            "sheetNo": 0,
                            "sheetName": "评分任务"
                        }
                    ],
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_survey_mission_md",
                        "modelName": "评分任务"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 评分详情导入导出管理 ================
    @case_decorator(
        story="评分详情导入导出管理",
        title="测试评分详情标准导入",
        description="验证评分详情标准导入服务功能",
        severity="normal",
        order=9,
        tags=["评分详情", "导入", "GEN_SURVEY_DETAIL_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导入需要文件上传，暂时跳过")
    def test_import_survey_detail(self):
        """评分详情标准导入用例 - GEN_SURVEY_DETAIL_MD_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("评分详情标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_DETAIL"),
                    "missionId": self.survey_mission_id,
                    "score": 90,
                    "comment": f"导入测试评分详情_{self.mock_util.get_timestamp()}"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sliceData"], ["params", "request"]
            )
            set_dict = {"sliceData": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分详情导入导出管理",
        title="测试评分详情标准导出",
        description="验证评分详情标准导出服务功能",
        severity="normal",
        order=10,
        tags=["评分详情", "导出", "GEN_SURVEY_DETAIL_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="标准导出需要复杂配置，暂时跳过")
    def test_export_survey_detail(self):
        """评分详情标准导出用例 - GEN_SURVEY_DETAIL_MD_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("评分详情标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "score", "type": "NUMBER"},
                    {"name": "comment", "type": "TEXT"},
                    {"name": "missionId", "type": "TEXT"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分详情任务管理",
        title="测试评分详情导出任务",
        description="验证评分详情-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=11,
        tags=["评分详情", "任务管理", "GEN_SURVEY_DETAIL_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="任务管理接口配置复杂，暂时跳过")
    def test_survey_detail_export_task(self):
        """评分详情导出任务用例 - GEN_SURVEY_DETAIL_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("评分详情-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            # 构造导出任务参数
            params = {
                "serviceKey": "GEN_SURVEY_DETAIL_MD_API_GEI_TASK_EXPORT_DIRECT_POST",
                "teamId": 22,
                "params": {
                    "taskName": f"评分详情_{self.nickname}_{self.mock_util.get_timestamp()}_导出",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_survey_detail_md",
                            "modelName": "评分详情",
                            "sheetNo": 0,
                            "sheetName": "评分详情",
                            "headerConfigList": [
                                {
                                    "name": "详情编码",
                                    "type": "TEXT",
                                    "field": "code"
                                },
                                {
                                    "name": "评分",
                                    "type": "NUMBER",
                                    "field": "score"
                                },
                                {
                                    "name": "评价",
                                    "type": "TEXT",
                                    "field": "comment"
                                }
                            ]
                        }
                    ],
                    "queryData": {
                        "containerKey": "GEN_MD$gen_survey_detail_md",
                        "viewKey": "GEN_MD$gen_survey_detail_md:list",
                        "sceneKey": "GEN_MD$gen_survey_detail_md",
                        "params": {
                            "request": {
                                "pageable": {
                                    "sortOrders": []
                                }
                            },
                            "selectFields": [
                                {"field": "code"},
                                {"field": "score"},
                                {"field": "comment"}
                            ],
                            "modelKey": "GEN_MD$gen_survey_detail_md"
                        }
                    },
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_survey_detail_md",
                        "modelName": "评分详情",
                        "containerKey": "GEN_MD$gen_survey_detail_md",
                        "viewKey": "GEN_MD$gen_survey_detail_md:list",
                        "sceneKey": "GEN_MD$gen_survey_detail_md"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="评分详情任务管理",
        title="测试评分详情OSS导入任务",
        description="验证评分详情-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=12,
        tags=["评分详情", "任务管理", "GEN_SURVEY_DETAIL_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="OSS导入任务需要OSS配置，复杂度较高")
    def test_survey_detail_oss_import_task(self):
        """评分详情OSS导入任务用例 - GEN_SURVEY_DETAIL_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("评分详情-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            # 构造OSS导入任务参数
            params = {
                "serviceKey": "GEN_SURVEY_DETAIL_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST",
                "teamId": 22,
                "params": {
                    "taskName": f"评分详情_{self.nickname}_{self.mock_util.get_timestamp()}_OSS导入",
                    "fileKey": "test_survey_detail_import.xlsx",
                    "fileName": "评分详情导入模板.xlsx",
                    "multiSheetConfig": [
                        {
                            "modelKey": "GEN_MD$gen_survey_detail_md",
                            "modelName": "评分详情",
                            "sheetNo": 0,
                            "sheetName": "评分详情"
                        }
                    ],
                    "processConfig": {
                        "processType": "TRANTOR",
                        "model": "GEN_MD$gen_survey_detail_md",
                        "modelName": "评分详情"
                    }
                }
            }

            response = self.http.post(url, json=params)
            self.assert_util.assert_response_data(response)

            a.json(params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
