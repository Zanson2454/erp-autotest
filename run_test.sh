#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPORT_DIR="$SCRIPT_DIR/reports/allure-results"

# 默认环境为 test
ENV=${1:-"test"}

# 检查环境配置文件是否存在
CONFIG_FILE="$SCRIPT_DIR/config/env/${ENV}.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found: ${CONFIG_FILE}"
    echo "Available environments:"
    ls -1 "$SCRIPT_DIR/config/env/" | sed 's/\.yaml$//'
    exit 1
fi

# 确保reports目录存在
echo "Creating reports directory if not exists..."
mkdir -p "$REPORT_DIR"

# 清除历史数据
echo "Cleaning previous test results..."
rm -rf "$REPORT_DIR"/*

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 从yaml文件中读取环境和版本信息
echo "Using configuration file: ${CONFIG_FILE}"
if command -v yq >/dev/null 2>&1; then
    # 使用 yq 读取 yaml 文件
    ENV_TYPE=$(yq eval '.erp_env' "$CONFIG_FILE")
    TRANTOR_VERSION=$(yq eval '.trantor_version' "$CONFIG_FILE")
else
    # 如果没有 yq，使用 Python 读取 yaml 文件
    ENV_TYPE=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['erp_env'])")
    TRANTOR_VERSION=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['trantor_version'])")
fi

echo "Environment: ${ENV_TYPE}"
echo "Trantor Version: ${TRANTOR_VERSION}"

# 运行测试并生成报告
echo "Running tests and generating report..."
PYTHONPATH="$SCRIPT_DIR" pytest testcases/SCM/SO -v \
  --alluredir="$REPORT_DIR" \
  --env="$ENV_TYPE" \
  --trantor_version="$TRANTOR_VERSION"

# 启动在线报告
echo "Starting Allure report server..."
allure serve "$REPORT_DIR" 