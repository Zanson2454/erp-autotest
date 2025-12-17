# -*- coding: utf-8 -*-
"""
财务代理模块测试用例
"""

import allure
import pytest
from testcases.erp_fin import FinBaseTest
from utils.report_util import a, case_decorator


@allure.epic("财务模块")
@allure.feature("财务代理管理")
class TestFinAgentManagement(FinBaseTest):
    """财务代理管理测试类"""
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.logger.info("财务代理管理测试类初始化完成")
    
    @classmethod
    def teardown_class(cls):
        """测试类结束后执行清理"""
        try:
            cls.logger.info("财务代理管理测试类清理完成")
        except Exception as e:
            cls.logger.error(f"测试类清理失败: {str(e)}")
    
    @case_decorator(
        story="财务代理",
        title="测试查询财务代理报销树节点单节点",
        description="验证财务代理报销(agent_reimbursement)树节点单节点查询接口的功能性",
        severity="critical",
        file_level_order=2,
        tags=["财务代理", "树节点查询", "报销"]
    )
    def test_query_agent_reimbursement_tree_node_single(self):
        """测试查询财务代理报销树节点单节点"""
        try:
            # 1. 构建完整URL（GET请求，路径中包含参数）
            api_path = "/api/trantor/meta/query/tree-node/single/ERP_FIN$agent_reimbursement"
            url = f"{self.portal_url}{api_path}"
            
            # 2. 发送GET请求
            self.logger.info(f"请求URL: {url}")
            response = self.http.get(url)
            
            # 3. 业务断言
            self.assert_util.assert_response_data(response)
            
            # 4. 记录请求和响应
            a.text(url, "请求URL")
            a.json(response, "响应数据")
            
            # 5. 验证返回的数据结构（根据实际响应调整）
            data = response.get("data", {})
            self.assert_util.assert_by_operator(data, "not_empty", None, "响应数据不应为空")
            
            self.logger.info("财务代理报销树节点单节点查询成功")
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise
    