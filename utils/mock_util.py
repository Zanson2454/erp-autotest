from faker import Faker
from faker.providers import BaseProvider
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import random
import re
from pathlib import Path
import sys
import time
import threading
import uuid
import os

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
    
    def business_scope(self, max_length: int = 200) -> str:
        """生成经营范围（200字内）"""
        scopes = [
            '软件开发', '信息技术咨询', '计算机系统集成', '网络技术服务', '数据处理服务',
            '电子商务', '互联网信息服务', '技术推广服务', '企业管理咨询', '市场营销策划',
            '广告设计制作', '会议服务', '展览展示服务', '商务信息咨询', '财务咨询',
            '人力资源服务', '物业管理', '设备租赁', '货物进出口', '技术进出口',
            '代理进出口', '销售电子产品', '销售计算机软硬件', '销售通讯设备', '销售办公用品'
        ]
        # 随机选择3-6个经营范围
        selected_scopes = random.sample(scopes, random.randint(3, 6))
        # 添加常见的结尾
        scope_text = '；'.join(selected_scopes)
        endings = ['等', '；法律、法规禁止的不得经营', '；依法须经批准的项目，经相关部门批准后方可开展经营活动']
        result = scope_text + random.choice(endings)
        
        # 如果超过最大长度，截取前面部分
        if len(result) > max_length:
            result = result[:max_length-3] + '等'
        return result
    
    def company_introduction(self, max_length: int = 200) -> str:
        """生成公司简介（200字内）"""
        intros = [
            f"我公司成立于{random.randint(2000, 2020)}年，是一家专业从事{random.choice(['软件开发', '信息技术', '电子商务', '技术服务'])}的现代化企业。",
            f"公司拥有{random.choice(['专业', '优秀', '资深', '高素质'])}的技术团队和{random.choice(['完善', '先进', '成熟'])}的管理体系。",
            f"我们致力于为客户提供{random.choice(['优质', '专业', '高效', '全方位'])}的{random.choice(['技术服务', '解决方案', '产品服务', '咨询服务'])}。",
            f"公司秉承{random.choice(['诚信经营', '客户至上', '创新发展', '质量第一'])}的理念，{random.choice(['不断创新', '持续发展', '精益求精', '追求卓越'])}。"
        ]
        # 随机选择2-3个句子组成简介
        selected_intros = random.sample(intros, random.randint(2, 3))
        result = ''.join(selected_intros)
        
        # 如果超过最大长度，截取前面部分
        if len(result) > max_length:
            result = result[:max_length-1] + '。'
        return result

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
    
    # 类级别的计数器，用于确保唯一性
    _counter = 0
    _counter_lock = threading.Lock()
    
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
            str: 基于时间戳生成的手机号
        """
        phone = int(time.time()*10)
 
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
    
    def get_mock_date(self, days_offset: int = 0, include_time: bool = True) -> datetime:
        """生成日期，支持日期偏移和时间包含选项
        
        Args:
            days_offset: 日期偏移量，正数为未来日期，负数为过去日期
            include_time: 是否包含时分秒，默认为True
        Returns:
            datetime: 生成的日期
        """
        target_date = datetime.now() + timedelta(days=days_offset)
        if not include_time:
            return target_date.date()
        return target_date
    
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

    def get_mock_currency(self) -> dict:
        """
        生成币种对象，字段一一对应：code、name、symbol、iso_name
        Returns:
            dict: {code, name, symbol, iso_name}
        """
        currency_list = [
            {"code": "CNY", "name": "人民币", "symbol": "¥", "iso_name": "Chinese Yuan"},
            {"code": "USD", "name": "美元", "symbol": "$", "iso_name": "US Dollar"},
            {"code": "EUR", "name": "欧元", "symbol": "€", "iso_name": "Euro"},
            {"code": "JPY", "name": "日元", "symbol": "¥", "iso_name": "Japanese Yen"},
            {"code": "GBP", "name": "英镑", "symbol": "£", "iso_name": "Pound Sterling"},
            {"code": "AUD", "name": "澳元", "symbol": "A$", "iso_name": "Australian Dollar"},
            {"code": "CAD", "name": "加元", "symbol": "C$", "iso_name": "Canadian Dollar"},
            {"code": "CHF", "name": "瑞士法郎", "symbol": "Fr.", "iso_name": "Swiss Franc"},
            {"code": "HKD", "name": "港币", "symbol": "HK$", "iso_name": "Hong Kong Dollar"},
            {"code": "SGD", "name": "新加坡元", "symbol": "S$", "iso_name": "Singapore Dollar"},
        ]
        return random.choice(currency_list)
    
    def generate_unique_code(self, prefix="AT_", tag=None):
        """
        生成唯一编码，使用简化格式确保唯一性
        """
        with self._counter_lock:
            # 原子递增计数器
            MockData._counter += 1
            if MockData._counter > 999:  # 3位计数器
                MockData._counter = 1
            counter = MockData._counter
        
        # 使用时间戳的后8位 + 计数器 + 随机数
        timestamp = int(time.time() * 1000) % 100000000  # 8位时间戳
        random_num = random.randint(100, 999)  # 3位随机数
        
        if tag:
            return f"{prefix}{tag}{timestamp}{counter:03d}{random_num}"
        else:
            return f"{prefix}{timestamp}{counter:03d}{random_num}"
    
    
    def get_mock_remark(self):
        """
        生成备注信息
        
        返回:
            str: 生成的备注信息，包含当前时间
        """
        return f"自动化测试创建 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_timestamp(self, timestamp=False,day_offset=0):
        """
        生成时间戳
        """
        if timestamp:
            return int(time.time() * 1000 + day_offset * 24 * 60 * 60 * 1000)
        return time.strftime("%Y%m%d%H%M%S")

    def get_mock_org_info(self, org_type: str, org_name: str) -> dict:
        """
        生成组织信息
        """
        return {
            "org_code": self.generate_unique_code(tag=org_type),
            "org_name": f"{org_name}_{random.randint(100, 999)}"
        }

    def get_mock_coordinates(self) -> Dict[str, float]:
        """生成随机经纬度坐标
        
        Returns:
            Dict[str, float]: 包含经度和纬度的字典
                - latitude: 纬度 (-90 到 90)
                - longitude: 经度 (-180 到 180)
        """
        return {
            'latitude': round(random.uniform(-90, 90), 6),
            'longitude': round(random.uniform(-180, 180), 6)
        }

    def get_mock_business_scope(self, max_length: int = 200) -> str:
        """生成经营范围（200字内）
        
        Args:
            max_length: 最大长度限制，默认200字
            
        Returns:
            str: 生成的经营范围
        """
        return self.fake.business_scope(max_length)

    def get_mock_company_intro(self, max_length: int = 200) -> str:
        """生成公司简介（200字内）
        
        Args:
            max_length: 最大长度限制，默认200字
            
        Returns:
            str: 生成的公司简介
        """
        return self.fake.company_introduction(max_length)

    def get_mock_enterprise_credentials(self) -> Dict[str, str]:
        """生成企业证照信息（营业执照号、纳税人识别号、统一社会信用代码）
        
        现在企业通常使用统一社会信用代码作为营业执照号和纳税人识别号，
        但有些老企业可能还有独立的纳税人识别号。
        
        统一社会信用代码由18位数字和字母组成：
        - 第1位：登记管理部门代码（1-事业单位，5-社会团体，9-企业，Y-其他组织）
        - 第2位：机构类别代码
        - 第3-8位：登记管理机关行政区划码
        - 第9-17位：主体标识码（组织机构代码）
        - 第18位：校验码
        
        Returns:
            Dict[str, str]: 包含营业执照号、纳税人识别号、统一社会信用代码的字典
        """
        # 生成统一社会信用代码
        # 登记管理部门代码，企业使用9
        dept_code = '9'
        
        # 机构类别代码，企业法人使用1
        org_type = '1'
        
        # 行政区划码（6位），使用faker生成的随机数字
        area_code = self.fake.numerify('######')
        
        # 主体标识码（9位），使用faker生成随机字母数字组合
        main_code = self.fake.bothify('#########').upper()
        
        # 校验码，使用faker随机选择
        check_code = self.fake.random_element(['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'])
        
        # 统一社会信用代码
        business_license_no = f"{dept_code}{org_type}{area_code}{main_code}{check_code}"
        
        # 现在大部分企业的营业执照号和纳税人识别号都是统一社会信用代码
        # 但也提供独立的15位纳税人识别号选项，使用faker生成
        taxpayer_number_15 = self.fake.numerify('###############')
        
        return business_license_no

if __name__ == '__main__':
    # 测试代码
    mock = MockData()
    
    # 测试各种数据生成
    # print("姓名:", mock.get_mock_name())
    # print("地址:", mock.get_mock_address())
    # print("电话:", mock.get_mock_phone_number())
    # print("身份证:", mock.get_mock_ssn())
    # print("邮箱:", mock.get_mock_email())
    # print("公司:", mock.get_mock_company())
    # print("银行信息:", mock.get_mock_bank_info())
    # print("日期:", mock.get_mock_date(include_time=False))
    # print("用户代理:", mock.get_mock_user_agent())
    # print("IP地址:", mock.get_mock_ip())
    # print("URL:", mock.get_mock_url())
    # print("随机文本:", mock.get_mock_text())
    # print("随机选择:", mock.get_mock_choice(['A', 'B', 'C', 'D']))
    # print("币种对象:", mock.get_mock_currency())
    # print("备注:", mock.get_mock_remark())
    # print("时间戳:", mock.get_timestamp(timestamp=True))
    # print("唯一编码:", mock.generate_unique_code())
    print("企业证照信息:", mock.get_mock_enterprise_credentials())
    print("经营范围:", mock.get_mock_business_scope())
    print("公司简介:", mock.get_mock_company_intro())
    
    # print("业务组织数据:", mock.get_mock_org_info(org_type="ComOrg", org_name="某公司"))
    # print("时间戳:", mock.get_mock_date(include_time=False,days_offset=-1))
    # print("坐标:", mock.get_mock_coordinates())
