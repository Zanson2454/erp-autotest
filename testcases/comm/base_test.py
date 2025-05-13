"""测试基类模块

提供测试用例的基础功能，包括：
1. 环境初始化
2. 数据库操作
3. HTTP 请求处理
4. 断言工具
5. 日志记录
6. 测试数据管理

使用示例：python -m pytest testcases/comm/base_test.py
@allure.epic("进销存管理")
@allure.feature("订单管理")
class TestOrder(BaseTest):
    @allure.story("供应商订单创建")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_supplier_order(self):
        # 验证不同供应商类型的折扣计算逻辑
        pass

"""

import json
import pytest
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys
import os
import time

# Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))

from common.login_manager import LoginManager
from utils.yaml_util import YamlUtil
from utils.assert_util import AssertHelper
from utils.log_util import Loggers
from utils.mysql_util import DBManager
from utils.http_util import HttpUtil
from utils.exception_util import handle_exception, safe_api_call, handle_class_method_exception
from utils.mock_util import MockData

# 初始化日志工具
log = Loggers()

class DecimalEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 Decimal 类型
    
    支持以下类型的序列化：
    - Decimal: 转换为 float
    - datetime: 转换为 ISO 格式字符串
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DecimalEncoder, self).default(obj)


class InitSQL:
    """SQL初始化测试类
    
    用于执行和验证数据库初始化SQL，支持缓存机制。
    """
    def __init__(self) -> None:
        """初始化测试类"""
        self.log = log  # 使用模块级别的日志工具
        # 更新配置文件路径
        self.gen_config_path = project_root / "config" / "biz" / "gen.yaml"
        self.db = DBManager()
        # 修改缓存目录到 testcases/comm/cache
        self.cache_dir = Path(__file__).parent / "cache"
        self.cache_file = self.cache_dir / "init_cache.json"
        self.log.info(f"缓存文件路径: {self.cache_file}")
        self.cache_expire_minutes = 30

    def _get_cache_data(self) -> Optional[Dict[str, Any]]:
        """获取缓存数据
        
        Returns:
            Optional[Dict[str, Any]]: 缓存数据，如果不存在则返回None
        """
        try:
            if not self.cache_file.exists():
                self.log.info(f"缓存文件不存在: {self.cache_file}")
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                self.log.info(f"成功从缓存文件加载数据: {self.cache_file}")
                return cache_data
        except Exception as e:
            self.log.warning(f"读取缓存数据失败: {str(e)}")
            return None
            
    def _write_cache_data(self, data: Dict[str, Any]) -> None:
        """写入缓存数据
        
        Args:
            data: 要缓存的数据
        """
        try:
            # 确保缓存目录存在
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # 写入缓存文件
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
            self.log.info(f"成功写入缓存文件: {self.cache_file}")
        except Exception as e:
            self.log.warning(f"写入缓存数据失败: {str(e)}")
   

    def init_sql(self) -> Dict[str, Any]:
        """初始化SQL数据
        
        Returns:
            Dict[str, Any]: 初始化数据
        """
        try:
            # 尝试从缓存获取数据
            cache_data = self._get_cache_data()
            if cache_data:
                self.log.info("从缓存获取数据成功")
                return cache_data
                
            # 缓存不存在或已过期，重新初始化数据
            self.log.info("缓存数据不存在或已过期，开始初始化数据")
            init_data = self._init_sql_impl()
            
            # 写入缓存
            self._write_cache_data(init_data)
            self.log.info("数据初始化完成并写入缓存")
            
            return init_data
        except Exception as e:
            self.log.error(f"初始化SQL时出错: {str(e)}")
            raise

    def _init_sql_impl(self) -> Dict[str, Any]:
        """实际的SQL初始化实现
        
        Returns:
            Dict[str, Any]: 初始化数据
        """
        self.log.info("开始执行init_sql方法...")
        
        # 读取YAML配置文件
        self.log.info(f"尝试读取配置文件: {self.gen_config_path}")
        yaml_util = YamlUtil()
        
        if not self.gen_config_path.exists():
            error_msg = f"配置文件不存在: {self.gen_config_path}"
            self.log.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        scm_config = yaml_util.read_yaml(self.gen_config_path)
        if not scm_config:
            error_msg = f"配置文件为空: {self.gen_config_path}"
            self.log.error(error_msg)
            raise ValueError(error_msg)
            
        self.log.info(f"成功读取配置文件: {self.gen_config_path}")
        self.log.debug(f"配置文件内容: {json.dumps(scm_config, ensure_ascii=False, indent=2)}")

        # 初始化返回结果
        init_data = {
            "user_info": {},
            "base_info": {},
            "org_info": {},
            "partner_info": {},
            "material_info": {}
        }

        # 获取用户信息
        if 'base_info' not in scm_config:
            error_msg = "配置文件中缺少 base_info 配置"
            self.log.error(error_msg)
            raise ValueError(error_msg)
            
        if 'user_info' not in scm_config['base_info']:
            error_msg = "配置文件中缺少 user_info 配置"
            self.log.error(error_msg)
            raise ValueError(error_msg)
            
        user_info_sql = scm_config['base_info']['user_info'].get('sql')
        if not user_info_sql:
            error_msg = "user_info 配置中缺少 SQL 语句"
            self.log.error(error_msg)
            raise ValueError(error_msg)
            
        self.log.info(f"执行用户信息查询SQL: {user_info_sql}")
        user_info = self.db.execute_query(user_info_sql)
        if not user_info:
            error_msg = "未找到用户信息"
            self.log.error(error_msg)
            raise ValueError(error_msg)
            
        init_data['user_info'] = user_info[0]
        self.log.info(f"成功初始化用户信息: {user_info[0]}")

        # 执行查询并格式化结果
        for query_key, query_config in scm_config.get('base_info', {}).items():
            try:
                self.log.info(f"执行查询: {query_key}")
                sql = query_config.get('sql', '')
                self.log.debug(f"SQL: {sql}")
                
                if not sql:
                    self.log.warning(f"查询配置缺少SQL语句: {query_key}")
                    continue
                    
                query_result = self.db.execute_query(sql)
                formatted_result = self._format_result(query_result)
                
                # 根据查询类型分类存储结果
                if 'org' in query_key:
                    init_data['org_info'][query_key] = formatted_result[0] if formatted_result else None
                elif 'partner' in query_key or 'vend' in query_key or 'cust' in query_key:
                    init_data['partner_info'][query_key] = formatted_result[0] if formatted_result else None
                elif 'mat' in query_key or 'atp' in query_key or 'inv' in query_key:
                    init_data['material_info'][query_key] = formatted_result[0] if formatted_result else None
                else:
                    init_data['base_info'][query_key] = formatted_result[0] if formatted_result else None
                    
                self.log.info(f"查询 {query_key} 执行成功")
            except Exception as e:
                self.log.error(f"执行查询 {query_key} 时出错: {str(e)}")
                raise

        self.log.info("所有查询执行完成")
        return init_data

    def _format_result(self, result: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """格式化查询结果
        
        Args:
            result: 原始查询结果列表
            
        Returns:
            List[Dict[str, Any]]: 格式化后的结果列表
        """
        if not result:
            return []
            
        # 处理Decimal类型
        formatted_result = []
        for row in result:
            formatted_row = {}
            for key, value in row.items():
                if isinstance(value, Decimal):
                    formatted_row[key] = float(value)
                elif isinstance(value, datetime):
                    formatted_row[key] = value.isoformat()
                else:
                    formatted_row[key] = value
            formatted_result.append(formatted_row)
            
        return formatted_result


class BaseTest:
    """测试基类
    
    提供测试用例的公共功能，包括：
    1. 环境初始化
    2. 数据库操作
    3. HTTP 请求处理
    4. 断言工具
    5. 日志记录
    6. 测试数据管理
    """
    
    @classmethod
    @handle_class_method_exception(log_level="ERROR")
    def setup_class(cls) -> None:
        """测试类初始化
        
        初始化必要的组件和配置信息，包括：
        1. 日志工具
        2. 数据库管理器
        3. HTTP 工具
        4. 断言工具
        5. SQL 初始化工具
        6. 登录管理器
        7. 请求头配置
        """
        # 初始化基础组件
        cls.log = log  # 使用模块级别的日志工具
        cls.db = DBManager()
        cls.http = HttpUtil()
        cls.assert_util = AssertHelper()
        
        # 初始化SQL工具并获取初始化数据
        cls.log.info("开始初始化SQL工具...")
        cls.init_sql = InitSQL()
        cls.log.info("SQL工具初始化完成，开始获取初始化数据...")
        
        # 直接调用实例方法，而不是通过属性访问
        init_data = cls.init_sql.init_sql()
        cls.log.info(f"获取到的初始化数据类型: {type(init_data)}")
        
        if not isinstance(init_data, dict):
            error_msg = f"初始化数据格式错误，期望dict类型，实际为{type(init_data)}"
            cls.log.error(error_msg)
            raise TypeError(error_msg)
            
        # 提取必要的配置信息
        cls.log.info("开始提取配置信息...")
        cls.init_data = {
            "user_info": {
                "user_info": init_data.get("base_info", {}).get("user_info", {})
            },
            "base_info": {
                "so_type_info": init_data.get("base_info", {}).get("so_type_info", {}),
                "sales_channel_info": init_data.get("base_info", {}).get("sales_channel_info", {}),
                "exchange_rate_type_info": init_data.get("base_info", {}).get("exchange_rate_type_info", {}),
                "currency_info": init_data.get("base_info", {}).get("currency_info", {})
            },
            "org_info": {
                "sls_org_info": init_data.get("org_info", {}).get("sls_org_info", {}),
                "pur_org_info": init_data.get("org_info", {}).get("pur_org_info", {}),
                "inv_org_info": init_data.get("org_info", {}).get("inv_org_info", {}),
                "com_org_info": init_data.get("org_info", {}).get("com_org_info", {})
            },
            "partner_info": {
                "cust_info": init_data.get("partner_info", {}).get("cust_info", {})
            },
            "material_info": {
                "inv_loc_info": init_data.get("material_info", {}).get("inv_loc_info", {})
            }
        }
        cls.log.info("配置信息提取完成")
        
        # 提取必要的ID
        cls.log.info("开始提取ID信息...")
        cls._extract_ids()
        cls.log.info("ID信息提取完成")
        
        # 初始化登录和API配置
        cls.log.info("开始初始化登录和API配置...")
        cls.login_manager = LoginManager()
        cls.session = cls.login_manager.login()
        cls.base_url = YamlUtil().get_base_url()
        cls.log.info("登录和API配置初始化完成")
        
        # 初始化请求头
        cls.log.info("开始初始化请求头...")
        cls.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': cls.base_url,
            'Pragma': 'no-cache',
            'Referer': f"{cls.base_url}/TERP_PORTAL-TERP",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': MockData().get_mock_user_agent()
        }
        cls.log.info("请求头初始化完成")
        
        # 初始化测试数据
        cls.test_data = {}
        cls.log.info("测试类初始化完成")

    @classmethod
    def _extract_ids(cls) -> None:
        """提取必要的ID并验证
        
        从初始化数据中提取各种ID，并进行存在性验证。
        包括：用户ID、客户ID、订单类型ID、组织ID等。
        """
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
                value = value.get(key, {})
            setattr(cls, attr_name, value)
            cls.assert_util.assert_id_exists(value, f"{attr_name.replace('_', ' ').title()}")

    def setup_method(self, method: Optional[pytest.Function] = None) -> None:
        """测试方法开始前的设置
        
        Args:
            method: 当前执行的测试方法
        """
        if method and hasattr(method, '__name__'):
            self.log.info(f"开始测试: {method.__name__}")
        else:
            self.log.info("开始测试方法")
        self.test_data = {}



if __name__ == "__main__":
    test = BaseTest()
    test.setup_class()