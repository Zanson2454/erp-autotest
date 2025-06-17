"""销售订单配置检查测试用例"""

import pytest
from pathlib import Path
from loguru import logger
import sys
import allure
from utils.allure_simple import a

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.exception_util import safe_api_call
from testcases.sls import SlsBase

class TestSalesOrderConfig(SlsBase):
    """销售订单配置检查测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        # 先初始化 SlsBase，因为它包含了基础配置
        super().setup_class()
        
        cls.order_type_ids = {}
        cls.order_line_type_ids = {}
        cls.yaml_util = YamlUtil()
  

    @allure.title("查询订单类型配置")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型配置请求
    2. 验证响应状态
    3. 获取各订单类型ID
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @safe_api_call(error_message="查询订单类型配置失败")
    def test_01_query_order_type(self):
        """查询订单类型配置"""
        try:
            with a.step("发送查询订单类型配置请求"):
                url = self.sls_api_paths["销售配置"]["查询订单类型配置"]
                data = self.sls_api_params.get(url, {})
                a.json(data, "请求数据")
                response = self.http.post(
                    url=url,
                    json=data,
                    description="查询订单类型"
                )
                a.json(response, "响应数据")
                self.assert_util.assert_response_success(response)
            with a.step("获取所有订单类型ID"):
                response_data = response.get("data", {}).get("data", {}).get("data", [])
                self.order_type_ids = {}
                for order_type_code, order_type_name in self.ORDER_TYPES.items():
                    record = next(
                        (record for record in response_data if record.get("soTypeCode") == order_type_code),
                        None
                    )
                    if record:
                        self.order_type_ids[order_type_code] = record["id"]
                        a.text(f"{order_type_name}订单类型ID: {record['id']}", "类型ID")
                    else:
                        a.text(f"未找到{order_type_name}订单类型({order_type_code})", "缺失类型")
                a.json(self.order_type_ids, "订单类型ID映射")
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.title("查询订单类型详情")
    @allure.description("""
    测试步骤：
    1. 发送查询订单类型详情请求
    2. 验证响应状态
    3. 验证所有订单类型详情数据
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(2)
    def test_02_query_order_type_detail(self):
        """测试查询所有订单类型详情"""
        try:
            with a.step("准备订单类型ID"):
                if not self.order_type_ids:
                    self.test_01_query_order_type()
            for order_type_code, order_type_name in self.ORDER_TYPES.items():
                order_type_id = self.order_type_ids.get(order_type_code)
                if not order_type_id:
                    a.text(f"未找到{order_type_name}订单类型ID，跳过详情查询", "缺失类型")
                    continue
                with a.step(f"查询{order_type_name}订单类型详情，ID: {order_type_id}"):
                    url = self.sls_api_paths["销售配置"]["查询订单类型详情"]
                    data = self.sls_api_params.get(url, {})
                    data['params']['request']['id'] = order_type_id
                    a.json(data, "请求数据")
                    try:
                        response = self.http.post(
                            url=url,
                            json=data,
                            description=f"查询{order_type_name}订单类型详情"
                        )
                        a.json(response, "响应数据")
                        self.assert_util.assert_response_success(response)
                        response_data = response.get("data", {}).get("data", {})
                        assert response_data.get("id") == order_type_id, f"{order_type_name}返回的ID与请求的ID不匹配"
                        assert response_data.get("soTypeCode") == order_type_code, f"{order_type_name}订单类型代码不匹配"
                        assert response_data.get("status") == "ENABLED", f"{order_type_name}订单类型状态不匹配"
                        a.text(f"{order_type_name}订单类型详情验证通过", "断言结果")
                    except Exception as e:
                        a.text(str(e), f"{order_type_name}详情查询失败")
                        raise
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

    @allure.title("查询订单行类型配置")
    @allure.description("""
    测试步骤：
    1. 发送查询订单行类型配置请求
    2. 验证响应状态
    3. 获取各订单行类型ID
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(3)
    @safe_api_call(error_message="查询订单行类型配置失败")
    def test_03_query_order_line_type(self):
        """查询订单行类型配置"""
        try:
            with a.step("发送查询订单行类型配置请求"):
                url = self.sls_api_paths["销售配置"]["查询订单行类型配置"]
                data = self.sls_api_params.get(url, {})
                a.json(data, "请求数据")
                result = self.http.post(url, json=data, description="查询订单行类型配置")
                a.json(result, "响应数据")
            with a.step("处理订单行类型数据"):
                response_data = result.get("data", {}).get("data", {})
                order_line_types = response_data.get("data", [])
                a.json(order_line_types, "订单行类型列表")
                for item in order_line_types:
                    a.text(f"订单行类型代码: {item.get('soItemTypeCode')}, ID: {item.get('id')}, 名称: {item.get('soItemTypeName')}", "类型明细")
                self.order_line_type_ids = {
                    item.get("soItemTypeCode"): item.get("id")
                    for item in order_line_types
                }
                a.json(self.order_line_type_ids, "订单行类型ID映射")
                required_types = ["NORM", "CENT", "CONS_ISSU", "VEND_CONS", "CONS_FILL", "THRD", "SERV"]
                missing_types = [t for t in required_types if t not in self.order_line_type_ids]
                if missing_types:
                    a.text(f"缺少以下订单行类型: {missing_types}", "缺失类型")
                    a.text("可用的订单行类型: " + ", ".join(self.order_line_type_ids.keys()), "可用类型")
            self.assert_util.assert_response_success(result)
            
        except Exception as e:
            a.text(str(e), "失败原因")
            raise

if __name__ == "__main__":
    test = TestSalesOrderConfig()
    test.setup_class()
    test.test_01_query_order_type()
    test.test_02_query_order_type_detail()
    test.test_03_query_order_line_type()
    #allure_dir = Path(project_root) / "reports" / "allure-results"
    #pytest.main(["-v", __file__, f"--alluredir={allure_dir}", "--env=test"])
