"""
合作伙伴模块测试用例
包含新增、查询、启用、停用、删除等操作
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

@allure.epic("通用基础")
@allure.feature("合作伙伴管理")
class TestPartners(GenBaseTest):
    # 保存合作伙伴相关信息的类变量，所有测试用例共享
    partner_info = {}
    @classmethod
    def setup_class(cls):
        # 调用GenBaseTest的初始化方法
        # 这会初始化logger、http客户端、断言工具和YAML处理器等
        super().setup_class()
        # 获取合作伙伴相关的API路径配置
        # partner_path内容示例: {'新增合作伙伴': '/api/xxx/yyy', '查询合作伙伴': '/api/xxx/zzz', ...}
        cls.partner_path = cls.get_module_paths("通用基础", "合作伙伴")
        cls.logger.info("合作伙伴测试类初始化完成")

    @pytest.mark.run(order=1)
    @allure.story("新增合作伙伴")
    @allure.description("测试步骤：1.生成合作伙伴基础信息 2.调用新增接口 3.验证响应结果")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_partner_add(self):
        try:
            # 1. 生成合作伙伴基础信息
            # 使用时间戳和随机数生成唯一编码和名称
            timestamp = time.strftime("%Y%m%d%H%M%S")  # 当前时间，格式如: 20250522100512
            partner_code = f"PAR{timestamp}{random.randint(1000, 9999)}"  # 编码格式如: PAR202505221005121234
            partner_name = f"TEST_PARTNER_{random.randint(100, 999)}"  # 名称格式如: TEST_PARTNER_123
            
            # 2. 准备请求数据
            # 从partner_path获取API路径，如: /api/trantor/service/engine/execute/ERP_GEN$GEN_COM_PARTNER_SAVE_EVENT_SERVICE?tmodule=ERP_GEN
            url = self.partner_path["新增合作伙伴"]
            
            # 使用get_request_data方法获取请求数据，并替换动态参数
            # data内容示例: {'params': {'request': {...}}}，其中request中的partner_code和partner_name被替换为随机生成的值
            data = self.get_request_data(
                url,
                partner_code=partner_code,
                partner_name=partner_name
            )
            
            # 3. 发送请求并验证响应
            # result内容示例: {'success': True, 'data': {'data': {'id': 12345, ...}}}
            result = self.http.post(url, json=data, description="新增合作伙伴")
            
            # 4. 断言响应成功
            # 验证响应中的success字段为True，否则抛出异常
            self.assert_util.assert_response_success(result)
            
            # 从响应中获取合作伙伴ID
            # response_data内容示例: {'id': 12345, 'code': 'PAR202505221005121234', ...}
            response_data = result.get("data", {}).get("data", {})
            partner_id = response_data.get("id")  # 获取ID，示例: 12345
            
            # 确保返回了有效的ID
            assert partner_id, "新增合作伙伴失败：返回的ID为空"
            
            # 5. 保存测试数据到类变量，供后续测试用例使用
            # partner_info内容示例: {'partner_id': 12345, 'partner_code': 'PAR202505221005121234', 'partner_name': 'TEST_PARTNER_123'}
            TestPartners.partner_info.update({
                "partner_id": partner_id,
                "partner_code": partner_code,
                "partner_name": partner_name
            })
            
            self.logger.info(f"新增合作伙伴成功 - ID: {partner_id}, 编码: {partner_code}")
            
        except Exception as e:
            self.logger.error(f"新增合作伙伴失败: {str(e)}")
            raise

    @pytest.mark.run(order=2)
    @allure.story("查询合作伙伴")
    @allure.description("测试步骤：1.使用新增的合作伙伴编码查询 2.验证查询结果")
    @allure.severity(allure.severity_level.NORMAL)
    def test_partner_search(self):
        try:
            # 1. 验证前置条件 - 确保partner_info中有数据
            # 检查partner_code是否存在，如果不存在则测试失败
            assert TestPartners.partner_info.get("partner_code"), "未找到要查询的合作伙伴编码，请先执行新增用例"
            
            # 2. 准备查询参数
            # 从partner_path获取查询API路径
            url = self.partner_path["查询合作伙伴"]
            
            # 使用get_request_data方法获取请求数据，并替换动态参数
            # 这里传入partner_code作为查询条件
            data = self.get_request_data(
                url,
                partner_code=TestPartners.partner_info["partner_code"]
            )
            
            # 3. 发送查询请求
            # result内容示例: {'success': True, 'data': {'data': {'data': [{...}, ...], 'total': 1}}}
            result = self.http.post(url, json=data, description="查询合作伙伴")
            
            # 4. 断言响应成功
            self.assert_util.assert_response_success(result)
            
            # 5. 验证查询结果
            # response_data内容示例: {'data': [{...}, ...], 'total': 1}
            response_data = result.get("data", {}).get("data", {})
            
            # data_list内容示例: [{'id': 12345, 'code': 'PAR202505221005121234', ...}, ...]
            data_list = response_data.get("data", [])
            
            # 验证返回的数据列表不为空
            assert data_list, "查询结果为空"
            
            # 验证查询结果包含新增的合作伙伴编码
            # 使用any函数检查data_list中是否有任何一项的code等于partner_code
            assert any(item.get("code") == TestPartners.partner_info["partner_code"] for item in data_list), \
                   f"未找到合作伙伴编码: {TestPartners.partner_info['partner_code']}"
            
            # 验证总数大于0
            total = response_data.get("total", 0)
            assert total > 0, "查询结果总数为0"
            
            self.logger.info(f"查询合作伙伴成功 - 总数: {total}")
            
        except Exception as e:
            self.logger.error(f"查询合作伙伴失败: {str(e)}")
            raise

    @pytest.mark.run(order=3)
    @allure.story("启用合作伙伴")
    @allure.description("测试步骤：1.使用合作伙伴ID调用启用接口 2.验证响应结果")
    @allure.severity(allure.severity_level.BLOCKER) 
    def test_partner_enable(self):
        try:
            # 1. 验证前置条件 - 确保partner_info中有数据
            assert TestPartners.partner_info.get("partner_id"), "未找到要启用的合作伙伴ID，请先执行新增用例"
            
            # 2. 准备请求数据
            # 从partner_path获取启用API路径
            url = self.partner_path["启用合作伙伴"]
            
            # 使用get_request_data方法获取请求数据，并替换partner_id参数
            data = self.get_request_data(
                url,
                partner_id=TestPartners.partner_info["partner_id"]
            )
            
            # 3. 发送启用请求
            # result内容示例: {'success': True, 'data': {...}}
            result = self.http.post(url, json=data, description="启用合作伙伴")
            
            # 4. 断言响应成功
            self.assert_util.assert_response_success(result)
            
            self.logger.info(f"启用合作伙伴成功 - ID: {TestPartners.partner_info['partner_id']}")
            
        except Exception as e:
            self.logger.error(f"启用合作伙伴失败: {str(e)}")
            raise

    @pytest.mark.run(order=4)
    @allure.story("停用合作伙伴")
    @allure.description("测试步骤：1.使用合作伙伴ID调用停用接口 2.验证响应结果")
    @allure.severity(allure.severity_level.BLOCKER) 
    def test_partner_disable(self):
        try:
            # 1. 验证前置条件 - 确保partner_info中有数据
            assert TestPartners.partner_info.get("partner_id"), "未找到要停用的合作伙伴ID，请先执行新增用例"
            
            # 2. 准备请求数据
            # 从partner_path获取停用API路径
            url = self.partner_path["停用合作伙伴"]
            
            # 使用get_request_data方法获取请求数据，并替换partner_id参数
            data = self.get_request_data(
                url,
                partner_id=TestPartners.partner_info["partner_id"]
            )
            
            # 3. 发送停用请求
            # result内容示例: {'success': True, 'data': {...}}
            result = self.http.post(url, json=data, description="停用合作伙伴")
            
            # 4. 断言响应成功
            self.assert_util.assert_response_success(result)
            
            self.logger.info(f"停用合作伙伴成功 - ID: {TestPartners.partner_info['partner_id']}")
            
        except Exception as e:
            self.logger.error(f"停用合作伙伴失败: {str(e)}")
            raise

    @pytest.mark.run(order=5)
    @allure.story("删除合作伙伴")
    @allure.description("测试步骤：1.使用合作伙伴ID调用删除接口 2.验证响应结果")
    @allure.severity(allure.severity_level.BLOCKER) 
    def test_partner_delete(self):
        try:
            # 1. 验证前置条件 - 确保partner_info中有数据
            assert TestPartners.partner_info.get("partner_id"), "未找到要删除的合作伙伴ID，请先执行新增用例"
            
            # 2. 准备请求数据
            # 从partner_path获取删除API路径
            url = self.partner_path["删除合作伙伴"]
            
            # 使用get_request_data方法获取请求数据，并替换partner_id参数
            data = self.get_request_data(
                url,
                partner_id=TestPartners.partner_info["partner_id"]
            )
            
            # 3. 发送删除请求
            # result内容示例: {'success': True, 'data': {...}}
            result = self.http.post(url, json=data, description="删除合作伙伴")
            
            # 4. 断言响应结果
            self.assert_util.assert_response_success(result)
            
            self.logger.info(f"删除合作伙伴成功 - ID: {TestPartners.partner_info['partner_id']}")
            
            # 5. 清空测试数据，避免后续测试误用
            TestPartners.partner_info = {}
            
        except Exception as e:
            self.logger.error(f"删除合作伙伴失败: {str(e)}")
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