#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
根据对比文件过滤主文件，只保留对比文件中存在的单号
"""
import sys
from pathlib import Path

# 避免导入本地csv.py
script_dir = Path(__file__).parent
if str(script_dir) in sys.path:
    sys.path.remove(str(script_dir))

import csv

# 文件路径
script_dir = Path(__file__).parent
main_file = script_dir / "cscscsc.csv"
compare_file = script_dir / "cscscsc copy.csv"
output_file = script_dir / "cscscsc_filtered.csv"

def read_compare_file():
    """读取对比文件，返回单号集合"""
    order_nos = set()
    
    with open(compare_file, 'r', encoding='utf-8') as f:
        for line in f:
            order_no = line.strip()
            if order_no:
                order_nos.add(order_no)
    
    return order_nos

def filter_main_file():
    """根据对比文件过滤主文件"""
    # 读取对比文件的单号
    compare_order_nos = read_compare_file()
    print(f"对比文件单号数: {len(compare_order_nos)}")
    
    # 读取并过滤主文件
    filtered_rows = []
    total_rows = 0
    
    with open(main_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            total_rows += 1
            order_no = row.get('单号', '').strip()
            if order_no and order_no in compare_order_nos:
                filtered_rows.append(row)
    
    print(f"主文件总行数: {total_rows}")
    print(f"过滤后行数: {len(filtered_rows)}")
    print(f"删除了: {total_rows - len(filtered_rows)} 行")
    
    # 保存过滤后的文件
    if filtered_rows:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['采购日期', '单号', '采购数量', '已交数量']
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            writer.writerows(filtered_rows)
        print(f"\n过滤后的文件已保存到: {output_file}")
    
    # 统计去重后的单号数
    unique_orders = set()
    for row in filtered_rows:
        order_no = row.get('单号', '').strip()
        if order_no:
            unique_orders.add(order_no)
    print(f"过滤后去重单号数: {len(unique_orders)}")

if __name__ == "__main__":
    filter_main_file()






















