#!/bin/bash

# 仅重新生成 Allure 报告的脚本（不执行测试）

echo "是否清理重复的历史数据？(y/n, 默认: n)"
read -r CLEAN_DATA

if [ "$CLEAN_DATA" = "y" ] || [ "$CLEAN_DATA" = "Y" ]; then
    echo "清理 allure-results 目录..."
    if [ -d "reports/allure-results" ]; then
        rm -rf reports/allure-results
        echo "已清理历史数据"
        echo "注意：由于已清理数据，需要重新执行测试才能生成报告"
        exit 0
    else
        echo "allure-results 目录不存在，无需清理"
    fi
fi

# 检查是否存在测试结果数据
if [ ! -d "reports/allure-results" ] || [ -z "$(ls -A reports/allure-results 2>/dev/null)" ]; then
    echo "错误：reports/allure-results 目录不存在或为空"
    echo "请先执行测试用例或运行 run_tests.sh"
    exit 1
fi

# 生成 allure 报告
echo "正在重新生成 Allure 报告..."
allure generate reports/allure-results -o reports/allure-report --clean --report-language zh

if [ $? -eq 0 ]; then
    echo "报告生成成功！"
    echo "是否打开报告？(y/n, 默认: y)"
    read -r OPEN_REPORT
    if [ "$OPEN_REPORT" != "n" ] && [ "$OPEN_REPORT" != "N" ]; then
        allure open reports/allure-report
    fi
else
    echo "报告生成失败！"
    exit 1
fi

