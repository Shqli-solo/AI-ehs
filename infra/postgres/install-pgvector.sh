#!/bin/bash
# 在 PostgreSQL 容器首次启动时安装 pgvector 扩展
# 仅在向量扩展不存在时执行

set -e

# 检查是否已安装 vector 扩展
if psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dx vector" 2>/dev/null | grep -q vector; then
    echo "pgvector already installed, skipping build"
    exit 0
fi

echo "Installing pgvector from source..."

# 安装编译依赖
apt-get update -qq
apt-get install -y -qq build-essential postgresql-server-dev-$PG_MAJOR git > /dev/null 2>&1

# 克隆并编译 pgvector
cd /tmp
git clone --branch v0.7.4 --depth 1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

# 清理
cd /
rm -rf /tmp/pgvector
apt-get remove -y -qq build-essential git > /dev/null 2>&1
apt-get autoremove -y -qq > /dev/null 2>&1

echo "pgvector installed successfully"
