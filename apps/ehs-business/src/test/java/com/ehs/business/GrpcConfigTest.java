package com.ehs.business;

import com.ehs.business.config.GrpcConfig;
import com.ehs.business.config.GrpcConfig.CircuitBreakerStatus;
import io.grpc.stub.ClientCallStreamObserver;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * GrpcConfig 单元测试
 *
 * 测试熔断器逻辑、超时配置、响应 Observer
 * 不测试 @Bean 方法（需要真实网络）
 */
@ExtendWith(MockitoExtension.class)
class GrpcConfigTest {

    private GrpcConfig grpcConfig;

    @Mock
    private ClientCallStreamObserver<Object> requestStream;

    @BeforeEach
    void setUp() {
        grpcConfig = new GrpcConfig();
        // 设置默认配置值（通过反射设置，模拟 Spring @Value 注入效果）
        setField(grpcConfig, "timeoutSeconds", 120);
        setField(grpcConfig, "maxRetryAttempts", 3);
        setField(grpcConfig, "circuitBreakerFailureThreshold", 10);
        setField(grpcConfig, "circuitBreakerResetTimeoutMs", 60000);
    }

    // ============== 超时配置 ==============

    @Nested
    @DisplayName("超时配置")
    class TimeoutTests {

        @Test
        @DisplayName("getTimeoutSeconds 返回配置值")
        void getTimeoutSeconds() {
            assertEquals(120, grpcConfig.getTimeoutSeconds());
        }

        @Test
        @DisplayName("getTimeoutMillis 返回毫秒值")
        void getTimeoutMillis() {
            assertEquals(120_000L, grpcConfig.getTimeoutMillis());
        }
    }

    // ============== 熔断器 ==============

    @Nested
    @DisplayName("熔断器状态")
    class CircuitBreakerTests {

        @Test
        @DisplayName("初始状态 - 熔断器关闭")
        void initiallyClosed() {
            assertFalse(grpcConfig.isCircuitOpen());
        }

        @Test
        @DisplayName("recordSuccess 重置失败计数器")
        void recordSuccessResetsCounter() {
            // 先记录一些失败
            for (int i = 0; i < 5; i++) {
                grpcConfig.recordFailure();
            }
            // 然后记录成功
            grpcConfig.recordSuccess();
            // 熔断器仍应关闭
            assertFalse(grpcConfig.isCircuitOpen());
        }

        @Test
        @DisplayName("连续失败达到阈值 - 熔断器打开")
        void circuitOpensAtThreshold() {
            // 失败 9 次 - 阈值是 10
            for (int i = 0; i < 9; i++) {
                grpcConfig.recordFailure();
            }
            assertFalse(grpcConfig.isCircuitOpen());

            // 第 10 次失败 - 达到阈值
            grpcConfig.recordFailure();
            assertTrue(grpcConfig.isCircuitOpen());
        }

        @Test
        @DisplayName("熔断器打开后继续失败 - 保持打开")
        void staysOpenAfterOpening() {
            // 打开熔断器
            for (int i = 0; i < 10; i++) {
                grpcConfig.recordFailure();
            }
            assertTrue(grpcConfig.isCircuitOpen());

            // 继续失败
            grpcConfig.recordFailure();
            assertTrue(grpcConfig.isCircuitOpen());
        }

        @Test
        @DisplayName("get 熔断器状态信息")
        void getCircuitBreakerStatus() {
            grpcConfig.recordFailure();
            grpcConfig.recordFailure();

            CircuitBreakerStatus status = grpcConfig.getCircuitBreakerStatus();

            assertNotNull(status);
            assertEquals(2, status.failureCount);
            assertEquals(10, status.threshold);
            assertFalse(status.open);
        }

        @Test
        @DisplayName("CircuitBreakerStatus toString 包含关键字段")
        void circuitBreakerStatusToString() {
            CircuitBreakerStatus status = new CircuitBreakerStatus(true, 5, 10, System.currentTimeMillis());
            String str = status.toString();

            assertTrue(str.contains("open=true"));
            assertTrue(str.contains("failures=5/10"));
        }

        @Test
        @DisplayName("成功调用后失败计数重置")
        void successAfterFailuresResetsCount() {
            for (int i = 0; i < 5; i++) {
                grpcConfig.recordFailure();
            }
            grpcConfig.recordSuccess();

            CircuitBreakerStatus status = grpcConfig.getCircuitBreakerStatus();
            assertEquals(0, status.failureCount);
        }
    }

    // ============== ResponseObserver ==============

    @Nested
    @DisplayName("ResponseObserver")
    class ResponseObserverTests {

        @Test
        @DisplayName("onNext 记录成功")
        void onNextRecordsSuccess() {
            var observer = grpcConfig.<Object, Object>createResponseObserver();

            // 先记录失败
            grpcConfig.recordFailure();
            grpcConfig.recordFailure();

            // 然后 onNext
            observer.onNext("response");

            // 失败计数应被重置
            CircuitBreakerStatus status = grpcConfig.getCircuitBreakerStatus();
            assertEquals(0, status.failureCount);
        }

        @Test
        @DisplayName("onError 记录失败")
        void onErrorRecordsFailure() {
            var observer = grpcConfig.<Object, Object>createResponseObserver();

            observer.onError(new RuntimeException("错误"));

            CircuitBreakerStatus status = grpcConfig.getCircuitBreakerStatus();
            assertEquals(1, status.failureCount);
        }

        @Test
        @DisplayName("onCompleted 不改变状态")
        void onCompletedNoStateChange() {
            var observer = grpcConfig.<Object, Object>createResponseObserver();

            observer.onCompleted();

            // 状态不变
            CircuitBreakerStatus status = grpcConfig.getCircuitBreakerStatus();
            assertEquals(0, status.failureCount);
            assertFalse(status.open);
        }

        @Test
        @DisplayName("beforeStart 无副作用")
        void beforeStartNoSideEffect() {
            var observer = grpcConfig.<Object, Object>createResponseObserver();

            assertDoesNotThrow(() -> observer.beforeStart(requestStream));
        }

        @Test
        @DisplayName("多次 onError 累积失败")
        void multipleOnErrorsAccumulate() {
            var observer = grpcConfig.<Object, Object>createResponseObserver();

            observer.onError(new RuntimeException("err1"));
            observer.onError(new RuntimeException("err2"));
            observer.onError(new RuntimeException("err3"));

            CircuitBreakerStatus status = grpcConfig.getCircuitBreakerStatus();
            assertEquals(3, status.failureCount);
        }
    }

    // ============== Shutdown ==============

    @Nested
    @DisplayName("Shutdown")
    class ShutdownTests {

        @Test
        @DisplayName("shutdown 在 channel 为 null 时不抛异常")
        void shutdownWithNullChannel() {
            assertDoesNotThrow(() -> grpcConfig.shutdown());
        }
    }

    // Helper to set private fields via reflection
    @SuppressWarnings("unchecked")
    private <T> void setField(Object target, String fieldName, T value) {
        try {
            java.lang.reflect.Field field = GrpcConfig.class.getDeclaredField(fieldName);
            field.setAccessible(true);
            field.set(target, value);
        } catch (Exception e) {
            throw new RuntimeException("Failed to set field: " + fieldName, e);
        }
    }
}
