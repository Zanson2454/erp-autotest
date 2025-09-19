#!/usr/bin/env python3
"""
使用新的create_delivery_order方法的示例
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from testcases.scm_sls import SlsBase

def example_usage():
    """展示如何使用新的create_delivery_order方法"""
    
    # 初始化测试类
    sls_test = SlsBase()
    sls_test.setup_class()
    
    try:
        # 1. 创建已生效的销售订单
        print("1. 创建已生效的销售订单...")
        order_id = sls_test.create_sales_order(order_type="STND", submit=True)
        print(f"   销售订单创建成功，订单ID: {order_id}")
        
        # 2. 基于销售订单创建交货单
        print("2. 基于销售订单创建交货单...")
        delivery_id = sls_test.create_delivery_order(order_id)
        print(f"   交货单创建成功，交货单ID: {delivery_id}")
        
        print("✅ 完整流程执行成功！")
        
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        raise

if __name__ == "__main__":
    example_usage()
