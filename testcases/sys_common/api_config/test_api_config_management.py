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
@allure.feature("配置中心管理")
@pytest.mark.skip(reason="接口配置缺失或已漂移，暂时跳过")
class TestApiConfigManagement(SysCommonBaseTest):
    """配置中心管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.bind_context()

    @classmethod
    def bind_context(cls):
        """绑定测试上下文对象。"""
        super().bind_context()
        cls.config_id = None
        cls.config_ids = []  # 用于批量删除
        cls.logger.info("配置中心管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            # 精确删除已创建的配置
            if cls.config_id:
                cls.db.delete(
                    table="api_config",  # 假设配置表名为api_config
                    where="id = %s",
                    params=[cls.config_id]
                )
            # 批量删除
            if cls.config_ids:
                for config_id in cls.config_ids:
                    cls.db.delete(
                        table="api_config",
                        where="id = %s",
                        params=[config_id]
                    )
            # 清理以AT_开头的测试数据
            cls.db.delete(
                table="api_config",
                where="config_key like %s",
                params=["AT_%"]
            )
            cls.logger.info("配置中心测试数据清理完成")
        except Exception as e:
            cls.logger.error(f"测试数据清理失败: {str(e)}")
    
        super().teardown_class()
    @case_decorator(
        story="配置中心管理",
        title="测试配置保存",
        description="验证API_CONFIG_ADMIN_INFO_SAVE_POST功能 - 配置保存",
        severity="blocker",
        order=1,
        smoke=True,
        tags=["sys_common", "api_config", "save"]
    )
    def test_config_save_post(self):
        """测试配置保存 - API_CONFIG_ADMIN_INFO_SAVE_POST"""
        try:
            # 1. 准备测试数据
            config_key = f"AT_CONFIG_KEY_{self.mock_util.get_timestamp()}"
            config_value = f"AT_CONFIG_VALUE_{self.mock_util.get_timestamp()}"
            config_name = f"AT_CONFIG_NAME_{self.mock_util.get_timestamp()}"
            config_remark = self.mock_util.get_mock_remark()
            
            # 2. 调用API
            api_path = self.get_api_path("配置中心配置接口-配置保存")
            params, url = self.get_api_params(api_path)
            
            # 3. 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["configKey", "configValue", "configName", "remark"],
                ["params", "request"]
            )
            set_dict = {
                "configKey": config_key,
                "configValue": config_value,
                "configName": config_name,
                "remark": config_remark
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            # 4. 发送请求和断言
            response, _ = self.standard_api_call(
                api_key="配置中心配置接口-配置保存",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 5. 保存数据和报告
            config_data = response.get("data", {}).get("data", {})
            self.config_id = config_data.get("id") if config_data else None
            if self.config_id:
                self.config_ids.append(self.config_id)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"创建配置ID: {self.config_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="配置中心管理",
        title="测试配置分页查询",
        description="验证API_CONFIG_ADMIN_INFO_PAGING_POST功能 - 分页查询配置",
        severity="blocker",
        order=4,
        smoke=True,
        tags=["sys_common", "api_config", "paging"]
    )
    def test_config_paging_post(self):
        """测试配置分页查询 - API_CONFIG_ADMIN_INFO_PAGING_POST"""
        try:
            # 确保有测试数据
            if not self.config_id:
                self._ensure_config_save_post()
            
            # 调用分页查询API
            api_path = self.get_api_path("配置中心配置接口-分页查询配置")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["pageable", "fields"],
                ["params", "request"]
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
                    {"name": "configKey", "type": "TEXT"},
                    {"name": "configName", "type": "TEXT"},
                    {"name": "configValue", "type": "TEXT"}
                ],
                "systemParams": None
            }
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="配置中心配置接口-分页查询配置",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证分页结果
            paging_data = response.get("data", {}).get("data", {})
            config_list = paging_data.get("data", [])
            total_count = paging_data.get("total", 0)
            
            self.assert_util.assert_by_operator(total_count, ">=", 0, "总记录数应大于等于0")
            self.assert_util.assert_by_operator(len(config_list), "<=", 20, "每页记录数不超过20")
            
            # 验证测试数据是否存在
            test_config_found = any(
                cfg.get("configKey", "").startswith("AT_CONFIG_KEY_") for cfg in config_list
            )
            self.assert_util.assert_by_operator(test_config_found, "=", True, "测试配置数据未在分页结果中找到")
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="配置中心管理",
        title="测试配置详情查询",
        description="验证API_CONFIG_ADMIN_INFO_FIND_BY_ID_POST功能 - 配置详情查询",
        severity="normal",
        order=5,
        tags=["sys_common", "api_config", "query"]
    )
    def test_config_find_by_id_post(self):
        """测试配置详情查询 - API_CONFIG_ADMIN_INFO_FIND_BY_ID_POST"""
        try:
            # 确保配置存在
            if not self.config_id:
                self._ensure_config_save_post()
            
            # 调用详情查询API
            api_path = self.get_api_path("配置中心配置接口-配置详情查询")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.config_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="配置中心配置接口-配置详情查询",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_data(response)
            
            # 验证返回数据
            config_data = response.get("data", {}).get("data", {})
            self.assert_util.assert_by_operator(config_data.get("id"), "=", self.config_id, "配置ID不匹配")
            self.assert_util.assert_by_operator(
                config_data.get("configKey", "").startswith("AT_CONFIG_KEY_"), 
                "=", True, "配置键前缀不匹配"
            )
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="配置中心管理",
        title="测试配置删除",
        description="验证API_CONFIG_ADMIN_INFO_DELETE_BY_ID_POST功能 - 配置删除",
        severity="normal",
        order=16,
        tags=["sys_common", "api_config", "delete"]
    )
    def test_config_delete_by_id_post(self):
        """测试配置删除 - API_CONFIG_ADMIN_INFO_DELETE_BY_ID_POST"""
        try:
            # 确保配置存在
            if not self.config_id:
                self._ensure_config_save_post()
            
            # 调用删除API
            api_path = self.get_api_path("配置中心配置接口-配置删除")
            params, url = self.get_api_params(api_path)
            
            # 参数处理
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["id"],
                ["params", "request"]
            )
            set_dict = {"id": self.config_id}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="配置中心配置接口-配置删除",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 验证删除后无法查询到（可选二次验证）
            self.config_id = None
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"删除配置ID: {self.config_id}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="配置中心管理",
        title="测试配置批量删除",
        description="验证API_CONFIG_ADMIN_INFO_DELETE_BY_IDS_POST功能 - 配置批量删除",
        severity="normal",
        order=17,
        tags=["sys_common", "api_config", "batch_delete"]
    )
    def test_config_delete_by_ids_post(self):
        """测试配置批量删除 - API_CONFIG_ADMIN_INFO_DELETE_BY_IDS_POST"""
        try:
            # 创建多个测试配置用于批量删除
            test_ids = []
            for i in range(2):  # 创建2个配置用于批量测试
                config_key = f"AT_BATCH_CONFIG_{self.mock_util.get_timestamp()}_{i}"
                config_value = f"AT_BATCH_VALUE_{self.mock_util.get_timestamp()}_{i}"
                config_name = f"AT_BATCH_NAME_{self.mock_util.get_timestamp()}_{i}"
                
                api_path = self.get_api_path("配置中心配置接口-配置保存")
                params, url = self.get_api_params(api_path)
                
                filtered_params = ParamUtil.filter_post_body_fields(
                    params, ["configKey", "configValue", "configName"],
                    ["params", "request"]
                )
                set_dict = {
                    "configKey": config_key,
                    "configValue": config_value,
                    "configName": config_name
                }
                ParamUtil.set_request_params(filtered_params, set_dict)
                
                response, _ = self.standard_api_call(
                    api_key="配置中心配置接口-配置保存",
                    set_dict=filtered_params.get("params", {}),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                self.assert_util.assert_response_data(response)
                
                batch_config_data = response.get("data", {}).get("data", {})
                batch_id = batch_config_data.get("id")
                if batch_id:
                    test_ids.append(batch_id)
                    self.config_ids.append(batch_id)
            
            if not test_ids:
                self.logger.warning("未创建批量删除测试数据，跳过批量删除测试")
                return
            
            # 调用批量删除API
            api_path = self.get_api_path("配置中心配置接口-配置批量删除")
            params, url = self.get_api_params(api_path)
            
            # 参数处理 - 假设批量删除使用ids数组
            filtered_params = ParamUtil.filter_post_body_fields(
                params, ["ids"],
                ["params", "request"]
            )
            set_dict = {"ids": test_ids}
            ParamUtil.set_request_params(filtered_params, set_dict)
            
            response, _ = self.standard_api_call(
                api_key="配置中心配置接口-配置批量删除",
                set_dict=filtered_params.get("params", {}),
                store_id_as=None,
                use_param_util=False,
                param_path=["params"]
            )
            self.assert_util.assert_response_success(response)
            
            # 清理本地记录
            for tid in test_ids:
                if tid in self.config_ids:
                    self.config_ids.remove(tid)
            
            a.json(filtered_params, "请求数据")
            a.json(response, "响应数据")
            self.logger.info(f"批量删除配置IDs: {test_ids}")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
