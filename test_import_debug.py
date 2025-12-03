#!/usr/bin/env python3.11
"""
临时导入调试文件 - 验证 GenMdBaseTest 导入和类定义
"""

import sys
from pathlib import Path

# 确保在项目根目录执行
project_root = Path(__file__).resolve().parent
print(f"当前工作目录: {project_root}")
print(f"Python 路径: {sys.path}")

try:
    # 手动添加项目根目录到 Python 路径
    sys.path.insert(0, str(project_root))
    print("已添加项目根目录到 Python 路径")
    
    # 导入测试
    from testcases.gen_md import GenMdBaseTest
    print("✅ GenMdBaseTest 导入成功!")
    
    # 验证类定义
    print(f"GenMdBaseTest 类型: {type(GenMdBaseTest)}")
    print(f"GenMdBaseTest 基类: {GenMdBaseTest.__bases__}")
    
    # 测试 setup_class
    print("测试 setup_class 方法...")
    test_instance = GenMdBaseTest()
    test_instance.setup_class()
    print("✅ setup_class 执行成功!")
    
    # 验证关键方法
    print("验证 standard_api_call 方法...")
    if hasattr(test_instance, 'standard_api_call'):
        print("✅ standard_api_call 方法存在")
    else:
        print("❌ standard_api_call 方法缺失!")
    
    # 验证 mock_util
    if hasattr(test_instance, 'mock_util'):
        print("✅ mock_util 属性存在")
        print(f"mock_util 类型: {type(test_instance.mock_util)}")
    else:
        print("❌ mock_util 属性缺失!")
    
    print("\n🎉 所有导入和类定义验证通过!")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    print("\n调试完成。请运行: python3.11 test_import_debug.py")
