package com.ehs.business;

import com.ehs.business.infrastructure.grpc.GrpcChannel;
import com.ehs.business.infrastructure.grpc.PythonAiClient;
import com.ehs.business.infrastructure.grpc.proto.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * PythonAiClient 单元测试
 *
 * Mock gRPC stub，测试成功路径和 fallback 降级逻辑
 */
class PythonAiClientTest {

    private GrpcChannel grpcChannel;
    private EhsAiServiceGrpc.EhsAiServiceBlockingStub stub;
    private PythonAiClient client;

    @BeforeEach
    void setUp() {
        grpcChannel = mock(GrpcChannel.class);
        stub = mock(EhsAiServiceGrpc.EhsAiServiceBlockingStub.class);
        when(grpcChannel.getStub()).thenReturn(stub);
        client = new PythonAiClient(grpcChannel);
    }

    // ============== classifyRisk ==============

    @Nested
    @DisplayName("classifyRisk - 风险分级")
    class ClassifyRiskTests {

        @Test
        @DisplayName("gRPC 成功 - 返回正确级别")
        void grpcSuccess() {
            RiskClassificationResponse grpcResponse = RiskClassificationResponse.newBuilder()
                .setRiskLevel(RiskLevel.RISK_LEVEL_HIGH)
                .build();
            when(stub.classifyRisk(any(RiskClassificationRequest.class))).thenReturn(grpcResponse);

            String result = client.classifyRisk("测试文本");

            assertEquals("HIGH", result);
        }

        @Test
        @DisplayName("gRPC 成功 - LOW 级别")
        void grpcSuccessLow() {
            RiskClassificationResponse grpcResponse = RiskClassificationResponse.newBuilder()
                .setRiskLevel(RiskLevel.RISK_LEVEL_LOW)
                .build();
            when(stub.classifyRisk(any(RiskClassificationRequest.class))).thenReturn(grpcResponse);

            assertEquals("LOW", client.classifyRisk("测试"));
        }

        @Test
        @DisplayName("gRPC 成功 - CRITICAL 级别")
        void grpcSuccessCritical() {
            RiskClassificationResponse grpcResponse = RiskClassificationResponse.newBuilder()
                .setRiskLevel(RiskLevel.RISK_LEVEL_CRITICAL)
                .build();
            when(stub.classifyRisk(any(RiskClassificationRequest.class))).thenReturn(grpcResponse);

            assertEquals("CRITICAL", client.classifyRisk("测试"));
        }

        @Test
        @DisplayName("gRPC 失败 - fallback: 长文本返回 HIGH")
        void fallbackLongText() {
            when(stub.classifyRisk(any(RiskClassificationRequest.class)))
                .thenThrow(new RuntimeException("gRPC 连接失败"));

            String result = client.classifyRisk("A".repeat(101));

            assertEquals("HIGH", result);
        }

        @Test
        @DisplayName("gRPC 失败 - fallback: 包含'危险'返回 CRITICAL")
        void fallbackDangerText() {
            when(stub.classifyRisk(any(RiskClassificationRequest.class)))
                .thenThrow(new RuntimeException("timeout"));

            assertEquals("CRITICAL", client.classifyRisk("危险品泄漏事故"));
        }

        @Test
        @DisplayName("gRPC 失败 - fallback: 包含'事故'返回 CRITICAL")
        void fallbackAccidentText() {
            when(stub.classifyRisk(any(RiskClassificationRequest.class)))
                .thenThrow(new RuntimeException("timeout"));

            assertEquals("CRITICAL", client.classifyRisk("发生事故"));
        }

        @Test
        @DisplayName("gRPC 失败 - fallback: 包含'警告'返回 MEDIUM")
        void fallbackWarningText() {
            when(stub.classifyRisk(any(RiskClassificationRequest.class)))
                .thenThrow(new RuntimeException("timeout"));

            assertEquals("MEDIUM", client.classifyRisk("系统警告"));
        }

        @Test
        @DisplayName("gRPC 失败 - fallback: 默认返回 LOW")
        void fallbackDefaultLow() {
            when(stub.classifyRisk(any(RiskClassificationRequest.class)))
                .thenThrow(new RuntimeException("timeout"));

            assertEquals("LOW", client.classifyRisk("普通文本"));
        }

        @Test
        @DisplayName("gRPC 失败 - 包含 '危险' 和 '事故'")
        void fallbackDangerAndAccident() {
            when(stub.classifyRisk(any(RiskClassificationRequest.class)))
                .thenThrow(new RuntimeException("timeout"));

            // '危险' 在 '事故' 之前检查，应返回 CRITICAL
            assertEquals("CRITICAL", client.classifyRisk("检测到危险，可能发生事故"));
        }
    }

    // ============== generateResponse ==============

    @Nested
    @DisplayName("generateResponse - 指令微调生成")
    class GenerateResponseTests {

        @Test
        @DisplayName("gRPC 成功 - 返回生成内容")
        void grpcSuccess() {
            ResponseGenerationResponse grpcResponse = ResponseGenerationResponse.newBuilder()
                .setResponse("AI 生成的回答")
                .build();
            when(stub.generateResponse(any(ResponseGenerationRequest.class))).thenReturn(grpcResponse);

            String result = client.generateResponse("上下文", "如何灭火？");

            assertEquals("AI 生成的回答", result);
        }

        @Test
        @DisplayName("gRPC 成功 - context 为 null")
        void grpcSuccessNullContext() {
            ResponseGenerationResponse grpcResponse = ResponseGenerationResponse.newBuilder()
                .setResponse("响应内容")
                .build();
            when(stub.generateResponse(any(ResponseGenerationRequest.class))).thenReturn(grpcResponse);

            String result = client.generateResponse(null, "问题");

            assertEquals("响应内容", result);
        }

        @Test
        @DisplayName("gRPC 失败 - fallback 返回默认响应")
        void fallback() {
            when(stub.generateResponse(any(ResponseGenerationRequest.class)))
                .thenThrow(new RuntimeException("服务不可用"));

            String result = client.generateResponse("上下文", "问题");

            assertEquals("基于上下文和查询生成的 AI 响应", result);
        }
    }

    // ============== analyzeAlert ==============

    @Nested
    @DisplayName("analyzeAlert - 告警分析")
    class AnalyzeAlertTests {

        @Test
        @DisplayName("gRPC 成功 - 返回分析结果")
        void grpcSuccess() {
            AlertAnalysisResponse grpcResponse = AlertAnalysisResponse.newBuilder()
                .setAnalysis("火源确认")
                .setSuggestedAction("立即疏散")
                .setRecommendedLevel(RiskLevel.RISK_LEVEL_CRITICAL)
                .setConfidence(0.95f)
                .build();
            when(stub.analyzeAlert(any(AlertAnalysisRequest.class))).thenReturn(grpcResponse);

            AlertAnalysisResponse result = client.analyzeAlert("烟雾报警", "A栋", "fire", 4);

            assertEquals("火源确认", result.getAnalysis());
            assertEquals("立即疏散", result.getSuggestedAction());
            assertEquals(RiskLevel.RISK_LEVEL_CRITICAL, result.getRecommendedLevel());
            assertEquals(0.95f, result.getConfidence());
        }

        @Test
        @DisplayName("gRPC 成功 - 不同告警类型映射")
        void grpcSuccessDifferentTypes() {
            AlertAnalysisResponse grpcResponse = AlertAnalysisResponse.newBuilder()
                .setAnalysis("ok")
                .setSuggestedAction("ok")
                .setRecommendedLevel(RiskLevel.RISK_LEVEL_LOW)
                .setConfidence(1.0f)
                .build();
            when(stub.analyzeAlert(any(AlertAnalysisRequest.class))).thenReturn(grpcResponse);

            // gas 类型
            client.analyzeAlert("内容", "B栋", "gas", 2);
            verify(stub).analyzeAlert(argThat(req ->
                req.getAlertType() == AlertType.ALERT_TYPE_GAS));
        }

        @Test
        @DisplayName("gRPC 失败 - fallback 分析")
        void fallback() {
            when(stub.analyzeAlert(any(AlertAnalysisRequest.class)))
                .thenThrow(new RuntimeException("超时"));

            AlertAnalysisResponse result = client.analyzeAlert("内容", "位置", "fire", 3);

            assertEquals("AI 服务暂不可用，使用默认分析", result.getAnalysis());
            assertEquals("请值班人员现场确认", result.getSuggestedAction());
            assertEquals(RiskLevel.RISK_LEVEL_MEDIUM, result.getRecommendedLevel());
            assertEquals(0.3f, result.getConfidence());
        }

        @Test
        @DisplayName("gRPC 失败 - location 为 null")
        void fallbackNullLocation() {
            when(stub.analyzeAlert(any(AlertAnalysisRequest.class)))
                .thenThrow(new RuntimeException("超时"));

            // 不应抛 NPE
            assertDoesNotThrow(() -> client.analyzeAlert("内容", null, "fire", 3));
        }
    }

    // ============== getTermEmbedding ==============

    @Nested
    @DisplayName("getTermEmbedding - 术语 Embedding")
    class GetTermEmbeddingTests {

        @Test
        @DisplayName("gRPC 成功 - 返回 embedding 数组")
        void grpcSuccess() {
            TermEmbeddingResponse grpcResponse = TermEmbeddingResponse.newBuilder()
                .addEmbedding(0.1)
                .addEmbedding(0.2)
                .addEmbedding(0.3)
                .build();
            when(stub.getTermEmbedding(any(TermEmbeddingRequest.class))).thenReturn(grpcResponse);

            double[] result = client.getTermEmbedding("fire_alarm");

            assertArrayEquals(new double[]{0.1, 0.2, 0.3}, result, 0.001);
        }

        @Test
        @DisplayName("gRPC 失败 - fallback 返回 768 维向量")
        void fallback() {
            when(stub.getTermEmbedding(any(TermEmbeddingRequest.class)))
                .thenThrow(new RuntimeException("服务不可用"));

            double[] result = client.getTermEmbedding("fire_alarm");

            assertNotNull(result);
            assertEquals(768, result.length);
        }
    }
}
