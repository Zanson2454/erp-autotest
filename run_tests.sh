#!/bin/bash

# 清理之前的 allure 结果数据（避免数据累积）
if [ -d "reports/allure-results" ]; then
    rm -rf reports/allure-results
fi
mkdir -p reports/allure-results

# 执行测试并生成 allure 数据
python3 -m pytest testcases/ -v --alluredir=reports/allure-results \
    --ignore=testcases/prd \
    --ignore=testcases/fin/fin_ap \
    --ignore=testcases/fin/fin_ar
TEST_EXIT_CODE=$?

# 生成 allure 报告（无论测试是否成功都生成报告）
allure generate reports/allure-results -o reports/allure-report --clean --report-language zh

# 打开报告
allure open reports/allure-report

# 根据测试结果返回退出码
exit $TEST_EXIT_CODE