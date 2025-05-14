"""缓存工具模块

提供缓存数据的读写功能，支持过期机制。
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from utils.response_util import DecimalEncoder

class CacheUtil:
    """缓存工具类
    
    使用示例:
        # 基础用法
        cache_util = CacheUtil(cache_dir="cache")
        cache_util.set("user_info", {"id": 1, "name": "test"})
        user_info = cache_util.get("user_info")
        
        # 自定义过期时间
        cache_util = CacheUtil(cache_dir="cache", expire_minutes=60)
        cache_util.set("config", {"key": "value"})
        
        # 检查缓存是否存在
        if cache_util.exists("user_info"):
            data = cache_util.get("user_info")
    """
    
    def __init__(self, cache_dir: str = "cache", expire_minutes: int = 30):
        """初始化缓存工具类
        
        Args:
            cache_dir: 缓存目录路径，默认为"cache"
            expire_minutes: 缓存过期时间(分钟)，默认30分钟
        """
        self.cache_dir = Path(cache_dir)
        self.expire_minutes = expire_minutes
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self) -> None:
        """确保缓存目录存在"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存数据
        
        Args:
            key: 缓存键名
            
        Returns:
            Optional[Dict[str, Any]]: 缓存数据，如果不存在或已过期则返回None
            
        使用示例:
            data = cache_util.get("user_info")
            if data:
                user_id = data.get("id")
        """
        cache_file = self.cache_dir / f"{key}.json"
        try:
            if not cache_file.exists():
                return None
            
            if self._is_expired(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取缓存失败: {str(e)}")
            return None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """设置缓存数据
        
        Args:
            key: 缓存键名
            data: 要缓存的数据
            
        使用示例:
            cache_util.set("user_info", {"id": 1, "name": "test"})
        """
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)
        except Exception as e:
            logger.error(f"写入缓存失败: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在且未过期
        
        Args:
            key: 缓存键名
            
        Returns:
            bool: 缓存是否存在且未过期
            
        使用示例:
            if cache_util.exists("user_info"):
                data = cache_util.get("user_info")
        """
        cache_file = self.cache_dir / f"{key}.json"
        return cache_file.exists() and not self._is_expired(cache_file)
    
    def _is_expired(self, cache_file: Path) -> bool:
        """检查缓存是否过期
        
        Args:
            cache_file: 缓存文件路径
            
        Returns:
            bool: 是否过期
        """
        file_time = cache_file.stat().st_mtime
        current_time = time.time()
        return (current_time - file_time) > (self.expire_minutes * 60) 