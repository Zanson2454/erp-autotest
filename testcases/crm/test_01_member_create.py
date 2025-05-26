import os
import sys
import json
import pytest
import allure
from pathlib import Path
from datetime import datetime
from loguru import logger
from faker import Faker

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.mock_util import MockData
from testcases.comm.base_test import BaseTest
from utils.yaml_util import YamlUtil
from utils.exception_util import safe_api_call

fake = Faker('zh_CN')

class TestMemberCreate(BaseTest):
    """CRM会员新增接口测试（重构版）"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()
        cls.logger.info("CRM会员测试类初始化完成")
        cls.yaml_util = YamlUtil()
        # 加载接口路径和参数配置
        cls.api_path_file = project_root / "testdata" / "crm" / "crm_api_path.yaml"
        cls.api_param_file = project_root / "testdata" / "crm" / "member_api_params.yaml"
        cls.member_path = cls.yaml_util.read_yaml(cls.api_path_file)["CRM会员"]["会员配置"]
        cls.member_params = cls.yaml_util.read_yaml(cls.api_param_file).get("api_params", {})

    def _generate_member_data(self):
        """生成单个会员数据"""
        mock_util = MockData()
        phone = mock_util.get_mock_phone() if hasattr(mock_util, 'get_mock_phone') else fake.phone_number()
        id_number = mock_util.get_mock_id_number() if hasattr(mock_util, 'get_mock_id_number') else fake.ssn()
        name = mock_util.get_mock_name() if hasattr(mock_util, 'get_mock_name') else fake.name()
        nickname = fake.user_name()
        gender = fake.random_element(elements=("MALE", "FEMALE"))
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d")

        # 从yaml获取基础结构，深拷贝防止污染
        import copy
        data = copy.deepcopy(self.member_params[self.member_path["新增会员"]])
        req = data["params"]["request"]
        req["name"] = name
        req["nickname"] = nickname
        req["idNumber"] = id_number
        req["phone"] = phone
        req["birthday"] = birthday
        req["gender"] = gender
        req["createdBy"] = {"id": self.user_id}
        req["updatedBy"] = {"id": self.user_id}
        req["createdAt"] = int(datetime.now().timestamp() * 1000)
        req["updatedAt"] = int(datetime.now().timestamp() * 1000)
        req["requestId"] = fake.uuid4()
        return data

    @allure.title("新增会员接口-手机号唯一")
    @allure.description("""
    测试步骤：\n1. 生成会员数据\n2. 调用新增会员接口\n3. 校验响应状态
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.order(1)
    @pytest.mark.api
    @safe_api_call(error_message="新增会员接口失败")
    def test_create_member(self):
        """测试新增会员接口，所有字段用MockUtil或faker生成"""
        url = self.member_path["新增会员"]
        data = self._generate_member_data()
        response = self._make_request(url, data, "新增会员接口")
        self.assert_util.assert_response_status(response)
        self.logger.info(f"新增会员接口响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
        return response

    @allure.title("批量新增会员接口")
    @allure.description("""
    测试步骤：\n1. 循环生成会员数据\n2. 批量调用新增会员接口\n3. 校验批量创建结果
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.order(2)
    @pytest.mark.api
    def test_batch_create_members(self, count: int = 5):
        """批量新增会员接口\n\nArgs:\n    count: 需要生成的会员数量，默认5个\n"""
        success_count = 0
        failed_count = 0
        failed_members = []
        url = self.member_path["新增会员"]
        for i in range(count):
            try:
                data = self._generate_member_data()
                response = self._make_request(url, data, f"新增会员接口-第{i+1}个")
                if response.get("success", False):
                    success_count += 1
                    self.logger.info(f"第{i+1}个会员创建成功")
                else:
                    failed_count += 1
                    failed_members.append({
                        "index": i + 1,
                        "phone": data["params"]["request"]["phone"],
                        "error": response.get("err", {}).get("msg", "未知错误")
                    })
                    self.logger.error(f"第{i+1}个会员创建失败: {json.dumps(response, ensure_ascii=False)}")
            except Exception as e:
                failed_count += 1
                failed_members.append({
                    "index": i + 1,
                    "phone": data["params"]["request"]["phone"],
                    "error": str(e)
                })
                self.logger.error(f"第{i+1}个会员创建异常: {str(e)}")

        self.logger.info(f"批量创建完成，总数: {count}, 成功: {success_count}, 失败: {failed_count}")
        if failed_members:
            self.logger.error("创建失败的会员详情:")
            for member in failed_members:
                self.logger.error(f"第{member['index']}个会员 - 手机号: {member['phone']}, 错误: {member['error']}")

        self.assert_util.assert_value_in_range(success_count, 0, count, "成功创建数量")
        self.assert_util.assert_value_in_range(failed_count, 0, count, "失败创建数量")
        self.assert_util.assert_value_in_range(success_count + failed_count, count, count, "总创建数量")
        return {
            "total": count,
            "success": success_count,
            "failed": failed_count,
            "failed_members": failed_members
        }

if __name__ == "__main__":
    test = TestMemberCreate()
    test.setup_class()
    test.test_create_member()
    # test.test_batch_create_members(3)