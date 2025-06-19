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
from testcases.prd.order import PrdBaseTest
from utils.report_util import a
from utils.param_util import ParamUtil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("生产管理")
@allure.feature("生产订单管理")
class TestPrdOrder(PrdBaseTest):
    """生产订单管理测试类"""
    
    # 保存测试过程中的数据
    prd_order_info = {}
    
    # 定义基础数量
    base_qty = 10
    
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
    @allure.story("查询物料生产视图")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送查询物料生产视图请求
    3. 验证响应结果
    4. 保存物料生产视图数据供后续使用
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("根据生产工厂和物料查询物料生产视图")
    def test_find_prd_mat_view(self):
        """根据生产工厂和物料查询物料生产视图测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = ParamUtil.get_api_path(self.apis, "根据生产工厂和物料查询物料生产视图服务")
                self.logger.debug(f"查询物料生产视图API路径: {api_path}")
                
                # 获取请求参数
                params, url = ParamUtil.get_api_params(self.api_params, api_path)
                
                # 设置必要参数值
                filtered_params = ParamUtil.filter_post_body_fields(
                    params,
                    ["invOrgId", "genMatMdId"],
                    ["params", "request"]
                )
                ParamUtil.set_request_params(filtered_params, {
                    "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                    "genMatMdId": {"id": self.base_info["prd_mat_info"]["id"]}
                })
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params)
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取物料生产视图数据
                response_data = result.get("data", {}).get("data", {})
                
                # 确保返回了物料生产视图数据
                assert response_data, "未返回物料生产视图数据"
                assert response_data.get("id"), "未返回物料生产视图ID"
                
                # 获取容差字段
                insufficient_tolerance = response_data.get("insufficientDeliveryTolerance", 0)
                excessive_tolerance = response_data.get("excessiveDeliveryTolerance", 0)
                unlimited_over_delivery = response_data.get("unlimitedOverDelivery", False)
                
                # 记录验证结果
                a.text(
                    f"物料生产视图ID: {response_data.get('id')}\n"
                    f"欠交容差: {insufficient_tolerance}\n"
                    f"超交容差: {excessive_tolerance}\n"
                    f"无限制超交: {unlimited_over_delivery}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存物料生产视图数据"):
                # 保存物料生产视图数据到类变量，供后续测试用例使用
                TestPrdOrder.prd_order_info.update({
                    "prd_mat_view_info": response_data,
                    "insufficient_tolerance": insufficient_tolerance,
                    "excessive_tolerance": excessive_tolerance,
                    "unlimited_over_delivery": unlimited_over_delivery
                })
                
                self.logger.info(f"物料生产视图查询成功 - ID: {response_data.get('id')}")
                
                # 记录保存的数据
                a.json(TestPrdOrder.prd_order_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"查询物料生产视图失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("初始化计划完工时间")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送初始化计划完工时间请求
    3. 验证响应结果
    4. 保存计划时间数据供后续使用
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("初始化计划完工时间")
    def test_init_planned_end_date(self):
        """初始化计划完工时间测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("生产订单维护-计划结束时间初始化服务")
                self.logger.debug(f"初始化计划完工时间API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置计划开始时间为当前时间
                planned_start_date = int(time.time() * 1000)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            "invOrgId": {
                                "id": self.base_info["inv_org_info"]["id"]
                            },
                            "plannedStartDate": planned_start_date,
                            "matId": {
                                "id": self.base_info["prd_mat_info"]["id"]
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
                result = self.http.post(url, json=filtered_params, description="初始化计划完工时间")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取计划完工时间
                response_data = result.get("data", {}).get("data", {})
                planned_end_date = response_data.get("plannedEndDate")
                
                # 确保返回了计划完工时间
                assert planned_end_date, "未返回计划完工时间"
                
                # 记录验证结果
                a.text(
                    f"计划开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(planned_start_date/1000))}\n"
                    f"计划完工时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(planned_end_date/1000))}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存计划时间数据"):
                # 保存计划时间数据到类变量，供后续测试用例使用
                TestPrdOrder.prd_order_info.update({
                    "planned_start_date": planned_start_date,
                    "planned_end_date": planned_end_date
                })
                
                self.logger.info(f"计划时间初始化成功")
                
                # 记录保存的数据
                a.json(TestPrdOrder.prd_order_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"初始化计划完工时间失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("查询生产版本")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送查询生产版本请求
    3. 验证响应结果
    4. 保存生产版本数据供后续使用
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("根据物料查询生产版本")
    def test_find_prd_version(self):
        """根据物料查询生产版本测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("根据物料获取生产版本服务")
                self.logger.debug(f"查询生产版本API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            "woTypeId": {"id": self.base_info["wo_type_info"]["id"]},
                            "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                            "qty": self.base_qty,
                            "plannedStartDate": self.prd_order_info["planned_start_date"],
                            "plannedEndDate": self.prd_order_info["planned_end_date"],
                            "matId": {"id": self.base_info["prd_mat_info"]["id"]},
                            "pageable": {
                                "pageNo": 1,
                                "pageSize": 20,
                                "conditionGroup": None,
                                "sortOrders": None,
                                "keyword": None
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
                result = self.http.post(url, json=filtered_params, description="查询生产版本")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取生产版本数据列表
                response_data = result.get("data", {}).get("data", [])
                
                # 确保返回了生产版本数据
                assert response_data, "未返回生产版本数据"
                assert len(response_data) > 0, "生产版本列表为空"
                
                # 获取第一个生产版本数据
                version_data = response_data[0]
                assert version_data.get("id"), "未返回生产版本ID"
                
                # 记录验证结果
                a.text(
                    f"生产版本ID: {version_data.get('id')}\n"
                    f"生产版本编码: {version_data.get('prdVrsCode')}\n"
                    f"生产版本名称: {version_data.get('prdVrsName')}\n"
                    f"验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("4. 保存生产版本数据"):
                # 保存生产版本数据到类变量，供后续测试用例使用
                TestPrdOrder.prd_order_info.update({
                    "prd_version_info": version_data
                })
                
                self.logger.info(f"生产版本查询成功 - ID: {version_data.get('id')}")
                
                # 记录保存的数据
                a.json(TestPrdOrder.prd_order_info, "保存的测试数据")
        
        except Exception as e:
            self.logger.error(f"查询生产版本失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.story("查询生产订单移动类型")
    @allure.description("""
    ## 测试步骤
    1. 准备请求数据
    2. 发送查询移动类型请求
    3. 验证响应结果
    4. 保存移动类型信息
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查询生产订单移动类型")
    def test_query_mvm_type_id(self):
        """查询生产订单移动类型测试用例"""
        try:
            with a.step("1. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("生产订单头查移动类型")
                self.logger.debug(f"查询移动类型API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                            "woTypeId": self.base_info["wo_type_info"]["id"],
                            "postInvTypeId":self.prd_order_info["prd_mat_view_info"]["postInvTypeId"]
                    }
                }
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("2. 发送请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="查询移动类型")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("3. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取移动类型ID
                mvm_type_id = result.get("data", {}).get("data", {}).get("id")
                assert mvm_type_id, "未返回移动类型ID"
                
                # 记录验证结果
                a.text(f"移动类型ID: {mvm_type_id}", "验证结果")
            
            with a.step("4. 保存移动类型信息"):
                # 保存移动类型ID到测试数据中
                self.prd_order_info["mvm_type_id"] = mvm_type_id
                
                self.logger.info(f"保存移动类型ID: {mvm_type_id}")
                a.json(self.prd_order_info, "保存的测试数据")
                
        except Exception as e:
            self.logger.error(f"查询移动类型失败: {str(e)}")
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
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
                            "plannedStartDate": self.prd_order_info["planned_start_date"],
                            "plannedEndDate": self.prd_order_info["planned_end_date"],
                            "matId": {"id": self.base_info["prd_mat_info"]["id"]},
                            "prdMatId": {"id": self.prd_order_info["prd_mat_view_info"]["id"]},
                            
                            # 状态信息
                            "status": "DRAFT",
                            "confirmStatus": "UNCONFIRMED",
                            "deliveredStatus": "UNDELIVERED",
                            
                            # 数量和单位
                            "qty": self.base_qty,
                            "prdUomId": {"id": self.prd_order_info["prd_mat_view_info"]["prdUomId"]["id"]},
                            "locId": {"id": self.prd_order_info["prd_mat_view_info"]["invLocId"]["id"]},
                            
                            # 库存相关
                            "postInvTypeId": {"id": self.prd_order_info["prd_mat_view_info"]["postInvTypeId"]},
                            "mvmTypeId": {"id": self.prd_order_info["mvm_type_id"]},
                            
                            # 生产版本信息
                            "prdVrsId": {"id": self.prd_order_info["prd_version_info"]["id"]},
                            "matCode": self.base_info["prd_mat_info"]["mat_code"],
                            "matName": self.base_info["prd_mat_info"]["mat_name"],
                            "invLocId": self.prd_order_info["prd_mat_view_info"]["invLocId"]["id"],
                            "invOrgId": self.base_info["inv_org_info"]["id"]
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

    @pytest.mark.run(order=6)
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
                api_path = self.get_api_path("根据生产版本获取物料组件服务")
                self.logger.debug(f"查询BOM清单API路径: {api_path}")
                
                # 获取请求参数
                params, url = self.get_api_params(api_path)
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            "woTypeId": {
                                "id": self.base_info["wo_type_info"]["id"]
                            },
                            "invOrgId": {
                                "id": self.base_info["inv_org_info"]["id"]
                            },
                            "matId": {
                                "id": self.base_info["prd_mat_info"]["id"]
                            },
                            "status": "DRAFT",
                            "confirmStatus": "UNCONFIRMED",
                            "deliveredStatus": "UNDELIVERED",
                            "prdMatId": {
                                "id": self.prd_order_info["prd_mat_view_info"]["id"]
                            },
                            "qty": self.base_qty,
                            "prdUomId": {
                                "id": self.prd_order_info["prd_mat_view_info"]["prdUomId"]["id"]
                            },
                            "insufficientDeliveryTolerance": self.prd_order_info["insufficient_tolerance"],
                            "unlimitedOverDelivery": self.prd_order_info["unlimited_over_delivery"],
                            "excessiveDeliveryTolerance": self.prd_order_info["excessive_tolerance"],
                            "plannedStartDate": self.prd_order_info["planned_start_date"],
                            "plannedEndDate": self.prd_order_info["planned_end_date"],
                            "locId": {
                                "id": self.prd_order_info["prd_mat_view_info"]["invLocId"]["id"]
                            },
                            "postInvTypeId": {
                                "id": self.prd_order_info["prd_mat_view_info"]["postInvTypeId"]
                            },
                            "mvmTypeId": {
                                "id": self.prd_order_info["mvm_type_id"]
                            },
                            "prdVrsId": {
                                "id": self.prd_order_info["prd_version_info"]["id"]
                            },
                            "routingList": [],
                            "bomList": []
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

    @pytest.mark.run(order=7)
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
                
                # 设置必要参数值
                filtered_params = {
                    "params": {
                        "request": {
                            # 基本信息
                            "woTypeId": {"id": self.base_info["wo_type_info"]["id"]},
                            "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                            "matId": {"id": self.base_info["prd_mat_info"]["id"]},
                            "prdMatId": {"id": self.prd_order_info["prd_mat_view_info"]["id"]},
                            "qty": self.base_qty,

                            # 状态信息
                            "status": "DRAFT",
                            "confirmStatus": "UNCONFIRMED",
                            "deliveredStatus": "UNDELIVERED",
                            "printed": False,

                            # 时间信息
                            "plannedStartDate": self.prd_order_info["planned_start_date"],
                            "plannedEndDate": self.prd_order_info["planned_end_date"],

                            # 单位与库位
                            "prdUomId": {"id": self.prd_order_info["prd_mat_view_info"]["prdUomId"]["id"]},
                            "locId": {"id": self.prd_order_info["prd_mat_view_info"]["invLocId"]["id"]},
                            "postInvTypeId": {"id": self.prd_order_info["prd_mat_view_info"]["postInvTypeId"]},
                            "mvmTypeId": {"id": self.prd_order_info["mvm_type_id"]},

                            # 容差设置
                            "insufficientDeliveryTolerance": self.prd_order_info["insufficient_tolerance"],
                            "excessiveDeliveryTolerance": self.prd_order_info["excessive_tolerance"],
                            "unlimitedOverDelivery": self.prd_order_info["unlimited_over_delivery"],

                            # 工艺与物料清单
                            "prdVrsId": {
                                "id": self.prd_order_info["prd_version_info"]["id"],
                                "invOrgId": {"id": self.base_info["inv_org_info"]["id"]},
                                "matId": {"id": self.base_info["prd_mat_info"]["id"]},
                                "bomVrsId": {"id": self.prd_order_info["prd_version_info"]["bomVrsId"]["id"]}
                            },
                            "routingList": routing_items,
                            "bomList": bom_items
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
    test.test_find_prd_mat_view()    # 查询物料生产视图
    test.test_init_planned_end_date() # 初始化计划完工时间
    test.test_find_prd_version()      # 查询生产版本
    test.test_query_mvm_type_id()     # 查询移动类型
    test.test_find_routings_items()   # 查询工艺路线项目
    test.test_find_bom_items()        # 查询BOM清单
    test.test_create_prd_order()      # 创建生产订单 