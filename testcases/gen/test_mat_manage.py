"""
物料管理模块测试用例
包含新增、启用、停用等操作
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
@allure.feature("物料管理")
class TestMatAdd(GenBaseTest):
    """物料管理测试类"""
    
    # 保存物料相关信息的类变量，所有测试用例共享
    mat_info = {}
    
    @classmethod
    def setup_class(cls):
        """
        测试类初始化
        1. 调用父类初始化方法
        2. 获取物料管理模块的API配置
        """
        # 调用GenBaseTest的初始化方法
        # 这会初始化logger、http客户端、断言工具和YAML处理器等
        super().setup_class()
        
        cls.logger.info("物料管理测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("新增物料")
    @allure.description(""" 
    ## 测试步骤
    1. 生成唯一的物料编码和名称
    2. 准备物料创建请求数据
    3. 发送创建物料API请求
    4. 验证返回结果是否成功
    5. 保存物料ID供后续测试使用
    """)
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("新增物料流程")
    @allure.tag("物料管理", "功能测试")
    def test_mat_add(self):
        try:
            with a.step("1. 生成物料基础信息"):
                # 使用时间戳和随机数生成唯一编码和名称
                timestamp = time.strftime("%Y%m%d%H%M%S")
                mat_code = f"MAT{timestamp}{random.randint(1000, 9999)}"
                mat_name = f"TEST_MAT_{random.randint(100, 999)}"
                remark = f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
                # 记录生成的信息
                self.logger.info(f"生成物料编码: {mat_code}, 名称: {mat_name}")
                # 添加到报告中
                a.text(
                    f"物料编码: {mat_code}\n物料名称: {mat_name}\n备注: {remark}",
                    "物料基本信息"
                )
                
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-物料保存清除缓存服务")
                self.logger.debug(f"物料新增API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                 ["mat_code", "mat_name","cateId","genMatTypeCfId", "baseUomId", "status", "remark","matCharaClassList"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["mat_code"] = mat_code
                filtered_params['params']["request"]["mat_name"] = mat_name
                filtered_params['params']["request"]["remark"] = remark
                
                filtered_params['params']["request"]["cateId"] = {"id":2000001}
                filtered_params['params']["request"]["genMatTypeCfId"] = {"id":2000001}
                filtered_params['params']["request"]["baseUomId"] = {"id":2000001}
                filtered_params['params']["request"]["status"] = "INACTIVE"
                filtered_params['params']["request"]["matCharaClassList"] = []
            
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")

            with a.step("3. 发送请求并验证响应"):
                # 发送请求
                result = self.http.post(url, json=filtered_params, description="新增物料")
                # 添加响应数据到报告
                a.json(result, "响应数据")

            with a.step("4. 验证响应结果"):
                # 验证响应中的success字段为True
                self.assert_util.assert_response_success(result)
                # 从响应中获取物料ID
                response_data = result.get("data", {}).get("data", {})
                mat_id = response_data.get("id")
                # 确保返回了有效的ID
                assert mat_id, "新增物料失败：返回的ID为空"
                # 记录验证结果
                a.text(
                    f"物料ID: {mat_id}\n验证结果: 成功",
                    "验证结果"
                )

            with a.step("5. 保存测试数据"):
                # 保存测试数据到类变量，供后续测试用例使用
                TestMatAdd.mat_info.update({
                    "mat_id": mat_id,
                    "mat_code": mat_code,
                    "mat_name": mat_name
                })
                self.logger.info(f"新增物料成功 - ID: {mat_id}, 编码: {mat_code}")
                # 记录保存的数据
                a.json(TestMatAdd.mat_info, "保存的物料数据")

        except Exception as e:
            self.logger.error(f"新增物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=2)
    @allure.story("启用物料")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送启用请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("启用物料流程")
    @allure.tag("物料管理", "功能测试")
    def test_mat_enable(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保mat_info中有数据
                assert TestMatAdd.mat_info.get("mat_id"), "未找到待启用的物料ID，请先执行新增物料测试"
                
                # 添加到报告中
                a.json(TestMatAdd.mat_info, "待启用物料信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-物料启用清除缓存服务")
                self.logger.debug(f"物料启用API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                 ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestMatAdd.mat_info["mat_id"]                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送启用请求"):
                # 发送启用请求
                result = self.http.post(url, json=filtered_params, description="启用物料")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"物料启用成功 - ID: {TestMatAdd.mat_info['mat_id']}", "验证结果")
                
                self.logger.info(f"物料启用成功 - ID: {TestMatAdd.mat_info['mat_id']}")
            
        except Exception as e:
            self.logger.error(f"启用物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

    @pytest.mark.run(order=3)
    @allure.story("停用物料")
    @allure.description("""
    ## 测试步骤
    1. 验证前置条件
    2. 准备请求数据
    3. 发送停用请求
    4. 验证响应结果
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("停用物料流程")
    @allure.tag("物料管理", "功能测试")
    def test_mat_disable(self):
        try:
            with a.step("1. 验证前置条件"):
                # 验证前置条件 - 确保mat_info中有数据
                assert TestMatAdd.mat_info.get("mat_id"), "未找到待停用的物料ID，请先执行新增物料测试"
                
                # 添加到报告中
                a.json(TestMatAdd.mat_info, "待停用物料信息")
            
            with a.step("2. 准备请求数据"):
                # 获取API路径
                api_path = self.get_api_path("GEN-物料停用清除缓存服务")
                self.logger.debug(f"物料停用API路径: {api_path}")
                
                # 获取请求参数和完整URL
                params, url = self.get_api_params(api_path)
                
                # 使用ParamUtil过滤字段，同时保留嵌套结构
                filtered_params = ParamUtil.filter_post_body_fields(params, 
                                 ["id"], ["params", "request"])
                
                # 设置必要参数值
                filtered_params['params']["request"]["id"] = TestMatAdd.mat_info["mat_id"]                
                self.logger.info(f"请求URL: {url}")
                self.logger.info(f"请求参数: {filtered_params}")
                # 添加请求数据到报告
                a.json(filtered_params, "请求数据")
            
            with a.step("3. 发送停用请求"):
                # 发送停用请求
                result = self.http.post(url, json=filtered_params, description="停用物料")
                
                # 添加响应数据到报告
                a.json(result, "响应数据")
            
            with a.step("4. 验证响应结果"):
                # 断言响应成功
                self.assert_util.assert_response_success(result)
                
                # 记录验证结果
                a.text(f"物料停用成功 - ID: {TestMatAdd.mat_info['mat_id']}", "验证结果")
                
                self.logger.info(f"物料停用成功 - ID: {TestMatAdd.mat_info['mat_id']}")
            
        except Exception as e:
            self.logger.error(f"停用物料失败: {str(e)}")
            # 记录失败信息
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestMatAdd()
    test.setup_class()
    test.test_mat_add()      # 第1步：新增物料
    test.test_mat_enable()   # 第2步：启用物料
    test.test_mat_disable()  # 第3步：停用物料