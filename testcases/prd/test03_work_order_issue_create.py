# -*- coding: utf-8 -*-
"""
生产订单领料单创建测试用例
包含根据生产订单BOM清单创建领料单等操作
"""
import sys
import time
import json
import allure
import pytest
from pathlib import Path
from testcases.prd import PrdBaseTest
from utils.allure_simple import a
from utils.param_util import ParamUtil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("生产管理")
@allure.feature("生产订单领料")
class TestPrdOrderIssueCreate(PrdBaseTest):
    """生产订单领料单创建测试类"""
    
    # 保存测试过程中的数据
    issue_create_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        super().setup_class()
        cls.logger.info("生产订单领料单创建测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("创建生产订单领料单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送创建领料单请求
    3. 验证响应结果
    4. 保存创建结果数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("根据生产订单BOM清单创建领料单")
    def test_create_issue_by_order_bom_list(self):
        """根据生产订单BOM清单创建领料单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("根据生产订单BOM行创建领料单服务")
                self.logger.debug(f"创建领料单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 获取最新的BOM项
                latest_bom_items = self.get_prd_order_pending_issue_bom_items()
                bom_item_ids = [{"id": item.get("id")} for item in latest_bom_items]
                
                # 构建创建领料单的请求参数
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": bom_item_ids,
                            "issueRule": {
                                "issueRuleItems": [
                                    {
                                        "label": "库存组织",
                                        "value": 2000001,
                                        "item": "INV_ORG",
                                        "defaultValue": True,
                                        "isModified": False,
                                        "disabled": True
                                    },
                                    {
                                        "label": "库存地点",
                                        "value": 2000002,
                                        "item": "INV_LOC",
                                        "defaultValue": True,
                                        "isModified": True,
                                        "disabled": False
                                    },
                                    {
                                        "label": "工作中心",
                                        "value": 2000006,
                                        "item": "WORK_CENTER",
                                        "defaultValue": True,
                                        "isModified": True,
                                        "disabled": False
                                    }
                                ],
                                "issueRule": {
                                    "code": "aaa",
                                    "name": "默认分单规则",
                                    "defaultValue": True
                                }
                            }
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="创建领料单")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取创建的领料单信息
                response_data = result.get("data", {})
                
                # 确保返回了领料单信息
                assert response_data is not None, "未返回领料单信息"
                
                # 记录验证结果
                a.text(
                    f"生产订单BOM项ID: {[item.get('id') for item in filtered_params['params']['request']['ids']]}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存创建结果数据"):
                # 保存领料单信息到类变量
                TestPrdOrderIssueCreate.issue_create_info.update({
                    "bom_item_ids": filtered_params['params']['request']['ids'],
                    "issue_info": response_data
                })
                
                self.logger.info(f"领料单创建成功 - BOM项ID: {[item.get('id') for item in filtered_params['params']['request']['ids']]}")
                
                # 记录保存的数据
                a.json(TestPrdOrderIssueCreate.issue_create_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"创建领料单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdOrderIssueCreate()
    test.setup_class()
    test.test_create_issue_by_order_bom_list()    # 创建生产订单领料单 