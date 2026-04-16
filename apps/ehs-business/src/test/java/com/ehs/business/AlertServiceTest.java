package com.ehs.business;

import com.ehs.business.application.alert.AlertService;
import com.ehs.business.domain.alert.Alert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 告警服务测试
 *
 * 测试 AlertService 的业务逻辑
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@SpringBootTest
class AlertServiceTest {

    @Autowired
    private AlertService alertService;

    @BeforeEach
    void setUp() {
        // 清理之前的数据
        alertService.getAllAlerts().forEach(alert ->
            alertService.deleteAlert(alert.getId())
        );
    }

    @Test
    @DisplayName("创建告警 - 成功")
    void testCreateAlert() {
        // Given
        String type = "FIRE";
        String level = "HIGH";
        String content = "检测到火灾风险";

        // When
        Alert alert = alertService.createAlert(type, level, content);

        // Then
        assertNotNull(alert);
        assertNotNull(alert.getId());
        assertEquals(type, alert.getType());
        assertEquals(level, alert.getLevel());
        assertEquals(content, alert.getContent());
        assertEquals(Alert.AlertStatus.PENDING, alert.getStatus());
    }

    @Test
    @DisplayName("创建告警 - 验证告警级别")
    void testCreateAlertWithInvalidLevel() {
        // Given / When / Then
        assertThrows(IllegalArgumentException.class, () -> {
            alertService.createAlert("TEST", "INVALID_LEVEL", "内容");
        });
    }

    @Test
    @DisplayName("根据 ID 获取告警 - 成功")
    void testGetAlertById() {
        // Given
        Alert created = alertService.createAlert("SECURITY", "MEDIUM", "安全警告");

        // When
        Optional<Alert> found = alertService.getAlertById(created.getId());

        // Then
        assertTrue(found.isPresent());
        assertEquals(created.getId(), found.get().getId());
        assertEquals("安全警告", found.get().getContent());
    }

    @Test
    @DisplayName("根据 ID 获取告警 - 不存在")
    void testGetAlertByIdNotFound() {
        // When
        Optional<Alert> found = alertService.getAlertById(9999L);

        // Then
        assertFalse(found.isPresent());
    }

    @Test
    @DisplayName("获取所有告警")
    void testGetAllAlerts() {
        // Given
        alertService.createAlert("TYPE1", "LOW", "内容 1");
        alertService.createAlert("TYPE2", "HIGH", "内容 2");

        // When
        List<Alert> alerts = alertService.getAllAlerts();

        // Then
        assertTrue(alerts.size() >= 2);
    }

    @Test
    @DisplayName("根据级别获取告警")
    void testGetAlertsByLevel() {
        // Given
        alertService.createAlert("TYPE1", "HIGH", "高危告警 1");
        alertService.createAlert("TYPE2", "HIGH", "高危告警 2");
        alertService.createAlert("TYPE3", "LOW", "低危告警");

        // When
        List<Alert> highAlerts = alertService.getAlertsByLevel("HIGH");

        // Then
        assertEquals(2, highAlerts.size());
        highAlerts.forEach(alert -> assertEquals("HIGH", alert.getLevel()));
    }

    @Test
    @DisplayName("处理告警 - 成功")
    void testHandleAlert() {
        // Given
        Alert created = alertService.createAlert("BUG", "MEDIUM", "发现 Bug");
        String handler = "张三";

        // When
        Optional<Alert> handled = alertService.handleAlert(created.getId(), handler);

        // Then
        assertTrue(handled.isPresent());
        assertEquals(Alert.AlertStatus.HANDLED, handled.get().getStatus());
        assertEquals(handler, handled.get().getHandledBy());
        assertNotNull(handled.get().getHandledAt());
    }

    @Test
    @DisplayName("删除告警 - 成功")
    void testDeleteAlert() {
        // Given
        Alert created = alertService.createAlert("TEST", "LOW", "测试告警");

        // When
        boolean deleted = alertService.deleteAlert(created.getId());

        // Then
        assertTrue(deleted);
        assertFalse(alertService.getAlertById(created.getId()).isPresent());
    }

    @Test
    @DisplayName("AI 分析告警")
    void testAnalyzeAlertWithAi() {
        // Given
        Alert alert = alertService.createAlert("NETWORK", "CRITICAL", "网络异常");

        // When
        String analysis = alertService.analyzeAlertWithAi(alert.getId());

        // Then
        assertNotNull(analysis);
        assertTrue(analysis.contains("AI 分析"));
    }

    @Test
    @DisplayName("AI 分析不存在的告警")
    void testAnalyzeNonExistentAlert() {
        // When
        String analysis = alertService.analyzeAlertWithAi(9999L);

        // Then
        assertEquals("告警不存在", analysis);
    }
}
