#!/usr/bin/env python3
"""新项目/新环境初始化检查脚本。

用途：确保新接入的业务模块或新环境能快速把测试框架用起来。
检查项：
  1. 运行环境（Python 版本、依赖包、目录结构）
  2. 环境配置（config/env/.env 和 YAML 必填字段）
  3. 数据库连通性（ERP DB / IAM DB）
  4. 登录有效性（Cookie 或账密登录）
  5. SQL 初始化配置（执行后结果是否有值）
  6. API 配置（YAML 格式、模块完整性、swagger_parser 可用性）

用法：
  python script/test_init_check.py                  # 全量检查
  python script/test_init_check.py --env test       # 指定环境
  python script/test_init_check.py --section env    # 仅检查某一项
  python script/test_init_check.py --project my_prj # 多项目模式
"""

from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# ─────────────────────────────────────────────────────────────────────────────
# 路径常量
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_ENV_DIR = PROJECT_ROOT / "config" / "env"
CONFIG_API_DIR = PROJECT_ROOT / "config" / "api"
CONFIG_ERP_DIR = PROJECT_ROOT / "config" / "erp"
TESTDATA_CACHE_DIR = PROJECT_ROOT / "testdata" / "cache"

# 环境 YAML 中 portal 配置必须包含的字段
PORTAL_REQUIRED_FIELDS = ["iam_url", "username", "password"]

# 环境 YAML 中 database 配置必须包含的字段
DB_REQUIRED_FIELDS = ["host", "port", "user", "password", "database"]

# 必须的目录结构
REQUIRED_DIRS = [
    "config/api",
    "config/env",
    "config/erp",
    "testcases/comm",
    "testdata/cache",
    "utils",
    "script",
]

# 必须的文件
REQUIRED_FILES = [
    "config/env/test.yaml",
    "pytest.ini",
    "requirements.txt",
    "testcases/conftest.py",
    "testcases/comm/base_test.py",
    "testcases/comm/api_client_facade.py",
    "script/swagger_parser.py",
]

# 关键依赖包
CRITICAL_PACKAGES = [
    "pytest",
    "requests",
    "pymysql",
    "yaml",
    "loguru",
    "dotenv",
    "allure_pytest",
    "faker",
]

# SQL 初始化文件与对应缓存 key 的映射
SQL_INIT_FILES = {
    "base_init_sql.yaml": "base_info",
    "md_init_sql.yaml": "org_info",
    "sls_init_sql.yaml": "sls_config",
    "pur_init_sql.yaml": "pur_config",
    # fin_init_sql 顶层为 calender_info / sett_* 等分段，无 fin_config 包裹
    "fin_init_sql.yaml": "calender_info",
    "del_init_sql.yaml": "scm_del_config",
    "acc_init_sql.yaml": "acc_config",
}


# ─────────────────────────────────────────────────────────────────────────────
# 检查结果收集器
# ─────────────────────────────────────────────────────────────────────────────


class CheckResult:
    """单条检查结果的容器。"""

    def __init__(self, section: str, name: str, passed: bool, message: str = ""):
        self.section = section
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        icon = "PASS" if self.passed else "FAIL"
        msg = f" -- {self.message}" if self.message else ""
        return f"  [{icon}] [{self.section}] {self.name}:{msg}"


class CheckReport:
    """检查报告收集器。"""

    def __init__(self):
        self.results: List[CheckResult] = []

    def add(self, section: str, name: str, passed: bool, message: str = ""):
        self.results.append(CheckResult(section, name, passed, message))

    def summary(self) -> str:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        lines = ["", "=" * 60, "初始化检查报告", "=" * 60]
        for r in self.results:
            lines.append(str(r))
        lines.append("-" * 60)
        lines.append(f"总计: {total}  通过: {passed}  失败: {failed}")
        if failed:
            lines.append("\n存在失败项，请根据上述提示修复后重新运行。")
        else:
            lines.append("\n所有检查项通过，可以开始编写用例！")
        lines.append("=" * 60)
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 环境配置加载辅助
# ─────────────────────────────────────────────────────────────────────────────


def _replace_env_vars(obj: Any) -> None:
    """递归将配置中的 ${VAR} 替换为实际环境变量值。"""
    pattern = re.compile(r"^\$\{([^}]+)\}$")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                m = pattern.match(v)
                if m:
                    obj[k] = os.getenv(m.group(1), v)
            else:
                _replace_env_vars(v)
    elif isinstance(obj, list):
        for item in obj:
            _replace_env_vars(item)


def load_env_config(env: str, project: Optional[str] = None) -> Dict[str, Any]:
    """加载并解析环境 YAML 配置，自动替换 ${VAR} 占位符。"""
    if project:
        yaml_path = CONFIG_ENV_DIR / project / f"{env}.yaml"
        if not yaml_path.exists():
            yaml_path = CONFIG_ENV_DIR / f"{env}.yaml"
    else:
        yaml_path = CONFIG_ENV_DIR / f"{env}.yaml"

    if not yaml_path.exists():
        return {}

    with open(yaml_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    _replace_env_vars(config)
    return config


# ─────────────────────────────────────────────────────────────────────────────
# 检查项：运行环境
# ─────────────────────────────────────────────────────────────────────────────


def check_python_version(report: CheckReport) -> None:
    """检查 Python 版本是否 >= 3.10。"""
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 10)
    report.add(
        "运行环境",
        "Python 版本",
        ok,
        f"当前 {major}.{minor}，要求 >= 3.10",
    )


def check_critical_packages(report: CheckReport) -> None:
    """检查关键依赖包是否已安装。"""
    missing = []
    for pkg in CRITICAL_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    report.add(
        "运行环境",
        "关键依赖包",
        len(missing) == 0,
        f"缺失: {', '.join(missing)}" if missing else "全部已安装",
    )


def check_directory_structure(report: CheckReport) -> None:
    """检查必须的目录是否存在。"""
    missing = [d for d in REQUIRED_DIRS if not (PROJECT_ROOT / d).is_dir()]
    report.add(
        "运行环境",
        "目录结构",
        len(missing) == 0,
        f"缺失目录: {', '.join(missing)}" if missing else "完整",
    )


def check_required_files(report: CheckReport) -> None:
    """检查必须的文件是否存在。"""
    missing = [f for f in REQUIRED_FILES if not (PROJECT_ROOT / f).is_file()]
    report.add(
        "运行环境",
        "必须文件",
        len(missing) == 0,
        f"缺失文件: {', '.join(missing)}" if missing else "完整",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 检查项：环境配置
# ─────────────────────────────────────────────────────────────────────────────


def check_env_file(report: CheckReport) -> None:
    """检查 config/env/.env 文件是否存在且包含必要变量。"""
    env_file = CONFIG_ENV_DIR / ".env"
    if not env_file.exists():
        # 检查是否有 .env_template
        template = CONFIG_ENV_DIR / ".env_template"
        report.add(
            "环境配置",
            ".env 文件",
            False,
            f"不存在，请复制 {template} 并填写",
        )
        return

    content = env_file.read_text(encoding="utf-8")
    # 检查关键变量是否为空
    empty_vars = []
    for key in [
        "TEST_TERP_PORTAL_USERNAME",
        "TEST_TERP_PORTAL_PASSWORD",
        "TEST_TERP_PORTAL_IAM_URL",
        "TEST_TERP_PORTAL_URL",
        "TEST_DB_HOST",
        "TEST_DB_USER",
        "TEST_DB_PASSWORD",
        "TEST_DB_NAME",
    ]:
        match = re.search(rf"^{key}\s*=\s*['\"]?([^'\"]*)['\"]?\s*$", content, re.MULTILINE)
        if match and not match.group(1).strip():
            empty_vars.append(key)

    report.add(
        "环境配置",
        ".env 必填项",
        len(empty_vars) == 0,
        f"未填写: {', '.join(empty_vars)}" if empty_vars else "已填写",
    )


def check_env_yaml_structure(report: CheckReport, env: str, project: Optional[str]) -> None:
    """检查环境 YAML 配置的结构完整性。"""
    config = load_env_config(env, project)
    if not config:
        report.add("环境配置", "YAML 配置", False, f"config/env/{env}.yaml 不存在或为空")
        return

    errors = []

    # 检查 portal_config
    portal_config = config.get("portal_config", {})
    terp_config = portal_config.get("terp", {})
    if not terp_config:
        errors.append("缺少 portal_config.terp")
    else:
        for portal_name, portal_cfg in terp_config.items():
            if not isinstance(portal_cfg, dict):
                continue
            for field in PORTAL_REQUIRED_FIELDS:
                if not portal_cfg.get(field):
                    errors.append(f"portal_config.terp.{portal_name}.{field} 未配置")

    # 检查 database
    database = config.get("database", {})
    if not database:
        errors.append("缺少 database 配置")
    else:
        for db_name, db_cfg in database.items():
            if not isinstance(db_cfg, dict):
                continue
            for field in DB_REQUIRED_FIELDS:
                if not db_cfg.get(field):
                    errors.append(f"database.{db_name}.{field} 未配置")

    report.add(
        "环境配置",
        "YAML 结构",
        len(errors) == 0,
        "; ".join(errors) if errors else "完整",
    )


# ─────────────────────────────────────────────────────────────────────────────
# 检查项：数据库连通性
# ─────────────────────────────────────────────────────────────────────────────


def check_database_connectivity(report: CheckReport, env: str, project: Optional[str]) -> None:
    """检查数据库是否能正常连接。"""
    config = load_env_config(env, project)
    if not config:
        report.add("数据库", "配置加载", False, "无法加载环境配置")
        return

    database = config.get("database", {})
    if not database:
        report.add("数据库", "配置", False, "缺少 database 配置")
        return

    for db_name, db_cfg in database.items():
        if not isinstance(db_cfg, dict):
            continue
        try:
            import pymysql

            conn = pymysql.connect(
                host=db_cfg.get("host", ""),
                port=int(db_cfg.get("port", 3306)),
                user=db_cfg.get("user", ""),
                password=db_cfg.get("password", ""),
                database=db_cfg.get("database", ""),
                charset=db_cfg.get("charset", "utf8mb4"),
                connect_timeout=10,
            )
            conn.close()
            report.add("数据库", f"{db_name} 连通性", True, "连接成功")
        except Exception as e:
            report.add("数据库", f"{db_name} 连通性", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 检查项：登录有效性
# ─────────────────────────────────────────────────────────────────────────────


def check_login_effective(report: CheckReport, env: str, project: Optional[str]) -> None:
    """检查登录是否有效（Cookie 或账密登录）。"""
    config = load_env_config(env, project)
    if not config:
        report.add("登录", "配置加载", False, "无法加载环境配置")
        return

    portal_config = config.get("portal_config", {}).get("terp", {})
    if not portal_config:
        report.add("登录", "Portal 配置", False, "缺少 portal_config.terp")
        return

    # 检查是否有 Cookie 登录配置
    has_cookie = False
    for portal_name, portal_cfg in portal_config.items():
        if not isinstance(portal_cfg, dict):
            continue
        cookie = portal_cfg.get("cookie", "")
        if cookie:
            has_cookie = True
            # 尝试用 Cookie 验证
            try:
                import requests

                portal_url = portal_cfg.get("portal_url", "").rstrip("/")
                if not portal_url:
                    report.add("登录", f"{portal_name} Cookie", False, "缺少 portal_url")
                    continue

                session = requests.Session()
                # 设置 Cookie
                for cookie_pair in cookie.split(";"):
                    pair = cookie_pair.strip()
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        session.cookies.set(k.strip(), v.strip())

                # 尝试访问一个简单接口验证 Cookie
                resp = session.get(f"{portal_url}/api/trantor/page/default", timeout=15)
                if resp.status_code == 200:
                    report.add("登录", f"{portal_name} Cookie", True, "有效")
                else:
                    report.add("登录", f"{portal_name} Cookie", False, f"状态码: {resp.status_code}")
            except Exception as e:
                report.add("登录", f"{portal_name} Cookie", False, str(e))

    # 检查账密登录配置
    for portal_name, portal_cfg in portal_config.items():
        if not isinstance(portal_cfg, dict):
            continue
        username = portal_cfg.get("username", "")
        password = portal_cfg.get("password", "")
        iam_url = portal_cfg.get("iam_url", "").rstrip("/")

        if username and password and iam_url:
            try:
                import requests

                login_url = f"{iam_url}/iam/api/v1/user/login/account"
                resp = requests.post(
                    login_url,
                    json={"account": username, "password": password},
                    headers={"Content-Type": "application/json"},
                    timeout=15,
                )
                body = resp.json()
                if body.get("success") or resp.status_code == 200:
                    report.add("登录", f"{portal_name} 账密", True, "登录成功")
                else:
                    report.add("登录", f"{portal_name} 账密", False, f"登录失败: {body}")
            except Exception as e:
                report.add("登录", f"{portal_name} 账密", False, str(e))
        elif not has_cookie:
            report.add(
                "登录",
                f"{portal_name} 账密",
                False,
                "缺少 username/password/iam_url 且无 Cookie 配置",
            )


# ─────────────────────────────────────────────────────────────────────────────
# 检查项：SQL 初始化配置
# ─────────────────────────────────────────────────────────────────────────────


def check_sql_init_config(report: CheckReport, env: str, project: Optional[str]) -> None:
    """检查 SQL 初始化配置文件及执行结果。"""
    config = load_env_config(env, project)
    if not config:
        report.add("SQL 初始化", "配置加载", False, "无法加载环境配置")
        return

    database = config.get("database", {})
    erp_db_cfg = database.get("erp_db")
    if not erp_db_cfg:
        report.add("SQL 初始化", "ERP DB 配置", False, "缺少 database.erp_db")
        return

    try:
        import pymysql
    except ImportError:
        report.add("SQL 初始化", "PyMySQL", False, "未安装 pymysql")
        return

    # 连接数据库
    try:
        conn = pymysql.connect(
            host=erp_db_cfg.get("host", ""),
            port=int(erp_db_cfg.get("port", 3306)),
            user=erp_db_cfg.get("user", ""),
            password=erp_db_cfg.get("password", ""),
            database=erp_db_cfg.get("database", ""),
            charset=erp_db_cfg.get("charset", "utf8mb4"),
            connect_timeout=10,
        )
    except Exception as e:
        report.add("SQL 初始化", "数据库连接", False, str(e))
        return

    # 遍历 SQL 初始化文件
    for sql_file, root_key in SQL_INIT_FILES.items():
        sql_path = CONFIG_ERP_DIR / sql_file
        if not sql_path.exists():
            report.add("SQL 初始化", sql_file, False, "文件不存在")
            continue

        try:
            with open(sql_path, encoding="utf-8") as f:
                sql_config = yaml.safe_load(f) or {}
        except Exception as e:
            report.add("SQL 初始化", sql_file, False, f"YAML 解析失败: {e}")
            continue

        if root_key not in sql_config:
            report.add("SQL 初始化", sql_file, False, f"缺少根 key: {root_key}")
            continue

        # 执行每个 SQL 并检查结果
        errors = []
        empty_keys = []
        root_data = sql_config[root_key]
        if not isinstance(root_data, dict):
            report.add("SQL 初始化", sql_file, False, f"根 key '{root_key}' 不是字典结构")
            continue

        for key, item in root_data.items():
            if not isinstance(item, dict) or "sql" not in item:
                continue

            sql_text = item["sql"]
            # 替换 ${ENV_VAR:-default} 语法
            sql_text = re.sub(
                r"\$\{([^}:]+):-([^}]*)\}",
                lambda m: os.getenv(m.group(1), m.group(2)),
                sql_text,
            )

            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute(sql_text)
                    rows = cursor.fetchall()

                # 检查 validation 规则
                validation = item.get("validation", {})
                required = validation.get("required", False)
                min_records = validation.get("min_records", 0)
                required_fields = validation.get("required_fields", [])

                if len(rows) < min_records:
                    if required:
                        errors.append(f"{key}: 记录数 {len(rows)} < 最小要求 {min_records}")
                    else:
                        empty_keys.append(key)
                    continue

                # 检查必填字段是否有值
                if rows and required_fields:
                    for field in required_fields:
                        if not rows[0].get(field):
                            if required:
                                errors.append(f"{key}.{field}: 字段为空")
                            else:
                                empty_keys.append(f"{key}.{field}")

            except Exception as e:
                errors.append(f"{key}: SQL 执行失败 - {e}")

        if errors:
            report.add("SQL 初始化", sql_file, False, "; ".join(errors))
        elif empty_keys:
            report.add("SQL 初始化", sql_file, True, f"非必需项为空: {', '.join(empty_keys[:5])}")
        else:
            report.add("SQL 初始化", sql_file, True, "所有必需项有值")

    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# 检查项：API 配置
# ─────────────────────────────────────────────────────────────────────────────


def _module_prefix(module: str) -> str:
    """gen_md -> md, scm_pur -> pur, erp_fin -> fin."""
    return module.split("_")[-1].lower() if "_" in module else module.lower()


def check_api_config_structure(report: CheckReport) -> None:
    """检查 API 配置目录结构和 YAML 格式。"""
    if not CONFIG_API_DIR.exists():
        report.add("API 配置", "目录", False, "config/api 不存在")
        return

    modules = [d for d in CONFIG_API_DIR.iterdir() if d.is_dir()]
    if not modules:
        report.add("API 配置", "模块", False, "无 API 模块目录")
        return

    errors = []
    for mod_dir in modules:
        # 查找目录下所有的 *_api_path.yaml 和 *_api_params.yaml
        path_yamls = list(mod_dir.glob("*_api_path.yaml"))
        params_yamls = list(mod_dir.glob("*_api_params.yaml"))

        if not path_yamls:
            errors.append(f"{mod_dir.name}: 缺少 *_api_path.yaml")
        else:
            for path_yaml in path_yamls:
                try:
                    with open(path_yaml, encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    if "apis" not in data:
                        errors.append(f"{mod_dir.name}/{path_yaml.name}: 缺少 apis 节点")
                    elif not data["apis"]:
                        errors.append(f"{mod_dir.name}/{path_yaml.name}: apis 为空")
                except Exception as e:
                    errors.append(f"{mod_dir.name}/{path_yaml.name}: YAML 解析失败 - {e}")

        if not params_yamls:
            errors.append(f"{mod_dir.name}: 缺少 *_api_params.yaml")
        else:
            for params_yaml in params_yamls:
                try:
                    with open(params_yaml, encoding="utf-8") as f:
                        data = yaml.safe_load(f) or {}
                    if "api_params" not in data:
                        errors.append(f"{mod_dir.name}/{params_yaml.name}: 缺少 api_params 节点")
                except Exception as e:
                    errors.append(f"{mod_dir.name}/{params_yaml.name}: params YAML 解析失败 - {e}")

    report.add(
        "API 配置",
        "模块结构",
        len(errors) == 0,
        "; ".join(errors) if errors else f"{len(modules)} 个模块配置完整",
    )


def check_swagger_parser(report: CheckReport) -> None:
    """检查 swagger_parser.py 是否可用。"""
    parser_script = PROJECT_ROOT / "script" / "swagger_parser.py"
    if not parser_script.exists():
        report.add("API 配置", "swagger_parser", False, "脚本不存在")
        return

    # 检查依赖
    try:
        import requests  # noqa: F401
        import yaml  # noqa: F401
        from dotenv import load_dotenv  # noqa: F401
        from loguru import logger  # noqa: F401

        report.add("API 配置", "swagger_parser 依赖", True, "依赖已安装")
    except ImportError as e:
        report.add("API 配置", "swagger_parser 依赖", False, f"缺失: {e}")
        return

    # 尝试导入脚本检查语法
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("swagger_parser", parser_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report.add("API 配置", "swagger_parser 语法", True, "可正常导入")
    except Exception as e:
        report.add("API 配置", "swagger_parser 语法", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 主入口
# ─────────────────────────────────────────────────────────────────────────────

SECTIONS = {
    "env": "运行环境",
    "config": "环境配置",
    "db": "数据库",
    "login": "登录",
    "sql": "SQL 初始化",
    "api": "API 配置",
}


def run_all_checks(env: str, project: Optional[str], section: Optional[str]) -> int:
    """执行所有或指定检查项。"""
    report = CheckReport()

    if section is None or section == "env":
        print("\n[运行环境检查]")
        check_python_version(report)
        check_critical_packages(report)
        check_directory_structure(report)
        check_required_files(report)

    if section is None or section == "config":
        print("\n[环境配置检查]")
        check_env_file(report)
        check_env_yaml_structure(report, env, project)

    if section is None or section == "db":
        print("\n[数据库连通性检查]")
        check_database_connectivity(report, env, project)

    if section is None or section == "login":
        print("\n[登录有效性检查]")
        check_login_effective(report, env, project)

    if section is None or section == "sql":
        print("\n[SQL 初始化配置检查]")
        check_sql_init_config(report, env, project)

    if section is None or section == "api":
        print("\n[API 配置检查]")
        check_api_config_structure(report)
        check_swagger_parser(report)

    print(report.summary())

    failed = sum(1 for r in report.results if not r.passed)
    return 1 if failed else 0


def main() -> int:
    """解析命令行参数并执行检查。"""
    parser = argparse.ArgumentParser(
        description="新项目/新环境初始化检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 全量检查
  python script/test_init_check.py

  # 指定环境
  python script/test_init_check.py --env staging

  # 仅检查环境配置
  python script/test_init_check.py --section config

  # 多项目模式
  python script/test_init_check.py --project my_project --env test

可用检查项:
  env     运行环境（Python 版本、依赖包、目录结构）
  config  环境配置（.env 和 YAML 必填字段）
  db      数据库连通性
  login   登录有效性
  sql     SQL 初始化配置
  api     API 配置
        """,
    )
    parser.add_argument("--env", default="test", help="环境名称（默认: test）")
    parser.add_argument("--project", default=None, help="项目名称（多项目模式）")
    parser.add_argument(
        "--section",
        choices=list(SECTIONS.keys()),
        default=None,
        help="仅检查指定项",
    )
    args = parser.parse_args()

    return run_all_checks(args.env, args.project, args.section)


if __name__ == "__main__":
    sys.exit(main())
