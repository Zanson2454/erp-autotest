import os
import sys
import json
import pytest
import allure
from datetime import datetime
from loguru import logger
from faker import Faker




# Add project root to Python path
root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_path)

from utils.mock_util import MockData
from testcases.comm.base_test import BaseTest


fake = Faker('zh_CN')

class TestMemberCreate(BaseTest):
    """CRM会员新增接口测试"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        super().setup_class()  # 调用父类的setup_class方法
        cls.logger.info("CRM会员测试类初始化完成")

    def _generate_member_data(self):
        """生成单个会员数据"""
        # Mock数据
        mock_util = MockData()
        phone = mock_util.get_mock_phone() if hasattr(mock_util, 'get_mock_phone') else fake.phone_number()
        id_number = mock_util.get_mock_id_number() if hasattr(mock_util, 'get_mock_id_number') else fake.ssn()
        name = mock_util.get_mock_name() if hasattr(mock_util, 'get_mock_name') else fake.name()
        nickname = fake.user_name()  # 生成随机昵称
        gender = fake.random_element(elements=("MALE", "FEMALE"))
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=60).strftime("%Y-%m-%d")

        # 组装请求数据
        data = {
            "params": {
                "request": {
                    "crmRetailFormatCfId": {
                        "name": "TERMINUS",
                        "code": "DEFAULT-RETAIL",
                        "ruleType": "REGISTER",
                        "id": 2001001,
                        "createdBy": {"id": self.user_id},
                        "updatedBy": {"id": self.user_id},
                        "createdAt": int(datetime.now().timestamp() * 1000),
                        "updatedAt": int(datetime.now().timestamp() * 1000),
                        "version": 4,
                        "deleted": 0,
                        "requestId": fake.uuid4(),
                        "originOrgId": 0,
                        "tenantId": 0
                    },
                    "name": name,
                    "code": None,
                    "nickname": nickname,
                    "idNumber": id_number,
                    "phone": phone,
                    "birthday": birthday,
                    "gender": gender,
                    "genBusinessPartnerMdId": None,
                    "id": None,
                    "createdBy": {"id": self.user_id},
                    "updatedBy": {"id": self.user_id},
                    "createdAt": int(datetime.now().timestamp() * 1000),
                    "updatedAt": int(datetime.now().timestamp() * 1000),
                    "version": 0,
                    "deleted": 0,
                    "requestId": fake.uuid4(),
                    "originOrgId": 0,
                    "tenantId": 0
                }
            }
        }
        return data

    @allure.title("新增会员接口-手机号唯一")
    @pytest.mark.api
    def test_create_member(self):
        """测试新增会员接口，所有字段用MockUtil或faker生成"""
        data = self._generate_member_data()
        url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_CRM$CRM_MEMBER_MD_CREATE_ACTION_SERVICE?tmodule=ERP_CRM"
        response = self._make_request(url, data, "新增会员接口")
        assert response.get("success", False), f"接口返回失败: {json.dumps(response, ensure_ascii=False)}"
        logger.info(f"新增会员接口响应: {json.dumps(response, ensure_ascii=False, indent=2)}")

    @allure.title("批量新增会员接口")
    @pytest.mark.api
    def test_batch_create_members(self, count: int = 5):
        """批量新增会员接口
        
        Args:
            count: 需要生成的会员数量，默认5个
        """
        success_count = 0
        failed_count = 0
        failed_members = []

        for i in range(count):
            try:
                data = self._generate_member_data()
                url = f"{self.base_url}/api/trantor/service/engine/execute/ERP_CRM$CRM_MEMBER_MD_CREATE_ACTION_SERVICE?tmodule=ERP_CRM"
                response = self._make_request(url, data, f"新增会员接口-第{i+1}个")
                
                if response.get("success", False):
                    success_count += 1
                    logger.info(f"第{i+1}个会员创建成功")
                else:
                    failed_count += 1
                    failed_members.append({
                        "index": i + 1,
                        "phone": data["params"]["request"]["phone"],
                        "error": response.get("err", {}).get("msg", "未知错误")
                    })
                    logger.error(f"第{i+1}个会员创建失败: {json.dumps(response, ensure_ascii=False)}")
            except Exception as e:
                failed_count += 1
                failed_members.append({
                    "index": i + 1,
                    "phone": data["params"]["request"]["phone"],
                    "error": str(e)
                })
                logger.error(f"第{i+1}个会员创建异常: {str(e)}")

        # 输出批量创建结果
        logger.info(f"批量创建完成，总数: {count}, 成功: {success_count}, 失败: {failed_count}")
        if failed_members:
            logger.error("创建失败的会员详情:")
            for member in failed_members:
                logger.error(f"第{member['index']}个会员 - 手机号: {member['phone']}, 错误: {member['error']}")
        
        return {
            "total": count,
            "success": success_count,
            "failed": failed_count,
            "failed_members": failed_members
        }


if __name__ == "__main__":
    test_member_create = TestMemberCreate()
    test_member_create.setup_class()  # 确保初始化
    
    # 测试单个会员创建
    test_member_create.test_create_member()
    
    # 测试批量创建会员（创建3个）
    result = test_member_create.test_batch_create_members(1000)
    logger.info(f"批量创建结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    # 测试批量创建会员（使用Locust）
    # test_member_create.test_batch_create_members_with_locust()