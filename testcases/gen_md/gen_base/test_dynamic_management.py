import allure
import pytest
from typing import Any
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("动态表单管理")
class TestDynamicManagement(GenMdBaseTest):
    """动态表单管理测试类 - 覆盖所有动态表单相关服务"""
    
    # 类型提示：继承的动态属性
    assert_util: Any

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.template_id = None
        cls.template_code = None
        cls.template_ids = []  # 批量ID存储
        cls.logger.info("动态表单管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            tables = ["gen_dynamic_form_template_md"]
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

    # ================ 动态表单基础管理 ================
    @case_decorator(
        story="动态表单管理",
        title="测试创建动态表单模板",
        description="验证GEN-动态表单-创建修改动态表单模板服务功能",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["动态表单", "创建", "GEN_DYNAMIC_CREATE_UPDATE_TEMPLATE_SERVICE"]
    )
    def test_create_template(self):
        """创建动态表单模板用例 - GEN_DYNAMIC_CREATE_UPDATE_TEMPLATE_SERVICE"""
        try:
            template_code = self.mock_util.generate_unique_code(tag="DYNAMIC")
            template_name = f"测试动态表单模板_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-动态表单-创建修改动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "templateType", "formConfig", "description"], ["params", "request"]
            )
            set_dict = {
                "code": template_code,
                "name": template_name,
                "templateType": "FORM",  # 模板类型：表单
                "formConfig": {  # 表单配置
                    "fields": [
                        {
                            "fieldName": "testField",
                            "fieldType": "INPUT",
                            "fieldLabel": "测试字段",
                            "required": True
                        }
                    ]
                },
                "description": f"测试动态表单模板描述_{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.template_id = response.get("data", {}).get("data", {})
            self.template_code = template_code
            self.template_ids.append(self.template_id)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试创建修改动态表单模板（备用服务）",
        description="验证GEN-创建修改动态表单模板服务功能",
        severity="normal",
        order=2,
        tags=["动态表单", "创建修改", "GEN_CREATE_DYNAMIC_FORM_TEMPLATE_SERVICE"]
    )
    def test_create_dynamic_form_template(self):
        """创建修改动态表单模板用例 - GEN_CREATE_DYNAMIC_FORM_TEMPLATE_SERVICE"""
        try:
            template_code = self.mock_util.generate_unique_code(tag="DYN_FORM")
            template_name = f"备用动态表单模板_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-创建修改动态表单模板")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "templateConfig", "status"], ["params", "request"]
            )
            set_dict = {
                "code": template_code,
                "name": template_name,
                "templateConfig": {
                    "layout": "vertical",
                    "columns": 2,
                    "fields": []
                },
                "status": "DRAFT"  # 状态：草稿
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 保存额外的模板ID
            backup_template_id = response.get("data", {}).get("data", {})
            if backup_template_id:
                self.template_ids.append(backup_template_id)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试分页查询动态表单模板",
        description="验证GEN-动态表单-分页查询动态表单模板服务功能",
        severity="normal",
        order=3,
        tags=["动态表单", "查询", "GEN_DYNAMIC_PAGING_TEMPLATE_SERVICE"]
    )
    def test_paging_template(self):
        """分页查询动态表单模板用例 - GEN_DYNAMIC_PAGING_TEMPLATE_SERVICE"""
        try:
            api_path = self.get_api_path("GEN-动态表单-分页查询动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20, "needTotal": True},
                "fields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "templateType", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
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
        story="动态表单管理",
        title="测试根据ID查询动态表单模板",
        description="验证GEN-动态表单-根据id查询动态表单模板服务功能",
        severity="normal",
        order=4,
        tags=["动态表单", "查询", "GEN_DYNAMIC_FIND_BY_ID_TEMPLATE_SERVICE"]
    )
    def test_find_by_id_template(self):
        """根据ID查询动态表单模板用例 - GEN_DYNAMIC_FIND_BY_ID_TEMPLATE_SERVICE"""
        try:
            if not self.template_id:
                self.test_create_template()

            api_path = self.get_api_path("GEN-动态表单-根据id查询动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的详情数据包含必要字段
            template_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(template_data.get("code"), "not_empty")
            self.assert_util.assert_by_operator(template_data.get("name"), "not_empty")

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试根据IDs查询动态表单模板集合",
        description="验证GEN-动态表单-根据ids查询动态表单模板集合服务功能",
        severity="normal",
        order=5,
        tags=["动态表单", "批量查询", "GEN_DYNAMIC_FIND_BY_IDS_TEMPLATE_SERVICE"]
    )
    def test_find_by_ids_template(self):
        """根据IDs查询动态表单模板集合用例 - GEN_DYNAMIC_FIND_BY_IDS_TEMPLATE_SERVICE"""
        try:
            if not self.template_ids:
                self.test_create_template()

            api_path = self.get_api_path("GEN-动态表单-根据ids查询动态表单模板集合服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": self.template_ids[:5]}  # 最多查询5个
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            # 验证返回的集合数据
            templates_data = response.get("data", {}).get("data", [])
            if templates_data:
                self.assert_util.assert_by_operator(len(templates_data), ">", 0)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试启用动态表单模板",
        description="验证GEN-动态表单-启用动态表单模板服务功能",
        severity="normal",
        order=6,
        tags=["动态表单", "启用", "GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE"]
    )
    def test_enable_template(self):
        """启用动态表单模板用例 - GEN_DYNAMIC_ENABLE_TEMPLATE_SERVICE"""
        try:
            if not self.template_id:
                self.test_create_template()

            api_path = self.get_api_path("GEN-动态表单-启用动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试禁用动态表单模板",
        description="验证GEN-动态表单-禁用动态表单模板服务功能",
        severity="normal",
        order=7,
        tags=["动态表单", "禁用", "GEN_DYNAMIC_DISABLE_TEMPLATE_SERVICE"]
    )
    def test_disable_template(self):
        """禁用动态表单模板用例 - GEN_DYNAMIC_DISABLE_TEMPLATE_SERVICE"""
        try:
            if not self.template_id:
                self.test_create_template()

            api_path = self.get_api_path("GEN-动态表单-禁用动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单管理",
        title="测试删除动态表单模板",
        description="验证GEN-动态表单-删除动态表单模板服务功能",
        severity="critical",
        order=8,
        tags=["动态表单", "删除", "GEN_DYNAMIC_DELETE_TEMPLATE_SERVICE"]
    )
    def test_delete_template(self):
        """删除动态表单模板用例 - GEN_DYNAMIC_DELETE_TEMPLATE_SERVICE"""
        try:
            if not self.template_id:
                self.test_create_template()

            api_path = self.get_api_path("GEN-动态表单-删除动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 动态表单导入导出管理 ================
    @case_decorator(
        story="动态表单导入导出管理",
        title="测试动态表单模板标准导入",
        description="验证动态表单模板类标准导入服务功能",
        severity="normal",
        order=9,
        tags=["动态表单", "导入", "GEN_DYNAMIC_FORM_TEMPLATE_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_import(self):
        """动态表单模板标准导入用例 - GEN_DYNAMIC_FORM_TEMPLATE_MD_GEI_IMPORT_SERVICE"""
        try:
            api_path = self.get_api_path("动态表单模板类标准导入服务")
            params, url = self.get_api_params(api_path)

            # 构建导入数据
            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_DYN"),
                    "name": f"导入测试动态表单模板_{self.mock_util.get_timestamp()}",
                    "templateType": "FORM",
                    "formConfig": {
                        "fields": [
                            {
                                "fieldName": "importField",
                                "fieldType": "INPUT",
                                "fieldLabel": "导入字段"
                            }
                        ]
                    },
                    "description": "导入的动态表单模板描述"
                }
            ]

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["data"], ["params", "request"]
            )
            set_dict = {"data": import_data}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="动态表单导入导出管理",
        title="测试动态表单模板标准导出",
        description="验证动态表单模板类标准导出服务功能",
        severity="normal",
        order=10,
        tags=["动态表单", "导出", "GEN_DYNAMIC_FORM_TEMPLATE_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_export(self):
        """动态表单模板标准导出用例 - GEN_DYNAMIC_FORM_TEMPLATE_MD_GEI_EXPORT_SERVICE"""
        try:
            api_path = self.get_api_path("动态表单模板类标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
                    {"name": "templateType", "type": "TEXT"},
                    {"name": "status", "type": "TEXT"},
                    {"name": "description", "type": "TEXT"}
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
        story="动态表单任务管理",
        title="测试动态表单模板OSS导入任务",
        description="验证动态表单模板类-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        order=11,
        tags=["动态表单", "任务管理", "GEN_DYNAMIC_FORM_TEMPLATE_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_oss_import_task(self):
        """动态表单模板OSS导入任务用例 - GEN_DYNAMIC_FORM_TEMPLATE_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"""
        try:
            api_path = self.get_api_path("动态表单模板类-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["fileKey", "taskName", "templateId"], ["params", "request"]
            )
            set_dict = {
                "fileKey": "test_dynamic_template_import_file.xlsx",
                "taskName": f"动态表单模板导入任务_{self.mock_util.get_timestamp()}",
                "templateId": 1
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
        story="动态表单任务管理",
        title="测试动态表单模板导出任务",
        description="验证动态表单模板类-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        order=12,
        tags=["动态表单", "任务管理", "GEN_DYNAMIC_FORM_TEMPLATE_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_template_export_task(self):
        """动态表单模板导出任务用例 - GEN_DYNAMIC_FORM_TEMPLATE_MD_API_GEI_TASK_EXPORT_DIRECT_POST"""
        try:
            api_path = self.get_api_path("动态表单模板类-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["taskName", "queryData"], ["params", "request"]
            )
            set_dict = {
                "taskName": f"动态表单模板导出任务_{self.mock_util.get_timestamp()}",
                "queryData": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "templateType", "type": "TEXT"},
                        {"name": "status", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ]
                }
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
