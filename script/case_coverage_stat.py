import argparse
import re
import json
from pathlib import Path
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description="统计ERP自动化用例接口覆盖率")
    parser.add_argument('--api_path_yaml', required=True, help='接口路径yaml文件，如 md_api_path.yaml')
    parser.add_argument('--case_dir', required=True, help='用例目录，如 testcases')
    parser.add_argument('--output_json', required=True, help='输出json文件路径，如 case_coverage_stat.json')
    return parser.parse_args()

def load_yaml(path):
    path = Path(path).expanduser().resolve()
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_covered_details(case_dir, apis):
    all_paths = {v['path']: k for k, v in apis.items()}
    covered_detail = []
    covered_paths_set = set()
    for py_file in Path(case_dir).rglob('test_*.py'):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 找到所有 test_ 开头的方法
            for match in re.finditer(r'def (test_\w+)\s*\((.*?)\):', content):
                method_name = match.group(1)
                method_start = match.end()
                # 获取方法体（到下一个def或文件结尾）
                next_def = re.search(r'\ndef \w', content[method_start:])
                method_end = method_start + (next_def.start() if next_def else len(content) - method_start)
                method_body = content[method_start:method_end]
                # 查找 self.get_api_path("xxx")
                for api_key in re.findall(r'self\.get_api_path\([\'\"](.+?)[\'\"]\)', method_body):
                    if api_key in apis:
                        api_path = apis[api_key]['path']
                        api_name = all_paths[api_path]
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": api_path,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(api_path)
                # 查找 url = "xxx"
                for path in re.findall(r'url\s*=\s*[\'\"](.+?)[\'\"]', method_body):
                    if path in all_paths:
                        api_name = all_paths[path]
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": path,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(path)
                # 查找 self.fin_path["xxx"]["path"]
                for fin_key in re.findall(r'self\.fin_path\[\"(.+?)\"\]\[\"path\"\]', method_body):
                    if fin_key in apis:
                        api_path = apis[fin_key]['path']
                        api_name = fin_key
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": api_path,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(api_path)
    return covered_detail, covered_paths_set

def main():
    args = parse_args()
    api_path_yaml = load_yaml(args.api_path_yaml)
    apis = api_path_yaml.get('apis', {})
    case_dir = Path(args.case_dir).expanduser().resolve()
    output_json = Path(args.output_json).expanduser().resolve()
    all_paths = {v['path']: k for k, v in apis.items()}
    covered_detail, covered_paths = extract_covered_details(case_dir, apis)
    total = len(all_paths)
    covered = len(covered_paths)
    coverage = round(covered / total * 100, 2) if total else 0.0
    uncovered = [
        {"api_name": all_paths[path], "api_path": path}
        for path in all_paths if path not in covered_paths
    ]
    stat = {
        "total": total,
        "covered": covered,
        "coverage": f"{coverage}%",
        "covered_detail": covered_detail,
        "uncovered": uncovered
    }
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(stat, f, ensure_ascii=False, indent=2)
    print(f"统计完成，结果已保存到: {output_json}")
    print(f"接口总数: {total}，已覆盖: {covered}，覆盖率: {coverage}%")
    print(f"覆盖详情条目: {len(covered_detail)}，未覆盖接口: {len(uncovered)}，详情见json文件")
    print(f"验证: 已覆盖({covered}) + 未覆盖({len(uncovered)}) = 总数({total}) ✓")
    if not uncovered:
        print("所有接口均已覆盖！")

if __name__ == '__main__':
    main() 