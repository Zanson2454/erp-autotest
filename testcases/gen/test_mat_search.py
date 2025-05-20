import os
import sys
from pathlib import Path
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil

# 添加项目根目录到 Python 路径，确保可以正确导入项目模块
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

class TestMatSearch(BaseTest):
    """物料搜索测试用例类
    
    继承自BaseTest基类，用于测试物料列表查询功能
    包含物料列表的查询和验证逻辑
    """
    
    @classmethod
    def setup_class(cls):
        """测试类初始化方法
        
        执行以下初始化操作：
        1. 调用父类的初始化方法
        2. 初始化配置文件路径
        3. 读取接口路径和参数配置
        """
        # 调用父类的初始化方法
        super().setup_class()
        
        # 初始化配置文件路径和YAML工具
        # testdata/gen/mat.yaml: 存储接口路径配置
        # testdata/gen/mat_api_params.yaml: 存储接口参数配置
        cls.base_api_path = Path(project_root) / "testdata" / "gen" / "mat.yaml"
        cls.base_config_path = Path(project_root) / "testdata" / "gen" / "mat_api_params.yaml"
        cls.yaml_util = YamlUtil()
        
        # 从YAML文件读取接口路径和参数
        # mat_path: 获取物料管理相关的接口路径
        # mat_params: 获取接口调用需要的参数
        cls.mat_path = cls.yaml_util.read_yaml(cls.base_api_path)["通用基础"]["物料管理"]
        cls.mat_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})
        
        cls.logger.info("测试类初始化完成")

    def test_mat_search(self):
        """物料列表查询测试方法
        
        测试步骤：
        1. 获取物料查询接口的URL和请求参数
        2. 发送POST请求查询物料列表
        3. 验证响应结果的正确性
        
        异常处理：
        - 捕获并记录请求过程中的异常
        - 记录错误日志并向上抛出异常
        """
        try:
            # 1. 获取接口路径和参数
            # 从配置中获取物料主数据查询接口的URL和对应的请求参数
            url = self.mat_path["物料主数据默认页面"]
            data = self.mat_params.get(url, {})
            
            # 2. 发送POST请求并获取响应
            # 调用http工具发送请求，并从响应中提取data字段
            result = self.http.post(url, json=data, description="查询物料列表")
            response_data = result.get("data", {}).get("data", {})
            
            # 3. 验证响应结果
            # 3.1 验证请求是否成功
            self.assert_util.assert_response_success(result)
            
            # 3.2 验证返回的total字段（总记录数）不为空且大于等于0
            total = response_data.get("total")
            assert total is not None and total > 0, f"物料总数异常: {total}"
            
            self.logger.info(f"物料列表查询完成，总记录数: {total}")
            
        except Exception as e:
            # 异常处理：记录错误日志并向上抛出异常
            self.logger.error(f"物料列表查询失败: {str(e)}")
            raise

if __name__ == "__main__":
    # 直接运行测试用例
    test = TestMatSearch()
    test.setup_class()
    test.test_mat_search()