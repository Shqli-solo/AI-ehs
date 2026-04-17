package com.ehs.business.infrastructure.grpc;

import com.ehs.business.infrastructure.grpc.proto.EhsAiServiceGrpc;
import com.ehs.business.infrastructure.grpc.proto.HealthCheckRequest;
import com.ehs.business.infrastructure.grpc.proto.HealthCheckResponse;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

/**
 * gRPC 通道管理类
 *
 * 负责与 Python AI 服务的 gRPC 连接生命周期
 *
 * @author EHS Team
 * @since 2026-04-17
 */
@Component
public class GrpcChannel {

    private static final Logger log = LoggerFactory.getLogger(GrpcChannel.class);

    @Value("${grpc.python-ai.host:localhost}")
    private String host;

    @Value("${grpc.python-ai.port:50051}")
    private int port;

    @Value("${grpc.python-ai.enabled:true}")
    private boolean enabled;

    private ManagedChannel channel;
    private EhsAiServiceGrpc.EhsAiServiceBlockingStub stub;

    @PostConstruct
    public void init() {
        if (!enabled) {
            log.info("gRPC Python AI 服务已禁用");
            return;
        }
        log.info("初始化 gRPC 通道: {}:{}", host, port);
        channel = ManagedChannelBuilder.forAddress(host, port)
            .usePlaintext()
            .build();
        stub = EhsAiServiceGrpc.newBlockingStub(channel);
        log.info("gRPC 通道初始化完成");
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            log.info("关闭 gRPC 通道");
            channel.shutdown();
        }
    }

    public EhsAiServiceGrpc.EhsAiServiceBlockingStub getStub() {
        return stub;
    }

    public boolean isHealthy() {
        if (!enabled || stub == null) {
            return false;
        }
        try {
            HealthCheckResponse response = stub.healthCheck(
                HealthCheckRequest.newBuilder().setService("ehs-ai").build()
            );
            return response.getHealthy();
        } catch (Exception e) {
            log.debug("gRPC 健康检查失败: {}", e.getMessage());
            return false;
        }
    }
}
