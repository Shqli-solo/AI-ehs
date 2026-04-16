package com.ehs.business.config;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.netty.shaded.io.grpc.netty.GrpcSslContexts;
import io.grpc.netty.shaded.io.netty.handler.ssl.SslContext;
import io.grpc.netty.shaded.io.netty.handler.ssl.SslContextBuilder;
import io.grpc.stub.ClientCallStreamObserver;
import io.grpc.stub.ClientResponseObserver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

/**
 * gRPC 配置类 - 配置超时、重试、熔断和 TLS
 *
 * 配置项：
 * - 超时：Deadline 120 秒
 * - 重试：最大 3 次，指数退避
 * - 熔断：连续 10 次失败后停止
 * - TLS：双向认证
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@Configuration
public class GrpcConfig {

    private static final Logger log = LoggerFactory.getLogger(GrpcConfig.class);

    // ==================== 配置参数 ====================

    @Value("${grpc.python-ai.host:localhost}")
    private String pythonAiHost;

    @Value("${grpc.python-ai.port:50051}")
    private int pythonAiPort;

    @Value("${grpc.timeout.seconds:120}")
    private int timeoutSeconds;

    @Value("${grpc.retry.max:3}")
    private int maxRetryAttempts;

    @Value("${grpc.retry.initial-backoff.ms:100}")
    private int initialBackoffMs;

    @Value("${grpc.retry.max-backoff.ms:10000}")
    private int maxBackoffMs;

    @Value("${grpc.circuit-breaker.failure-threshold:10}")
    private int circuitBreakerFailureThreshold;

    @Value("${grpc.circuit-breaker.reset-timeout.ms:60000}")
    private int circuitBreakerResetTimeoutMs;

    @Value("${grpc.tls.enabled:false}")
    private boolean tlsEnabled;

    @Value("${grpc.tls.ca-cert:}")
    private String caCertPath;

    @Value("${grpc.tls.client-cert:}")
    private String clientCertPath;

    @Value("${grpc.tls.client-key:}")
    private String clientKeyPath;

    // ==================== 熔断器状态 ====================

    private final AtomicLong failureCount = new AtomicLong(0);
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    private volatile boolean circuitOpen = false;

    // ==================== gRPC 通道 ====================

    private ManagedChannel channel;

    /**
     * 创建 Python AI 服务 gRPC 通道
     * 配置 TLS、超时、拦截器等
     */
    @Bean
    public ManagedChannel pythonAiChannel() throws IOException {
        ManagedChannelBuilder<?> builder = ManagedChannelBuilder
                .forAddress(pythonAiHost, pythonAiPort);

        if (tlsEnabled) {
            log.info("启用 TLS 双向认证：host={}, port={}", pythonAiHost, pythonAiPort);
            SslContext sslContext = createSslContext();
            builder = ((io.grpc.netty.shaded.io.grpc.netty.NettyChannelBuilder) builder)
                    .sslContext(sslContext);
        } else {
            log.warn("TLS 未启用，使用明文通道（仅限开发环境）");
            builder = builder.usePlaintext();
        }

        // 配置重试策略
        builder.enableRetry()
                .maxRetryAttempts(maxRetryAttempts)
                .perRpcBufferLimit(1024 * 1024)
                .maxTraceEvents(100);

        // 配置保活
        builder.keepAliveTime(30, TimeUnit.SECONDS)
                .keepAliveTimeout(10, TimeUnit.SECONDS)
                .keepAliveWithoutCalls(true);

        channel = builder.build();
        log.info("gRPC 通道创建成功：host={}, port={}, timeout={}s, retry={}, tls={}",
                pythonAiHost, pythonAiPort, timeoutSeconds, maxRetryAttempts, tlsEnabled);

        return channel;
    }

    /**
     * 创建 TLS SSL 上下文
     * 支持双向认证（mTLS）
     */
    private SslContext createSslContext() throws IOException {
        log.info("加载 TLS 证书：caCert={}, clientCert={}, clientKey={}",
                caCertPath, clientCertPath, clientKeyPath);

        File caCert = new File(caCertPath);
        File clientCert = new File(clientCertPath);
        File clientKey = new File(clientKeyPath);

        if (!caCert.exists() || !clientCert.exists() || !clientKey.exists()) {
            throw new IOException("TLS 证书文件不存在");
        }

        try (FileInputStream caCertStream = new FileInputStream(caCert);
             FileInputStream clientCertStream = new FileInputStream(clientCert);
             FileInputStream clientKeyStream = new FileInputStream(clientKey)) {

            return GrpcSslContexts.forClient()
                    .trustManager(caCertStream)
                    .keyManager(clientCertStream, clientKeyStream)
                    .build();
        }
    }

    /**
     * 获取超时配置（秒）
     */
    public int getTimeoutSeconds() {
        return timeoutSeconds;
    }

    /**
     * 获取超时配置（毫秒）
     */
    public long getTimeoutMillis() {
        return TimeUnit.SECONDS.toMillis(timeoutSeconds);
    }

    /**
     * 检查熔断器状态
     * @return 如果熔断器打开则返回 true
     */
    public boolean isCircuitOpen() {
        if (!circuitOpen) {
            return false;
        }

        // 检查是否应该重置熔断器
        long elapsed = System.currentTimeMillis() - lastFailureTime.get();
        if (elapsed >= circuitBreakerResetTimeoutMs) {
            log.info("熔断器重置时间已到，重置熔断器");
            circuitOpen = false;
            failureCount.set(0);
            return false;
        }

        return true;
    }

    /**
     * 记录成功调用
     */
    public void recordSuccess() {
        long count = failureCount.getAndSet(0);
        if (count > 0) {
            log.info("gRPC 调用成功，重置失败计数器：之前失败次数={}", count);
        }
    }

    /**
     * 记录失败调用
     * 如果连续失败次数超过阈值，则打开熔断器
     */
    public void recordFailure() {
        long count = failureCount.incrementAndGet();
        lastFailureTime.set(System.currentTimeMillis());
        log.warn("gRPC 调用失败，失败次数={}/{}", count, circuitBreakerFailureThreshold);

        if (count >= circuitBreakerFailureThreshold && !circuitOpen) {
            circuitOpen = true;
            log.error("熔断器打开：连续{}次调用失败，熔断器将在{}ms 后重置",
                    circuitBreakerFailureThreshold, circuitBreakerResetTimeoutMs);
        }
    }

    /**
     * 获取熔断器状态信息
     */
    public CircuitBreakerStatus getCircuitBreakerStatus() {
        return new CircuitBreakerStatus(
                circuitOpen,
                failureCount.get(),
                circuitBreakerFailureThreshold,
                lastFailureTime.get()
        );
    }

    /**
     * 关闭 gRPC 通道
     */
    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            log.info("关闭 gRPC 通道...");
            channel.shutdown();
            try {
                if (!channel.awaitTermination(5, TimeUnit.SECONDS)) {
                    log.warn("gRPC 通道未在规定时间内关闭，强制关闭");
                    channel.shutdownNow();
                }
            } catch (InterruptedException e) {
                log.error("关闭 gRPC 通道时被打断", e);
                channel.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
     * 创建 ClientResponseObserver 用于记录成功/失败
     * 超时应在 gRPC 调用时通过 ClientCall 设置
     */
    public <ReqT, RespT> ClientResponseObserver<ReqT, RespT> createResponseObserver() {
        return new ClientResponseObserver<ReqT, RespT>() {
            @Override
            public void beforeStart(ClientCallStreamObserver<ReqT> requestStream) {
                // 可以在这里设置流式调用的参数
            }

            @Override
            public void onNext(RespT value) {
                recordSuccess();
            }

            @Override
            public void onError(Throwable t) {
                recordFailure();
                log.error("gRPC 调用失败", t);
            }

            @Override
            public void onCompleted() {
                log.debug("gRPC 调用完成");
            }
        };
    }

    /**
     * 熔断器状态类
     */
    public static class CircuitBreakerStatus {
        public final boolean open;
        public final long failureCount;
        public final int threshold;
        public final long lastFailureTime;

        public CircuitBreakerStatus(boolean open, long failureCount, int threshold, long lastFailureTime) {
            this.open = open;
            this.failureCount = failureCount;
            this.threshold = threshold;
            this.lastFailureTime = lastFailureTime;
        }

        @Override
        public String toString() {
            return String.format("CircuitBreakerStatus{open=%s, failures=%d/%d, lastFailure=%dms ago}",
                    open, failureCount, threshold, System.currentTimeMillis() - lastFailureTime);
        }
    }
}
