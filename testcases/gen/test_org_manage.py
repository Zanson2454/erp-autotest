"""
行政组织管理模块测试用例
包含组织保存、启用、编辑、停用等操作
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
import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("通用基础")
@allure.feature("行政组织管理")
class TestOrgStruct(GenBaseTest):
    """行政组织管理测试类"""
    
    # 保存组织相关信息的类变量，所有测试用例共享
    org_info = {}
    
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
        
        cls.logger.info("行政组织管理测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("保存行政组织")
    @allure.description(""" 
    ## 测试步骤
    1. 生成唯一的组织编码和名称
    2. 准备组织保存请求数据
    3. 发送保存组织API请求
    4. 验证返回结果是否成功
    5. 保存组织ID供后续测试使用
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("保存行政组织流程")
    @allure.tag("行政组织管理", "功能测试")
    def test_org_struct_save(self):
        try:
            with a.step("1. 生成组织基础信息"):
                # 使用时间戳和随机数生成唯一编码和名称
                timestamp = time.strftime("%Y%m%d%H%M%S")
                org_code = f"ORG{timestamp}{random.randint(1000, 9999)}"
                org_name = f"TEST_ORG_{random.randint(100, 999)}"
                remark = f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                # 记录生成的信息
                self.logger.info(f"生成组织编码: {org_code}, 名称: {org_name}")
                # 添加到报告中
                a.text(
                    f"组织编码: {org_code}\n组织名称: {org_name}",
                    "组织基本信息"
                )
                
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"保存行政组织API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgCode", "orgName", "orgSort", "orgDimensionCode","orgBusinessTypeIds","orgEnableDate"], 
                                ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["orgCode"] = org_code
                filtered_params['params']["request"]["orgName"] = org_name
                filtered_params['params']["request"]["orgSort"] = 1  # 组织排序
                filtered_params['params']["request"]["orgDimensionCode"] = "ADM_ORG_GRP"  # 组织维度代码
                filtered_params['params']["request"]["orgBusinessTypeIds"] = [2010001]  # 组织业务类型ID
                # 生成当前日期作为启用日期
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                filtered_params['params']["request"]["orgEnableDate"] = current_date  # 使用当前日期作为启用日期
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")

            with a.step("3. 发送请求并验证响应"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="保存行政组织")
                # 添加响应数据到报告
                a.json(result, "响应数据")

            with a.step("4. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                # 从响应中获取组织ID
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                # 确保返回了有效的ID
                assert org_id, "保存行政组织失败：返回的ID为空"
                # 记录验证结果
                a.text(
                    f"组织ID: {org_id}\n验证结果: 成功",
                    "验证结果"
                )

            with a.step("5. 保存测试数据"):
                # 保存测试数据到类变量，供后续测试用例使用
                TestOrgStruct.org_info.update({
                    "org_id": org_id,
                    "org_code": org_code,
                    "org_name": org_name
                })
                self.logger.info(f"保存行政组织成功 - ID: {org_id}, 编码: {org_code}")
                # 记录保存的数据
                a.json(TestOrgStruct.org_info, "保存的组织数据")

        except Exception as e:
            self.logger.error(f"保存行政组织失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("启用行政组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送启用请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("启用行政组织流程")
    @allure.tag("行政组织管理", "功能测试")
    def test_org_struct_enable(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保org_info中有数据
                assert TestOrgStruct.org_info.get("org_id"), "未找到待启用的组织ID，请先执行保存行政组织测试"
                
                # 添加到报告中
                a.json(TestOrgStruct.org_info, "待启用组织信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("ORG-组织管理-启动EHR组织单元服务")
                self.logger.debug(f"行政组织启用API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                 ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestOrgStruct.org_info["org_id"]                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送启用请求"):
                # 发送启用请求
                result = self.http.post(url, json=filtered_params, description="启用行政组织")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"行政组织启用成功 - ID: {TestOrgStruct.org_info['org_id']}", "验证结果")
                
                self.logger.info(f"行政组织启用成功 - ID: {TestOrgStruct.org_info['org_id']}")
            
        except Exception as e:
            self.logger.error(f"启用行政组织失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("编辑行政组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 生成新的组织名称
    3. 准备编辑请求数据
    4. 发送编辑请求
    5. 验证响应结果
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("编辑行政组织流程")
    @allure.tag("行政组织管理", "功能测试")
    def test_org_struct_edit(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保org_info中有数据
                assert TestOrgStruct.org_info.get("org_id"), "未找到待编辑的组织ID，请先执行保存行政组织测试"
                
                # 添加到报告中
                a.json(TestOrgStruct.org_info, "待编辑组织信息")
            
            with a.step("2. 生成新的组织名称"):
                # 生成新的组织名称（添加EDIT标识）
                new_org_name = f"{TestOrgStruct.org_info['org_name']}_EDIT_{random.randint(100, 999)}"
                self.logger.info(f"新的组织名称: {new_org_name}")
                
                # 添加到报告中
                a.text(f"新的组织名称: {new_org_name}", "编辑信息")
            
            with a.step("3. 准备编辑请求数据"):
                # 获取API路径（与保存使用相同的API路径，但传入ID）
                api_path = self.get_api_path("ORG-组织管理-保存EHR组织单元服务")
                self.logger.debug(f"编辑行政组织API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["id", "orgCode", "orgName", "orgSort", "orgDimensionCode", "orgBusinessTypeIds", "orgEnableDate"], 
                                ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestOrgStruct.org_info["org_id"]  # 设置组织ID
                filtered_params['params']["request"]["orgCode"] = TestOrgStruct.org_info["org_code"]  # 保持原编码不变
                filtered_params['params']["request"]["orgName"] = new_org_name  # 设置新名称
                filtered_params['params']["request"]["orgSort"] = 1  # 组织排序
                filtered_params['params']["request"]["orgDimensionCode"] = "ADM_ORG_GRP"  # 组织维度代码
                filtered_params['params']["request"]["orgBusinessTypeIds"] = [2010001]  # 组织业务类型ID
                
                # 生成当前日期作为启用日期
                current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                filtered_params['params']["request"]["orgEnableDate"] = current_date
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("4. 发送编辑请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="编辑行政组织")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("5. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                
                # 从响应中获取组织ID，应与原ID相同
                response_data = result.get("data", {}).get("data", {})
                org_id = response_data.get("id")
                
                # 确保返回了有效的ID，且与原ID一致
                assert org_id, "编辑行政组织失败：返回的ID为空"
                assert org_id == TestOrgStruct.org_info["org_id"], "编辑行政组织失败：返回的ID与原ID不一致"
                
                # 记录验证结果
                a.text(
                    f"编辑组织成功\n组织ID: {org_id}\n新组织名称: {new_org_name}",
                    "验证结果"
                )
                
                # 更新测试数据
                TestOrgStruct.org_info["org_name"] = new_org_name
                self.logger.info(f"编辑行政组织成功 - ID: {org_id}, 新名称: {new_org_name}")
                
                # 记录更新后的数据
                a.json(TestOrgStruct.org_info, "更新后的组织数据")
                
        except Exception as e:
            self.logger.error(f"编辑行政组织失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=4)
    @allure.story("停用行政组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送停用请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("停用行政组织流程")
    @allure.tag("行政组织管理", "功能测试")
    def test_org_struct_disable(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保org_info中有数据
                assert TestOrgStruct.org_info.get("org_id"), "未找到待停用的组织ID，请先执行保存行政组织测试"
                
                # 添加到报告中
                a.json(TestOrgStruct.org_info, "待停用组织信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("ORG-组织管理-停用组织EHR组织单元服务")
                self.logger.debug(f"停用行政组织API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                 ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestOrgStruct.org_info["org_id"]
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送停用请求"):
                # 发送停用请求
                result = self.http.post(url, json=filtered_params, description="停用行政组织")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"行政组织停用成功 - ID: {TestOrgStruct.org_info['org_id']}", "验证结果")
                
                self.logger.info(f"行政组织停用成功 - ID: {TestOrgStruct.org_info['org_id']}")
            
        except Exception as e:
            self.logger.error(f"停用行政组织失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=5)
    @allure.story("查询行政组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备查询条件
    3. 发送查询请求
    4. 验证查询结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("精确查询行政组织流程")
    @allure.tag("行政组织管理", "功能测试")
    def test_org_struct_query(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保org_info中有组织名称
                assert TestOrgStruct.org_info.get("org_name"), "未找到待查询的组织名称，请先执行保存行政组织测试"
                
                # 添加到报告中
                a.json(TestOrgStruct.org_info, "待查询组织信息")
            
            with a.step("2. 准备查询条件"):
                # 获取API路径
                api_path = self.get_api_path("ORG-新版组织-搜索服务")
                self.logger.debug(f"查询行政组织API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                ["orgName", "orgStatus", "orgDimensionCode"], ["params", "request"])
                
                # 设置查询条件
                filtered_params['params']["request"]["orgStatus"] = ["ENABLED","INACTIVE", "DRAFT", "DISABLED"] 
                filtered_params['params']["request"]["orgName"] = TestOrgStruct.org_info["org_name"]
                filtered_params['params']["request"]["orgDimensionCode"] = "ADM_ORG_GRP"
                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送查询请求"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="查询行政组织")
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证查询结果"):
                # 验证响应成功
                self.assert_util.assert_response_success(result)
                
                # 获取响应数据
                response_data = result.get("data", {}).get("data", [])
                
                # 验证查询结果不为空
                assert response_data, "未查询到组织数据"
                
                # 验证查询结果是否匹配
                found = False
                for org in response_data:
                    if org.get("orgName") == TestOrgStruct.org_info["org_name"]:
                        found = True
                        break
                
                assert found, f"未找到名称为 {TestOrgStruct.org_info['org_name']} 的组织"
                
                # 记录验证结果
                a.text(
                    f"查询到组织数据，名称匹配成功: {TestOrgStruct.org_info['org_name']}\n验证结果: 成功",
                    "验证结果"
                )
                
                self.logger.info(f"查询行政组织成功 - 名称: {TestOrgStruct.org_info['org_name']}")
            
        except Exception as e:
            self.logger.error(f"查询行政组织失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=6)
    @allure.story("删除行政组织")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送删除请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("删除行政组织流程")
    @allure.tag("行政组织管理", "功能测试")
    def test_org_struct_delete(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保org_info中有数据且组织已停用
                assert TestOrgStruct.org_info.get("org_id"), "未找到待删除的组织ID，请先执行保存行政组织测试"
                
                # 添加到报告中
                a.json(TestOrgStruct.org_info, "待删除组织信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("ORG-组织管理-删除EHR组织单元服务")
                self.logger.debug(f"删除行政组织API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                 ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestOrgStruct.org_info["org_id"]
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送删除请求"):
                # 发送删除请求
                result = self.http.post(url, json=filtered_params, description="删除行政组织")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"行政组织删除成功 - ID: {TestOrgStruct.org_info['org_id']}", "验证结果")
                
                self.logger.info(f"行政组织删除成功 - ID: {TestOrgStruct.org_info['org_id']}")
                
                # 清除组织信息
                TestOrgStruct.org_info = {}
                a.text("组织数据已清除", "数据清理")
            
        except Exception as e:
            self.logger.error(f"删除行政组织失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestOrgStruct()
    test.setup_class()
    test.test_org_struct_save()    # 保存行政组织
    test.test_org_struct_enable()   # 启用行政组织
    test.test_org_struct_edit()     # 编辑行政组织
    test.test_org_struct_disable()  # 停用行政组织
    test.test_org_struct_query()    # 查询行政组织
    test.test_org_struct_delete()   # 删除行政组织