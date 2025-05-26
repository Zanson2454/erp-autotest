#!/bin/bash

# 确保脚本在出错时停止执行
set -e

echo "==== ERP 自动化测试平台启动脚本 ===="

# 检查并创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate || source .venv/Scripts/activate

# 安装依赖
echo "检查并安装依赖..."
pip install flask pytest allure-pytest

# 创建必要的目录结构
echo "确保目录结构完整..."
mkdir -p reports/allure-results
mkdir -p reports/allure-report
mkdir -p reports/archive
mkdir -p reports/history

# 确保正确退出
function cleanup {
    echo "停止服务..."
    # 查找并终止运行的test_runner.py进程
    pkill -f "python test_runner.py" || true
}

# 注册清理函数
trap cleanup EXIT

# 启动服务
echo "启动测试平台服务..."
python test_runner.py