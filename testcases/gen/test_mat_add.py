import os
import sys
import time
import random
from pathlib import Path
from typing import Dict, Any, Tuple
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

class TestMatAdd(BaseTest):
    """物料新增测试用例类
    
    继承自BaseTest基类，用于测试物料新增和启用功能
    包含物料创建、验证和状态更新的测试方法
    """
    
    @classmethod
    def setup_class(cls):
        """测试类初始化方法"""
        try:
            super().setup_class()
            
            # 初始化配置文件和YAML工具
            cls.base_api_path = Path(project_root) / "testdata" / "gen" / "mat.yaml"
            cls.base_config_path = Path(project_root) / "testdata" / "gen" / "mat_api_params.yaml"
            cls.yaml_util = YamlUtil()
            
            # 获取接口路径和参数
            cls.mat_path = cls.yaml_util.read_yaml(cls.base_api_path)["通用基础"]["物料管理"]
            cls.mat_params = cls.yaml_util.read_yaml(cls.base_config_path).get("api_params", {})
            
            # 初始化测试数据存储
            cls.test_data = {}
            
            cls.logger.info("测试类初始化完成")
            
        except Exception as e:
            cls.logger.error(f"测试类初始化失败: {str(e)}")
            raise

    def _generate_mat_code_and_name(self) -> Tuple[str, str]:
        """生成物料编码和名称
        
        Returns:
            Tuple[str, str]: 物料编码和名称的元组
        """
        timestamp = time.strftime("%Y%m%d%H%M%S")
        random_code = f"MAT{timestamp}{random.randint(1000, 9999)}"
        random_name = f"TEST_MAT_{random.randint(100, 999)}"
        return random_code, random_name

    def _validate_mat_response(self, response_data: Dict[str, Any], mat_code: str) -> None:
        """验证物料响应数据
        
        Args:
            response_data: 响应数据字典
            mat_code: 物料编码
            
        Raises:
            AssertionError: 当验证失败时抛出
        """
        # 验证基本字段
        assert response_data.get("id") is not None, "物料ID不能为空"
        assert response_data.get("matCode") == mat_code, "物料编码不匹配"
        assert response_data.get("matName") is not None, "物料名称不能为空"
        assert response_data.get("status") in ["ACTIVE", "INACTIVE"], "物料状态无效"
        
        # 验证其他必要字段
        required_fields = ["cateId", "genMatTypeCfId", "baseUomId"]
        for field in required_fields:
            assert field in response_data, f"响应缺少必要字段: {field}"
            assert response_data[field] is not None, f"字段 {field} 不能为空"

    def test_mat_add(self):
        """新增物料测试方法
        
        测试步骤：
        1. 生成随机的物料编码和名称
        2. 准备新增物料的请求数据
        3. 发送请求并验证响应
        4. 保存新增物料的信息供后续测试使用
        """
        try:
            # 1. 生成物料编码和名称
            mat_code, mat_name = self._generate_mat_code_and_name()
            self.logger.info(f"生成物料编码: {mat_code}, 名称: {mat_name}")
            
            # 2. 准备请求数据
            url = self.mat_path["新增物料"]
            data = self.mat_params.get(url, {}).copy()
            
            # 更新请求参数
            data["params"]["request"].update({
                "matCode": mat_code,
                "matName": mat_name,
                "status": "INACTIVE",  # 初始状态为未启用
                "bizStatus": "SALE",   # 业务状态为可销售
                "remark": f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            })
            
            # 3. 发送请求并验证
            result = self.http.post(url, json=data, description="新增物料")
            self.assert_util.assert_response_success(result)
            
            # 4. 验证响应数据
            response_data = result.get("data", {}).get("data", {})
            self._validate_mat_response(response_data, mat_code)
            
            # 5. 保存物料信息供后续测试使用
            self.test_data["mat_id"] = response_data["id"]
            self.test_data["mat_code"] = mat_code
            self.test_data["mat_name"] = mat_name
            
            self.logger.info(f"新增物料成功，ID: {self.test_data['mat_id']}, 编码: {mat_code}")
            
        except AssertionError as ae:
            self.logger.error(f"新增物料断言失败: {str(ae)}")
            raise
        except Exception as e:
            self.logger.error(f"新增物料失败: {str(e)}")
            raise

    def test_mat_enable(self):
        """启用物料测试方法
        
        测试步骤：
        1. 验证是否存在待启用的物料
        2. 准备启用物料的请求数据
        3. 发送请求并验证响应
        4. 验证物料状态是否更新为已启用
        """
        try:
            # 1. 验证是否存在待启用的物料
            if not self.test_data.get("mat_id"):
                self.test_mat_add()  # 如果没有物料，先创建一个
            
            # 2. 准备请求数据
            url = self.mat_path["启用物料"]
            data = self.mat_params.get(url, {}).copy()
            
            # 更新请求参数
            data["params"]["request"].update({
                "id": self.test_data["mat_id"],
                "matCode": self.test_data["mat_code"],
                "status": "ACTIVE"
            })
            
            # 3. 发送启用请求
            result = self.http.post(url, json=data, description="启用物料")
            self.assert_util.assert_response_success(result)
            
            # 4. 验证启用结果
            response_data = result.get("data", {}).get("data", {})
            assert response_data.get("status") == "ACTIVE", "物料状态未更新为已启用"
            
            self.logger.info(f"物料启用成功，ID: {self.test_data['mat_id']}")
            
        except AssertionError as ae:
            self.logger.error(f"启用物料断言失败: {str(ae)}")
            raise
        except Exception as e:
            self.logger.error(f"启用物料失败: {str(e)}")
            raise

    def teardown_method(self):
        """测试方法清理
        记录测试完成状态
        """
        self.logger.info(f"测试方法执行完成，测试数据: {self.test_data}")

if __name__ == "__main__":
    # 直接运行测试用例
    test = TestMatAdd()
    test.setup_class()
    test.test_mat_add()
    test.test_mat_enable()