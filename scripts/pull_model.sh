#!/bin/bash
# 拉取 Ollama 模型脚本
# 用法: ./scripts/pull_model.sh [model_name]
# 默认模型: qwen3:7b

set -e

MODEL_NAME="${1:-qwen3:7b}"
CONTAINER_NAME="ehs-ollama"

echo "=== 拉取 Ollama 模型: ${MODEL_NAME} ==="

# 检查容器是否运行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "错误: Ollama 容器 '${CONTAINER_NAME}' 未运行"
    echo "请先执行: docker compose up -d ollama"
    exit 1
fi

echo "正在拉取模型 ${MODEL_NAME}..."
echo "这可能需要几分钟，取决于网络速度..."

docker exec "${CONTAINER_NAME}" ollama pull "${MODEL_NAME}"

echo ""
echo "=== 模型拉取完成 ==="
echo "验证模型:"
docker exec "${CONTAINER_NAME}" ollama list

echo ""
echo "模型 ${MODEL_NAME} 已就绪，可以被 EHS AI 服务调用"
