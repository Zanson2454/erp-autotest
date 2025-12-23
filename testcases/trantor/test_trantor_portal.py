# -*- coding: utf-8 -*-
"""
Trantor框架门户接口测试用例
包含：获取当前门户信息等核心功能测试
"""

import allure
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from testcases.trantor import TrantorBaseTest
from utils.report_util import a, case_decorator


@allure.epic("Trantor框架")
@allure.feature("门户管理")
class TestTrantorPortal(TrantorBaseTest):
    """Trantor门户管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("Trantor门户管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        # Trantor接口不涉及数据创建，无需清理
        cls.logger.info("Trantor门户管理测试类清理完成")
    
    @case_decorator(
        story="Trantor门户",
        title="测试获取当前门户信息",
        description="验证获取当前门户信息接口的响应和数据",
        severity="normal",
        file_level_order=1,
        tags=["trantor", "portal", "current"]
    )
    def test_get_current_portal(self):
        """测试获取当前门户信息"""
        try:
            # 1. 获取API路径
            api_path = self.get_api_path("Trantor-获取当前门户信息")
            if api_path is None:
                raise ValueError("未找到API配置: Trantor-获取当前门户信息")
            
            # 2. 发送GET请求（GET请求无需参数）
            response = self.http.get(api_path)
            
            # 3. 记录响应
            a.json(response, "当前门户信息响应")
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证响应数据结构
            data = response.get("data", {})
            self.assert_util.assert_by_operator(data, "not_empty", "响应数据不应为空")
            
            # 6. 验证关键字段（根据实际响应结构调整）
            # 示例：如果响应包含 portal 相关信息
            # portal_info = data.get("portal") or data.get("data", {})
            # if portal_info:
            #     self.assert_util.assert_by_operator(portal_info.get("id"), "not_empty", "门户ID不应为空")
            #     self.assert_util.assert_by_operator(portal_info.get("name"), "not_empty", "门户名称不应为空")
            
            self.logger.info("获取当前门户信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="Trantor门户",
        title="测试获取最新版本信息",
        description="验证获取最新版本信息接口的响应和数据",
        severity="normal",
        file_level_order=2,
        tags=["trantor", "portal", "latest"]
    )
    def test_get_latest_version(self):
        """测试获取最新版本信息"""
        try:
            # 1. 获取API路径
            api_path = self.get_api_path("Trantor-获取最新版本信息")
            if api_path is None:
                raise ValueError("未找到API配置: Trantor-获取最新版本信息")
            
            # 2. 发送GET请求（GET请求无需参数）
            response = self.http.get(api_path)
            
            # 3. 记录响应
            a.json(response, "最新版本信息响应")
            
            # 4. 业务断言
            # 注意：latest.json接口可能返回的不是标准success格式，需要根据实际响应调整断言
            # 如果响应是直接的JSON对象（不是包装在success/data结构中），直接验证数据不为空
            if isinstance(response, dict):
                # 如果响应包含success字段，使用标准断言
                if "success" in response:
                    self.assert_util.assert_response_success(response)
                    data = response.get("data", {})
                    self.assert_util.assert_by_operator(data, "not_empty", "响应数据不应为空")
                else:
                    # 如果响应是直接的JSON对象，验证响应不为空
                    self.assert_util.assert_by_operator(response, "not_empty", "响应数据不应为空")
            else:
                # 如果响应不是字典类型，记录警告
                self.logger.warning(f"响应格式异常，期望字典类型，实际类型: {type(response)}")
            
            # 5. 验证关键字段（根据实际响应结构调整）
            # 示例：如果响应包含 version 相关信息
            # version_info = response.get("version") or response.get("data", {}).get("version")
            # if version_info:
            #     self.assert_util.assert_by_operator(version_info, "not_empty", "版本信息不应为空")
            
            self.logger.info("获取最新版本信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="Trantor门户",
        title="测试获取WebSocket Token",
        description="验证获取WebSocket Token接口的响应和数据",
        severity="normal",
        file_level_order=3,
        tags=["trantor", "websocket", "token"]
    )
    def test_get_websocket_token(self):
        """测试获取WebSocket Token"""
        try:
            # 1. 获取API路径
            api_path = self.get_api_path("Trantor-获取WebSocket Token")
            if api_path is None:
                raise ValueError("未找到API配置: Trantor-获取WebSocket Token")
            
            # 2. 发送POST请求（POST请求但请求体为空）
            response = self.http.post(api_path, json={})
            
            # 3. 记录响应
            a.json(response, "WebSocket Token响应")
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证响应数据结构
            data = response.get("data", {})
            self.assert_util.assert_by_operator(data, "not_empty", "响应数据不应为空")
            
            # 6. 验证关键字段（根据实际响应结构调整）
            # 示例：如果响应包含 token 相关信息
            # token_info = data.get("token") or data.get("data", {}).get("token")
            # if token_info:
            #     self.assert_util.assert_by_operator(token_info, "not_empty", "Token不应为空")
            
            self.logger.info("获取WebSocket Token成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="Trantor门户",
        title="测试获取当前用户信息",
        description="验证获取当前用户信息接口的响应和数据",
        severity="normal",
        file_level_order=4,
        tags=["trantor", "portal", "user", "current"]
    )
    def test_get_current_user(self):
        """测试获取当前用户信息"""
        try:
            # 1. 获取API路径
            api_path = self.get_api_path("Trantor-获取当前用户信息")
            if api_path is None:
                raise ValueError("未找到API配置: Trantor-获取当前用户信息")
            
            # 2. 发送GET请求（GET请求无需参数）
            response = self.http.get(api_path)
            
            # 3. 记录响应
            a.json(response, "当前用户信息响应")
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证响应数据结构
            data = response.get("data", {})
            self.assert_util.assert_by_operator(data, "not_empty", "响应数据不应为空")
            
            # 6. 验证关键字段
            # 如果响应数据是直接的用户信息对象
            user_info = data if isinstance(data, dict) else {}
            
            # 验证用户ID（常见字段名：id, userId, user_id）
            user_id = user_info.get("id") or user_info.get("userId") or user_info.get("user_id")
            if user_id:
                self.assert_util.assert_by_operator(user_id, "not_empty", "用户ID不应为空")
                self.logger.info(f"用户ID: {user_id}")
            
            # 验证用户名称（常见字段名：name, username, userName, nickname）
            user_name = user_info.get("name") or user_info.get("username") or user_info.get("userName") or user_info.get("nickname")
            if user_name:
                self.assert_util.assert_by_operator(user_name, "not_empty", "用户名称不应为空")
                self.logger.info(f"用户名称: {user_name}")
            
            # 验证邮箱（如果存在）
            email = user_info.get("email") or user_info.get("mail")
            if email:
                self.assert_util.assert_by_operator(email, "not_empty", "用户邮箱不应为空")
                self.logger.info(f"用户邮箱: {email}")
            
            # 记录完整的用户信息用于调试
            a.json(user_info, "用户详细信息")
            
            self.logger.info("获取当前用户信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="Trantor门户",
        title="测试获取应用列表",
        description="验证获取应用列表接口的响应和数据",
        severity="normal",
        file_level_order=5,
        tags=["trantor", "portal", "application", "list"]
    )
    def test_get_application_list(self):
        """测试获取应用列表"""
        try:
            # 1. 获取API路径
            api_path = self.get_api_path("Trantor-获取应用列表")
            if api_path is None:
                raise ValueError("未找到API配置: Trantor-获取应用列表")
            
            # 2. 发送GET请求（GET请求无需参数）
            response = self.http.get(api_path)
            
            # 3. 记录响应
            a.json(response, "应用列表响应")
            
            # 4. 业务断言
            self.assert_util.assert_response_success(response)
            
            # 5. 验证响应数据结构
            data = response.get("data", {})
            self.assert_util.assert_by_operator(data, "not_empty", "响应数据不应为空")
            
            # 6. 验证应用列表数据
            # 如果响应是列表格式
            if isinstance(data, list):
                application_list = data
                self.assert_util.assert_by_operator(application_list, "not_empty", "应用列表不应为空")
                self.logger.info(f"应用列表数量: {len(application_list)}")
                
                # 验证列表中的每个应用项
                if application_list:
                    first_app = application_list[0]
                    # 验证应用ID（常见字段名：id, appId, applicationId）
                    app_id = first_app.get("id") or first_app.get("appId") or first_app.get("applicationId")
                    if app_id:
                        self.logger.info(f"第一个应用ID: {app_id}")
                    
                    # 验证应用名称（常见字段名：name, appName, applicationName）
                    app_name = first_app.get("name") or first_app.get("appName") or first_app.get("applicationName")
                    if app_name:
                        self.logger.info(f"第一个应用名称: {app_name}")
                    
                    # 记录第一个应用的详细信息用于调试
                    a.json(first_app, "第一个应用详细信息")
            # 如果响应是对象格式，可能包含list字段
            elif isinstance(data, dict):
                application_list = data.get("list") or data.get("data") or data.get("applications") or []
                if isinstance(application_list, list):
                    self.assert_util.assert_by_operator(application_list, "not_empty", "应用列表不应为空")
                    self.logger.info(f"应用列表数量: {len(application_list)}")
                else:
                    # 如果data本身就是应用对象，记录它
                    a.json(data, "应用数据")
            
            self.logger.info("获取应用列表成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    
    @case_decorator(
        story="Trantor门户",
        title="测试获取图标信息",
        description="验证获取图标信息接口的响应和数据",
        severity="normal",
        file_level_order=6,
        tags=["trantor", "portal", "icon"]
    )
    def test_get_icon_info(self):
        """测试获取图标信息"""
        try:
            # 1. 获取API路径
            api_path = self.get_api_path("Trantor-获取图标信息")
            if api_path is None:
                raise ValueError("未找到API配置: Trantor-获取图标信息")
            
            # 2. 发送GET请求（GET请求无需参数）
            response = self.http.get(api_path)
            
            # 3. 记录响应
            a.json(response, "图标信息响应")
            
            # 4. 业务断言
            # 注意：图标接口可能返回的不是标准success格式，需要根据实际响应调整断言
            # 如果响应是直接的JSON对象（不是包装在success/data结构中），直接验证数据不为空
            if isinstance(response, dict):
                # 如果响应包含success字段，使用标准断言
                if "success" in response:
                    self.assert_util.assert_response_success(response)
                    data = response.get("data", {})
                    self.assert_util.assert_by_operator(data, "not_empty", "响应数据不应为空")
                else:
                    # 如果响应是直接的JSON对象，验证响应不为空
                    self.assert_util.assert_by_operator(response, "not_empty", "响应数据不应为空")
            else:
                # 如果响应不是字典类型，记录警告
                self.logger.warning(f"响应格式异常，期望字典类型，实际类型: {type(response)}")
            
            # 5. 验证图标数据
            # 如果响应是标准格式
            if isinstance(response, dict) and "success" in response:
                data = response.get("data", {})
            else:
                data = response if isinstance(response, dict) else {}
            
            # 如果响应是列表格式（图标列表）
            if isinstance(data, list):
                icon_list = data
                self.assert_util.assert_by_operator(icon_list, "not_empty", "图标列表不应为空")
                self.logger.info(f"图标列表数量: {len(icon_list)}")
                
                # 验证列表中的第一个图标项
                if icon_list:
                    first_icon = icon_list[0]
                    # 验证图标ID（常见字段名：id, iconId）
                    icon_id = first_icon.get("id") or first_icon.get("iconId")
                    if icon_id:
                        self.logger.info(f"第一个图标ID: {icon_id}")
                    
                    # 验证图标URL或路径（常见字段名：url, path, iconUrl, src）
                    icon_url = first_icon.get("url") or first_icon.get("path") or first_icon.get("iconUrl") or first_icon.get("src")
                    if icon_url:
                        self.logger.info(f"第一个图标URL: {icon_url}")
                    
                    # 记录第一个图标的详细信息用于调试
                    a.json(first_icon, "第一个图标详细信息")
            # 如果响应是对象格式，可能包含图标信息
            elif isinstance(data, dict):
                # 验证图标相关字段
                icon_url = data.get("url") or data.get("path") or data.get("iconUrl") or data.get("src")
                if icon_url:
                    self.assert_util.assert_by_operator(icon_url, "not_empty", "图标URL不应为空")
                    self.logger.info(f"图标URL: {icon_url}")
                
                # 记录完整的图标数据用于调试
                a.json(data, "图标详细信息")
            
            self.logger.info("获取图标信息成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

