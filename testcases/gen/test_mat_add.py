"""
物料管理模块测试用例
包含新增、启用、停用等操作
"""

import sys
import time
import random
import allure
import pytest
from pathlib import Path
from testcases.gen import GenBaseTest

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("ERP通用基础模块")
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
        
        # 获取物料管理相关的API路径配置
        # mat_path内容示例: {'新增物料': '/api/xxx/yyy', '启用物料': '/api/xxx/zzz', ...}
        cls.mat_path = cls.get_module_paths("通用基础", "物料管理")
        
        cls.logger.info("物料管理测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.title("新增物料")
    @allure.description("测试步骤：1.生成物料基础信息 2.调用新增接口 3.验证响应结果")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_mat_add(self):
        """
        新增物料测试用例
        1. 生成随机编码和名称
        2. 调用新增API
        3. 验证响应并保存ID信息
        """
        try:
            # 1. 生成物料基础信息
            # 使用时间戳和随机数生成唯一编码和名称
            timestamp = time.strftime("%Y%m%d%H%M%S")  # 当前时间，格式如: 20250522100512
            mat_code = f"MAT{timestamp}{random.randint(1000, 9999)}"  # 编码格式如: MAT202505221005121234
            mat_name = f"TEST_MAT_{random.randint(100, 999)}"  # 名称格式如: TEST_MAT_123
            remark = f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"  # 备注，包含创建时间
            
            # 2. 准备请求数据
            # 从mat_path获取API路径，如: /api/trantor/service/engine/execute/ERP_GEN$GEN_MD_MAT_CLEAR_CACHE_BY_IDS_EVENT_SERVICE?tmodule=ERP_SCM
            url = self.mat_path["新增物料"]
            
            # 使用get_request_data方法获取请求数据，并替换动态参数
            # data内容示例: {'params': {'request': {...}}}，其中request中的mat_code和mat_name被替换为随机生成的值
            data = self.get_request_data(
                url,
                mat_code=mat_code,
                mat_name=mat_name,
                remark=remark
            )
            
            # 3. 发送请求并验证响应
            # result内容示例: {'success': True, 'data': {'data': {'id': 12345, ...}}}
            result = self.http.post(url, json=data, description="新增物料")
            
            # 4. 断言响应成功
            # 验证响应中的success字段为True，否则抛出异常
            self.assert_util.assert_response_success(result)
            
            # 从响应中获取物料ID
            # response_data内容示例: {'id': 12345, 'matCode': 'MAT202505221005121234', ...}
            response_data = result.get("data", {}).get("data", {})
            mat_id = response_data.get("id")  # 获取ID，示例: 12345
            
            # 确保返回了有效的ID
            assert mat_id, "新增物料失败：返回的ID为空"
            
            # 5. 保存测试数据到类变量，供后续测试用例使用
            # mat_info内容示例: {'mat_id': 12345, 'mat_code': 'MAT202505221005121234', 'mat_name': 'TEST_MAT_123'}
            TestMatAdd.mat_info.update({
                "mat_id": mat_id,
                "mat_code": mat_code,
                "mat_name": mat_name
            })
            
            self.logger.info(f"新增物料成功 - ID: {mat_id}, 编码: {mat_code}")
            
        except Exception as e:
            self.logger.error(f"新增物料失败: {str(e)}")
            raise

    @pytest.mark.run(order=2)
    @allure.title("启用物料")
    @allure.description("测试步骤：1.验证前置条件 2.调用启用接口 3.验证响应结果")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_mat_enable(self):
        """
        启用物料测试用例
        1. 验证前置条件
        2. 调用启用API
        3. 验证响应结果
        """
        try:
            # 1. 验证前置条件 - 确保mat_info中有数据
            assert TestMatAdd.mat_info.get("mat_id"), "未找到待启用的物料ID，请先执行新增物料测试"
            
            # 2. 准备请求数据
            # 从mat_path获取启用API路径
            url = self.mat_path["启用物料"]
            
            # 使用get_request_data方法获取请求数据，并替换mat_id和mat_code参数
            data = self.get_request_data(
                url,
                mat_id=TestMatAdd.mat_info["mat_id"],
                mat_code=TestMatAdd.mat_info["mat_code"]
            )
            
            # 3. 发送启用请求
            # result内容示例: {'success': True, 'data': {...}}
            result = self.http.post(url, json=data, description="启用物料")
            
            # 4. 断言响应成功
            self.assert_util.assert_response_success(result)
            
            self.logger.info(f"物料启用成功 - ID: {TestMatAdd.mat_info['mat_id']}")
            
        except Exception as e:
            self.logger.error(f"启用物料失败: {str(e)}")
            raise

    @pytest.mark.run(order=3)
    @allure.title("停用物料")
    @allure.description("测试步骤：1.验证前置条件 2.调用停用接口 3.验证响应结果")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_mat_disable(self):
        """
        停用物料测试用例
        1. 验证前置条件
        2. 调用停用API
        3. 验证响应结果
        """
        try:
            # 1. 验证前置条件 - 确保mat_info中有数据
            assert TestMatAdd.mat_info.get("mat_id"), "未找到待停用的物料ID，请先执行新增物料测试"
            
            # 2. 准备请求数据
            # 从mat_path获取停用API路径
            url = self.mat_path["停用物料"]
            
            # 使用get_request_data方法获取请求数据，并替换mat_id和mat_code参数
            data = self.get_request_data(
                url,
                mat_id=TestMatAdd.mat_info["mat_id"],
                mat_code=TestMatAdd.mat_info["mat_code"]
            )
            
            # 3. 发送停用请求
            # result内容示例: {'success': True, 'data': {...}}
            result = self.http.post(url, json=data, description="停用物料")
            
            # 4. 断言响应成功
            self.assert_util.assert_response_success(result)
            
            self.logger.info(f"物料停用成功 - ID: {TestMatAdd.mat_info['mat_id']}")
            
        except Exception as e:
            self.logger.error(f"停用物料失败: {str(e)}")
            raise

if __name__ == "__main__":
    """直接运行测试用例的入口点"""
    test = TestMatAdd()
    test.setup_class()
    test.test_mat_add()      # 第1步：新增物料
    test.test_mat_enable()   # 第2步：启用物料
    test.test_mat_disable()  # 第3步：停用物料