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
        cls.logger.info("动态表单管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="gen_dynamic_form_template_md",
                where="name like %s",
                params=["测试动态表单模板_%"]
            )
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
            template_name = f"测试动态表单模板_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-动态表单-创建修改动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "templateType", "formConfig", "description"], ["params", "request"]
            )
            set_dict = {
                "desc": template_name,
                "name": template_name,
                "templateType": "gen_cust_dynamic_form_record_md",  # 模板类型：表单
                "templateInfo": {  # 表单配置
                    "header":[
                        {
                            "defaultValue": "正常",
                            "index": None,
                            "length": "40",
                            "name": "序号",
                            "required": "TRUE",
                            "showWay": "ONLY_VIEW",
                            "type": "TextArea"
                        },
                        {
                            "defaultValue": "-",
                            "index": None,
                            "length": "40",
                            "name": "客户名称",
                            "required": "TRUE",
                            "showWay": "EDITABLE",
                            "type": "TextArea"
                        }
                    ],
                    "body":[
                        {
                            "title": "问题组 1",
                            "u_id": self.mock_util.get_mock_uuid(),
                            "items": [
                                {
                                    "maxScore": 10,
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"score",
                                    "contentText": "基础信息评估及合作稳定性"
                                },
                                {
                                    "selectItems": [
                                        {
                                            "label": "不满",
                                            "score": 0
                                        },
                                        {
                                            "label": "一般",
                                            "score": 5
                                        },
                                        {
                                            "label": "满意",
                                            "score": 10
                                        }
                                    ],
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"select",
                                    "contentText": "客户满意度如何"
                                },
                                {
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"boolean",
                                    "contentText": "客户是否有重大违约记录"
                                },
                                {
                                    "service": {
                                        "label": "30天销量",
                                        "sectionItems": [],
                                        "service": {}
                                    },
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"section",
                                    "contentText": "客户的 30 天销量"
                                }
                            ]
                        }
                    ]    
                    
                },
                "description": f"测试动态表单模板描述_{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.template_id = response.get("data", {}).get("data", {}).get("id")

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
    @pytest.mark.skip(reason="dynamic_form场景,业务用不上")
    def test_create_dynamic_form_template(self):
        """创建修改动态表单模板用例 - GEN_CREATE_DYNAMIC_FORM_TEMPLATE_SERVICE"""
        try:
            template_name = f"备用动态表单模板_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-创建修改动态表单模板")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "templateConfig", "status"], ["params", "request"]
            )
            set_dict ={
                "desc": template_name,
                "name": template_name,
                "templateType": "gen_cust_dynamic_form_record_md",  # 模板类型：表单
                "templateInfo": {  # 表单配置
                    "header":[
                        {
                            "defaultValue": "正常",
                            "index": None,
                            "length": "40",
                            "name": "序号",
                            "required": "TRUE",
                            "showWay": "ONLY_VIEW",
                            "type": "TextArea"
                        },
                        {
                            "defaultValue": "-",
                            "index": None,
                            "length": "40",
                            "name": "客户名称",
                            "required": "TRUE",
                            "showWay": "EDITABLE",
                            "type": "TextArea"
                        }
                    ],
                    "body":[
                        {
                            "title": "问题组 1",
                            "u_id": self.mock_util.get_mock_uuid(),
                            "items": [
                                {
                                    "maxScore": 10,
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"score",
                                    "contentText": "基础信息评估及合作稳定性"
                                },
                                {
                                    "selectItems": [
                                        {
                                            "label": "不满",
                                            "score": 0
                                        },
                                        {
                                            "label": "一般",
                                            "score": 5
                                        },
                                        {
                                            "label": "满意",
                                            "score": 10
                                        }
                                    ],
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"select",
                                    "contentText": "客户满意度如何"
                                },
                                {
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"boolean",
                                    "contentText": "客户是否有重大违约记录"
                                },
                                {
                                    "service": {
                                        "label": "30天销量",
                                        "sectionItems": [],
                                        "service": {}
                                    },
                                    "u_id": self.mock_util.get_mock_uuid(),
                                    "type":"section",
                                    "contentText": "客户的 30 天销量"
                                }
                            ]
                        }
                    ]    
                    
                },
                "description": f"测试动态表单模板描述_{self.mock_util.get_timestamp()}"
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
                params, ["templateType", "state", "pageable"], ["params", "request"]
            )
            set_dict =  {
                "templateType": "gen_cust_dynamic_form_record_md",
                "state": "ENABLED",
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "conditionGroup": None,
                    "sortOrders": None,
                    "keyword": None
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
            if not self.template_id:
                self.test_create_template()

            api_path = self.get_api_path("GEN-动态表单-根据ids查询动态表单模板集合服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"], ["params", "request"]
            )
            set_dict = {"ids": [self.template_id]}  # 最多查询5个
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
            self.assert_util.assert_response_success(response)

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
                self.test_enable_template()

            api_path = self.get_api_path("GEN-动态表单-禁用动态表单模板服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

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
            self.assert_util.assert_response_success(response)

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
