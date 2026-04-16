#!/bin/bash
# EHS 智能安保决策中台 - 启动脚本
#
# 用法:
#   ./scripts/start.sh              # 启动所有服务
#   ./scripts/start.sh --infra      # 仅启动基础设施
#   ./scripts/start.sh --seed       # 启动 + 导入数据
#   ./scripts/start.sh --pull-model # 拉取 LLM 模型
#   ./scripts/start.sh --stop       # 停止所有服务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

case "${1:-}" in
    --infra)
        echo "=== 启动基础设施 ==="
        docker compose up -d ollama elasticsearch etcd minio milvus postgres
        echo "等待基础设施就绪..."
        sleep 5
        ;;

    --seed)
        echo "=== 启动所有服务并导入数据 ==="
        docker compose up -d
        echo "等待服务启动..."
        sleep 10
        echo ""
        echo "=== 导入数据 ==="
        docker compose run --rm data-seed || echo "数据导入失败，可以手动执行: docker compose run --rm data-seed"
        ;;

    --pull-model)
        echo "=== 拉取 LLM 模型 ==="
        bash "$SCRIPT_DIR/pull_model.sh"
        ;;

    --stop)
        echo "=== 停止所有服务 ==="
        docker compose down
        ;;

    --clean)
        echo "=== 停止并删除所有数据 ==="
        docker compose down -v
        ;;

    *)
        echo "=== 启动 EHS 智能安保决策中台 ==="
        docker compose up -d
        echo ""
        echo "服务列表:"
        echo "  - Ollama (LLM):     http://localhost:11434"
        echo "  - Elasticsearch:    http://localhost:9200"
        echo "  - MinIO Console:    http://localhost:9001"
        echo "  - Milvus:           localhost:19530"
        echo "  - PostgreSQL:       localhost:5432"
        echo "  - EHS AI API:       http://localhost:8000"
        echo "  - EHS Business:     http://localhost:8080"
        echo "  - Admin Console:    http://localhost:3000"
        echo ""
        echo "下一步:"
        echo "  1. 首次运行需要拉取模型: ./scripts/start.sh --pull-model"
        echo "  2. 导入种子数据:       ./scripts/start.sh --seed"
        echo "  3. 查看日志:           docker compose logs -f ehs-ai"
        ;;
esac
