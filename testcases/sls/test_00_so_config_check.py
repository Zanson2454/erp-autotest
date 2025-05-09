import os
import sys
import json
import pytest
import allure
import allure_pytest
from datetime import datetime
from loguru import logger
from typing import Dict, Any, Optional

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.yaml_util import YamlUtil

# 获取项目根目录
def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from testcases.comm.base_test import BaseTest, DecimalEncoder
from utils.exception_util import safe_api_call

@allure.epic("ERP系统")
@allure.feature("SCM模块")
@allure.story("销售订单配置检查")
class TestOrderTypeConfig(BaseTest):
    """订单类型配置测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.so_stnd_id = None
    
    @pytest.mark.order(1)
    @allure.title("查询订单类型")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型请求
    2. 验证响应数据
    3. 检查标准订单类型是否存在
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    def test_01_query_order_type(self):
        """测试查询订单类型"""
        # 1. 准备请求参数
        with allure.step("准备请求参数"):
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_PagingDataService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_type_cf"
            data = {
                "params": {
                    "request": {
                        "pageable": {
                            "pageNo": 1,
                            "pageSize": 20,
                            "conditionItems": None
                        }
                    },
                    "modelKey": "ERP_SCM$sls_so_type_cf"
                }
            }
            allure.attach(
                json.dumps(data, indent=2, ensure_ascii=False),
                "请求参数",
                allure.attachment_type.JSON
            )
        
        # 2. 发送请求
        with allure.step("发送查询请求"):
            response = self._make_request(url, data, "查询订单类型", extract_nested_data=True)
            allure.attach(
                json.dumps(response, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                "响应数据",
                allure.attachment_type.JSON
            )
        
        # 3. 验证响应
        with allure.step("验证响应数据"):
            assert isinstance(response, list), "响应数据格式错误"
            assert len(response) > 0, "未找到任何订单类型"
            
            # 查找标准订单类型
            stnd_record = next(
                (record for record in response if record.get("soTypeCode") == "STND"),
                None
            )
            assert stnd_record is not None, "未找到标准订单类型(STND)"
            assert stnd_record.get("id") is not None, "标准订单类型ID为空"
            
            # 记录标准订单类型ID
            self.so_stnd_id = stnd_record["id"]
            logger.info(f"找到STND记录, ID: {self.so_stnd_id}")
            allure.attach(
                str(self.so_stnd_id),
                "标准订单类型ID",
                allure.attachment_type.TEXT
            )
    
    @pytest.mark.order(2)
    @allure.title("查询订单类型详情")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型详情请求
    2. 验证响应数据
    3. 检查标准订单类型配置
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        # 1. 检查并获取标准订单类型ID
        with allure.step("检查标准订单类型ID"):
            if not self.so_stnd_id:
                self.test_01_query_order_type()
            logger.info(f"self.so_stnd_id: {self.so_stnd_id}")
        
        # 2. 准备请求参数
        with allure.step("准备请求参数"):
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_FindDataByIdService?tmodule=ERP_SCM&modelKey=ERP_SCM%24sls_so_type_cf"
            data = {
                "params": {
                    "request": {
                        "id": self.so_stnd_id
                    },
                    "modelKey": "ERP_SCM$sls_so_type_cf"
                }
            }
            allure.attach(
                json.dumps(data, indent=2, ensure_ascii=False),
                "请求参数",
                allure.attachment_type.JSON
            )
        
        # 3. 发送请求
        with allure.step("发送查询详情请求"):
            response = self._make_request(url, data, "查询订单类型详情", extract_nested_data=True)
            logger.info(f"response: {response}")
            allure.attach(
                json.dumps(response, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                "响应数据",
                allure.attachment_type.JSON
            )
        
        # 4. 验证响应
        with allure.step("验证响应数据"):
            assert response is not None, "响应数据为空"
            assert response["id"] == self.so_stnd_id, "返回的ID与请求的ID不匹配"
            assert response["soTypeCode"] == "STND", "订单类型代码不匹配"
            assert response["status"] == "ENABLED", "订单类型状态不匹配"
            
            # 检查必要字段
            required_fields = ["soTypeCode", "soTypeName", "id", "status"]
            for field in required_fields:
                assert field in response, f"缺少必要字段: {field}"
            
            # 记录订单类型详情
            allure.attach(
                json.dumps(response, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                "订单类型详情",
                allure.attachment_type.JSON
            )
    
if __name__ == "__main__":
    # project_root = get_project_root()
    # reports_dir = os.path.join(project_root, "reports", "allure-results")
    # logger.info(f"reports_dir: {reports_dir}")
    # pytest.main(["-v", __file__, f"--alluredir={reports_dir}"])
    test = TestOrderTypeConfig()
    test.setup_class()
    test.test_01_query_order_type()
