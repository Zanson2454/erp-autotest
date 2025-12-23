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

