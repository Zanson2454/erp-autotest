#!/usr/bin/env python3
"""主数据 / 缓存预热入口（不替代 DBA 在库内创建 AUTOTEST_* 业务数据）。

典型用途：
  - 新环境接入后执行一次，将 config/erp/*_init_sql.yaml 结果写入 testdata/cache/
  - 与 GET_START.md 中「准备主数据 + .env」配合使用

子命令：
  warm-cache   调用 DataFactory 拉取 base + md SQL 缓存（需可连 ERP DB）
  print-guide  仅打印人工准备清单（不连库）

用法：
  python script/seed_test_data.py warm-cache --env test
  python script/seed_test_data.py print-guide
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _bootstrap_path() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))


def cmd_print_guide() -> int:
    print(
        """
=== ERP 自动化测试主数据准备（摘要）===

1. 在被测库中创建 AUTOTEST_* 前缀的组织/客户/供应商/物料等（参见 GET_START.md）。
2. 配置 config/env/.env 与 config/env/{env}.yaml，保证 ${VAR} 可解析。
3. 执行缓存预热：
     python script/seed_test_data.py warm-cache --env test
4. 或运行全量检查：
     python script/test_init_check.py

说明：本仓库不内置「一键 INSERT 全量主数据」；seed_test_data.py 负责触发 SQL 初始化缓存。
"""
    )
    return 0


def cmd_warm_cache(env: str, project: str | None) -> int:
    _bootstrap_path()
    os.environ.setdefault("TEST_ENV", env)
    if project:
        os.environ["TEST_PROJECT"] = project
    try:
        from data_factory.base import DataFactory
    except ImportError as e:
        print(f"导入失败: {e}", file=sys.stderr)
        return 2

    DataFactory.__init__(env_name=env, project=project)
    print(f"环境: TEST_ENV={env}" + (f", TEST_PROJECT={project}" if project else ""))

    try:
        base = DataFactory.get_base_data(project="erp")
        print(f"base_init_sql → init_cache: keys={list((base or {}).keys())[:8]}...")
    except Exception as e:
        print(f"get_base_data 失败: {e}", file=sys.stderr)
        return 1

    try:
        from utils.yaml_util import YamlUtil
        YamlUtil.init("config")
        sql_path = PROJECT_ROOT / "config" / "erp" / "md_init_sql.yaml"
        DataFactory.init_sql_cache(
            sql_config_path=str(sql_path),
            db_config_name="erp_db",
            cache_key="md_init_cache",
            cache_dir=str(PROJECT_ROOT / "testdata" / "cache"),
        )
        print("md_init_sql → md_init_cache: OK")
    except Exception as e:
        print(f"md_init_cache 失败: {e}", file=sys.stderr)
        return 1

    print("warm-cache 完成：testdata/cache/ 下已写入/更新缓存（仍受过期时间与 hash 失效策略影响）。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="主数据缓存预热 / 指引")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_guide = sub.add_parser("print-guide", help="打印人工准备步骤")
    p_warm = sub.add_parser("warm-cache", help="连接 DB 并预热 init + md 缓存")
    p_warm.add_argument("--env", default=os.getenv("TEST_ENV", "test"), help="对应 TEST_ENV")
    p_warm.add_argument("--project", default=os.getenv("TEST_PROJECT"), help="对应 TEST_PROJECT（多项目）")

    args = parser.parse_args()
    if args.cmd == "print-guide":
        return cmd_print_guide()
    if args.cmd == "warm-cache":
        return cmd_warm_cache(env=args.env, project=args.project)
    return 2


if __name__ == "__main__":
    sys.exit(main())
