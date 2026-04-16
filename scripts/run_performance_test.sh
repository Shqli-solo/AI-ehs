#!/bin/bash

# =============================================================================
# EHS 智能安保决策中台 - 性能测试运行脚本
# =============================================================================
#
# 使用方法:
#   ./scripts/run_performance_test.sh [locust|k6|all] [options]
#
# 示例:
#   ./scripts/run_performance_test.sh locust     # 运行 Locust 测试
#   ./scripts/run_performance_test.sh k6         # 运行 k6 测试
#   ./scripts/run_performance_test.sh all        # 运行所有测试
#   ./requests=100 ./scripts/run_performance_test.sh locust  # 自定义请求数
#
# 环境变量:
#   BASE_URL         - 目标服务地址 (默认：http://localhost:8000)
#   LOCUST_USERS     - Locust 并发用户数 (默认：50)
#   LOCUST_SPAWN_RATE - Locust 用户生成速率 (默认：5)
#   LOCUST_RUN_TIME  - Locust 运行时间 (默认：60s)
#   K6_DURATION      - k6 测试持续时间 (默认：3m)
#   K6_VUS           - k6 并发用户数 (默认：50)
#
# 验收标准:
#   - P95 延迟 < 800ms
#   - 错误率 < 1%
#
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
BASE_URL=${BASE_URL:-"http://localhost:8000"}
LOCUST_USERS=${LOCUST_USERS:-50}
LOCUST_SPAWN_RATE=${LOCUST_SPAWN_RATE:-5}
LOCUST_RUN_TIME=${LOCUST_RUN_TIME:-60s}
K6_DURATION=${K6_DURATION:-3m}
K6_VUS=${K6_VUS:-50}

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PERFORMANCE_TEST_DIR="$PROJECT_ROOT/tests/performance"

# =============================================================================
# 辅助函数
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "  $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 未安装，请先安装：$2"
        exit 1
    fi
}

# =============================================================================
# 前置检查
# =============================================================================

check_prerequisites() {
    print_header "前置检查"

    # 检查 Python
    check_command "python3" "pip install python3"
    print_success "Python 已安装: $(python3 --version)"

    # 检查 Locust
    if ! python3 -c "import locust" 2>/dev/null; then
        print_warning "Locust 未安装，尝试安装..."
        pip3 install locust
        if [ $? -eq 0 ]; then
            print_success "Locust 安装成功"
        else
            print_error "Locust 安装失败"
            exit 1
        fi
    else
        print_success "Locust 已安装"
    fi

    # 检查 k6
    if command -v "k6" &> /dev/null; then
        print_success "k6 已安装: $(k6 version 2>/dev/null || echo 'unknown')"
    else
        print_warning "k6 未安装 (可选)"
        print_info "如需安装 k6,请访问：https://k6.io/docs/getting-started/installation/"
    fi

    # 检查测试文件
    if [ ! -f "$PERFORMANCE_TEST_DIR/locustfile.py" ]; then
        print_error "Locust 测试文件不存在：$PERFORMANCE_TEST_DIR/locustfile.py"
        exit 1
    fi
    print_success "Locust 测试文件存在"

    if [ ! -f "$PERFORMANCE_TEST_DIR/k6/script.js" ]; then
        print_warning "k6 测试文件不存在：$PERFORMANCE_TEST_DIR/k6/script.js"
    else
        print_success "k6 测试文件存在"
    fi

    # 检查服务是否可用
    print_info "检查服务可用性：$BASE_URL"
    if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" | grep -q "200"; then
        print_success "服务可访问"
    else
        print_warning "服务不可访问 ($BASE_URL), 性能测试可能失败"
        print_info "请确保服务已启动：python -m uvicorn src.api.rest:app --reload --host 0.0.0.0 --port 8000"
    fi
}

# =============================================================================
# Locust 测试
# =============================================================================

run_locust() {
    print_header "运行 Locust 性能测试"

    print_info "配置:"
    print_info "  BASE_URL: $BASE_URL"
    print_info "  并发用户数：$LOCUST_USERS"
    print_info "  用户生成速率：$LOCUST_SPAWN_RATE 用户/秒"
    print_info "  运行时间：$LOCUST_RUN_TIME"

    # 创建报告目录
    REPORT_DIR="$PERFORMANCE_TEST_DIR/reports/locust/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$REPORT_DIR"

    cd "$PERFORMANCE_TEST_DIR"

    # 运行 Locust 无头模式
    print_info "开始测试..."
    echo ""

    locust \
        --headless \
        --host "$BASE_URL" \
        --users "$LOCUST_USERS" \
        --spawn-rate "$LOCUST_SPAWN_RATE" \
        --run-time "$LOCUST_RUN_TIME" \
        --html "$REPORT_DIR/report.html" \
        --csv "$REPORT_DIR/results" \
        --json "$REPORT_DIR/results.json" \
        -f locustfile.py

    # 检查结果
    if [ $? -eq 0 ]; then
        echo ""
        print_success "Locust 测试完成"
        print_info "报告保存在：$REPORT_DIR"
        print_info "  - HTML 报告：$REPORT_DIR/report.html"
        print_info "  - CSV 数据：$REPORT_DIR/results_*.csv"
        print_info "  - JSON 数据：$REPORT_DIR/results.json"
    else
        print_error "Locust 测试失败"
        exit 1
    fi

    cd "$PROJECT_ROOT"
}

# =============================================================================
# k6 测试
# =============================================================================

run_k6() {
    print_header "运行 k6 性能测试"

    # 检查 k6 是否安装
    if ! command -v "k6" &> /dev/null; then
        print_error "k6 未安装，无法运行 k6 测试"
        print_info "安装 k6: https://k6.io/docs/getting-started/installation/"
        exit 1
    fi

    print_info "配置:"
    print_info "  BASE_URL: $BASE_URL"
    print_info "  并发用户数：$K6_VUS"
    print_info "  测试持续时间：$K6_DURATION"

    # 创建报告目录
    REPORT_DIR="$PERFORMANCE_TEST_DIR/reports/k6/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$REPORT_DIR"

    # 运行 k6
    print_info "开始测试..."
    echo ""

    BASE_URL="$BASE_URL" k6 run \
        --out csv="$REPORT_DIR/results.csv" \
        --out json="$REPORT_DIR/results.json" \
        "$PERFORMANCE_TEST_DIR/k6/script.js" | tee "$REPORT_DIR/output.log"

    # 检查结果
    if [ $? -eq 0 ]; then
        echo ""
        print_success "k6 测试完成"
        print_info "报告保存在：$REPORT_DIR"
        print_info "  - CSV 数据：$REPORT_DIR/results.csv"
        print_info "  - JSON 数据：$REPORT_DIR/results.json"
        print_info "  - 日志输出：$REPORT_DIR/output.log"
    else
        print_warning "k6 测试完成 (可能有阈值未通过)"
        print_info "详细结果请查看：$REPORT_DIR"
    fi
}

# =============================================================================
# 运行所有测试
# =============================================================================

run_all() {
    print_header "运行所有性能测试"

    run_locust
    echo ""
    run_k6

    print_header "所有测试完成"
    print_success "性能测试全部完成"
}

# =============================================================================
# 显示帮助信息
# =============================================================================

show_help() {
    echo ""
    echo "使用方法:"
    echo "  $0 [command] [options]"
    echo ""
    echo "命令:"
    echo "  locust     运行 Locust 测试"
    echo "  k6         运行 k6 测试"
    echo "  all        运行所有测试"
    echo "  help       显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  BASE_URL          目标服务地址 (默认：http://localhost:8000)"
    echo "  LOCUST_USERS      Locust 并发用户数 (默认：50)"
    echo "  LOCUST_SPAWN_RATE Locust 用户生成速率 (默认：5)"
    echo "  LOCUST_RUN_TIME   Locust 运行时间 (默认：60s)"
    echo "  K6_DURATION       k6 测试持续时间 (默认：3m)"
    echo "  K6_VUS            k6 并发用户数 (默认：50)"
    echo ""
    echo "示例:"
    echo "  # 运行 Locust 测试"
    echo "  ./run_performance_test.sh locust"
    echo ""
    echo "  # 运行 k6 测试"
    echo "  ./run_performance_test.sh k6"
    echo ""
    echo "  # 运行所有测试"
    echo "  ./run_performance_test.sh all"
    echo ""
    echo "  # 自定义配置运行"
    echo "  LOCUST_USERS=100 LOCUST_RUN_TIME=120s ./run_performance_test.sh locust"
    echo ""
    echo "验收标准:"
    echo "  - P95 延迟 < 800ms"
    echo "  - 错误率 < 1%"
    echo ""
}

# =============================================================================
# 主函数
# =============================================================================

main() {
    local command="${1:-all}"

    case "$command" in
        locust)
            check_prerequisites
            run_locust
            ;;
        k6)
            check_prerequisites
            run_k6
            ;;
        all)
            check_prerequisites
            run_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令：$command"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
