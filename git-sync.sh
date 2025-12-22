#!/bin/bash

# Git 同步脚本：拉取 + 推送
# 1. 拉取远程代码
# 2. 推送本地修改（排除 .env）

cd "$(dirname "$0")"

echo "🔄 Git 同步开始..."
echo ""

# 1. 拉取
echo "1️⃣ 拉取远程代码..."
git pull origin feature/develop
echo "✅ 拉取完成"
echo ""

# 2. 推送
echo "2️⃣ 推送本地修改..."
git add -A
git reset .env 2>/dev/null || true  # 排除 .env

if git diff --cached --quiet; then
    echo "✅ 无改动需要推送"
else
    git commit -m "[auto] $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin feature/develop
    echo "✅ 推送完成"
fi

echo ""
echo "✨ 完成！"

