"""缓存工具模块

提供缓存数据的读写功能，支持过期机制。
支持方案2：重新拉取并覆盖过期缓存。
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Union
from loguru import logger

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.response_util import DecimalEncoder

class CacheUtil:
    """缓存工具类（全类属性+类方法风格）
    
    使用示例:
        CacheUtil.init(cache_dir="cache", expire_minutes=1440)  # 24小时
        CacheUtil.set("user_info", {"id": 1, "name": "test"})
        user_info = CacheUtil.get("user_info")
        
        缓存刷新策略（方案2）:
        def refresh_callback(cache_key: str) -> Dict[str, Any]:
            # 重新执行SQL或API调用获取数据
            return new_data
        CacheUtil.refresh_expired_cache(refresh_callbacks={"init_cache": refresh_callback})
    """
    _cache_dir = Path("cache")
    _expire_minutes = 5  # 默认5分钟（测试环境），生产环境建议1440（24小时）
    _initialized = False
    _cache_data = {}  # 存储加载的缓存数据

    @classmethod
    def init(cls, cache_dir: str = "cache", expire_minutes: int = 5):
        """
        初始化缓存工具
        
        :param cache_dir: 缓存目录
        :param expire_minutes: 过期时间（分钟），默认10分钟（测试环境），生产环境建议1440（24小时）
        """
        # 首次初始化：设置目录和过期时间
        if not cls._initialized:
            cls._cache_dir = Path(cache_dir)
            cls._expire_minutes = expire_minutes
            cls._cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"缓存目录: {cls._cache_dir.absolute()}")
            logger.info(f"缓存过期时间: {cls._expire_minutes}分钟 ({cls._expire_minutes/60:.1f}小时)")
            logger.info(f"缓存目录创建状态: 存在={cls._cache_dir.exists()}")
            cls._initialized = True
        else:
            # 已初始化：允许更新过期时间和目录（如果目录不同）
            new_cache_dir = Path(cache_dir)
            if new_cache_dir != cls._cache_dir:
                cls._cache_dir = new_cache_dir
                cls._cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"更新缓存目录: {cls._cache_dir.absolute()}")
            if expire_minutes != cls._expire_minutes:
                logger.info(f"更新缓存过期时间: {cls._expire_minutes}分钟 -> {expire_minutes}分钟")
                cls._expire_minutes = expire_minutes

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
        """
        检查缓存文件是否过期
        
        判断逻辑：使用文件修改时间（st_mtime）
        - 缓存存在时间 = 当前时间 - 文件修改时间
        - 如果存在时间 > 过期时间，则过期
        """
        file_time = cache_file.stat().st_mtime
        current_time = time.time()
        return (current_time - file_time) > (cls._expire_minutes * 60)
    
    @classmethod
    def get_cache_age(cls, key: str) -> Optional[float]:
        """
        获取缓存文件的存在时间（分钟）
        
        :param key: 缓存key
        :return: 存在时间（分钟），如果文件不存在返回None
        """
        cache_file = cls._cache_dir / f"{key}.json"
        if not cache_file.exists():
            return None
        
        file_time = cache_file.stat().st_mtime
        current_time = time.time()
        age_seconds = current_time - file_time
        age_minutes = age_seconds / 60.0
        
        return age_minutes
    
    @classmethod
    def get_expired_cache_keys(cls) -> List[str]:
        """
        获取所有过期的缓存key列表
        
        :return: 过期的缓存key列表
        """
        if not cls._cache_dir.exists():
            return []
        
        expired_keys = []
        for cache_file in cls._cache_dir.glob("*.json"):
            if cls._is_expired(cache_file):
                expired_keys.append(cache_file.stem)
        
        return expired_keys
    
    @classmethod
    def refresh_expired_cache(cls, refresh_callbacks: Dict[str, Callable[[str], Dict[str, Any]]]) -> Dict[str, bool]:
        """
        方案2：重新拉取并覆盖过期的缓存
        
        :param refresh_callbacks: 刷新回调函数字典，key为缓存key，value为刷新函数
                                 刷新函数接收cache_key参数，返回新的数据字典
        :return: 刷新结果字典，key为缓存key，value为是否成功刷新
        """
        if not cls._cache_dir.exists():
            logger.info("缓存目录不存在，无需刷新")
            return {}
        
        refresh_results = {}
        for cache_file in cls._cache_dir.glob("*.json"):
            cache_key = cache_file.stem  # 去掉.json后缀
            
            # 只处理过期的缓存
            if not cls._is_expired(cache_file):
                continue
            
            # 检查是否有对应的刷新回调函数
            if cache_key not in refresh_callbacks:
                logger.warning(f"缓存 {cache_key} 已过期，但未提供刷新回调函数，跳过")
                continue
            
            refresh_func = refresh_callbacks[cache_key]
            try:
                logger.info(f"开始刷新过期缓存: {cache_key}")
                new_data = refresh_func(cache_key)
                
                if new_data is None:
                    logger.warning(f"刷新回调函数返回None，跳过缓存 {cache_key}")
                    refresh_results[cache_key] = False
                    continue
                
                # 写入新数据覆盖旧缓存
                cls.set(cache_key, new_data)
                refresh_results[cache_key] = True
                logger.info(f"成功刷新缓存: {cache_key}")
                
            except Exception as e:
                logger.error(f"刷新缓存失败: {cache_key}, 错误: {str(e)}")
                refresh_results[cache_key] = False
        
        success_count = sum(1 for v in refresh_results.values() if v)
        logger.info(f"缓存刷新完成: 成功 {success_count}/{len(refresh_results)}")
        
        return refresh_results

    @classmethod
    def purge_disk_cache_files(cls, cache_dir: Optional[Union[str, Path]] = None) -> int:
        """
        删除缓存目录下的 *.json 及 .*.source_hash（SQL 源 hash 旁路文件），用于 --fresh-cache。
        不重置类状态；下次 get 会 miss 并触发重新拉数。

        :param cache_dir: 默认使用当前已初始化的 _cache_dir；可显式指定 testdata/cache
        :return: 删除的文件数量
        """
        root = Path(cache_dir) if cache_dir is not None else cls._cache_dir
        if not root.exists():
            return 0
        n = 0
        for p in root.iterdir():
            if not p.is_file():
                continue
            if p.suffix == ".json":
                try:
                    p.unlink()
                    n += 1
                except OSError as e:
                    logger.warning(f"删除缓存文件失败: {p}, {e}")
            elif p.name.startswith(".") and "source_hash" in p.name:
                try:
                    p.unlink()
                    n += 1
                except OSError as e:
                    logger.warning(f"删除 hash 文件失败: {p}, {e}")
        logger.info(f"已清理磁盘缓存文件 {n} 个，目录: {root.resolve()}")
        return n

   

if __name__ == "__main__":
    cache_util = CacheUtil()
    cache_util.init()
    print(cache_util.get("test"))