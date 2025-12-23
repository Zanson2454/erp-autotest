#!/bin/bash

# 配置：哪些模块不走并发（串行执行）
SERIAL_MODULES="scm_inv scm_sls"

# 并发进程数
WORKERS=4

# 环境
ENV="test"

# ============================================================================

# 第1步：串行执行指定的模块
for module in $SERIAL_MODULES; do
    echo "▶️  执行 $module（串行）..."
    pytest testcases/$module --env=$ENV -v
    if [ $? -ne 0 ]; then
        echo "❌ $module 失败！"
        exit 1
    fi
done

# 第2步：构建排除参数
ignore=""
for module in $SERIAL_MODULES; do
    ignore="$ignore --ignore=testcases/$module"
done

# 第3步：其他模块并行执行
echo "▶️  执行其他模块（并行，$WORKERS 进程）..."
pytest testcases/ $ignore -n $WORKERS --dist=loadfile --env=$ENV -v

if [ $? -eq 0 ]; then
    echo "✅ 所有测试通过！"
else
    echo "❌ 部分测试失败！"
    exit 1
fi

