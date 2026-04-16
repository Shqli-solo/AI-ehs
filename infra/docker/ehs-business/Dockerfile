# EHS Business Service Dockerfile
# Java Spring Boot + COLA + gRPC 服务
# 构建：docker build -f infra/docker/ehs-business/Dockerfile -t ehs-business-service:latest .
# 运行：docker run -p 8080:8080 ehs-business-service:latest

FROM maven:3.9-eclipse-temurin-17 AS builder

# 设置工作目录
WORKDIR /build

# 复制 Maven 配置
COPY apps/ehs-business/pom.xml ./

# 下载依赖（利用 Docker 缓存层）
RUN mvn dependency:go-offline -B

# 复制源代码
COPY apps/ehs-business/src ./src
COPY apps/ehs-business/proto ./proto 2>/dev/null || true

# 构建项目
RUN mvn clean package -DskipTests -B

# ==================== 运行阶段 ====================
FROM eclipse-temurin:17-jre-alpine

# 设置工作目录
WORKDIR /app

# 创建非 root 用户
RUN addgroup -g 1001 -S java && \
    adduser -S java -u 1001 -G java

# 从构建阶段复制 jar 包
COPY --from=builder /build/target/ehs-business-*.jar app.jar

# 修改所有者
RUN chown -R java:java /app

USER java

# 暴露端口
EXPOSE 8080

# JVM 参数优化
ENV JAVA_OPTS="-Xms512m -Xmx1g -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# 启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
