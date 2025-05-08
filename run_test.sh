#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPORT_DIR="$SCRIPT_DIR/reports/allure-results"

# 设置默认参数
ENV="test"
TEST_PATH="testcases"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --env=*)
            ENV="${1#*=}"
            shift
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# 确保报告目录存在
mkdir -p "$REPORT_DIR"

# 运行测试
pytest "$TEST_PATH" -v --alluredir="$REPORT_DIR" --clean-alluredir --env="$ENV"

# 启动 Allure 服务
allure serve "$REPORT_DIR" --port 8080 