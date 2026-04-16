# syntax=docker/dockerfile:1

# ============================================
# Stage 1: 依赖安装
# ============================================
FROM python:3.11-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装 Poetry
ENV POETRY_VERSION=1.8.0
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 -

# 复制依赖文件并安装
COPY pyproject.toml poetry.lock* ./

# 只安装生产依赖，跳过 dev 依赖
# --no-root 避免安装项目本身（包结构在下一阶段复制）
RUN poetry install --only main --no-interaction --no-ansi --no-root

# ============================================
# Stage 2: 运行镜像
# ============================================
FROM python:3.11-slim AS runtime

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 安装运行时依赖（curl 用于健康检查）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 阶段复制 Python 包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 生成 gRPC 代码（如果 proto 文件存在）
RUN if [ -f src/main/proto/ehs.proto ]; then \
        python -m grpc_tools.protoc \
        -I src/main/proto \
        --python_out=. \
        --grpc_python_out=. \
        src/main/proto/ehs.proto; \
    fi

# 暴露端口
EXPOSE 8000 50051

# 健康检查
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "src.adapters.primary.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
