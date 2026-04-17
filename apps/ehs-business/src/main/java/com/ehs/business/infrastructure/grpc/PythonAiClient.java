package com.ehs.business.infrastructure.grpc;

import com.ehs.business.infrastructure.grpc.proto.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

/**
 * Python AI 服务 gRPC 客户端 - 基础设施层
 *
 * 通过 gRPC 调用 Python AI 服务的 AI 能力：
 * - 风险分级
 * - 告警分析
 * - 指令微调生成
 * - 术语 Embedding
 *
 * 调用失败时自动降级为模拟实现
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@Component
public class PythonAiClient {

    private static final Logger log = LoggerFactory.getLogger(PythonAiClient.class);

    private final GrpcChannel grpcChannel;

    public PythonAiClient(GrpcChannel grpcChannel) {
        this.grpcChannel = grpcChannel;
    }

    /**
     * 风险分级 - 调用 Python AI 服务
     */
    public String classifyRisk(String text) {
        log.info("调用 Python AI 服务进行风险分级：text={}", text);

        RiskClassificationRequest request = RiskClassificationRequest.newBuilder()
            .setText(text)
            .setRequestId(java.util.UUID.randomUUID().toString())
            .setTimestamp(System.currentTimeMillis())
            .build();

        try {
            RiskClassificationResponse response = grpcChannel.getStub().classifyRisk(request);
            return riskLevelToString(response.getRiskLevel());
        } catch (Exception e) {
            log.warn("gRPC 风险分级调用失败，使用 fallback: {}", e.getMessage());
            return simulateRiskClassification(text);
        }
    }

    /**
     * 指令微调生成 - 调用 Python AI 服务
     */
    public String generateResponse(String context, String query) {
        log.info("调用 Python AI 服务生成响应：query={}", query);

        ResponseGenerationRequest.Builder builder = ResponseGenerationRequest.newBuilder()
            .setQuery(query)
            .setRequestId(java.util.UUID.randomUUID().toString())
            .setTimestamp(System.currentTimeMillis())
            .setMaxTokens(512)
            .setTemperature(0.7f);
        if (context != null && !context.isEmpty()) {
            builder.setContext(context);
        }

        try {
            ResponseGenerationResponse response = grpcChannel.getStub().generateResponse(builder.build());
            return response.getResponse();
        } catch (Exception e) {
            log.warn("gRPC 响应生成调用失败，使用 fallback: {}", e.getMessage());
            return simulateResponseGeneration(context, query);
        }
    }

    /**
     * 告警分析 - 调用 Python AI 服务
     */
    public AlertAnalysisResponse analyzeAlert(
            String content, String location, String alertType, int alertLevel) {

        log.info("调用 Python AI 服务分析告警：type={}, level={}, location={}", alertType, alertLevel, location);

        AlertAnalysisRequest request = AlertAnalysisRequest.newBuilder()
            .setAlertType(parseAlertType(alertType))
            .setAlertLevel(parseRiskLevel(alertLevel))
            .setContent(content)
            .setLocation(location != null ? location : "")
            .setRequestId(java.util.UUID.randomUUID().toString())
            .setTimestamp(System.currentTimeMillis())
            .build();

        try {
            return grpcChannel.getStub().analyzeAlert(request);
        } catch (Exception e) {
            log.warn("gRPC 告警分析调用失败，使用 fallback: {}", e.getMessage());
            return createFallbackAlertAnalysis(alertType, content);
        }
    }

    /**
     * 术语 Embedding - 调用 Python AI 服务
     */
    public double[] getTermEmbedding(String term) {
        log.info("调用 Python AI 服务获取术语 Embedding：term={}", term);

        TermEmbeddingRequest request = TermEmbeddingRequest.newBuilder()
            .setTerm(term)
            .setRequestId(java.util.UUID.randomUUID().toString())
            .setTimestamp(System.currentTimeMillis())
            .build();

        try {
            TermEmbeddingResponse response = grpcChannel.getStub().getTermEmbedding(request);
            return response.getEmbeddingList().stream().mapToDouble(Double::doubleValue).toArray();
        } catch (Exception e) {
            log.warn("gRPC Embedding 调用失败，使用 fallback: {}", e.getMessage());
            return simulateEmbedding(term);
        }
    }

    // ==================== 解析辅助方法 ====================

    private AlertType parseAlertType(String type) {
        return switch (type.toLowerCase()) {
            case "fire", "烟火告警" -> AlertType.ALERT_TYPE_FIRE;
            case "gas", "气体泄漏" -> AlertType.ALERT_TYPE_GAS;
            case "intrusion", "入侵检测" -> AlertType.ALERT_TYPE_INTRUSION;
            case "temperature", "温度异常" -> AlertType.ALERT_TYPE_TEMPERATURE;
            default -> AlertType.ALERT_TYPE_OTHER;
        };
    }

    private RiskLevel parseRiskLevel(int level) {
        return switch (level) {
            case 1 -> RiskLevel.RISK_LEVEL_LOW;
            case 2 -> RiskLevel.RISK_LEVEL_MEDIUM;
            case 3 -> RiskLevel.RISK_LEVEL_HIGH;
            case 4 -> RiskLevel.RISK_LEVEL_CRITICAL;
            default -> RiskLevel.RISK_LEVEL_UNSPECIFIED;
        };
    }

    private String riskLevelToString(RiskLevel level) {
        return switch (level) {
            case RISK_LEVEL_LOW -> "LOW";
            case RISK_LEVEL_MEDIUM -> "MEDIUM";
            case RISK_LEVEL_HIGH -> "HIGH";
            case RISK_LEVEL_CRITICAL -> "CRITICAL";
            default -> "LOW";
        };
    }

    private AlertAnalysisResponse createFallbackAlertAnalysis(String alertType, String content) {
        return AlertAnalysisResponse.newBuilder()
            .setAnalysis("AI 服务暂不可用，使用默认分析")
            .setSuggestedAction("请值班人员现场确认")
            .setRecommendedLevel(RiskLevel.RISK_LEVEL_MEDIUM)
            .setConfidence(0.3f)
            .build();
    }

    // ==================== 模拟实现（Fallback）=====================

    private String simulateRiskClassification(String text) {
        if (text.length() > 100) return "HIGH";
        if (text.contains("危险") || text.contains("事故")) return "CRITICAL";
        if (text.contains("警告")) return "MEDIUM";
        return "LOW";
    }

    private String simulateResponseGeneration(String context, String query) {
        return "基于上下文和查询生成的 AI 响应";
    }

    private double[] simulateEmbedding(String term) {
        return new double[768];
    }
}
