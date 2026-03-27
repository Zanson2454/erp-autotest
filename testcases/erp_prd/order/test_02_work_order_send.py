# -*- coding: utf-8 -*-
"""
生产订单下达测试用例
包含生产订单下达等操作
"""
import sys
import time
import json
import allure
import pytest
from pathlib import Path
from testcases.erp_prd import PrdBaseTest
from utils.report_util import a
from utils.param_util import ParamUtil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("生产管理")
@allure.feature("生产订单下达")
class TestPrdOrderSend(PrdBaseTest):
    """生产订单下达测试类"""
    
    # 保存测试过程中的数据
    prd_order_info = {}
    
    def init(self):
        """初始化测试数据"""
        self.logger.info("开始初始化生产订单下达测试数据")
        
        # 获取最新的生产订单信息
        order_info = self.get_latest_prd_order()
        
        # 检查生产订单状态
        assert order_info["status"] == "DRAFT", f"生产订单状态不是草稿状态，当前状态: {order_info['status']}"
        assert order_info["confirm_status"] == "UNCONFIRMED", f"生产订单确认状态不是未确认状态，当前状态: {order_info['confirm_status']}"
        assert order_info["delivered_status"] == "UNDELIVERED", f"生产订单交付状态不是未交付状态，当前状态: {order_info['delivered_status']}"
        
        # 保存生产订单信息
        self.prd_order_info.update(order_info)
        self.logger.info(f"获取到生产订单ID: {self.prd_order_info['id']}, 编号: {self.prd_order_info['wo_code']}, 状态: {self.prd_order_info['status']}")

    @pytest.mark.run(order=8)
    @allure.story("生产订单下达")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送生产订单下达请求
    3. 验证响应结果
    4. 保存生产订单下达信息
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("生产订单下达")
    def test_send_prd_order(self):
        """生产订单下达测试用例"""
        try:
            # 初始化测试数据
            self.init()
            
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("生产订单下达服务")
                self.logger.debug(f"生产订单下达API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            "ids": [self.prd_order_info["id"]]  # 使用从数据库获取的生产订单ID
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result, _ = self.standard_api_call(
                    api_key="生产订单下达服务",
                    set_dict=(filtered_params.get("params", {}) if isinstance(filtered_params, dict) else filtered_params),
                    store_id_as=None,
                    use_param_util=False,
                    param_path=["params"]
                )
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取生产订单下达结果
                response_data = result.get("data", {}).get("data", {})
                
                # 确保返回了生产订单下达结果
                assert response_data, "未返回生产订单下达结果"
                
                # 验证下达结果
                assert response_data.get("succeed", 0) > 0, f"生产订单下达失败: {response_data.get('items', [{}])[0].get('failReason', '未知原因')}"
                
                # 记录验证结果
                a.text(
                    f"生产订单下达结果: {json.dumps(response_data, ensure_ascii=False, indent=2)}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存生产订单下达信息"):
                # 保存生产订单下达信息到类变量，供后续测试用例使用
                self.prd_order_info.update({
                    "send_result": response_data
                })
                
                self.logger.info(f"生产订单下达成功")
                
                # 记录保存的数据
                a.json(self.prd_order_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"生产订单下达失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdOrderSend()
    test.test_send_prd_order()  # 生产订单下达 
