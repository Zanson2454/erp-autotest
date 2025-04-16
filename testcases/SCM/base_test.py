import json
import pytest
from loguru import logger
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from common.login_manager import LoginManager
from config.config import Config
from utils.AssertUtil import AssertHelper
from utils.LogUtil import Loggers
from utils.MysqlUtil import DBManager
from utils.HttpUtil import HttpUtil
from utils.ExceptionUtil import handle_exception, safe_api_call, handle_class_method_exception
from testcases.SCM.scm_init import InitSQL

class DecimalEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 Decimal 类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DecimalEncoder, self).default(obj)

class BaseTest:
    """SCM 测试基类，提供公共方法"""
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls):
        """测试类初始化，获取必要的配置信息"""
        # 初始化基础组件
        cls.logger = Loggers()
        cls.db = DBManager()
        cls.http = HttpUtil()
        cls.assert_util = AssertHelper()
        
        # 初始化SQL工具并获取初始化数据（利用缓存机制）
        cls.init_sql = InitSQL()
        init_data = cls.init_sql.init_sql()
        logger.info(f"初始化数据: {init_data}")
        # 只获取需要的配置信息
        cls.init_data = {
            "user_info": {
                "user_info": init_data["base_info"]["user_info"]
            },
            "base_info": {
                "so_type_info": init_data["base_info"]["so_type_info"],
                "sales_channel_info": init_data["base_info"]["sales_channel_info"],
                "exchange_rate_type_info": init_data["base_info"]["exchange_rate_type_info"],
                "currency_info": init_data["base_info"]["currency_info"]
            },
            "org_info": {
                "sls_org_info": init_data["org_info"]["sls_org_info"],
                "pur_org_info": init_data["org_info"]["pur_org_info"],
                "inv_org_info": init_data["org_info"]["inv_org_info"],
                "com_org_info": init_data["org_info"]["com_org_info"]
            },
            "partner_info": {
                "cust_info": init_data["partner_info"]["cust_info"]
            },
            "material_info": {
                "inv_loc_info": init_data["material_info"]["inv_loc_info"]
            }
        }
        
        # 提取必要的ID
        cls._extract_ids()
        
        # 初始化登录和API配置
        cls.login_manager = LoginManager()
        cls.session = cls.login_manager.login()
        cls.base_url = Config.get_api_base_url()
        
        # 初始化测试数据
        cls.test_data = {}
        
        cls.logger.info("测试类初始化完成")
    
    @classmethod
    def _extract_ids(cls) -> None:
        """提取必要的ID并验证"""
        id_mappings = {
            'user_id': ('user_info', 'user_info', 'id'),
            'cust_id': ('partner_info', 'cust_info', 'id'),
            'so_type_id': ('base_info', 'so_type_info', 'id'),
            'sls_org_id': ('org_info', 'sls_org_info', 'id'),
            'pur_org_id': ('org_info', 'pur_org_info', 'id'),
            'inv_org_id': ('org_info', 'inv_org_info', 'id'),
            'com_org_id': ('org_info', 'com_org_info', 'id'),
            'sls_dc_id': ('base_info', 'sales_channel_info', 'id'),
            'inv_loc_id': ('material_info', 'inv_loc_info', 'id'),
            'exchange_rate_type_id': ('base_info', 'exchange_rate_type_info', 'exchange_rate_type_id'),
            'base_curr_id': ('base_info', 'currency_info', 'curr_id'),
            'sls_curr_id': ('base_info', 'currency_info', 'curr_id')
        }
        
        for attr_name, path in id_mappings.items():
            value = cls.init_data
            for key in path:
                value = value[key]
            setattr(cls, attr_name, value)
            cls.assert_util.assert_id_exists(value, f"{attr_name.replace('_', ' ').title()}")
    
    def setup_method(self, method=None):
        """测试方法开始前的设置"""
        if method and hasattr(method, '__name__'):
            logger.info(f"开始测试: {method.__name__}")
        else:
            logger.info("开始测试方法")
        self.test_data = {}
    
    def _make_request(self, url: str, data: dict, description: str = "", extract_nested_data: bool = False) -> dict:
        """发送请求并处理响应
        
        Args:
            url: 请求URL
            data: 请求数据
            description: 请求描述，用于日志记录
            extract_nested_data: 是否提取嵌套的 data 结构
            
        Returns:
            dict: 响应数据
        """
        try:
            if description:
                logger.info(f"发送请求: {description}")
            response = self.session.post(url, json=data)
            response.raise_for_status()
            response_data = response.json()
            
            # 如果需要提取嵌套的 data 结构
            if extract_nested_data and "data" in response_data:
                nested_data = response_data["data"]
                if isinstance(nested_data, dict) and "data" in nested_data:
                    nested_data = nested_data["data"]
                    if isinstance(nested_data, dict) and "data" in nested_data:
                        nested_data = nested_data["data"]
                return nested_data
            
            return response_data
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            raise 