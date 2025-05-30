# -*- coding: utf-8 -*-
"""
生产订单管理测试用例
包含生产订单创建、查询、修改、删除等操作
"""
import sys
import time
import json
import random
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
@allure.feature("生产订单管理")
class TestPrdOrder(PrdBaseTest):
    """生产订单管理测试类"""
    
    # 保存生产订单相关信息的类变量
    prd_order_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        super().setup_class()
        cls.logger.info("生产订单管理测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("查询生产订单工艺路线项目")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送查询工艺路线项目请求
    3. 验证响应结果
    4. 保存工艺路线数据供后续使用
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查询生产订单工艺路线项目")
    def test_find_routings_items(self):
        """查询生产订单工艺路线项目测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("根据生产版本获取工艺路线行服务")
                self.logger.debug(f"查询工艺路线项目API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            # 基本信息
                            "woTypeId": {"id": self.base_info["wo_type_info"]["id"]},
                            "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                            "matId": {"id": 14652007},
                            "prdMatId": {"id": 14408001},
                            
                            # 状态信息
                            "status": "DRAFT",
                            "confirmStatus": "UNCONFIRMED",
                            "deliveredStatus": "UNDELIVERED",
                            
                            # 数量和单位
                            "qty": 10,
                            "prdUomId": {"id": 2004001},
                            "locId": {"id": 14336001},
                            
                            # 库存相关
                            "postInvTypeId": {"id": 2000001},
                            "mvmTypeId": {"id": 4010005},
                            
                            # 生产版本信息
                            "prdVrsId": {"id": 14323001}
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="查询工艺路线项目")
                # 添加响应数据到报告
                a.json(result, "响应数据")
                # 打印响应结果
                self.logger.info(f"工艺路线查询响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取工艺路线数据
                response_data = result.get("data", {}).get("data", [])
                routings_items = response_data
                
                # 确保返回了routings清单列表
                assert routings_items is not None, "未返回工艺路线列表"
                assert len(routings_items) > 0, "工艺路线为空"
                
                # 记录验证结果
                a.text(
                    f"工艺路线数量: {len(routings_items)}\n验证结果: 成功",
                    "验证结果"
                )

            with a.step("4. 保存工艺路线数据"):
                # 保存工艺路线数据到类变量，供后续测试用例使用
                TestPrdOrder.prd_order_info.update({
                    "routing_items": routings_items,
                    "prdVrsId": filtered_params["params"]["request"]["prdVrsId"]
                })
                
                self.logger.info(f"工艺路线查询成功 - 获取到{len(routings_items)}个工序")
                self.logger.info(f"保存的数据: {json.dumps(routings_items, indent=2, ensure_ascii=False)}")
                
                # 记录保存的数据
                a.json(routings_items, "保存的工艺路线数据")
        
        except Exception as e:
            self.logger.error(f"查询工艺路线项目失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("查询生产订单BOM清单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送查询BOM清单请求
    3. 验证响应结果
    4. 保存BOM数据供后续使用
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查询生产订单BOM清单")
    def test_find_bom_items(self):
        """查询生产订单BOM清单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("根据生产版本更新物料组件服务")
                self.logger.debug(f"查询BOM清单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            "woTypeId": {"id": self.base_info["wo_type_info"]["id"]},
                            "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                            "matId": {"id": 14652007},
                            "prdMatId": {"id": 14408001},
                            "status": "DRAFT",
                            "confirmStatus": "UNCONFIRMED",
                            "deliveredStatus": "UNDELIVERED",
                            "qty": 10,
                            "prdUomId": {"id": 2004001},
                            "locId": {"id": 14336001},
                            "postInvTypeId": {"id": 2000001},
                            "mvmTypeId": {"id": 4010005},
                            "prdVrsId": {
                                "id": 14323001,
                                "invOrgId": {"id": 2110010},
                                "matId": {"id": 14652007},
                                "bomVrsId": {"id": 14403001}
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
                result = self.http.post(url, json=filtered_params, description="查询BOM清单")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取BOM清单列表
                response_data = result.get("data", {}).get("data", [])
                bom_items = response_data
                
                # 确保返回了BOM清单列表
                assert bom_items is not None, "未返回BOM清单列表"
                assert len(bom_items) > 0, "BOM清单列表为空"
                
                # 记录验证结果
                a.text(
                    f"BOM清单数量: {len(bom_items)}\n验证结果: 成功",
                    "验证结果"
                )

            with a.step("4. 保存BOM数据"):
                # 保存BOM数据到类变量，供后续测试用例使用
                TestPrdOrder.prd_order_info.update({
                    "bom_items": bom_items
                })
                
                self.logger.info(f"BOM清单查询成功 - 获取到{len(bom_items)}个物料")
                
                # 记录保存的数据
                a.json(TestPrdOrder.prd_order_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"查询BOM清单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("创建生产订单")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送创建生产订单请求
    3. 验证响应结果
    4. 保存生产订单信息
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("创建生产订单")
    def test_create_prd_order(self):
        """创建生产订单测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("生产订单维护服务")
                self.logger.debug(f"创建生产订单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 从之前查询的结果中获取工艺路线数据和BOM数据
                routing_items = self.prd_order_info.get("routing_items", [])
                bom_items = self.prd_order_info.get("bom_items", [])
                prd_vrs_id = self.prd_order_info.get("prdVrsId", {})
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            # 基本信息
                            "woTypeId": {"id": self.base_info["wo_type_info"]["id"]},
                            "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                            "matId": {"id": 14652007},
                            "prdMatId": {"id": 14408001},
                            "qty": 10,

                            # 状态信息
                            "status": "DRAFT",
                            "confirmStatus": "UNCONFIRMED",
                            "deliveredStatus": "UNDELIVERED",
                            "printed": False,

                            # 时间信息
                            "plannedStartDate": int(time.time() * 1000),
                            "plannedEndDate": int((time.time() + 24*60*60) * 1000),

                            # 单位与库位
                            "prdUomId": {"id": 2004001},
                            "locId": {"id": 14336001},
                            "postInvTypeId": {"id": 2000001},
                            "mvmTypeId": {"id": 4010005},

                            # 容差设置
                            "insufficientDeliveryTolerance": 0.3,
                            "excessiveDeliveryTolerance": 0.4,
                            "unlimitedOverDelivery": False,

                            # 工艺与物料清单
                            "prdVrsId": prd_vrs_id,
                            "routingList": routing_items,
                            "bomList": bom_items,
                        }
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="创建生产订单")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取生产订单ID和编号
                response_data = result.get("data", {}).get("data", {})
                wo_id = response_data.get("id")
                wo_code = response_data.get("woCode")
                
                # 确保返回了有效的生产订单ID和编号
                assert wo_id, "未返回生产订单ID"
                assert wo_code, "未返回生产订单编号"
                
                # 记录验证结果
                a.text(
                    f"生产订单ID: {wo_id}\n生产订单编号: {wo_code}\n验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存生产订单信息"):
                # 保存生产订单信息到类变量，供后续测试用例使用
                TestPrdOrder.prd_order_info.update({
                    "wo_id": wo_id,
                    "wo_code": wo_code
                })
                
                self.logger.info(f"生产订单创建成功 - ID: {wo_id}, 编号: {wo_code}")
                
                # 记录保存的数据
                a.json(TestPrdOrder.prd_order_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"创建生产订单失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPrdOrder()
    test.setup_class()
    test.test_find_routings_items() # 查询工艺路线项目
    test.test_find_bom_items()      # 查询BOM清单
    test.test_create_prd_order()    # 创建生产订单 