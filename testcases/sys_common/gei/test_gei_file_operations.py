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
@allure.feature("导入导出文件操作")
class TestGeiFileOperations(SysCommonBaseTest):
    """导入导出文件操作测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.gei_task_id = None
        cls.logger.info("导入导出文件操作测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.gei_task_id:
                cls.db.delete(
                    table="gei_task",
                    where="id = %s",
                    params=[cls.gei_task_id]
                )
            cls.db.delete(
                table="gei_task",
                where="task_name like %s",
                params=["AT_%"]
            )
            cls.logger.info("导入导出文件操作测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="导入导出文件操作",
        title="测试通过任务ID下载文件",
        description="验证API_GEI_TASK_DOWNLOAD_BY_MAIN_TASK_ID_GET功能 - 下载文件",
        severity="normal",
        order=10,
        tags=["sys_common", "gei", "file", "download"]
    )
    def test_download_by_task_id_get(self):
        """测试通过任务ID下载文件 - API_GEI_TASK_DOWNLOAD_BY_MAIN_TASK_ID_GET"""
        try:
            if not self.gei_task_id:
                # 依赖任务创建，这里模拟调用或直接创建
                task_name = f"AT_DOWNLOAD_TASK_{self.mock_util.get_timestamp()}"
                api_path_create = self.get_api_path("导入导出任务管理接口-提交导出任务")
                params_create, url_create = self.get_api_params(api_path_create)
                filtered_params_create = ParamUtil.filter_post_body_fields(
                    params_create, ["taskName"], ["params"]
                )
                set_dict_create = {"taskName": task_name}
                ParamUtil.set_request_params(filtered_params_create, set_dict_create)
                create_response = self.http.post(url_create, json=filtered_params_create)
                self.assert_util.assert_response_data(create_response)
                task_data = create_response.get("data", {}).get("data", {})
                self.gei_task_id = task_data.get("taskId")
            
            api_path = self.get_api_path("导入导出任务管理接口-通过任务ID下载文件")
            url = self.get_api_url(api_path)  # 获取完整URL
            params = {"taskId": self.gei_task_id}
            response = self.http.get(url, params=params)
            self.assert_util.assert_response_success(response)
            
            a.text(f"下载URL: {url}", "下载链接")
            a.json({"taskId": self.gei_task_id}, "下载参数")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出文件操作",
        title="测试通过Key下载文件",
        description="验证API_GEI_TASK_DOWNLOAD_BY_KEY_GET功能 - 通过Key下载",
        severity="normal",
        order=11,
        tags=["sys_common", "gei", "file", "download_key"]
    )
    def test_download_by_key_get(self):
        """测试通过Key下载文件 - API_GEI_TASK_DOWNLOAD_BY_KEY_GET"""
        try:
            # 假设有文件Key，从任务中获取或模拟
            if not self.gei_task_id:
                self.test_download_by_task_id_get()
            file_key = f"AT_FILE_KEY_{self.mock_util.get_timestamp()}"
            
            api_path = self.get_api_path("导入导出任务管理接口-下载文件")
            url = self.get_api_url(api_path)
            params = {"key": file_key}
            response = self.http.get(url, params=params)
            self.assert_util.assert_response_success(response)
            
            a.text(f"下载URL: {url}", "下载链接")
            a.json(params, "下载参数")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="导入导出文件操作",
        title="测试下载导出文件",
        description="验证API_GEI_TASK_DOWNLOAD_GET功能 - 下载导出文件",
        severity="normal",
        order=12,
        tags=["sys_common", "gei", "file", "download_export"]
    )
    def test_download_export_get(self):
        """测试下载导出文件 - API_GEI_TASK_DOWNLOAD_GET"""
        try:
            api_path = self.get_api_path("导入导出任务管理接口-下载导出文件")
            url = self.get_api_url(api_path)
            response = self.http.get(url)
            self.assert_util.assert_response_success(response)
            
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
