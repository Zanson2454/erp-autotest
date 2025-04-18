from faker import Faker
from faker.providers import BaseProvider
from utils.LogUtil import Loggers


class MockData:
    def __init__(self):
        # 初始化日志
        self.log = Loggers()
        # 生成Faker实例，默认显示中文
        self.fake = Faker(locale='zh_CN')

    def get_mock_name(self):
        """
        获取姓名
        :return:
        """
        return self.fake.name()

    def get_mock_address(self):
        """
        获取详细地址
        :return:
        """
        return self.fake.address()

    def get_mock_phone_number(self):
        """
        获取手机号
        :return:
        """
        return self.fake.phone_number()

    def get_mock_ssn(self):
        """
        获取身份证号
        :return:
        """
        return self.fake.ssn()

    def get_mock_email(self):
        """
        获取邮箱号
        :return:
        """
        return self.fake.email()

    def get_mock_user_agent(self):
        """
        获取用户代理
        :return:
        """
        return self.fake.user_agent()

if __name__ == '__main__':
    mock_data = MockData()
    print(mock_data.get_mock_name())
    print(mock_data.get_mock_address())
    print(mock_data.get_mock_phone_number())
    print(mock_data.get_mock_ssn())
    print(mock_data.get_mock_email())
