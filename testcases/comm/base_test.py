import json
import pytest
import os
import sys
import yaml
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
import time

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from common.login_manager import LoginManager
from common.config_manager import ConfigManager
from utils.assert_util import AssertHelper
from utils.log_util import Loggers
from utils.mysql_util import DBManager
from utils.http_util import HttpUtil
from utils.exception_util import handle_exception, safe_api_call, handle_class_method_exception
from utils.yaml_util import YamlUtil
from utils.mock_util import MockData

class DecimalEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 Decimal 类型"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(DecimalEncoder, self).default(obj)

class InitSQL:
    """SQL初始化测试类，用于执行和验证数据库初始化SQL"""
    # 类变量，用于存储初始化结果
    _scm_init_cache = None
    _cache_file = os.path.join(project_root, "testcases", "comm", "cache", "scm_init_cache.json")

    def __init__(self):
        """初始化测试类"""
        # 初始化日志
        self.logger = Loggers()
        # 设置配置文件路径
        self.gen_config_path = os.path.join(project_root,  "config","biz", "gen_config.yml")
        # 初始化数据库管理器
        self.db = DBManager()

    def _load_cache(self) -> Dict[str, Any]:
        """从文件加载缓存"""
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"加载缓存文件失败: {str(e)}")
        return None

    def _save_cache(self, data: Dict[str, Any]) -> None:
        """保存缓存到文件"""
        try:
            os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
        except Exception as e:
            self.logger.warning(f"保存缓存文件失败: {str(e)}")

    def _format_datetime(self, value: Any) -> Any:
        """格式化日期时间值"""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value

    def _format_result(self, result: List[Dict]) -> List[Dict]:
        """格式化查询结果"""
        formatted = []
        for row in result:
            formatted_row = {}
            for key, value in row.items():
                formatted_row[key] = self._format_datetime(value)
            formatted.append(formatted_row)
        return formatted

    def init_sql(self) -> Dict[str, Any]:
        """
        从YAML配置文件读取SQL查询并执行
        Returns:
            Dict[str, Any]: {
                "base_info": {...},
                "org_info": {...},
                ...
            }
        """
        # 如果已经有缓存的结果，直接返回，不执行任何SQL查询
        if InitSQL._scm_init_cache is not None:
            self.logger.info("内存缓存命中：使用缓存的SCM初始化数据")
            return InitSQL._scm_init_cache
        # 尝试从文件加载缓存
        file_cache = self._load_cache()
        if file_cache is not None:
            self.logger.info("文件缓存命中：使用缓存的SCM初始化数据")
            InitSQL._scm_init_cache = file_cache
            return file_cache
        self.logger.info("缓存未命中：开始执行SCM初始化")
        self.logger.info(f"配置文件路径: {self.scm_config_path}")
        try:
            # 读取YAML配置文件
            yaml_reader = YamlReader(self.scm_config_path)
            scm_config = yaml_reader.data()
            # 初始化返回结果
            scm_init_data = {
                "user_info": {},  # 用户信息
                "base_info": {},  # 基础配置数据
                "org_info": {},   # 组织信息
                "partner_info": {},  # 合作伙伴信息
                "material_info": {}  # 物料相关信息
            }
            # 获取用户信息
            user_info = self.db.query_all(scm_config['base_info']['user_info']['sql'])
            if not user_info:
                raise ValueError("未找到用户信息")
            # 存储用户信息
            scm_init_data['user_info'] = user_info[0]  # 直接存储第一条用户记录
            self.logger.info(f"成功初始化用户信息: {user_info[0]}")
            # 执行查询并格式化结果
            for query_key, query_config in scm_config['base_info'].items():
                try:
                    self.logger.info(f"执行SCM查询: {query_key}")
                    self.logger.debug(f"SQL: {query_config['sql']}")
                    # 执行SQL查询
                    query_result = self.db.query_all(query_config['sql'])
                    formatted_result = self._format_result(query_result)
                    # 根据查询类型分类存储结果
                    if 'org' in query_key:
                        scm_init_data['org_info'][query_key] = formatted_result[0] if formatted_result else None
                    elif 'partner' in query_key or 'vend' in query_key or 'cust' in query_key:
                        scm_init_data['partner_info'][query_key] = formatted_result[0] if formatted_result else None
                    elif 'mat' in query_key or 'atp' in query_key or 'inv' in query_key:
                        scm_init_data['material_info'][query_key] = formatted_result[0] if formatted_result else None
                    else:
                        scm_init_data['base_info'][query_key] = formatted_result[0] if formatted_result else None
                    self.logger.info(f"SCM查询 {query_key} 执行成功")
                except Exception as e:
                    self.logger.error(f"执行SCM查询 {query_key} 时出错: {str(e)}")
                    raise
            # 将结果存入内存缓存和文件缓存
            InitSQL._scm_init_cache = scm_init_data
            self._save_cache(scm_init_data)
            self.logger.info("SCM初始化数据已缓存")
            return scm_init_data
        except Exception as e:
            self.logger.error(f"初始化SCM SQL时出错: {str(e)}")
            raise

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
        cls.base_url = YamlUtil().get_base_url()
        # 初始化请求头
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
            self.logger.info(f"开始测试: {method.__name__}")
        else:
            self.logger.info("开始测试方法")
        self.test_data = {}

    def _make_request(self, url: str, data: dict, description: str = "", extract_nested_data: bool = False, headers: dict = None) -> dict:
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
                self.logger.info(f"发送请求: {description}")
            response = self.session.post(url, json=data, headers=self.headers)
            self.last_response_text = response.text  # 保存原始响应内容
            response.raise_for_status()
            response_data = response.json()
            # 如果需要提取嵌套的 data 结构
            if extract_nested_data:
                if isinstance(response_data, dict) and "data" in response_data:
                    nested_data = response_data["data"]
                    if isinstance(nested_data, dict) and "data" in nested_data:
                        nested_data = nested_data["data"]
                        if isinstance(nested_data, dict) and "data" in nested_data:
                            nested_data = nested_data["data"]
                    return nested_data
                else:
                    # 没有嵌套结构时，强制输出原始HTTP响应内容
                    self.logger.error(f"extract_nested_data=True 但响应无嵌套data字段，原始response.text: {response.text}")
                    self.logger.error(f"extract_nested_data=True 但响应无嵌套data字段，response.json: {json.dumps(response_data, ensure_ascii=False, indent=2) if isinstance(response_data, dict) else response_data}")
                    return response_data
            return response_data
        except Exception as e:
            # 异常时也输出原始响应内容
            if 'response' in locals() and response is not None:
                try:
                    self.logger.error(f"接口原始响应内容: {response.text}")
                except Exception:
                    pass
            self.logger.error(f"请求失败: {str(e)}")
            raise

    def _make_request_with_assertion(self, url: str, data: dict, description: str = "", extract_nested_data: bool = False, headers: dict = None) -> dict:
        """发送请求并处理响应，并断言业务成功"""
        result = self._make_request(url, data, description, extract_nested_data, headers)
        if isinstance(result, dict) and not result.get("success", True):
            self.logger.error(f"业务失败，原始响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            raise ValueError(f"接口业务失败: {result.get('err', {}).get('msg', '未知错误')}")
        return result
if __name__ == "__main__":
    test = BaseTest()
    test.setup_class()