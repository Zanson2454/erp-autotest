import allure
import pytest
from testcases.gen_md import GenMdBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("通用基础数据")
@allure.feature("特征管理")
class TestCharacteristicManagement(GenMdBaseTest):
    """特征管理测试类 - 覆盖特征定义表和特征类定义表相关服务"""

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # 数据存储
        cls.chara_id = None
        cls.chara_class_id = None

        cls.logger.info("特征管理测试类初始化完成")

    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 清理测试数据
            cls.db.delete(
                table="gen_chara_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.db.delete(
                table="gen_chara_class_md",
                where="code like %s",
                params=["AT_%"]
            )
            cls.logger.info("测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")

    # ================ 特征类定义表基础管理 ================
    @case_decorator(
        story="特征类定义表管理",
        title="测试新增特征类定义",
        description="验证GEN-特征类定义表-保存服务功能",
        severity="blocker",
        file_level_order=1,
        smoke=True,
        tags=["特征管理", "新增", "GEN_CHARA_CLASS_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_chara_class(self):
        """新增特征类定义用例 - GEN_CHARA_CLASS_MD_SAVE_ACTION_SERVICE"""
        try:
            chara_class_code = self.mock_util.generate_unique_code(tag="CHARACLASS")
            chara_class_name = f"测试特征类_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-特征类定义表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "charaClassType", "charaList", "remark"], ["params", "request"]
            )
            set_dict = {
                "code": chara_class_code,
                "name": chara_class_name,
                "charaClassType":"BATCH",
                "charaList":[
                    {"charaId":{"id":self.chara_id},
                     "isRequired":True
                     }
                ],
                "remark": f"测试特征类描述_{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.chara_class_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试查询特征类定义分页列表",
        description="验证GEN-特征类定义表-查询分页服务功能",
        severity="normal",
        file_level_order=2,
        tags=["特征管理", "查询", "GEN_CHARA_CLASS_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_characteristic_class_page(self):
        """查询特征类定义分页列表用例"""
        try:
            api_path = self.get_api_path("GEN-特征类定义表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields", "systemParams"], ["params", "request"]
            )
            set_dict = {
                    "pageable": {
                        "pageNo": 1,
                        "pageSize": 20,
                        "needTotal": True,
                        "sortOrders": None,
                        "conditionItems": None
                    },
                    "fields": [
                        {
                            "name": "name",
                            "type": "TEXT"
                        },
                        {
                            "name": "code",
                            "type": "TEXT"
                        },
                        {
                            "name": "charaClassType",
                            "type": "SELECT"
                        }
                    ],
                    "systemParams": None
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
        story="特征类定义表管理",
        title="测试查询特征类定义详情",
        description="验证GEN-特征类定义表-查询详情服务功能",
        severity="normal",
        file_level_order=3,
        tags=["特征管理", "查询", "GEN_CHARA_CLASS_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_chara_class_detail(self):
        """查询特征类定义详情用例"""
        try:
            if not self.chara_class_id:
                self.test_save_chara_class()

            api_path = self.get_api_path("GEN-特征类定义表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_class_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试启用特征类定义",
        description="验证GEN-特征类定义表-启用服务功能",
        severity="normal",
        file_level_order=4,
        tags=["特征管理", "启用", "GEN_CHARA_CLASS_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_characteristic_class(self):
        """启用特征类定义用例"""
        try:
            if not self.chara_class_id:
                self.test_save_chara_class()

            api_path = self.get_api_path("GEN-特征类定义表-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_class_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试禁用特征类定义",
        description="验证GEN-特征类定义表-禁用服务功能",
        severity="normal",
        file_level_order=5,
        tags=["特征管理", "禁用", "GEN_CHARA_CLASS_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_characteristic_class(self):
        """禁用特征类定义用例"""
        try:
            if not self.chara_class_id:
                self.test_save_chara_class()

            api_path = self.get_api_path("GEN-特征类定义表-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_class_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征类定义表管理",
        title="测试删除特征类定义",
        description="验证GEN-特征类定义表-删除服务功能",
        severity="critical",
        file_level_order=6,
        tags=["特征管理", "删除", "GEN_CHARA_CLASS_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_characteristic_class(self):
        """删除特征类定义用例"""
        try:
            # 先创建一个测试数据用于删除
            if not self.chara_class_id:
                self.test_save_chara_class()

            # 删除特征类
            api_path = self.get_api_path("GEN-特征类定义表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_class_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 特征定义表基础管理 ================
    @case_decorator(
        story="特征定义表管理",
        title="测试新增特征定义",
        description="验证GEN-特征定义表-保存服务功能",
        severity="blocker",
        file_level_order=7,
        smoke=True,
        tags=["特征管理", "新增", "GEN_CHARA_MD_SAVE_ACTION_SERVICE"]
    )
    def test_save_chara(self):
        """新增特征定义用例 - GEN_CHARA_MD_SAVE_ACTION_SERVICE"""
        try:
            # 确保有特征类
            chara_code = self.mock_util.generate_unique_code(tag="CHARA")
            chara_name = f"测试特征_{self.mock_util.get_timestamp()}"

            api_path = self.get_api_path("GEN-特征定义表-保存服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["code", "name", "charaClassId", "dataType", "charNo", "isCustom", "isRequired", "isSingleValue", "remark", "presetValues"], ["params", "request"]
            )
            set_dict = {
                "code": chara_code,
                "name": chara_name,
                "dataType":"STRING",
                "charNo":40,
                "isCustom":False,
                "isRequired":False,
                "isSingleValue":True,
                "remark":f"测试特征描述_{self.mock_util.get_timestamp()}",
                "presetValues":[
                    {
                        "value": f"特征1_{self.mock_util.get_timestamp()}",
                        "defaultRelv": False
                    },
                    {
                        "value": f"特征2_{self.mock_util.get_timestamp()}",
                        "defaultRelv": True
                    } 
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            self.chara_id = response.get("data", {}).get("data", {})

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试查询特征定义分页列表",
        description="验证GEN-特征定义表-查询分页服务功能",
        severity="normal",
        file_level_order=8,
        tags=["特征管理", "查询", "GEN_CHARA_MD_QUERY_PAGE_ACTION_SERVICE"]
    )
    def test_query_characteristic_page(self):
        """查询特征定义分页列表用例"""
        try:
            api_path = self.get_api_path("GEN-特征定义表-查询分页服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"], ["params", "request"]
            )
            set_dict = {
                "pageable": {"pageNo": 1, "pageSize": 20}
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
        story="特征定义表管理",
        title="测试查询特征定义详情",
        description="验证GEN-特征定义表-查询详情服务功能",
        severity="normal",
        file_level_order=9,
        tags=["特征管理", "查询", "GEN_CHARA_MD_QUERY_DETAIL_ACTION_SERVICE"]
    )
    def test_query_characteristic_detail(self):
        """查询特征定义详情用例"""
        try:
            if not self.chara_id:
                self.test_save_chara()

            api_path = self.get_api_path("GEN-特征定义表-查询详情服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试启用特征定义",
        description="验证GEN-特征定义表-启用服务功能",
        severity="normal",
        file_level_order=10,
        tags=["特征管理", "启用", "GEN_CHARA_MD_ENABLED_ACTION_SERVICE"]
    )
    def test_enable_characteristic(self):
        """启用特征定义用例"""
        try:
            if not self.chara_id:
                self.test_save_chara()

            api_path = self.get_api_path("GEN-特征定义表-启用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试禁用特征定义",
        description="验证GEN-特征定义表-禁用服务功能",
        severity="normal",
        file_level_order=11,
        tags=["特征管理", "禁用", "GEN_CHARA_MD_DISABLED_ACTION_SERVICE"]
    )
    def test_disable_characteristic(self):
        """禁用特征定义用例"""
        try:
            if not self.chara_id:
                self.test_save_chara()

            api_path = self.get_api_path("GEN-特征定义表-禁用服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @case_decorator(
        story="特征定义表管理",
        title="测试删除特征定义",
        description="验证GEN-特征定义表-删除服务功能",
        severity="critical",
        file_level_order=12,
        tags=["特征管理", "删除", "GEN_CHARA_MD_DELETE_ACTION_SERVICE"]
    )
    def test_delete_characteristic(self):
        """删除特征定义用例"""
        try:
            # 确保有特征类
            if not self.chara_id:
                self.test_save_chara()

            # 删除特征
            api_path = self.get_api_path("GEN-特征定义表-删除服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"], ["params", "request"]
            )
            set_dict = {"id": self.chara_id}
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    # ================ 特征类定义表导入导出管理 ================
    @case_decorator(
        story="特征类定义表导入导出管理",
        title="测试特征类定义表标准导入",
        description="验证特征类定义表标准导入服务功能",
        severity="normal",
        file_level_order=13,
        tags=["特征管理", "导入", "GEN_CHARA_CLASS_MD_GEI_IMPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_import(self):
        """特征类定义表标准导入用例"""
        try:
            api_path = self.get_api_path("特征类定义表标准导入服务")
            params, url = self.get_api_params(api_path)

            import_data = [
                {
                    "code": self.mock_util.generate_unique_code(tag="IMPORT_CHARACLASS"),
                    "name": f"导入测试特征类_{self.mock_util.get_timestamp()}",
                    "description": "导入测试特征类描述"
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
        story="特征类定义表导入导出管理",
        title="测试特征类定义表标准导出",
        description="验证特征类定义表标准导出服务功能",
        severity="normal",
        file_level_order=14,
        tags=["特征管理", "导出", "GEN_CHARA_CLASS_MD_GEI_EXPORT_SERVICE"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_export(self):
        """特征类定义表标准导出用例"""
        try:
            api_path = self.get_api_path("特征类定义表标准导出服务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["selectFields"], ["params", "request"]
            )
            set_dict = {
                "selectFields": [
                    {"name": "code", "type": "TEXT"},
                    {"name": "name", "type": "TEXT"},
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
        story="特征类定义表任务管理",
        title="测试特征类定义表OSS导入任务",
        description="验证特征类定义表-导入导出任务管理接口-通过OSS提交导入任务功能",
        severity="normal",
        file_level_order=15,
        tags=["特征管理", "任务管理", "GEN_CHARA_CLASS_MD_API_GEI_TASK_IMPORT_DIRECT_BY_OSS_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_oss_import_task(self):
        """特征类定义表OSS导入任务用例"""
        try:
            api_path = self.get_api_path("特征类定义表-导入导出任务管理接口-通过OSS提交导入任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ossPath", "taskName"], ["params", "request"]
            )
            set_dict = {
                "ossPath": "/test/characteristic_class_import.xlsx",
                "taskName": f"特征类定义表导入任务_{self.mock_util.get_timestamp()}"
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
        story="特征类定义表任务管理",
        title="测试特征类定义表导出任务",
        description="验证特征类定义表-导入导出任务管理接口-提交导出任务功能",
        severity="normal",
        file_level_order=16,
        tags=["特征管理", "任务管理", "GEN_CHARA_CLASS_MD_API_GEI_TASK_EXPORT_DIRECT_POST"]
    )
    @pytest.mark.skip(reason="业务用不上")
    def test_characteristic_class_export_task(self):
        """特征类定义表导出任务用例"""
        try:
            api_path = self.get_api_path("特征类定义表-导入导出任务管理接口-提交导出任务")
            params, url = self.get_api_params(api_path)

            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["exportConfig", "taskName"], ["params", "request"]
            )
            set_dict = {
                "exportConfig": {
                    "fields": [
                        {"name": "code", "type": "TEXT"},
                        {"name": "name", "type": "TEXT"},
                        {"name": "description", "type": "TEXT"}
                    ],
                    "condition": {}
                },
                "taskName": f"特征类定义表导出任务_{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)

            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)

            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")

        except Exception as e:
            a.text(str(e), "失败原因")
            raise
