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
        cls.survey_mission_head_id = None
        cls.survey_mission_item_id = None
        cls.survey_detail_id = None

        cls.logger.info("评分管理测试类初始化完成")
        
        if cls.md_cache_data:
            cls.cust_template_id = cls.md_cache_data.get("dynamic_form_info", {}).get("dynamic_form_template_md", {}).get("cust_template", [])[0].get("id")
            cls.vend_template_id = cls.md_cache_data.get("dynamic_form_info", {}).get("dynamic_form_template_md", {}).get("vend_template", [])[0].get("id")
            cls.cust_id = cls.md_cache_data.get("partner_info", {}).get("cust_info", [])[0].get("id")
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
           
            cls.db.delete(
                table="gen_survey_detail_md",
                where="survey_mission in (select id from  gen_survey_mission_md where title like %s or title like %s)",
                params=["测试评分任务_%", "自动化_%"]
            )
            cls.db.delete(
                table="gen_survey_mission_item_md",
                where="gen_survey_mission_md_id in  (select id from  gen_survey_mission_md where title like %s or title like %s)",
                params=["测试评分任务_%", "自动化_%"]
            )
            cls.db.delete(
                table="gen_survey_mission_md",
                where="title like %s or title like %s",
                params=["测试评分任务_%", "自动化_%"]
            )
           

            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 评分任务管理 ================
    @case_decorator(
        story="评分任务管理",
        title="测试创建评分任务",
        description="验证GEN-评分任务-创建评分任务服务功能",
        severity="blocker",
        file_level_order=1,
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
                params, ["title", "surveyType", "surveyObj", "startDate", "endDate", "surveyMissionItem"], ["params", "request"]
            )
            set_dict = {
                "missionCode": mission_code,
                "title": mission_name,
                "surveyType": "CUST",
                "surveyObj":self.cust_id,
                "startDate": self.mock_util.get_timestamp(timestamp= True),
                "endDate": self.mock_util.get_timestamp(timestamp=True,day_offset=7),
                "surveyMissionItem": [
                    {
                        "weight": 10,
                        "template":{
                            "id":self.cust_template_id
                        },
                        "user":{
                            "id":self.user_id
                        }   
                    }
                ],
                "surveyObj":{
                    "id":self.cust_id
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.survey_mission_head_id = response.get("data", {}).get("data", {}).get("id")
            
            sql = f"select id from gen_survey_mission_item_md where gen_survey_mission_md_id = {self.survey_mission_head_id}"
            self.survey_mission_item_id = self.db.query(sql)[0].get("id")

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
        file_level_order=2,
        tags=["评分任务", "发布", "GEN_SURVEY_MISSION_RELEASE_ACTION_SERVICE"]
    )
    def test_release_survey_mission(self):
        """发布评分任务用例 - GEN_SURVEY_MISSION_RELEASE_ACTION_SERVICE"""
        try:
            if not self.survey_mission_head_id:
                self.test_create_survey_mission()

            api_path = self.get_api_path("GEN-评分任务-发布评分任务服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.survey_mission_head_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            sql = f"select state from gen_survey_mission_md where id = {self.survey_mission_head_id}"
            state = self.db.query(sql)[0].get("state")
            self.assert_util.assert_by_operator(state, "=", "RELEASED")

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
        file_level_order=3,
        tags=["评分任务", "评分", "GEN_SURVEY_SCORE_ACTION_SERVICE"]
    )
    def test_survey_score(self):
        """业务人员进行评分用例 - GEN_SURVEY_SCORE_ACTION_SERVICE"""
        try:
            if not self.survey_detail_id:
                self.test_query_survey_detail()

            api_path = self.get_api_path("GEN-评分任务-业务人员进行评分服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["missionId", "score", "comment", "surveyRecord", "surveyDate", "type", "user", "template", "surveyObj", "surveyMission", "surveyMissionItem"], ["params", "request"]
            )
            set_dict = {
                "id": self.survey_detail_id,
                "missionId": self.survey_mission_head_id,
                "score": 20,
                "state": "WAIT",
                "surveyRecord":None,
                "surveyDate":self.mock_util.get_timestamp(timestamp=True),
                "type": "CUST",
                "user":{
                    "id":self.user_id
                },
                "template":{
                    "id":self.cust_template_id,
                    "templateInfo":{
                        "header":[
                            {
                                "defaultValue":None,
                                "length":40,
                                "name":"序号",
                                "required":True,
                                "showWay":"ONLY_VIEW",
                                "type":"TextArea",
                                "value":None
                                },
                            {
                                "defaultValue": "-",
                                "length": 40,
                                "name": "客户名称",
                                "required": True,
                                "showWay": "EDITABLE",
                                "type": "TextArea",
                                "value": f"测试客户_{self.mock_util.get_timestamp()}"
                            }
                            ],
                        "body":[
                                {
                                "contentText":"基础信息评估及合作稳定性",
                                "contentType":"TEXT",
                                "formValue":10,
                                "maxScore":10,
                                "type":"score",
                                "u_id":self.mock_util.get_mock_uuid()
                                },
                                {
                                    "contentText":"客户满意度如何",
                                    "formValue":10,
                                    "selectItems":[
                                        {
                                            "label":"不满",
                                            "score":0
                                        },
                                        {
                                            "label":"一般",
                                            "score":2
                                        },
                                        {
                                            "label":"良好",
                                            "score":6
                                        },
                                        {
                                            "label":"满意",
                                            "score":10
                                        }
                                    ],
                                    "type":"select",
                                    "u_id":self.mock_util.get_mock_uuid()
                                },
                                {
                                    "contentText":"客户是否有重大违约记录",
                                    "formValue":0,
                                    "type":"boolean",
                                    "u_id":self.mock_util.get_mock_uuid()
                                },
                                {
                                    "contentText":"客户的 30 天销量",
                                    "formValue":0,
                                    "type":"section",
                                    "u_id":self.mock_util.get_mock_uuid(),
                                    "service":{}
                                }
                        ]
                    },
                "surveyObj":{
                    "id":self.cust_id
                },
                "surveyMission": {
                    "id":self.survey_mission_head_id
                    },
                "surveyMissionItem": {
                        "id": self.survey_mission_item_id
                    }
            }
            }
            
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

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
        file_level_order=4,
        tags=["评分详情", "查询", "GEN_SURVEY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_survey_detail(self):
        """查询评分详情用例 - GEN_SURVEY_DETAIL_ACTION_SERVICE"""
        try:
            if not self.survey_detail_id:
                if not self.survey_mission_head_id:
                    self.test_release_survey_mission()
                sql = f"select id from  gen_survey_detail_md where survey_mission= {self.survey_mission_head_id}"
                self.survey_detail_id = self.db.query(sql)[0].get("id")
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
        file_level_order=5,
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
        file_level_order=6,
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
        file_level_order=7,
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
        file_level_order=8,
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
        file_level_order=9,
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
                    "missionId": self.survey_mission_head_id,
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
        file_level_order=10,
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
        file_level_order=11,
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
        file_level_order=12,
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
