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
        cls.survey_detail_id = None
        cls.logger.info("评分管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.db.delete(
                table="gen_survey_mission_md",
                where="mission_code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_survey_detail_md",
                where="detail_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

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
        """创建评分任务用例"""
        try:
            mission_code = self.mock_util.generate_unique_code(tag="MISSION")
            mission_name = f"测试评分任务_{self.mock_util.get_timestamp()}"

            set_dict = {
                "missionCode": mission_code,
                "missionName": mission_name,
                "remark": f"评分任务描述_{self.mock_util.get_timestamp()}",
                "recipients": [
                    {
                        "userId": self.user_id,
                        "userName": self.nickname
                    }
                ]
            }
            
            response, survey_mission_id = self.standard_api_call(
                api_key="GEN-评分任务-创建评分任务服务",
                set_dict=set_dict,
                fields_to_filter=["missionCode", "missionName", "remark", "recipients"],
                store_id_as="survey_mission"
            )

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
        """发布评分任务用例"""
        try:
            if not self.survey_mission_id:
                self.test_create_survey_mission()

            set_dict = {"missionId": self.survey_mission_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-评分任务-发布评分任务服务",
                set_dict=set_dict,
                fields_to_filter=["missionId"],
                store_id_as=None
            )

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
        """业务人员进行评分用例"""
        try:
            if not self.survey_mission_id:
                self.test_create_survey_mission()

            set_dict = {
                "missionId": self.survey_mission_id,
                "userId": self.user_id,
                "scores": {
                    "question1": 4,
                    "question2": 5,
                    "feedback": "测试评分反馈"
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="GEN-评分任务-业务人员进行评分服务",
                set_dict=set_dict,
                fields_to_filter=["missionId", "userId", "scores"],
                store_id_as=None
            )

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
        """查询评分详情用例"""
        try:
            if not self.survey_mission_id:
                self.test_create_survey_mission()

            set_dict = {"missionId": self.survey_mission_id}
            
            response, _ = self.standard_api_call(
                api_key="GEN-评分详情-查询评分详情服务",
                set_dict=set_dict,
                fields_to_filter=["missionId"],
                store_id_as=None
            )

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
        """评分任务标准导入用例"""
        try:
            import_data = [
                {
                    "missionCode": self.mock_util.generate_unique_code(tag="IMPORT_MISSION"),
                    "missionName": f"导入测试评分任务_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试评分任务描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="评分任务标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

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
        """评分任务标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "missionCode", "type": "TEXT"},
                    {"name": "missionName", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="评分任务标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

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
        """评分任务导出任务用例"""
        try:
            set_dict = {
                "taskName": f"评分任务导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "missionCode", "type": "TEXT"},
                        {"name": "missionName", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="评分任务-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

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
        """评分任务OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_survey_mission_import.xlsx",
                "taskName": f"评分任务导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="评分任务-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

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
        """评分详情标准导入用例"""
        try:
            import_data = [
                {
                    "detailCode": self.mock_util.generate_unique_code(tag="IMPORT_DETAIL"),
                    "detailName": f"导入测试评分详情_{self.mock_util.get_timestamp()}",
                    "remark": "导入测试评分详情描述"
                }
            ]

            set_dict = {"data": import_data}
            
            response, _ = self.standard_api_call(
                api_key="评分详情标准导入服务",
                set_dict=set_dict,
                fields_to_filter=["data"],
                store_id_as=None
            )

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
        """评分详情标准导出用例"""
        try:
            set_dict = {
                "selectFields": [
                    {"name": "detailCode", "type": "TEXT"},
                    {"name": "detailName", "type": "TEXT"},
                    {"name": "remark", "type": "TEXT"}
                ]
            }
            
            response, _ = self.standard_api_call(
                api_key="评分详情标准导出服务",
                set_dict=set_dict,
                fields_to_filter=["selectFields"],
                store_id_as=None
            )

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
        """评分详情导出任务用例"""
        try:
            set_dict = {
                "taskName": f"评分详情导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "detailCode", "type": "TEXT"},
                        {"name": "detailName", "type": "TEXT"},
                        {"name": "remark", "type": "TEXT"}
                    ]
                }
            }
            
            response, _ = self.standard_api_call(
                api_key="评分详情-导入导出任务管理接口-提交导出任务",
                set_dict=set_dict,
                fields_to_filter=["taskName", "queryData"],
                store_id_as=None
            )

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
        """评分详情OSS导入任务用例"""
        try:
            set_dict = {
                "fileKey": "test_survey_detail_import.xlsx",
                "taskName": f"评分详情导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
            }
            
            response, _ = self.standard_api_call(
                api_key="评分详情-导入导出任务管理接口-通过OSS提交导入任务",
                set_dict=set_dict,
                fields_to_filter=["fileKey", "taskName", "templateId"],
                store_id_as=None
            )

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
