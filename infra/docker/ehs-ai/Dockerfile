# EHS AI Service Dockerfile
# Python FastAPI + LangGraph + GraphRAG 服务
# 构建：docker build -f infra/docker/ehs-ai/Dockerfile -t ehs-ai-service:latest .
# 运行：docker run -p 8000:8000 ehs-ai-service:latest

FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Poetry 配置
    POETRY_VERSION=1.8.0 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# 添加工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# 添加 Poetry 到 PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制 Poetry 配置
COPY apps/ehs-ai/pyproject.toml apps/ehs-ai/poetry.lock* ./

# 安装依赖（包含生产依赖和开发依赖）
RUN poetry install --no-interaction --no-ansi

# 复制源代码
COPY apps/ehs-ai/src/ ./src/
COPY apps/ehs-ai/proto/ ./proto/ 2>/dev/null || true

# 创建非 root 用户
RUN useradd -m -u 1000 ehs && chown -R ehs:ehs /app
USER ehs

# 暴露端口
EXPOSE 8000 9092

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["poetry", "run", "uvicorn", "src.api.rest:app", "--host", "0.0.0.0", "--port", "8000"]
