package com.ehs.business;

import com.ehs.business.application.alert.AlertService;
import com.ehs.business.domain.alert.Alert;
import com.ehs.business.domain.alert.Alert.AlertStatus;
import com.ehs.business.interfaces.AlertAssembler;
import com.ehs.business.interfaces.AlertController;
import com.ehs.business.interfaces.dto.AlertResponse;
import com.ehs.business.interfaces.dto.PageResponse;
import com.ehs.business.interfaces.dto.PageResponse.DataWrapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * AlertController 纯单元测试
 *
 * 不依赖 Spring Boot test 框架，直接使用 Mockito Mock
 * 测试 Controller 的业务逻辑
 */
class AlertControllerTest {

    private AlertService alertService;
    private AlertController controller;

    @BeforeEach
    void setUp() {
        alertService = Mockito.mock(AlertService.class);
        controller = new AlertController(alertService);
    }

    @SuppressWarnings("unchecked")
    private DataWrapper<AlertResponse> getData(PageResponse<?> response) {
        return (DataWrapper<AlertResponse>) response.getData();
    }

    @Test
    @DisplayName("获取告警列表 - 成功返回分页数据")
    void testGetAlerts() {
        // Given
        Alert alert1 = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert1.setLocation("A栋3楼");
        alert1.setDeviceId("DEV-001");

        Alert alert2 = new Alert(2L, "gas_leak", "MEDIUM", "气体泄漏");
        alert2.setLocation("B车间");
        alert2.setDeviceId("DEV-002");

        when(alertService.getAllAlerts()).thenReturn(List.of(alert1, alert2));

        // When
        PageResponse<?> response = controller.getAlerts(null, null, 1, 10);

        // Then
        assertTrue(response.isSuccess());
        @SuppressWarnings("unchecked")
        DataWrapper<AlertResponse> data = (DataWrapper<AlertResponse>) response.getData();
        assertEquals(2, data.getTotal());
        assertEquals(2, data.getAlerts().size());
        assertEquals("fire", data.getAlerts().get(0).getType());
        assertEquals("gas_leak", data.getAlerts().get(1).getType());
    }

    @Test
    @DisplayName("获取告警列表 - 按风险等级过滤")
    void testGetAlertsFilterByRiskLevel() {
        Alert alert1 = new Alert(1L, "fire", "HIGH", "烟感报警");
        Alert alert2 = new Alert(2L, "gas_leak", "LOW", "普通事件");

        when(alertService.getAllAlerts()).thenReturn(List.of(alert1, alert2));

        PageResponse<?> response = controller.getAlerts(null, "HIGH", 1, 10);

        assertTrue(response.isSuccess());
        @SuppressWarnings("unchecked")
        DataWrapper<AlertResponse> data = (DataWrapper<AlertResponse>) response.getData();
        assertEquals(1, data.getTotal());
        assertEquals("high", data.getAlerts().get(0).getRiskLevel());
    }

    @Test
    @DisplayName("获取告警列表 - 按状态过滤")
    void testGetAlertsFilterByStatus() {
        Alert alert1 = new Alert(1L, "fire", "HIGH", "烟感报警");
        Alert alert2 = new Alert(2L, "gas_leak", "MEDIUM", "气体泄漏");
        alert2.markAsHandled("张三");

        when(alertService.getAllAlerts()).thenReturn(List.of(alert1, alert2));

        PageResponse<?> response = controller.getAlerts("resolved", null, 1, 10);

        assertTrue(response.isSuccess());
        @SuppressWarnings("unchecked")
        DataWrapper<AlertResponse> data = (DataWrapper<AlertResponse>) response.getData();
        assertEquals(1, data.getTotal());
        assertEquals("gas_leak", data.getAlerts().get(0).getType());
    }

    @Test
    @DisplayName("获取告警列表 - 分页截断")
    void testGetAlertsPagination() {
        when(alertService.getAllAlerts()).thenReturn(List.of(
            new Alert(1L, "fire", "HIGH", "告警1"),
            new Alert(2L, "gas", "MEDIUM", "告警2"),
            new Alert(3L, "intrusion", "LOW", "告警3")
        ));

        PageResponse<?> response = controller.getAlerts(null, null, 1, 2);
        DataWrapper<AlertResponse> data = getData(response);

        assertEquals(3, data.getTotal());
        assertEquals(2, data.getAlerts().size());
    }

    @Test
    @DisplayName("获取告警列表 - 空列表")
    void testGetEmptyAlerts() {
        when(alertService.getAllAlerts()).thenReturn(List.of());

        PageResponse<?> response = controller.getAlerts(null, null, 1, 10);

        assertTrue(response.isSuccess());
        DataWrapper<AlertResponse> data = getData(response);
        assertEquals(0, data.getTotal());
        assertTrue(data.getAlerts().isEmpty());
    }

    @Test
    @DisplayName("获取告警列表 - 状态统计正确")
    void testGetAlertsStatusCounts() {
        Alert alert1 = new Alert(1L, "fire", "HIGH", "告警1");
        Alert alert2 = new Alert(2L, "gas", "MEDIUM", "告警2");
        alert2.markAsHandled("张三");
        Alert alert3 = new Alert(3L, "intrusion", "LOW", "告警3");
        alert3.escalate();

        when(alertService.getAllAlerts()).thenReturn(List.of(alert1, alert2, alert3));

        PageResponse<?> response = controller.getAlerts(null, null, 1, 10);
        DataWrapper<AlertResponse> data = getData(response);

        assertEquals(3, data.getTotal());
        assertEquals(1, data.getPending());
        assertEquals(1, data.getProcessing());  // ESCALATED
        assertEquals(1, data.getResolved());     // HANDLED
    }

    @Test
    @DisplayName("获取今日统计 - 返回总数和各状态数量")
    void testGetTodayStats() {
        Alert alert1 = new Alert(1L, "fire", "HIGH", "告警1");
        Alert alert2 = new Alert(2L, "gas", "MEDIUM", "告警2");
        Alert alert3 = new Alert(3L, "intrusion", "LOW", "告警3");

        when(alertService.getAllAlerts()).thenReturn(List.of(alert1, alert2, alert3));

        PageResponse<?> response = controller.getTodayStats();
        DataWrapper<AlertResponse> data = getData(response);

        assertTrue(response.isSuccess());
        assertEquals(3, data.getTotal());
        assertEquals(3, data.getPending());
        assertEquals(0, data.getProcessing());
        assertEquals(0, data.getResolved());
    }

    @Test
    @DisplayName("AlertAssembler - 级别映射正确")
    void testLevelMapping() {
        assertEquals("HIGH", AlertAssembler.levelFromInt(3));
        assertEquals("CRITICAL", AlertAssembler.levelFromInt(4));
        assertEquals("MEDIUM", AlertAssembler.levelFromInt(2));
        assertEquals("LOW", AlertAssembler.levelFromInt(1));
        assertEquals("MEDIUM", AlertAssembler.levelFromInt(0));  // 默认值
    }

    @Test
    @DisplayName("AlertAssembler - 状态匹配正确")
    void testStatusMatching() {
        Alert alert = new Alert(1L, "fire", "HIGH", "告警");

        assertTrue(AlertAssembler.statusMatches(alert, "pending"));
        assertFalse(AlertAssembler.statusMatches(alert, "resolved"));

        alert.markAsHandled("test");
        assertTrue(AlertAssembler.statusMatches(alert, "resolved"));
        assertFalse(AlertAssembler.statusMatches(alert, "pending"));
    }

    @Test
    @DisplayName("AlertAssembler - 统计各状态数量")
    void testCountByStatus() {
        Alert alert1 = new Alert(1L, "fire", "HIGH", "告警1");
        Alert alert2 = new Alert(2L, "gas", "MEDIUM", "告警2");
        alert2.markAsHandled("张三");
        Alert alert3 = new Alert(3L, "intrusion", "LOW", "告警3");
        alert3.escalate();

        Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(List.of(alert1, alert2, alert3));

        assertEquals(1L, counts.get(AlertStatus.PENDING));
        assertEquals(1L, counts.get(AlertStatus.HANDLED));
        assertEquals(1L, counts.get(AlertStatus.ESCALATED));
    }

    @Test
    @DisplayName("AlertAssembler - 告警转响应 DTO")
    void testToResponse() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.setLocation("A栋3楼");
        alert.setDeviceId("DEV-001");

        var response = AlertAssembler.toResponse(alert);

        assertEquals("ALT-1", response.getId());
        assertEquals("fire", response.getType());
        assertEquals("A栋3楼", response.getLocation());
        assertEquals("high", response.getRiskLevel());
        assertEquals("pending", response.getStatus());
        assertEquals("DEV-001", response.getDeviceId());
        assertEquals("烟感报警", response.getContent());
    }

    @Test
    @DisplayName("AlertAssembler - 告警转响应 DTO（带 AI 分析）")
    void testToResponseWithAi() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.setLocation("A栋3楼");

        var response = AlertAssembler.toResponseWithAi(alert, "AI 分析结果");

        assertEquals("AI 分析结果", response.getAiAnalysis());
        assertEquals("ALT-1", response.getId());
    }
}
