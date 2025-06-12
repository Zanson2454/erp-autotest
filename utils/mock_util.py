from faker import Faker
from faker.providers import BaseProvider
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import random
import re
from pathlib import Path
import sys

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.log_util import Loggers
from utils.exception_util import ValidationException

class ChineseProvider(BaseProvider):
    """自定义中文数据提供器"""
    
    def chinese_company_name(self) -> str:
        """生成中文公司名称"""
        company_types = ['科技', '信息', '网络', '电子', '软件', '数据', '智能', '系统']
        company_suffixes = ['有限公司', '股份有限公司', '集团', '科技有限公司']
        return f"{self.generator.company_prefix()}{random.choice(company_types)}{random.choice(company_suffixes)}"
    
    def chinese_bank_name(self) -> str:
        """生成中文银行名称"""
        banks = ['中国工商银行', '中国农业银行', '中国银行', '中国建设银行', '交通银行', 
                '招商银行', '浦发银行', '民生银行', '兴业银行', '中信银行']
        return random.choice(banks)
    
    def chinese_bank_account(self) -> str:
        """生成银行账号"""
        return ''.join([str(random.randint(0, 9)) for _ in range(19)])

class MockData:
    """模拟数据生成工具类
    
    提供各种类型的模拟数据生成方法，包括：
    1. 基础个人信息（姓名、电话、邮箱等）
    2. 地址信息
    3. 公司信息
    4. 银行信息
    5. 日期时间
    6. 网络信息
    
    使用示例：
    ```python
    mock = MockData()
    name = mock.get_mock_name()
    company = mock.get_mock_company()
    ```
    """
    
    def __init__(self, locale: str = 'zh_CN'):
        """初始化模拟数据生成器
        
        Args:
            locale: 地区设置，默认为中文
        """
        self.log = Loggers()
        self.fake = Faker(locale)
        self.fake.add_provider(ChineseProvider)
    
    def get_mock_name(self) -> str:
        """生成中文姓名
        
        Returns:
            str: 随机生成的中文姓名
        """
        return self.fake.name()
    
    def get_mock_address(self) -> str:
        """生成详细地址
        
        Returns:
            str: 随机生成的详细地址
        """
        return self.fake.address()
    
    def get_mock_phone_number(self) -> str:
        """生成手机号
        
        Returns:
            str: 随机生成的手机号
        """
        phone = self.fake.phone_number()
        # 确保生成的是有效的手机号
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return f"1{random.choice(['3', '5', '7', '8', '9'])}{''.join([str(random.randint(0, 9)) for _ in range(9)])}"
        return phone
    
    def get_mock_ssn(self) -> str:
        """生成身份证号
        
        Returns:
            str: 随机生成的身份证号
        """
        return self.fake.ssn()
    
    def get_mock_email(self) -> str:
        """生成邮箱地址
        
        Returns:
            str: 随机生成的邮箱地址
        """
        return self.fake.email()
    
    def get_mock_company(self) -> str:
        """生成公司名称
        
        Returns:
            str: 随机生成的公司名称
        """
        return self.fake.chinese_company_name()
    
    def get_mock_bank_info(self) -> Dict[str, str]:
        """生成银行信息
        
        Returns:
            Dict[str, str]: 包含银行名称和账号的字典
        """
        return {
            'bank_name': self.fake.chinese_bank_name(),
            'account_number': self.fake.chinese_bank_account()
        }
    
    def get_mock_date(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> datetime:
        """生成随机日期
        
        Args:
            start_date: 开始日期，默认为30天前
            end_date: 结束日期，默认为当前日期
            
        Returns:
            datetime: 随机生成的日期
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        return self.fake.date_time_between(start_date=start_date, end_date=end_date)
    
    def get_mock_user_agent(self) -> str:
        """生成用户代理字符串
        
        Returns:
            str: 随机生成的用户代理字符串
        """
        return self.fake.user_agent()
    
    def get_mock_ip(self) -> str:
        """生成IP地址
        
        Returns:
            str: 随机生成的IP地址
        """
        return self.fake.ipv4()
    
    def get_mock_url(self) -> str:
        """生成URL地址
        
        Returns:
            str: 随机生成的URL地址
        """
        return self.fake.url()
    
    def get_mock_text(self, min_length: int = 10, max_length: int = 100) -> str:
        """生成随机文本
        
        Args:
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            str: 随机生成的文本
        """
        return self.fake.text(max_nb_chars=random.randint(min_length, max_length))
    
    def get_mock_choice(self, choices: List[Any]) -> Any:
        """从列表中随机选择一个元素
        
        Args:
            choices: 候选列表
            
        Returns:
            Any: 随机选择的元素
        """
        if not choices:
            raise ValidationException("候选列表不能为空")
        return random.choice(choices)


if __name__ == '__main__':
    # 测试代码
    mock = MockData()
    
    # 测试各种数据生成
    print("姓名:", mock.get_mock_name())
    print("地址:", mock.get_mock_address())
    print("电话:", mock.get_mock_phone_number())
    print("身份证:", mock.get_mock_ssn())
    print("邮箱:", mock.get_mock_email())
    print("公司:", mock.get_mock_company())
    print("银行信息:", mock.get_mock_bank_info())
    print("日期:", mock.get_mock_date())
    print("用户代理:", mock.get_mock_user_agent())
    print("IP地址:", mock.get_mock_ip())
    print("URL:", mock.get_mock_url())
    print("随机文本:", mock.get_mock_text())
    print("随机选择:", mock.get_mock_choice(['A', 'B', 'C', 'D']))
