import re
import json
from pathlib import Path
import yaml
from collections import defaultdict

def load_yaml(path):
    path = Path(path).expanduser().resolve()
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_module_from_api_name(api_name):
    """
    从API名称中提取模块名称
    例如: "ORG-组织架构-保存服务" -> "ORG"
    "(系统)xxx" -> "SYS"
    """
    if api_name.startswith("(系统)"):
        return "SYS"  # 系统级服务统一为 SYS 模块
    if '-' in api_name:
        return api_name.split('-')[0]  # 如 "GEN-地址库-xxx" -> "GEN"
    elif '_' in api_name:
        # 处理 "GEN_MD$XXX" 格式，保留完整模块
        parts = api_name.split('_')
        if len(parts) >= 2 and parts[0] == "GEN":
            return "GEN_MD"  # 统一 GEN_MD 格式
        return f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else parts[0]
    else:
        # 其他情况，取前3个字符作为模块
        return api_name[:3] if len(api_name) >= 3 else api_name

def filter_system_apis(apis):
    """
    过滤掉以 "(系统)" 开头的系统级 API
    返回过滤后的 apis 字典
    """
    filtered = {}
    for api_name, config in apis.items():
        if not api_name.startswith("(系统)"):
            filtered[api_name] = config
    return filtered

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
                        module_name = extract_module_from_api_name(api_name)
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": api_path,
                            "module": module_name,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(api_path)
                
                # 查找 standard_api_call(api_key="xxx") 或 standard_api_call(api_key='xxx')
                # 支持单引号和双引号，支持多行调用（带换行）
                # 匹配模式：standard_api_call(... api_key="xxx" ...) 或 self.standard_api_call(... api_key='xxx' ...)
                # 使用 DOTALL 模式匹配多行，但限制匹配长度避免过度匹配
                standard_api_call_pattern = r'(?:self\.)?standard_api_call\s*\(.*?api_key\s*=\s*([\'"])([^\'"]+?)\1[^)]*?\)'
                for api_key_match in re.finditer(standard_api_call_pattern, method_body, re.DOTALL):
                    # 跳过过长的匹配（可能是正则表达式错误匹配）
                    if len(api_key_match.group(0)) > 1000:
                        continue
                    api_key = api_key_match.group(2).strip()
                    if api_key in apis:
                        api_path = apis[api_key]['path']
                        api_name = all_paths[api_path]
                        module_name = extract_module_from_api_name(api_name)
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": api_path,
                            "module": module_name,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(api_path)
                        
                # 查找 url = "xxx"
                for path in re.findall(r'url\s*=\s*[\'\"](.+?)[\'\"]', method_body):
                    if path in all_paths:
                        api_name = all_paths[path]
                        module_name = extract_module_from_api_name(api_name)
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": path,
                            "module": module_name,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(path)
                        
                # 查找 self.fin_path["xxx"]["path"]
                for fin_key in re.findall(r'self\.fin_path\[\"(.+?)\"\]\[\"path\"\]', method_body):
                    if fin_key in apis:
                        api_path = apis[fin_key]['path']
                        api_name = fin_key
                        module_name = extract_module_from_api_name(api_name)
                        covered_detail.append({
                            "api_name": api_name,
                            "api_path": api_path,
                            "module": module_name,
                            "testcase_file": str(py_file),
                            "testcase_method": method_name
                        })
                        covered_paths_set.add(api_path)
                        
    return covered_detail, covered_paths_set

def generate_module_statistics(apis, covered_detail, covered_paths):
    """
    生成模块维度的统计信息
    """
    all_paths = {v['path']: k for k, v in apis.items()}
    
    # 按模块分组所有API
    module_apis = defaultdict(list)
    for path, api_name in all_paths.items():
        module_name = extract_module_from_api_name(api_name)
        module_apis[module_name].append({
            "api_name": api_name,
            "api_path": path
        })
    
    # 按模块分组已覆盖的API
    module_covered = defaultdict(set)
    for detail in covered_detail:
        module_covered[detail["module"]].add(detail["api_path"])
    
    # 计算每个模块的覆盖率
    module_stats = {}
    for module_name, module_api_list in module_apis.items():
        total_apis = len(module_api_list)
        covered_apis = len(module_covered[module_name])
        coverage = round(covered_apis / total_apis * 100, 2) if total_apis else 0.0
        
        # 找出未覆盖的API
        covered_paths_in_module = module_covered[module_name]
        uncovered_apis = [
            api for api in module_api_list 
            if api["api_path"] not in covered_paths_in_module
        ]
        
        # 找出已覆盖的API详情
        covered_apis_detail = [
            detail for detail in covered_detail 
            if detail["module"] == module_name
        ]
        
        module_stats[module_name] = {
            "module_name": module_name,
            "total_apis": total_apis,
            "covered_apis": covered_apis,
            "coverage": f"{coverage}%",
            "coverage_rate": coverage,
            "covered_detail": covered_apis_detail,
            "uncovered_apis": uncovered_apis
        }
    
    # 按覆盖率降序排列
    sorted_modules = sorted(
        module_stats.values(), 
        key=lambda x: x["coverage_rate"], 
        reverse=True
    )
    
    return sorted_modules

def print_module_report(stats, module_stat):
    """
    打印模块统计报告
    """
    if not module_stat or 'module_statistics' not in stats:
        return
    
    print("\n" + "="*80)
    print("模块覆盖率统计报告")
    print("="*80)
    print(f"{'模块名称':<20} {'总接口数':<10} {'已覆盖':<10} {'覆盖率':<10} {'未覆盖':<10}")
    print("-" * 80)
    
    for module_stat in stats['module_statistics']:
        module_name = module_stat["module_name"]
        total_apis = module_stat["total_apis"]
        covered_apis = module_stat["covered_apis"]
        coverage_rate = module_stat["coverage"]
        uncovered_count = len(module_stat["uncovered_apis"])
        
        print(f"{module_name:<20} {total_apis:<10} {covered_apis:<10} {coverage_rate:<10} {uncovered_count:<10}")
    
    print("-" * 80)
    print(f"{'总计':<20} {stats['total']:<10} {stats['covered']:<10} {stats['coverage']:<10} {len(stats['uncovered']):<10}")
    print("="*80)

def generate_coverage_stats(api_path_yaml, case_dir, output_json, module_stat=False):
    """
    生成接口覆盖率统计
    
    Args:
        api_path_yaml (str): API路径YAML文件路径
        case_dir (str): 用例目录路径
        output_json (str): 输出JSON文件路径
        module_stat (bool): 是否生成模块统计报告
    
    Returns:
        dict: 统计结果字典
    """
    api_path_yaml = load_yaml(api_path_yaml)
    apis = api_path_yaml.get('apis', {})
    
    # 过滤掉 "(系统)" 前缀的系统级 API
    apis = filter_system_apis(apis)
    
    case_dir = Path(case_dir).expanduser().resolve()
    output_json = Path(output_json).expanduser().resolve()
    
    all_paths = {v['path']: k for k, v in apis.items()}
    covered_detail, covered_paths = extract_covered_details(case_dir, apis)
    
    total = len(all_paths)
    covered = len(covered_paths)
    coverage = round(covered / total * 100, 2) if total else 0.0
    
    uncovered = [
        {
            "api_name": all_paths[path], 
            "api_path": path,
            "module": extract_module_from_api_name(all_paths[path])
        }
        for path in all_paths if path not in covered_paths
    ]
    
    stat = {
        "total": total,
        "covered": covered,
        "coverage": f"{coverage}%",
        "coverage_rate": coverage,
        "covered_detail": covered_detail,
        "uncovered": uncovered
    }
    
    # 如果需要模块统计
    if module_stat:
        module_stats = generate_module_statistics(apis, covered_detail, covered_paths)
        stat["module_statistics"] = module_stats
    
    # 保存结果
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(stat, f, ensure_ascii=False, indent=2)
    
    # 打印基本统计
    print(f"\n统计完成，结果已保存到: {output_json}")
    print(f"接口总数: {total}，已覆盖: {covered}，覆盖率: {coverage}%")
    print(f"覆盖详情条目: {len(covered_detail)}，未覆盖接口: {len(uncovered)}，详情见json文件")
    print(f"验证: 已覆盖({covered}) + 未覆盖({len(uncovered)}) = 总数({total}) ✓")
    
    if not uncovered:
        print("所有接口均已覆盖！")
    
    if module_stat:
        print(f"\n模块统计: 共 {len(stat['module_statistics'])} 个模块，详细统计见下方报告")
        print_module_report(stat, module_stat)
    
    return stat

if __name__ == '__main__':
    # 示例用法：统计 GEN_MD 模块覆盖率
    # 注意：请根据实际项目结构调整 api_path_yaml 路径
    # 常见路径可能是 testdata/gen_md/md_api_path.yaml 或 config/erp/md_api_path.yaml
    api_yaml_path = 'config/api/gen_md/md_api_path.yaml'  # 请确认实际路径
    case_directory = 'testcases/gen_md'
    output_file = 'reports/gen_md_coverage.json'
    
    # 生成统计（包括模块统计）
    stats = generate_coverage_stats(
        api_path_yaml=api_yaml_path,
        case_dir=case_directory,
        output_json=output_file,
        module_stat=True
    )
    
    # 可以进一步处理 stats，例如只查看 GEN 模块
    if 'module_statistics' in stats:
        gen_module = next((m for m in stats['module_statistics'] if m['module_name'] == 'GEN_MD'), None)
        if gen_module:
            print(f"\nGEN_MD 模块覆盖率: {gen_module['coverage']} (已覆盖 {gen_module['covered_apis']}/{gen_module['total_apis']})")
