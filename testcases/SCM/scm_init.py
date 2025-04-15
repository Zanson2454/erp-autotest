import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime
from decimal import Decimal
import time

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)

from utils.YamlUtil import YamlReader
from utils.MysqlUtil import DBManager
from utils.LogUtil import Loggers

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
    _cache_file = os.path.join(project_root, "data", "cache", "scm_init_cache.json")
    
    def __init__(self):
        """初始化测试类"""
        # 初始化日志
        self.logger = Loggers()
        
        # 设置配置文件路径
        self.scm_config_path = os.path.join(project_root, "data", "init", "scm_config.yml")
        
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
                "base_info": {
                    "country_info": {...},
                    "currency_info": {...},
                    ...
                },
                "org_info": {
                    "group_org": {...},
                    "adm_org": {...},
                    "com_org": {...},
                    "pur_org": {...},
                    "inv_org": {...},
                    "sls_org": {...}
                }
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
                "base_info": {},  # 基础配置数据
                "org_info": {},   # 组织信息
                "partner_info": {},  # 合作伙伴信息
                "material_info": {}  # 物料相关信息
            }
            
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

if __name__ == "__main__":
    # 执行初始化
    scm_init = InitSQL()
    
    # 第一次调用，应该执行SQL查询
    print("\n第一次调用SCM初始化:")
    start_time = time.time()
    scm_data1 = scm_init.init_sql()
    end_time = time.time()
    print(f"第一次调用耗时: {end_time - start_time:.2f}秒")
    
    # 等待1秒
    time.sleep(1)
    
    # 第二次调用，应该使用缓存
    print("\n第二次调用SCM初始化:")
    start_time = time.time()
    scm_data2 = scm_init.init_sql()
    end_time = time.time()
    print(f"第二次调用耗时: {end_time - start_time:.2f}秒")
    
    # 验证两次结果是否相同
    if scm_data1 == scm_data2:
        print("两次调用结果相同，SCM初始化缓存机制工作正常")
    else:
        print("两次调用结果不同，SCM初始化缓存机制可能存在问题")
