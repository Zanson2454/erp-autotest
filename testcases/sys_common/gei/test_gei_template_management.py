import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("导入导出模板管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestGeiTemplateManagement(SysCommonBaseTest):
    """导入导出模板管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
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
    
        super().teardown_class()
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
            # 1. 准备测试数据
            template_name = f"AT_TEMPLATE_{self.mock_util.get_timestamp()}"
            set_dict = {
                "templateName": template_name,
                "headerConfigList": [
                    {"name": "字段1", "type": "TEXT", "field": "field1"}
                ]
            }
            
            # 2. 使用标准化API调用
            response, extracted_id = self.standard_api_call(
                api_key="导入导出模版管理接口-保存模版",
                set_dict=set_dict,
                fields_to_filter=["templateName", "headerConfigList"],
                param_path=["params"],
                store_id_as="gei_template"
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 保存模板ID
            template_data = response.get("data", {}).get("data", {})
            if extracted_id:
                self.gei_template_id = extracted_id
            elif template_data:
                self.gei_template_id = template_data.get("id")
            
            a.json(set_dict, "请求数据")
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据
            set_dict = {
                "sourceId": self.gei_template_id,
                "newName": f"AT_COPY_TEMPLATE_{self.mock_util.get_timestamp()}"
            }
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-复制模版",
                set_dict=set_dict,
                fields_to_filter=["sourceId", "newName"],
                param_path=["params"]
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_data(response)
            
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据
            set_dict = {"templateId": self.gei_template_id}
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-导出",
                set_dict=set_dict,
                fields_to_filter=["templateId"],
                param_path=["params"]
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            a.json(set_dict, "请求数据")
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
            # 1. 准备测试数据
            set_dict = {
                "pageable": {
                    "pageNo": 1,
                    "pageSize": 20,
                    "needTotal": True
                }
            }
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-分页查询模版",
                set_dict=set_dict,
                fields_to_filter=["pageable"],
                param_path=["params", "request"]
            )
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            a.json(set_dict, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出模板管理",
        title="测试导出模板查询",
        description="验证API_TRANTOR_PORTAL_META_LIST_EXPORT_TEMPLATE_GET功能 - 导出模板列表查询",
        severity="normal",
        order=3,
        tags=["sys_common", "gei", "template", "export_query"]
    )
    def test_export_template_query_list(self):
        """测试导出模板查询 - API_TRANTOR_PORTAL_META_LIST_EXPORT_TEMPLATE_GET"""
        try:
            # 1. 准备测试数据
            set_dict = {
                "serviceKey": "ERP_GEN$API_TRANTOR_PORTAL_META_LIST_EXPORT_TEMPLATE_GET",
                "params": {
                    "request": {
                        "pageNo": "1",
                        "pageSize": "20"
                    }
                }
            }
            
            # 2. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导出模版列表查询(/api/trantor/portal/meta/list/ExportTemplate#GET)",
                set_dict=set_dict,
                param_path=[] # 空路径，让 set_dict 直接作为顶层参数
            )
            
            # 3. 验证响应数据
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(
                data is not None,
                "=",
                True,
                "返回数据不应为空"
            )
            
            # 验证返回的数据列表
            data_list = data.get("data", [])
            self.assert_util.assert_by_operator(
                isinstance(data_list, list),
                "=",
                True,
                "返回数据应为列表类型"
            )
            
            self.logger.info(f"导出模板查询成功，共查询到 {len(data_list)} 条记录")
            
            a.json(set_dict, "请求数据")
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据
            set_dict = {"id": self.gei_template_id}
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-根据id查询模版",
                set_dict=set_dict,
                fields_to_filter=["id"],
                param_path=["params"]
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 5. 验证返回的模板ID
            template_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(template_data.get("id"), "=", self.gei_template_id)
            
            a.json(set_dict, "请求数据")
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据
            set_dict = {"id": self.gei_template_id}
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-启用模版",
                set_dict=set_dict,
                fields_to_filter=["id"],
                param_path=["params"]
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            a.json(set_dict, "请求数据")
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据
            set_dict = {"id": self.gei_template_id}
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-停用模版",
                set_dict=set_dict,
                fields_to_filter=["id"],
                param_path=["params"]
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            a.json(set_dict, "请求数据")
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据
            set_dict = {"id": self.gei_template_id}
            
            # 3. 使用标准化API调用
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-删除模版",
                set_dict=set_dict,
                fields_to_filter=["id"],
                param_path=["params"]
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 清理模板ID
            self.gei_template_id = None
            
            a.json(set_dict, "请求数据")
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据（GET请求参数通过query string传递）
            set_dict = {"templateId": self.gei_template_id}
            
            # 3. 使用标准化API调用（GET请求）
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-模版文件下载",
                set_dict=set_dict,
                method="GET"
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            a.json(set_dict, "请求参数")
            a.text(f"下载成功，模板ID: {self.gei_template_id}", "下载结果")
            
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
            # 1. 前置条件：确保模板已存在
            if not self.gei_template_id:
                self._ensure_template_save_post()
            
            # 2. 准备测试数据（GET请求参数通过query string传递）
            set_dict = {"templateId": self.gei_template_id}
            
            # 3. 使用标准化API调用（GET请求）
            response, _ = self.standard_api_call(
                api_key="导入导出模版管理接口-模版文件下载V2",
                set_dict=set_dict,
                method="GET"
            )
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            a.json(set_dict, "请求参数")
            a.text(f"V2下载成功，模板ID: {self.gei_template_id}", "V2下载结果")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
