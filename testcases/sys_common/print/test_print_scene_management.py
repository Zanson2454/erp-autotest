import sys
from pathlib import Path

import allure
import pytest

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.sys_common import SysCommonBaseTest
from utils.param_util import ParamUtil
from utils.report_util import a, case_decorator


@allure.epic("系统通用模块")
@allure.feature("打印场景管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestPrintSceneManagement(SysCommonBaseTest):
    """打印场景管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.print_scene_id = None
        cls.logger.info("打印场景管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            if cls.print_scene_id:
                cls.db.delete(
                    table="print_scene",  # 假设打印场景表名为print_scene
                    where="id = %s",
                    params=[cls.print_scene_id]
                )
            cls.db.delete(
                table="print_scene",
                where="scene_code like %s",
                params=["AT_%"]
            )
            cls.logger.info("打印场景测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="打印场景管理",
        title="测试保存打印场景",
        description="验证API_PRINT_PRINT_SCENE_SAVE_POST功能 - 打印场景保存",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "print", "scene", "save"]
    )
    def test_print_scene_save_post(self):
        """测试保存打印场景 - API_PRINT_PRINT_SCENE_SAVE_POST"""
        try:
            # 1. 准备测试数据
            scene_code = f"AT_PRINT_SCENE_{self.mock_util.get_timestamp()}"
            scene_name = f"AT_PRINT_SCENE_NAME_{self.mock_util.get_timestamp()}"
            model_key = "TEST_MODEL_KEY"
            description = self.mock_util.get_mock_remark()
            enabled = True
            remark = f"测试场景备注_{self.mock_util.get_timestamp()}"
            
            # 2. 调用API
            api_path = self.get_api_path("打印场景-保存")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["sceneCode", "sceneName", "modelKey", "description", "enabled", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "sceneCode": scene_code,
                "sceneName": scene_name,
                "modelKey": model_key,
                "description": description,
                "enabled": enabled,
                "remark": remark
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="打印场景-保存",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            scene_data = response.get("data", {}).get("data", {})
            self.print_scene_id = scene_data.get("id") if scene_data else None
            self.assert_util.assert_by_operator(self.print_scene_id, "not_empty", "打印场景ID不应为空")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建打印场景ID: {self.print_scene_id}, 场景编码: {scene_code}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="打印场景管理",
        title="测试打印场景详情查询",
        description="验证API_PRINT_PRINT_SCENE_DETAIL_POST功能 - 打印场景详情",
        severity="normal",
        order=4,
        tags=["sys_common", "print", "scene", "detail"]
    )
    def test_print_scene_detail_post(self):
        """测试打印场景详情 - API_PRINT_PRINT_SCENE_DETAIL_POST"""
        try:
            # 确保场景存在
            if not self.print_scene_id:
                self._ensure_print_scene_save_post()
            
            # 调用详情查询API
            api_path = self.get_api_path("打印场景-详情")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.print_scene_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="打印场景-详情",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            scene_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(scene_data.get("id"), "=", self.print_scene_id, "场景ID不匹配")
            self.assert_util.assert_by_operator(
                scene_data.get("sceneCode", "").startswith("AT_PRINT_SCENE_"), 
                "=", True, "场景编码前缀不匹配"
            )
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="打印场景管理",
        title="测试根据模型key查询打印场景列表",
        description="验证API_PRINT_PRINT_SCENE_LIST_BY_MODEL_KEY_POST功能 - 根据模型key查询列表",
        severity="normal",
        order=5,
        tags=["sys_common", "print", "scene", "list_by_model"]
    )
    def test_print_scene_list_by_model_key_post(self):
        """测试根据模型key查询打印场景列表 - API_PRINT_PRINT_SCENE_LIST_BY_MODEL_KEY_POST"""
        try:
            # 确保有测试数据，使用保存时的modelKey
            if not self.print_scene_id:
                self._ensure_print_scene_save_post()
            model_key = "TEST_MODEL_KEY"  # 从保存方法中使用相同的modelKey
            
            api_path = self.get_api_path("打印场景-根据模型key查询列表")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["modelKey"],
                ["params", "request"]
            )
            set_dict = {"modelKey": model_key}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="打印场景-根据模型key查询列表",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证列表结果
            list_data = response.get("data", {}).get("data", [])
            self.assert_util.assert_by_operator(list_data, "not_empty", "场景列表不应为空")
            
            # 验证测试场景是否在列表中
            test_scene_found = any(
                scene.get("sceneCode", "").startswith("AT_PRINT_SCENE_") for scene in list_data
            )
            self.assert_util.assert_by_operator(test_scene_found, "=", True, "测试打印场景未在列表中找到")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="打印场景管理",
        title="测试删除打印场景",
        description="验证API_PRINT_PRINT_SCENE_DELETE_POST功能 - 打印场景删除",
        severity="normal",
        order=16,
        tags=["sys_common", "print", "scene", "delete"]
    )
    def test_print_scene_delete_post(self):
        """测试删除打印场景 - API_PRINT_PRINT_SCENE_DELETE_POST"""
        try:
            # 确保场景存在
            if not self.print_scene_id:
                self._ensure_print_scene_save_post()
            
            api_path = self.get_api_path("打印场景-删除")
            params, url = self.get_api_params(api_path)
            
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.print_scene_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="打印场景-删除",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            self.print_scene_id = None  # 标记已删除
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除打印场景ID: {self.print_scene_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
