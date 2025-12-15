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
@allure.feature("打印场景视图管理")
class TestPrintSceneViewManagement(SysCommonBaseTest):
    """打印场景视图管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.print_scene_view_id = None
        cls.logger.info("打印场景视图管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.print_scene_view_id:
                cls.db.delete(
                    table="print_scene_view",  # 假设打印场景视图表名为print_scene_view
                    where="id = %s",
                    params=[cls.print_scene_view_id]
                )
            cls.db.delete(
                table="print_scene_view",
                where="view_key like %s",
                params=["AT_%"]
            )
            cls.logger.info("打印场景视图测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
    @case_decorator(
        story="打印场景视图管理",
        title="测试保存打印场景视图",
        description="验证API_PRINT_PRINT_SCENE_VIEW_KEY_SAVE_POST功能 - 打印场景视图保存",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "print", "scene_view", "save"]
    )
    def test_print_scene_view_save_post(self):
        """测试保存打印场景视图 - API_PRINT_PRINT_SCENE_VIEW_KEY_SAVE_POST"""
        try:
            # 1. 准备测试数据
            view_key = f"AT_PRINT_VIEW_{self.mock_util.get_timestamp()}"
            view_name = f"AT_PRINT_VIEW_NAME_{self.mock_util.get_timestamp()}"
            scene_id = "TEST_SCENE_ID"  # 假设关联的场景ID，或从场景管理获取
            model_key = "TEST_MODEL_KEY"
            description = self.mock_util.get_mock_remark()
            enabled = True
            remark = f"测试视图备注_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("打印场景视图-保存")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["viewKey", "viewName", "sceneId", "modelKey", "description", "enabled", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "viewKey": view_key,
                "viewName": view_name,
                "sceneId": scene_id,
                "modelKey": model_key,
                "description": description,
                "enabled": enabled,
                "remark": remark
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            view_data = response.get("data", {}).get("data", {})
            self.print_scene_view_id = view_data.get("id") if view_data else None
            self.assert_util.assert_by_operator(self.print_scene_view_id, "not_empty", "打印场景视图ID不应为空")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建打印场景视图ID: {self.print_scene_view_id}, 视图键: {view_key}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="打印场景视图管理",
        title="测试打印场景视图详情查询",
        description="验证API_PRINT_PRINT_SCENE_VIEW_KEY_DETAIL_POST功能 - 打印场景视图详情",
        severity="normal",
        order=4,
        tags=["sys_common", "print", "scene_view", "detail"]
    )
    def test_print_scene_view_detail_post(self):
        """测试打印场景视图详情 - API_PRINT_PRINT_SCENE_VIEW_KEY_DETAIL_POST"""
        try:
            # 确保视图存在
            if not self.print_scene_view_id:
                self.test_print_scene_view_save_post()
            
            # 调用详情查询API
            api_path = self.get_api_path("打印场景视图-详情")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.print_scene_view_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            view_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(view_data.get("id"), "=", self.print_scene_view_id, "视图ID不匹配")
            self.assert_util.assert_by_operator(
                view_data.get("viewKey", "").startswith("AT_PRINT_VIEW_"), 
                "=", True, "视图键前缀不匹配"
            )
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="打印场景视图管理",
        title="测试删除打印场景视图",
        description="验证API_PRINT_PRINT_SCENE_VIEW_KEY_DELETE_POST功能 - 打印场景视图删除",
        severity="normal",
        order=16,
        tags=["sys_common", "print", "scene_view", "delete"]
    )
    def test_print_scene_view_delete_post(self):
        """测试删除打印场景视图 - API_PRINT_PRINT_SCENE_VIEW_KEY_DELETE_POST"""
        try:
            # 确保视图存在
            if not self.print_scene_view_id:
                self.test_print_scene_view_save_post()
            
            api_path = self.get_api_path("打印场景视图-删除")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.print_scene_view_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response = self.http.post(url, json=filtered_params)
            self.assert_util.assert_response_success(response)
            
            self.print_scene_view_id = None  # 标记已删除
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除打印场景视图ID: {self.print_scene_view_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
