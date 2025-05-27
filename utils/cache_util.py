"""缓存工具模块

提供缓存数据的读写功能，支持过期机制。
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.response_util import DecimalEncoder

class CacheUtil:
    """缓存工具类（全类属性+类方法风格）
    
    使用示例:
        CacheUtil.init(cache_dir="cache", expire_minutes=60)
        CacheUtil.set("user_info", {"id": 1, "name": "test"})
        user_info = CacheUtil.get("user_info")
    """
    _cache_dir = Path("cache")
    _expire_minutes = 30
    _initialized = False
    _cache_data = {}  # 存储加载的缓存数据

    @classmethod
    def init(cls, cache_dir: str = "cache", expire_minutes: int = 30):
        if not cls._initialized:
            cls._cache_dir = Path(cache_dir)
            cls._expire_minutes = expire_minutes
            cls._cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"缓存目录: {cls._cache_dir.absolute()}")
            logger.info(f"缓存目录创建状态: 存在={cls._cache_dir.exists()}")
            cls._initialized = True

    @classmethod
    def get(cls, key: str) -> Optional[Dict[str, Any]]:
        cache_file = cls._cache_dir / f"{key}.json"
        logger.info(f"读取缓存文件: {cache_file.absolute()}")
        try:
            if not cache_file.exists():
                logger.info(f"缓存文件不存在: {cache_file.absolute()}")
                return None
            if cls._is_expired(cache_file):
                logger.info(f"缓存文件已过期: {cache_file.absolute()}")
                return None
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功读取缓存: {cache_file.name}")
                return data
        except Exception as e:
            logger.error(f"读取缓存失败: {str(e)}, 文件: {cache_file.absolute()}")
            return None

    @classmethod
    def set(cls, key: str, data: Dict[str, Any]) -> None:
        cache_file = cls._cache_dir / f"{key}.json"
        logger.info(f"写入缓存文件: {cache_file.absolute()}")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
                logger.info(f"成功写入缓存: {cache_file.name}")
        except Exception as e:
            logger.error(f"写入缓存失败: {str(e)}, 文件: {cache_file.absolute()}")

    @classmethod
    def exists(cls, key: str) -> bool:
        cache_file = cls._cache_dir / f"{key}.json"
        return cache_file.exists() and not cls._is_expired(cache_file)

    @classmethod
    def _is_expired(cls, cache_file: Path) -> bool:
        file_time = cache_file.stat().st_mtime
        current_time = time.time()
        return (current_time - file_time) > (cls._expire_minutes * 60) 

    @classmethod
    def load_sls_cache(cls, cache_file_path: str) -> None:
        """加载销售订单缓存数据
        
        Args:
            cache_file_path: 缓存文件路径
        """
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                cls._cache_data = json.load(f)
                logger.info(f"成功加载销售订单缓存: {cache_file_path}")
        except Exception as e:
            logger.error(f"加载销售订单缓存失败: {str(e)}, 文件: {cache_file_path}")
            raise

    @classmethod
    def get_order_type_id(cls, order_type: str) -> int:
        """获取订单类型ID
        
        Args:
            order_type: 订单类型代码
            
        Returns:
            int: 订单类型ID
        """
        order_type_ids = cls._cache_data.get("ORDER_TYPE_IDS", {})
        order_type_id = order_type_ids.get(order_type)
        if not order_type_id:
            raise ValueError(f"未找到订单类型: {order_type}")
        return order_type_id

    @classmethod
    def get_order_line_type_id(cls, order_line_type: str) -> int:
        """获取订单行类型ID
        
        Args:
            order_line_type: 订单行类型代码
            
        Returns:
            int: 订单行类型ID
        """
        order_line_type_ids = cls._cache_data.get("ORDER_LINE_TYPE_IDS", {})
        order_line_type_id = order_line_type_ids.get(order_line_type)
        if not order_line_type_id:
            raise ValueError(f"未找到订单行类型: {order_line_type}")
        return order_line_type_id

    @classmethod
    def get_order_type_name(cls, order_type: str) -> str:
        """获取订单类型名称
        
        Args:
            order_type: 订单类型代码
            
        Returns:
            str: 订单类型名称
        """
        order_types = cls._cache_data.get("ORDER_TYPES", {})
        order_type_name = order_types.get(order_type)
        if not order_type_name:
            raise ValueError(f"未找到订单类型: {order_type}")
        return order_type_name

    @classmethod
    def get_order_line_type_name(cls, order_line_type: str) -> str:
        """获取订单行类型名称
        
        Args:
            order_line_type: 订单行类型代码
            
        Returns:
            str: 订单行类型名称
        """
        order_line_types = cls._cache_data.get("ORDER_LINE_TYPES", {})
        order_line_type_name = order_line_types.get(order_line_type)
        if not order_line_type_name:
            raise ValueError(f"未找到订单行类型: {order_line_type}")
        return order_line_type_name

    @classmethod
    def get_valid_line_types(cls, order_type: str) -> list:
        """获取订单类型允许的行类型列表
        
        Args:
            order_type: 订单类型代码
            
        Returns:
            list: 允许的行类型代码列表
        """
        order_type_line_combinations = cls._cache_data.get("ORDER_TYPE_LINE_COMBINATIONS", {})
        valid_line_types = order_type_line_combinations.get(order_type)
        if not valid_line_types:
            raise ValueError(f"未找到订单类型: {order_type}")
        return valid_line_types

if __name__ == "__main__":
    cache_util = CacheUtil()
    cache_util.init()
    cache_util.set("test", {"test": "test"})
    print(cache_util.get("test"))