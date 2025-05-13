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
from utils.performance_util import measure_time
from utils.http_util import HttpUtil

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
        cls.http_util = HttpUtil()
    
    @pytest.mark.order(1)
    @allure.title("查询订单类型")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型请求
    2. 验证响应数据
    3. 检查标准订单类型是否存在
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @measure_time(name="查询订单类型", log_level="INFO")
    def test_01_query_order_type(self):
        """测试查询订单类型"""
        # 1. 准备请求参数
        with allure.step("准备请求参数"):
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_PagingDataService"
            params = {
                "tmodule": "ERP_SCM",
                "modelKey": "ERP_SCM$sls_so_type_cf"
            }
            data = {
                "sceneKey": "ERP_SCM$so_type_cf",
                "viewKey": "ERP_SCM$so_type_cf:list",
                "containerKey": "ERP_SCM$so_type_cf-list-ERP_SCM$sls_so_type_cf",
                "serviceKey": "ERP_SCM$SYS_PagingDataService",
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
            response = self.http_util.post(
                url,
                json=data,
                params=params,
                description="查询订单类型"
            )
            allure.attach(
                json.dumps(response, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                "响应数据",
                allure.attachment_type.JSON
            )
        
        # 3. 验证响应
        with allure.step("验证响应数据"):
            # 验证响应格式
            assert isinstance(response, dict), "响应数据格式错误"
            assert response.get("success") is not None, "响应缺少success字段"
            
            # 验证业务状态
            assert response["success"], f"请求失败: {response.get('errorMsg', '未知错误')}"
            
            # 验证数据列表 - 处理嵌套的数据结构
            response_data = response["data"]
            assert isinstance(response_data, dict), "响应data字段格式错误"
            
            inner_data = response_data["data"]
            assert isinstance(inner_data, dict), "响应内层data字段格式错误"
            
            data_list = inner_data["data"]
            assert isinstance(data_list, list), "响应数据列表格式错误"
            assert len(data_list) > 0, "未找到任何订单类型"
            
            # 查找标准订单类型
            stnd_record = next(
                (record for record in data_list if record.get("soTypeCode") == "STND"),
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
    @measure_time(name="查询订单类型详情", log_level="INFO")
    def test_02_query_order_type_detail(self):
        """测试查询订单类型详情"""
        # 1. 检查并获取标准订单类型ID
        with allure.step("检查标准订单类型ID"):
            if not self.so_stnd_id:
                self.test_01_query_order_type()
            logger.info(f"self.so_stnd_id: {self.so_stnd_id}")
        
        # 2. 准备请求参数
        with allure.step("准备请求参数"):
            url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_SCM$SYS_FindDataByIdService"
            params = {
                "tmodule": "ERP_SCM",
                "modelKey": "ERP_SCM$sls_so_type_cf"
            }
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
            response = self.http_util.post(
                url,
                json=data,
                params=params,
                description="查询订单类型详情"
            )
            logger.info(f"response: {response}")
            allure.attach(
                json.dumps(response, indent=2, ensure_ascii=False, cls=DecimalEncoder),
                "响应数据",
                allure.attachment_type.JSON
            )
        
        # 4. 验证响应
        with allure.step("验证响应数据"):
            assert response is not None, "响应数据为空"
            assert response.get("success"), f"请求失败: {response.get('errorMsg', '未知错误')}"
            
            # 获取嵌套的数据
            response_data = response.get("data", {}).get("data", {}) #解析 response 结构
            assert response_data.get("id") == self.so_stnd_id, "返回的ID与请求的ID不匹配"
            assert response_data.get("soTypeCode") == "STND", "订单类型代码不匹配"
            assert response_data.get("status") == "ENABLED", "订单类型状态不匹配"
            
            # 检查必要字段
            required_fields = ["soTypeCode", "soTypeName", "id", "status"]
            for field in required_fields:
                assert field in response_data, f"缺少必要字段: {field}"
            
            # 记录订单类型详情
            allure.attach(
                json.dumps(response_data, indent=2, ensure_ascii=False, cls=DecimalEncoder),
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
    test.test_02_query_order_type_detail()
