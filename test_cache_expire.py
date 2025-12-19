#!/usr/bin/env python3
"""
测试缓存过期逻辑
用于验证缓存文件过期后是否会重新拉取数据
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.cache_util import CacheUtil
from data_factory.base import DataFactory
from utils.log_util import Loggers

def test_cache_expire_logic():
    """测试缓存过期逻辑"""
    print("=" * 60)
    print("缓存过期逻辑测试（过期时间：5分钟）")
    print("=" * 60)
    
    # 1. 初始化缓存工具（5分钟过期）
    cache_dir = str(project_root / 'testdata' / 'cache')
    expire_minutes = 5
    CacheUtil.init(cache_dir, expire_minutes=expire_minutes)
    
    cache_key = "init_cache"
    cache_file = Path(cache_dir) / f"{cache_key}.json"
    
    # 2. 检查缓存文件状态
    print(f"\n【步骤1】检查缓存文件状态")
    print(f"缓存文件路径: {cache_file.absolute()}")
    
    if cache_file.exists():
        file_time = cache_file.stat().st_mtime
        current_time = time.time()
        age_seconds = current_time - file_time
        age_minutes = age_seconds / 60.0
        
        print(f"文件修改时间: {time.ctime(file_time)}")
        print(f"当前时间: {time.ctime(current_time)}")
        print(f"缓存存在时间: {age_minutes:.2f} 分钟")
        print(f"过期时间设置: {expire_minutes} 分钟")
        
        is_expired = age_minutes > expire_minutes
        print(f"是否过期: {'是 ✅' if is_expired else '否 ❌'}")
        
        # 使用 CacheUtil 检查是否过期
        cache_data = CacheUtil.get(cache_key)
        if cache_data:
            print(f"✅ CacheUtil.get() 返回数据: 缓存有效")
        else:
            print(f"❌ CacheUtil.get() 返回 None: 缓存已过期或不存在")
    else:
        print("缓存文件不存在")
    
    # 3. 测试重新拉取逻辑
    print(f"\n【步骤2】测试重新拉取逻辑")
    print("调用 DataFactory.get_base_data()（会自动处理缓存过期）...")
    
    try:
        # 初始化 DataFactory
        data_factory = DataFactory(env_name="test")
        
        # 获取基础数据（会自动处理缓存过期）
        start_time = time.time()
        base_data = data_factory.get_base_data(project="erp", expire_minutes=expire_minutes)
        elapsed_time = time.time() - start_time
        
        if base_data:
            print(f"✅ 成功获取基础数据，耗时: {elapsed_time:.2f}秒")
            keys = list(base_data.keys())
            print(f"数据包含的key数量: {len(keys)}")
            if keys:
                print(f"前5个key: {keys[:5]}")
            
            # 检查缓存文件是否更新
            if cache_file.exists():
                new_file_time = cache_file.stat().st_mtime
                print(f"\n缓存文件更新时间: {time.ctime(new_file_time)}")
                
                # 判断是否重新拉取了数据
                if 'file_time' in locals() and new_file_time > file_time:
                    print("✅ 缓存文件已更新，说明重新拉取了数据")
                elif 'file_time' in locals() and new_file_time == file_time:
                    print("ℹ️  缓存文件未更新，说明使用了缓存数据")
                else:
                    print("ℹ️  缓存文件是新创建的")
        else:
            print("❌ 获取基础数据失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 4. 验证缓存年龄
    print(f"\n【步骤3】验证缓存年龄")
    if cache_file.exists():
        final_file_time = cache_file.stat().st_mtime
        final_current_time = time.time()
        final_age_minutes = (final_current_time - final_file_time) / 60.0
        
        print(f"缓存文件修改时间: {time.ctime(final_file_time)}")
        print(f"当前时间: {time.ctime(final_current_time)}")
        print(f"缓存年龄: {final_age_minutes:.2f} 分钟")
        print(f"过期时间: {expire_minutes} 分钟")
        remaining_time = max(0, expire_minutes - final_age_minutes)
        print(f"剩余有效时间: {remaining_time:.2f} 分钟")
        if remaining_time > 0:
            print(f"✅ 缓存仍然有效")
        else:
            print(f"❌ 缓存已过期")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print("\n💡 提示：")
    print("  - 如果缓存已过期，下次调用时会自动重新拉取数据")
    print("  - 如果缓存未过期，会直接使用缓存数据（更快）")
    print("  - 可以通过修改文件时间或等待5分钟来测试过期逻辑")

if __name__ == "__main__":
    test_cache_expire_logic()

