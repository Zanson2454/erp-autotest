import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator

@allure.epic("系统通用模块")
@allure.feature("导入导出模板管理")
class TestGeiTemplateManagement(SysCommonBaseTest):
    """导入导出模板管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.gei_template_id = None
        cls.logger.info("导入导出模板管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.gei_template_id:
                cls.db.delete(
                    table="gei_template",
                    where="id = %s",
                    params=[cls.gei_template_id]
                )
            cls.db.delete(
                table="gei_template",
                where="template_name like %s",
                params=["AT_%"]
            )
            cls.logger.info("导入导出模板测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试保存模板",
        description="验证API_GEI_TEMPLATE_SAVE_POST功能 - 保存模板",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "gei", "template", "save"]
    )
    def test_template_save_post(self):
        """测试保存模板 - API_GEI_TEMPLATE_SAVE_POST"""
        try:
            template_name = f"AT_TEMPLATE_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("导入导出模版管理接口-保存模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["templateName", "headerConfigList"],
                ["params"]
            )
            set_dict = {
                "templateName": template_name,
                "headerConfigList": [
                    {"name": "字段1", "type": "TEXT", "field": "field1"}
                ]
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            template_data = response.get("data", {}).get("data", {})
            self.gei_template_id = template_data.get("id") if template_data else None
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试复制模板",
        description="验证API_GEI_TEMPLATE_COPY_POST功能 - 复制模板",
        severity="normal",
        order=2,
        tags=["sys_common", "gei", "template", "copy"]
    )
    def test_template_copy_post(self):
        """测试复制模板 - API_GEI_TEMPLATE_COPY_POST"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-复制模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["sourceId", "newName"], ["params"])
            set_dict = {
                "sourceId": self.gei_template_id,
                "newName": f"AT_COPY_TEMPLATE_{self.mock_util.get_timestamp()}"
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @pytest.mark.skip(reason="标准导入导出业务未引用，暂时跳过")
    @case_decorator(
        story="导入导出模板管理",
        title="测试导入模板",
        description="验证API_GEI_TEMPLATE_IMPORT_POST功能 - 导入模板（跳过）",
        severity="normal",
        order=13,
        tags=["sys_common", "gei", "template", "import"]
    )
    def test_template_import_post(self):
        """测试导入模板 - API_GEI_TEMPLATE_IMPORT_POST (跳过)"""
        try:
            pass
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试导出模板",
        description="验证API_GEI_TEMPLATE_EXPORT_POST功能 - 导出模板",
        severity="normal",
        order=10,
        tags=["sys_common", "gei", "template", "export"]
    )
    def test_template_export_post(self):
        """测试导出模板 - API_GEI_TEMPLATE_EXPORT_POST"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-导出")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["templateId"], ["params"])
            set_dict = {"templateId": self.gei_template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试分页查询模板",
        description="验证API_GEI_TEMPLATE_PAGING_POST功能 - 分页查询模板",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["sys_common", "gei", "template", "paging"]
    )
    def test_template_paging_post(self):
        """测试分页查询模板 - API_GEI_TEMPLATE_PAGING_POST"""
        try:
            api_path = self.get_api_path("导入导出模版管理接口-分页查询模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable"],
                ["params", "request"]
            )
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
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
        story="导入导出模板管理",
        title="测试根据ID查询模板",
        description="验证API_GEI_TEMPLATE_QUERY_BY_ID_POST功能 - 查询模板详情",
        severity="normal",
        order=5,
        tags=["sys_common", "gei", "template", "query"]
    )
    def test_template_query_by_id_post(self):
        """测试根据ID查询模板 - API_GEI_TEMPLATE_QUERY_BY_ID_POST"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-根据id查询模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params"])
            set_dict = {"id": self.gei_template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            template_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(template_data.get("id"), "=", self.gei_template_id)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试启用模板",
        description="验证API_GEI_TEMPLATE_ENABLE_POST功能 - 启用模板",
        severity="normal",
        order=7,
        tags=["sys_common", "gei", "template", "enable"]
    )
    def test_template_enable_post(self):
        """测试启用模板 - API_GEI_TEMPLATE_ENABLE_POST"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-启用模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params"])
            set_dict = {"id": self.gei_template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试停用模板",
        description="验证API_GEI_TEMPLATE_DISABLE_POST功能 - 停用模板",
        severity="normal",
        order=8,
        tags=["sys_common", "gei", "template", "disable"]
    )
    def test_template_disable_post(self):
        """测试停用模板 - API_GEI_TEMPLATE_DISABLE_POST"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-停用模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params"])
            set_dict = {"id": self.gei_template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试删除模板",
        description="验证API_GEI_TEMPLATE_DELETE_POST功能 - 删除模板",
        severity="normal",
        order=16,
        tags=["sys_common", "gei", "template", "delete"]
    )
    def test_template_delete_post(self):
        """测试删除模板 - API_GEI_TEMPLATE_DELETE_POST"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-删除模版")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(params, ["id"], ["params"])
            set_dict = {"id": self.gei_template_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            self.gei_template_id = None
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试模板文件下载",
        description="验证API_GEI_TEMPLATE_DOWNLOAD_GET功能 - 下载模板文件",
        severity="normal",
        order=11,
        tags=["sys_common", "gei", "template", "download"]
    )
    def test_template_download_get(self):
        """测试模板文件下载 - API_GEI_TEMPLATE_DOWNLOAD_GET"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-模版文件下载")
            url = self.get_api_url(api_path)
            params = {"templateId": self.gei_template_id}
            response = self.http.get(url, params=params)
            self.assert_util.assert_response_success(response)
            
            a.text(f"下载URL: {url}", "下载链接")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试模板文件下载V2",
        description="验证API_GEI_TEMPLATE_DOWNLOAD_V2_GET功能 - V2下载",
        severity="minor",
        order=12,
        tags=["sys_common", "gei", "template", "download_v2"]
    )
    def test_template_download_v2_get(self):
        """测试模板文件下载V2 - API_GEI_TEMPLATE_DOWNLOAD_V2_GET"""
        try:
            if not self.gei_template_id:
                self.test_template_save_post()
            
            api_path = self.get_api_path("导入导出模版管理接口-模版文件下载V2")
            url = self.get_api_url(api_path)
            params = {"templateId": self.gei_template_id}
            response = self.http.get(url, params=params)
            self.assert_util.assert_response_success(response)
            
            a.text(f"下载URL: {url}", "V2下载链接")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
