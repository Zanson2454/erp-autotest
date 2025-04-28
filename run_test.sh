#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPORT_DIR="$SCRIPT_DIR/reports/allure-results"

# 确保reports目录存在
echo "Creating reports directory if not exists..."
mkdir -p "$REPORT_DIR"

# 清除历史数据
echo "Cleaning previous test results..."
rm -rf "$REPORT_DIR"/*

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 运行测试并生成报告
echo "Running tests and generating report..."
PYTHONPATH="$SCRIPT_DIR" pytest testcases/SCM/SO -v \
  --alluredir="$REPORT_DIR" \
  --clean-alluredir

# 启动在线报告
echo "Starting Allure report server..."
allure serve "$REPORT_DIR" 