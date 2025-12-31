"""
主数据工厂模块

提供主数据工厂的基础功能，包括：
- 异常类定义
- 通用数据获取方法
- 基础初始化方法

具体的主数据工厂类（组织、物料、合作伙伴）继承基类
"""

from typing import Dict, Any, Optional
from data_factory.base import DataFactory
from utils.mysql_util import DBManager


# ========== 异常类定义 ==========

class MasterDataFactoryError(Exception):
    """主数据工厂基础异常"""
    pass


class OrganizationTypeError(MasterDataFactoryError):
    """组织类型错误"""
    pass


class DependencyNotFoundError(MasterDataFactoryError):
    """依赖数据未找到错误"""
    pass


class APICallError(MasterDataFactoryError):
    """API调用错误"""
    pass


# ========== 基类定义 ==========

class MasterDataFactory(DataFactory):
    """主数据工厂基类"""
    
    def __init__(self, http_client, apis: dict, api_params: dict,
                 mock_util, logger, init_data: dict = None,
                 md_cache_data: dict = None, db: DBManager = None,
                 standard_api_call=None):
        """
        初始化主数据工厂
        
        参数:
            http_client: HTTP客户端（从BaseTest获取）
            apis: API路径配置字典
            api_params: API参数配置字典
            mock_util: Mock工具实例
            logger: 日志实例
            init_data: 基础数据缓存
            md_cache_data: 主数据缓存
            db: 数据库管理器（可选，用于查询依赖数据）
            standard_api_call: standard_api_call方法（从BaseTest获取）
        """
        super().__init__()
        self.http = http_client
        self.apis = apis
        self.api_params = api_params
        self.mock_util = mock_util
        self.logger = logger
        self.init_data = init_data or {}
        self.md_cache_data = md_cache_data or {}
        self.db = db
        self.standard_api_call = standard_api_call
        
        if not self.standard_api_call:
            raise ValueError("standard_api_call 方法必须提供")
    
    # ========== 数据获取方法（内部使用，供子类调用）==========
    
    def _get_country_id(self) -> Optional[int]:
        """获取国家ID"""
        country_info = self.init_data.get("country_info", [])
        if country_info and len(country_info) > 0:
            return country_info[0].get("coun_id")
        return None
    
    def _get_currency_id(self) -> Optional[int]:
        """获取币种ID"""
        currency_info = self.init_data.get("currency_info", [])
        if currency_info and len(currency_info) > 0:
            return currency_info[0].get("curr_id")
        return None
    
    def _get_addr_id(self) -> Optional[int]:
        """获取地址ID"""
        addr_info = self.init_data.get("addr_info", [])
        if addr_info and len(addr_info) > 0:
            return addr_info[0].get("id")
        return None
    
    def _get_bank_id(self) -> Optional[int]:
        """获取银行ID"""
        bank_info = self.init_data.get("bank_info", [])
        if bank_info and len(bank_info) > 0:
            return bank_info[0].get("bank_id")
        return None
    
    def _get_calender_id(self) -> Optional[int]:
        """获取日历ID"""
        calender_info = self.init_data.get("calender_info", [])
        if calender_info and len(calender_info) > 0:
            return calender_info[0].get("id")
        return None
    
    def _get_wc_head_id(self) -> Optional[int]:
        """获取工作中心ID"""
        gen_wc_head_info = self.init_data.get("gen_wc_head_info", [])
        if gen_wc_head_info and len(gen_wc_head_info) > 0:
            return gen_wc_head_info[0].get("gen_wc_head_id")
        return None
    
    def _get_sls_dc_id(self) -> Optional[int]:
        """获取销售配送中心ID"""
        sls_dc_md = self.md_cache_data.get("org_info", {}).get("sls_dc_md", [])
        if sls_dc_md and len(sls_dc_md) > 0:
            return sls_dc_md[0].get("id")
        return None
    
    def _safe_get_from_list(self, data_list: list, key: str, default=None):
        """安全地从列表中获取第一个元素"""
        if data_list and len(data_list) > 0:
            return data_list[0].get(key, default)
        return default

