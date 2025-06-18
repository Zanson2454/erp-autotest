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

class ERPProvider(BaseProvider):
    """ERP主数据模拟数据提供器"""
    
    def erp_currency_code(self) -> str:
        """生成币种代码"""
        currencies = ['CNY', 'USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'HKD', 'SGD']
        return random.choice(currencies)
    
    def erp_tax_rate(self) -> float:
        """生成税率"""
        rates = [0.00, 0.03, 0.06, 0.09, 0.13, 0.17]
        return random.choice(rates)
    
    def erp_timezone(self) -> str:
        """生成时区"""
        timezones = ['UTC+8', 'UTC+0', 'UTC-5', 'UTC-8', 'UTC+1', 'UTC+2', 'UTC+9']
        return random.choice(timezones)
    
    def erp_exchange_rate(self) -> float:
        """生成汇率"""
        return round(random.uniform(0.1, 10.0), 4)
    
    def erp_material_code(self, prefix: str = 'MAT') -> str:
        """生成物料编码"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        return f"{prefix}{timestamp}{suffix}"
    
    def erp_material_type(self) -> str:
        """生成物料类型"""
        types = ['原材料', '半成品', '成品', '包装材料', '备品备件', '消耗品']
        return random.choice(types)
    
    def erp_material_unit(self) -> str:
        """生成物料单位"""
        units = ['个', '件', '套', 'kg', 'm', 'm²', 'm³', 'L', 'mL', 't']
        return random.choice(units)
    
    def erp_org_code(self, prefix: str = 'ORG') -> str:
        """生成组织编码"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(3)])
        return f"{prefix}{timestamp}{suffix}"
    
    def erp_org_type(self) -> str:
        """生成组织类型"""
        types = ['公司', '部门', '事业部', '工厂', '仓库', '车间', '班组']
        return random.choice(types)
    
    def erp_partner_type(self) -> str:
        """生成合作伙伴类型"""
        types = ['供应商', '客户', '承运商', '分销商', '服务商']
        return random.choice(types)
    
    def erp_partner_level(self) -> str:
        """生成合作伙伴等级"""
        levels = ['A', 'B', 'C', 'D']
        return random.choice(levels)
    
    def erp_qualification_type(self) -> str:
        """生成资质类型"""
        types = ['营业执照', '生产许可证', '经营许可证', '质量认证', '安全认证', '环保认证']
        return random.choice(types)
    
    def erp_bom_type(self) -> str:
        """生成BOM类型"""
        types = ['工程BOM', '生产BOM', '销售BOM', '成本BOM', '计划BOM']
        return random.choice(types)
    
    def erp_bom_version(self) -> str:
        """生成BOM版本号"""
        major = random.randint(1, 9)
        minor = random.randint(0, 99)
        patch = random.randint(0, 99)
        return f"V{major}.{minor:02d}.{patch:02d}"

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
    7. ERP主数据信息
    
    使用示例：
    ```python
    mock = MockData()
    name = mock.get_mock_name()
    company = mock.get_mock_company()
    material_code = mock.get_mock_material_code()
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
        self.fake.add_provider(ERPProvider)
    
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
    
    def get_mock_material_code(self, prefix: str = 'MAT') -> str:
        """生成物料编码
        
        Args:
            prefix: 编码前缀，默认为'MAT'
            
        Returns:
            str: 随机生成的物料编码
        """
        return self.fake.erp_material_code(prefix)
    
    def get_mock_material_info(self) -> Dict[str, str]:
        """生成物料基本信息
        
        Returns:
            Dict[str, str]: 包含物料基本信息的字典
        """
        return {
            'code': self.fake.erp_material_code(),
            'name': f"测试物料_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': self.fake.erp_material_type(),
            'unit': self.fake.erp_material_unit()
        }
    
    def get_mock_org_info(self) -> Dict[str, str]:
        """生成组织基本信息
        
        Returns:
            Dict[str, str]: 包含组织基本信息的字典
        """
        return {
            'code': self.fake.erp_org_code(),
            'name': f"测试组织_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': self.fake.erp_org_type()
        }
    
    def get_mock_partner_info(self) -> Dict[str, str]:
        """生成合作伙伴基本信息
        
        Returns:
            Dict[str, str]: 包含合作伙伴基本信息的字典
        """
        return {
            'code': f"PAR{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': self.get_mock_company(),
            'type': self.fake.erp_partner_type(),
            'level': self.fake.erp_partner_level()
        }
    
    def get_mock_bom_info(self) -> Dict[str, str]:
        """生成BOM基本信息
        
        Returns:
            Dict[str, str]: 包含BOM基本信息的字典
        """
        return {
            'code': f"BOM{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': f"测试BOM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'type': self.fake.erp_bom_type(),
            'version': self.fake.erp_bom_version()
        }
    
    def get_mock_currency_info(self) -> Dict[str, Union[str, float]]:
        """生成币种基本信息
        
        Returns:
            Dict[str, Union[str, float]]: 包含币种基本信息的字典
        """
        currency_code = self.fake.erp_currency_code()
        return {
            'code': currency_code,
            'name': f"{currency_code}币种",
            'exchange_rate': self.fake.erp_exchange_rate()
        }
    
    def get_mock_tax_info(self) -> Dict[str, Union[str, float]]:
        """生成税率基本信息
        
        Returns:
            Dict[str, Union[str, float]]: 包含税率基本信息的字典
        """
        tax_rate = self.fake.erp_tax_rate()
        return {
            'code': f"TAX{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': f"{int(tax_rate * 100)}%税率",
            'rate': tax_rate
        }

if __name__ == '__main__':
    # 测试代码
    mock = MockData()
    
    # 测试基础数据生成
    print("姓名:", mock.get_mock_name())
    print("地址:", mock.get_mock_address())
    print("电话:", mock.get_mock_phone_number())
    print("身份证:", mock.get_mock_ssn())
    print("邮箱:", mock.get_mock_email())
    print("公司:", mock.get_mock_company())
    print("银行信息:", mock.get_mock_bank_info())
    print("日期:", mock.get_mock_date())
    
    # 测试ERP主数据生成
    print("\nERP主数据测试:")
    print("物料信息:", mock.get_mock_material_info())
    print("组织信息:", mock.get_mock_org_info())
    print("合作伙伴信息:", mock.get_mock_partner_info())
    print("BOM信息:", mock.get_mock_bom_info())
    print("币种信息:", mock.get_mock_currency_info())
    print("税率信息:", mock.get_mock_tax_info())
