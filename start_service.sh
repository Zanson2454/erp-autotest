#!/bin/bash

# 确保报告目录存在
mkdir -p /app/reports/allure-results
mkdir -p /app/reports/allure-report

# 默认测试路径
TEST_PATH=${TEST_PATH:-"testcases/"}

# 打印环境信息和配置文件
echo "=== 环境信息 ==="
echo "容器内目录结构:"
ls -la /app
echo "配置文件:"
if [ -f /app/.env ]; then echo ".env 文件存在"; else echo ".env 文件不存在"; fi
if [ -f /app/pytest.ini ]; then echo "pytest.ini 文件存在"; else echo "pytest.ini 文件不存在"; fi
if [ -d /app/config/env ]; then echo "config/env 目录存在"; else echo "config/env 目录不存在"; fi

# 运行测试用例
echo "开始运行测试..."
pytest $TEST_PATH -v --alluredir=/app/reports/allure-results || echo "测试执行完成，返回码: $?"

# 生成Allure报告
echo "生成Allure HTML报告..."
allure generate /app/reports/allure-results -o /app/reports/allure-report --clean

echo "==========================================="
echo "Allure报告已生成，访问地址: http://$(hostname -i):8000"
echo "==========================================="

# 启动HTTP服务提供报告访问
cd /app/reports/allure-report && python -m http.server 8000 