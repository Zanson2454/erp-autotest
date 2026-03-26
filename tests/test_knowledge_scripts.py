import json
import subprocess
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "script" / "build_knowledge_index.py"
GENERATE_SCRIPT = REPO_ROOT / "script" / "generate_api_cases.py"
VALIDATE_SCRIPT = REPO_ROOT / "script" / "validate_generated_cases.py"


def run_cmd(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def test_build_knowledge_index_generates_expected_schema(tmp_path):
    api_path_file = tmp_path / "demo_api_path.yaml"
    api_path_file.write_text(
        yaml.safe_dump(
            {
                "apis": {
                    "DEMO-保存服务": {
                        "path": "/api/demo/save",
                        "method": "POST",
                    },
                    "DEMO-查询服务": {
                        "path": "/api/demo/query",
                        "method": "GET",
                    },
                }
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    sources_dir = tmp_path / "sources"
    (sources_dir / "requirements").mkdir(parents=True)
    (sources_dir / "design").mkdir(parents=True)
    (sources_dir / "history_cases").mkdir(parents=True)
    (sources_dir / "defects").mkdir(parents=True)

    (sources_dir / "requirements" / "demo.md").write_text(
        "DEMO-保存服务 规则：编码唯一，不可重复", encoding="utf-8"
    )
    (sources_dir / "design" / "demo.md").write_text(
        "DEMO-查询服务 规则：支持分页参数", encoding="utf-8"
    )
    (sources_dir / "defects" / "bug-1.md").write_text(
        "DEMO-保存服务 反例：空编码必须报错", encoding="utf-8"
    )

    testcase_dir = tmp_path / "testcases"
    testcase_dir.mkdir()
    (testcase_dir / "test_demo.py").write_text(
        'def test_demo():\n    self.standard_api_call(api_key="DEMO-保存服务")\n',
        encoding="utf-8",
    )

    out_file = tmp_path / "api_knowledge.yaml"

    result = run_cmd(
        [
            sys.executable,
            str(BUILD_SCRIPT),
            "--module",
            "demo",
            "--api-path-yaml",
            str(api_path_file),
            "--sources-dir",
            str(sources_dir),
            "--testcase-dir",
            str(testcase_dir),
            "--output",
            str(out_file),
        ],
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    data = yaml.safe_load(out_file.read_text(encoding="utf-8"))

    assert "apis" in data
    assert "DEMO-保存服务" in data["apis"]
    save_item = data["apis"]["DEMO-保存服务"]
    assert save_item["module"] == "demo"
    assert save_item["method"] == "POST"
    assert save_item["business_rules"]
    assert save_item["negative_cases"]
    assert save_item["history_refs"]


def test_generate_api_cases_creates_case_yaml(tmp_path):
    kb_file = tmp_path / "api_knowledge.yaml"
    kb_file.write_text(
        yaml.safe_dump(
            {
                "apis": {
                    "DEMO-保存服务": {
                        "module": "demo",
                        "api_key": "DEMO-保存服务",
                        "path": "/api/demo/save",
                        "method": "POST",
                        "business_rules": ["编码唯一"],
                        "assertions": ["返回code=0"],
                        "preconditions": ["准备组织数据"],
                        "negative_cases": ["空编码报错"],
                        "history_refs": ["testcases/demo/test_demo.py::test_save"],
                    }
                }
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "generated_cases"

    result = run_cmd(
        [
            sys.executable,
            str(GENERATE_SCRIPT),
            "--knowledge",
            str(kb_file),
            "--api-key",
            "DEMO-保存服务",
            "--output-dir",
            str(output_dir),
        ],
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    case_file = output_dir / "demo" / "DEMO-保存服务.yaml"
    assert case_file.exists()

    case_data = yaml.safe_load(case_file.read_text(encoding="utf-8"))
    assert case_data["api_key"] == "DEMO-保存服务"
    assert case_data["request_template"] == {}
    assert len(case_data["test_scenarios"]) >= 2


def test_validate_generated_cases_fails_for_invalid_file(tmp_path):
    generated_dir = tmp_path / "generated_cases"
    (generated_dir / "demo").mkdir(parents=True)

    valid = {
        "api_key": "DEMO-保存服务",
        "path": "/api/demo/save",
        "method": "POST",
        "request_template": {},
        "test_scenarios": [
            {
                "name": "正向",
                "type": "positive",
                "request": {},
                "assertions": ["code=0"],
            }
        ],
        "assertions": ["code=0"],
    }
    invalid = {
        "api_key": "DEMO-坏用例",
        "path": "/api/demo/bad",
        "method": "POST",
        "request_template": {},
        "test_scenarios": [],
        "assertions": [],
    }

    (generated_dir / "demo" / "valid.yaml").write_text(
        yaml.safe_dump(valid, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    (generated_dir / "demo" / "invalid.yaml").write_text(
        yaml.safe_dump(invalid, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )

    report_file = tmp_path / "validate_report.json"
    result = run_cmd(
        [
            sys.executable,
            str(VALIDATE_SCRIPT),
            "--generated-dir",
            str(generated_dir),
            "--report-json",
            str(report_file),
        ],
        cwd=REPO_ROOT,
    )

    assert result.returncode == 1
    report = json.loads(report_file.read_text(encoding="utf-8"))
    assert report["invalid_count"] == 1
    assert any("invalid.yaml" in item["file"] for item in report["invalid_files"])
