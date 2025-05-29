"""
合作伙伴模块测试用例
包含新增、查询、启用、停用、删除等操作
"""
import sys
import time
import json
import random
import allure
import pytest
from pathlib import Path
from testcases.gen import GenBaseTest
from utils.allure_simple import a  # 导入简化的Allure辅助类
from utils.param_util import ParamUtil  # 导入参数处理工具类

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("通用基础")
@allure.feature("合作伙伴管理")
class TestPartners(GenBaseTest):
    """合作伙伴管理测试类"""
    
    # 保存合作伙伴相关信息的类变量，所有测试用例共享
    partner_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 初始化日志记录器
        """
        # 调用GenBaseTest的初始化方法
        # 这会初始化logger、http客户端、断言工具和YAML处理器等
        super().setup_class()
        
        cls.logger.info("合作伙伴测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("新增合作伙伴")
    @allure.description("""
    ## 测试步骤
    1. 生成合作伙伴基础信息
    2. 准备请求数据
    3. 发送新增请求
    4. 验证响应结果
    5. 保存测试数据
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("新增合作伙伴流程")
    @allure.tag("合作伙伴管理", "功能测试")
    def test_partner_add(self):
        try:
            with a.step("1. 生成合作伙伴基础信息"):
                # 使用时间戳和随机数生成唯一编码和名称
                timestamp = time.strftime("%Y%m%d%H%M%S")
                partner_code = f"PAR{timestamp}{random.randint(1000, 9999)}"
                partner_name = f"TEST_PARTNER_{random.randint(100, 999)}"
                remark = f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                
                # 记录生成的信息
                self.logger.info(f"生成合作伙伴编码: {partner_code}, 名称: {partner_name}")
                # 添加到报告中
                a.text(
                    f"合作伙伴编码: {partner_code}\n合作伙伴名称: {partner_name}\n备注: {remark}",
                    "合作伙伴基本信息"
                )
                
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-合作伙伴-合作伙伴保存服务")
                self.logger.debug(f"合作伙伴新增API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["code", "name","classType","status","partnerTypeId","partnerIdentity"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["code"] = partner_code
                filtered_params['params']["request"]["name"] = partner_name
                filtered_params['params']["request"]["classType"] = "COMPANY"
                filtered_params['params']["request"]["status"] = "INACTIVE"
                filtered_params['params']["request"]["partnerTypeId"] = {"id":2011001}
                filtered_params['params']["request"]["partnerIdentity"] = ["SUPPLIER"]
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送新增请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="新增合作伙伴")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取合作伙伴ID
                response_data = result.get("data", {}).get("data", {})
                partner_id = response_data.get("id")
                
                # 确保返回了有效的ID
                assert partner_id, "新增合作伙伴失败：返回的ID为空"
                
                # 记录验证结果
                a.text(
                    f"合作伙伴ID: {partner_id}\n验证结果: 成功",
                    "验证结果"
                )
            
            with a.step("5. 保存测试数据"):
                # 保存测试数据到类变量，供后续测试用例使用
                TestPartners.partner_info.update({
                    "partner_id": partner_id,
                    "partner_code": partner_code,
                    "partner_name": partner_name
                })
                
                self.logger.info(f"新增合作伙伴成功 - ID: {partner_id}, 编码: {partner_code}")
                
                # 记录保存的数据
                a.json(TestPartners.partner_info, "保存的合作伙伴数据")
            
        except Exception as e:
            self.logger.error(f"新增合作伙伴失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("查询合作伙伴")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备查询参数
    3. 发送查询请求
    4. 验证响应结果
    5. 验证查询内容
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("查询合作伙伴流程")
    @allure.tag("合作伙伴管理", "功能测试")
    def test_partner_search(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保partner_info中有数据
                assert TestPartners.partner_info.get("partner_code"), "未找到要查询的合作伙伴编码，请先执行新增用例"
                
                # 添加到报告中
                a.json(TestPartners.partner_info, "待查询合作伙伴信息")
            
            with a.step("2. 准备查询参数"):
                # 获取API路径
                api_path = self.get_api_path("合作伙伴-分页数据服务")
                self.logger.debug(f"合作伙伴查询API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                              ["conditionItems", "pageable"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["pageable"]["conditionItems"] = {
                        "conditions": {
                            "code": {
                                "operator": "CONTAINS",
                                "value": TestPartners.partner_info["partner_code"]
                            }
                        },
                    }
                filtered_params['params']["request"]['pageable']["pageNo"] = 1
                filtered_params['params']["request"]['pageable']["pageSize"] = 20
                filtered_params['params']["request"]["pageable"]['sortOrders'] = None
                self.logger.info(f"查询的合作伙伴编码: {TestPartners.partner_info['partner_code']}")
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送查询请求"):
                # 发送查询请求
                result = self.http.post(url, json=filtered_params, description="查询合作伙伴")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 获取响应数据
                response_data = result.get("data", {}).get("data", {})
                
                # 验证总数大于0
                total = response_data.get("total", 0)
                assert total > 0, "查询结果总数为0"
                
                # 记录验证结果
                a.text(f"查询合作伙伴总数: {total}", "验证结果 - 总数")
            
            with a.step("5. 验证查询内容"):
                # 获取数据列表
                data_list = response_data.get("data", [])
                
                # 验证返回的数据列表不为空
                assert data_list, "查询结果为空"
                
                # 验证查询结果包含新增的合作伙伴编码
                found = any(item.get("code") == TestPartners.partner_info["partner_code"] for item in data_list)
                assert found, f"未找到合作伙伴编码: {TestPartners.partner_info['partner_code']}"
                
                # 记录验证结果
                a.text(
                    f"查询结果项数: {len(data_list)}\n包含目标编码: {found}",
                    "验证结果 - 内容"
                )
                
                # 添加查询到的第一条记录到报告
                if data_list:
                    a.json(data_list[0], "查询结果示例")
                
                self.logger.info(f"查询合作伙伴成功 - 总数: {total}")
            
        except Exception as e:
            self.logger.error(f"查询合作伙伴失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("启用合作伙伴")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送启用请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER) 
    @allure.title("启用合作伙伴流程")
    @allure.tag("合作伙伴管理", "功能测试")
    def test_partner_enable(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保partner_info中有数据
                assert TestPartners.partner_info.get("partner_id"), "未找到要启用的合作伙伴ID，请先执行新增用例"
                
                # 添加到报告中
                a.json(TestPartners.partner_info, "待启用合作伙伴信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-合作伙伴-合作伙伴启动服务")
                self.logger.debug(f"合作伙伴启用API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestPartners.partner_info["partner_id"]
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送启用请求"):
                # 发送启用请求
                result = self.http.post(url, json=filtered_params, description="启用合作伙伴")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"合作伙伴启用成功 - ID: {TestPartners.partner_info['partner_id']}", "验证结果")
                
                self.logger.info(f"启用合作伙伴成功 - ID: {TestPartners.partner_info['partner_id']}")
            
        except Exception as e:
            self.logger.error(f"启用合作伙伴失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.story("停用合作伙伴")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送停用请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER) 
    @allure.title("停用合作伙伴流程")
    @allure.tag("合作伙伴管理", "功能测试")
    def test_partner_disable(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保partner_info中有数据
                assert TestPartners.partner_info.get("partner_id"), "未找到要停用的合作伙伴ID，请先执行新增用例"
                
                # 添加到报告中
                a.json(TestPartners.partner_info, "待停用合作伙伴信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-合作伙伴-合作伙伴停用服务")
                self.logger.debug(f"合作伙伴停用API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestPartners.partner_info["partner_id"]
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送停用请求"):
                # 发送停用请求
                result = self.http.post(url, json=filtered_params, description="停用合作伙伴")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"合作伙伴停用成功 - ID: {TestPartners.partner_info['partner_id']}", "验证结果")
                
                self.logger.info(f"停用合作伙伴成功 - ID: {TestPartners.partner_info['partner_id']}")
            
        except Exception as e:
            self.logger.error(f"停用合作伙伴失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
    @allure.story("删除合作伙伴")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送删除请求
    4. 验证响应结果
    5. 清理测试数据
    """)
    @allure.severity(allure.severity_level.BLOCKER) 
    @allure.title("删除合作伙伴流程")
    @allure.tag("合作伙伴管理", "功能测试")
    def test_partner_delete(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保partner_info中有数据
                assert TestPartners.partner_info.get("partner_id"), "未找到要删除的合作伙伴ID，请先执行新增用例"
                
                # 添加到报告中
                a.json(TestPartners.partner_info, "待删除合作伙伴信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-合作伙伴-删除服务")
                self.logger.debug(f"合作伙伴删除API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestPartners.partner_info["partner_id"]
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送删除请求"):
                # 发送删除请求
                result = self.http.post(url, json=filtered_params, description="删除合作伙伴")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应结果
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"合作伙伴删除成功 - ID: {TestPartners.partner_info['partner_id']}", "验证结果")
                
                self.logger.info(f"删除合作伙伴成功 - ID: {TestPartners.partner_info['partner_id']}")
            
            with a.step("5. 清理测试数据"):
                # 记录待清理的数据
                a.json(TestPartners.partner_info, "待清理的数据")
                
                # 清空测试数据，避免后续测试误用
                TestPartners.partner_info = {}
                
                # 记录清理结果
                a.text("测试数据已清理完成", "清理结果")
            
        except Exception as e:
            self.logger.error(f"删除合作伙伴失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestPartners()
    test.setup_class()
    test.test_partner_add()    # 新增合作伙伴
    test.test_partner_search() # 查询合作伙伴
    test.test_partner_enable() # 启用合作伙伴
    test.test_partner_disable() # 停用合作伙伴
    test.test_partner_delete() # 删除合作伙伴