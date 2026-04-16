# EHS Admin Console Dockerfile
# Next.js 14 前端服务
# 构建：docker build -f infra/docker/admin-console/Dockerfile -t ehs-admin-console:latest .
# 运行：docker run -p 3000:3000 ehs-admin-console:latest

FROM node:20-alpine

# 安装依赖
RUN apk add --no-cache libc6-compat

# 设置工作目录
WORKDIR /app

# 复制 pnpm 配置
COPY pnpm-workspace.yaml ./
COPY package.json ./

# 复制前端配置
COPY apps/admin-console/package.json ./apps/admin-console/package.json

# 安装 pnpm
RUN npm install -g pnpm@9.0.0

# 安装依赖
COPY apps/admin-console ./apps/admin-console
RUN cd apps/admin-console && pnpm install --frozen-lockfile

# 复制完整的前端源码
COPY apps/admin-console/src ./apps/admin-console/src
COPY apps/admin-console/public ./apps/admin-console/public 2>/dev/null || true
COPY apps/admin-console/*.config.* ./apps/admin-console/
COPY apps/admin-console/*.json ./apps/admin-console/
COPY apps/admin-console/*.ts ./apps/admin-console/ 2>/dev/null || true

# 构建前端
RUN cd apps/admin-console && pnpm build

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 -G nodejs
USER nextjs

# 暴露端口
EXPOSE 3000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# 工作目录
WORKDIR /app/apps/admin-console

# 启动命令
CMD ["pnpm", "start"]
