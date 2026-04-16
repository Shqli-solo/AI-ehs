#!/bin/bash
# EHS 智能安保决策中台 - 面试演示脚本
#
# 一键启动所有服务并导入数据，准备演示环境

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  EHS 智能安保决策中台 - 面试演示环境启动   ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 1. 启动基础设施
echo -e "${YELLOW}[1/5] 启动基础设施服务...${NC}"
docker compose up -d ollama elasticsearch etcd minio milvus postgres 2>/dev/null
echo "  等待基础设施就绪..."
sleep 15

# 2. 启动应用服务
echo -e "${YELLOW}[2/5] 启动应用服务...${NC}"
docker compose up -d ehs-ai ehs-business admin-console 2>/dev/null
echo "  等待应用服务启动..."
sleep 15

# 3. 检查服务健康
echo -e "${YELLOW}[3/5] 检查服务健康...${NC}"

check_service() {
    local name=$1
    local url=$2
    local max_retries=20
    local i=0
    while [ $i -lt $max_retries ]; do
        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name 已就绪"
            return 0
        fi
        i=$((i+1))
        sleep 3
    done
    echo -e "  ${RED}✗${NC} $name 未能就绪"
    return 1
}

check_service "AI Service" "http://localhost:8000/health"
check_service "Elasticsearch" "http://localhost:9200/_cluster/health"

# 4. 导入数据（如果未导入过）
echo -e "${YELLOW}[4/5] 导入种子数据...${NC}"
if command -v python3 &> /dev/null; then
    python3 "$SCRIPT_DIR/seed_data.py" 2>/dev/null || echo "  数据导入可能有部分失败，继续..."
else
    echo "  Python3 未安装，跳过数据导入"
fi

# 5. 显示访问地址
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  演示环境已就绪！                          ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "访问地址:"
echo "  🌐 前端管理控制台:  http://localhost:3000"
echo "  📊 知识图谱可视化:  http://localhost:3000/graph"
echo "  📋 告警上报页面:    http://localhost:3000/alert/report"
echo "  🔧 AI 服务 API:     http://localhost:8000/health"
echo "  🔧 业务服务 API:    http://localhost:8080/actuator/health"
echo "  💾 MinIO 控制台:    http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "演示流程:"
echo "  1. 打开 http://localhost:3000 → 查看 Dashboard"
echo "  2. 打开 http://localhost:3000/alert/report → 提交告警"
echo "  3. 打开 http://localhost:3000/graph → 知识图谱可视化"
echo "  4. 讲解架构: COLA + 六边形 + LangGraph + GraphRAG"
echo ""
echo "停止服务: docker compose down"
echo "查看日志: docker compose logs -f ehs-ai"
