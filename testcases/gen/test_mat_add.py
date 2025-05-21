import sys
import time
import copy
import random
import allure
import pytest
from pathlib import Path
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil

# 添加项目根目录到 Python 路径，确保可以正确导入项目模块
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

@allure.epic("ERP通用基础模块")
@allure.feature("物料管理")
class TestMatAdd(BaseTest):
    
    # 类级别变量，用于在不同测试方法间共享物料信息
    # 结构: {
    #   "mat_id": "物料ID",  # 接口返回的物料唯一标识
    #   "mat_code": "物料编码",  # 格式: MAT + 时间戳 + 4位随机数
    #   "mat_name": "物料名称"   # 格式: TEST_MAT_ + 3位随机数
    # }
    mat_info = {}
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        # 配置文件路径定义
        cls.base_api_path = Path(project_root) / "testdata" / "gen" / "mat.yaml"  # 接口路径配置
        cls.base_config_path = Path(project_root) / "testdata" / "gen" / "mat_api_params.yaml"  # 接口参数配置
        cls.yaml_util = YamlUtil()
        
        # 读取YAML配置
        cls.mat_path = cls.yaml_util.read_yaml(cls.base_api_path)["通用基础"]["物料管理"]
        cls.mat_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})
        
        cls.logger.info("物料新增测试类初始化完成")

    def get_request_data(self, api_url, **kwargs):
        #从YAML配置中获取请求数据，并替换动态参数
        try:
            # 1. 获取API的默认参数配置
            api_config = self.mat_params.get(api_url, {})
            if not api_config:
                self.logger.error(f"在YAML中未找到API配置: {api_url}")
                return {}
                
            # 2. 深拷贝配置，避免修改原始数据
            request_data = copy.deepcopy(api_config)
            
            # 3. 获取请求参数部分
            # params格式: {"matCode": "${mat_code}", "matName": "${mat_name}", ...}
            params = request_data["params"]["request"]
            
            # 4. 替换动态参数
            # 遍历参数，将${xxx}格式的值替换为kwargs中对应的值
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    var_name = value[2:-1]  # 提取变量名，例如从${mat_code}提取出mat_code
                    if var_name in kwargs:
                        params[key] = kwargs[var_name]
                        
            return request_data
            
        except Exception as e:
            self.logger.error(f"处理请求数据时出错: {str(e)}")
            return {}

    @pytest.mark.run(order=1)
    @allure.title("新增物料")
    @allure.description("测试步骤：1.生成物料基础信息 2.调用新增接口 3.验证响应结果")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_mat_add(self):
        try:
            # 1. 生成物料基础信息
            timestamp = time.strftime("%Y%m%d%H%M%S")  # 格式：20240319152101
            mat_code = f"MAT{timestamp}{random.randint(1000, 9999)}"  # 示例：MAT202403191521011234
            mat_name = f"TEST_MAT_{random.randint(100, 999)}"  # 示例：TEST_MAT_123
            remark = f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # 2. 准备请求数据
            url = self.mat_path["新增物料"]  # 从YAML获取接口路径
            data = self.get_request_data(
                url,
                mat_code=mat_code,
                mat_name=mat_name,
                remark=remark
            )
            
            # 3. 发送请求并验证响应
            result = self.http.post(url, json=data, description="新增物料")
            self.assert_util.assert_response_success(result)
            
            # 4. 保存测试数据到类变量
            # response_data格式: {"id": "12345", "matCode": "MAT001", ...}
            response_data = result.get("data", {}).get("data", {})
            TestMatAdd.mat_info.update({
                "mat_id": response_data["id"],  # 物料ID，后续接口调用需要
                "mat_code": mat_code,  # 物料编码，用于查询和验证
                "mat_name": mat_name   # 物料名称，用于查询和验证
            })
            
            self.logger.info(f"新增物料成功 - ID: {TestMatAdd.mat_info['mat_id']}, 编码: {mat_code}")
            
        except Exception as e:
            self.logger.error(f"新增物料失败: {str(e)}")
            raise

    @pytest.mark.run(order=2)
    @allure.title("启用物料")
    @allure.description("测试步骤：1.验证前置条件 2.调用启用接口 3.验证响应结果")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_mat_enable(self):
        try:
            # 1. 验证前置条件
            assert TestMatAdd.mat_info.get("mat_id"), "未找到待启用的物料ID，请先执行新增物料测试"
            
            # 2. 准备请求数据
            url = self.mat_path["启用物料"]
            data = self.get_request_data(
                url,
                mat_id=TestMatAdd.mat_info["mat_id"],
                mat_code=TestMatAdd.mat_info["mat_code"]
            )
            
            # 3. 发送请求并验证响应
            result = self.http.post(url, json=data, description="启用物料")
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
        try:
            # 1. 验证前置条件
            assert TestMatAdd.mat_info.get("mat_id"), "未找到待停用的物料ID，请先执行新增物料测试"
            
            # 2. 准备请求数据
            url = self.mat_path["停用物料"]
            data = self.get_request_data(
                url,
                mat_id=TestMatAdd.mat_info["mat_id"],
                mat_code=TestMatAdd.mat_info["mat_code"]
            )
            
            # 3. 发送请求并验证响应
            result = self.http.post(url, json=data, description="停用物料")
            self.assert_util.assert_response_success(result)
            
            self.logger.info(f"物料停用成功 - ID: {TestMatAdd.mat_info['mat_id']}")
            
        except Exception as e:
            self.logger.error(f"停用物料失败: {str(e)}")
            raise

if __name__ == "__main__":
    # 直接运行测试用例
    test = TestMatAdd()
    test.setup_class()
    test.test_mat_add()      # 第1步：新增物料
    test.test_mat_enable()   # 第2步：启用物料
    test.test_mat_disable()  # 第3步：停用物料