#!/bin/bash

# 清除历史数据
echo "Cleaning previous test results..."
rm -rf ./reports/allure-results/*

# 运行测试并生成报告
echo "Running tests and generating report..."
pytest testcases/SCM/SO -v --alluredir=./reports/allure-results

# 启动在线报告
echo "Starting Allure report server..."
allure serve ./reports/allure-results 