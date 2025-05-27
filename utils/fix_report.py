#!/usr/bin/env python3
import json
import re
from pathlib import Path


def fix_report_title(report_dir: str, title: str = "ERP-AUTOTEST"):
    """修改 Allure 报告标题"""
    report_path = Path(report_dir)
    
    # 修改 summary.json
    with open(report_path / 'widgets' / 'summary.json', 'r+', encoding='utf-8') as f:
        data = json.load(f)
        data['reportName'] = title
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()
    
    # 修改 index.html
    with open(report_path / 'index.html', 'r+', encoding='utf-8') as f:
        content = f.read()
        content = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', content)
        f.seek(0)
        f.write(content)
        f.truncate()


if __name__ == '__main__':
    import os
    import sys
    
    # 支持命令行参数
    report_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'reports/allure-report')
    title = sys.argv[2] if len(sys.argv) > 2 else "ERP-AUTOTEST"
    
    fix_report_title(report_dir, title)
