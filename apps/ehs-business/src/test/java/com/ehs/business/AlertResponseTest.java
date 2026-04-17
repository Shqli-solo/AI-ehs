package com.ehs.business;

import com.ehs.business.interfaces.dto.AlertResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * AlertResponse DTO 单元测试
 */
class AlertResponseTest {

    @Test
    @DisplayName("无参构造函数 - 所有字段为 null")
    void noArgsConstructor() {
        AlertResponse response = new AlertResponse();
        assertNull(response.getId());
        assertNull(response.getType());
        assertNull(response.getLocation());
        assertNull(response.getRiskLevel());
        assertNull(response.getStatus());
        assertNull(response.getTime());
        assertNull(response.getDeviceId());
        assertNull(response.getContent());
        assertNull(response.getAiAnalysis());
    }

    @Test
    @DisplayName("全参构造函数 - 所有字段正确赋值")
    void allArgsConstructor() {
        AlertResponse response = new AlertResponse(
            "ALT-1", "fire", "A栋3楼", "high",
            "pending", "2026-04-17T10:00:00", "DEV-001",
            "烟感报警", "AI 分析结果"
        );

        assertEquals("ALT-1", response.getId());
        assertEquals("fire", response.getType());
        assertEquals("A栋3楼", response.getLocation());
        assertEquals("high", response.getRiskLevel());
        assertEquals("pending", response.getStatus());
        assertEquals("2026-04-17T10:00:00", response.getTime());
        assertEquals("DEV-001", response.getDeviceId());
        assertEquals("烟感报警", response.getContent());
        assertEquals("AI 分析结果", response.getAiAnalysis());
    }

    @Test
    @DisplayName("全参构造函数 - aiAnalysis 为 null")
    void allArgsConstructorNullAiAnalysis() {
        AlertResponse response = new AlertResponse(
            "ALT-1", "fire", "A栋", "high",
            "pending", "2026-04-17T10:00:00", "DEV-001",
            "烟感报警", null
        );

        assertNull(response.getAiAnalysis());
        assertEquals("ALT-1", response.getId());
    }

    @Test
    @DisplayName("setter 正常工作")
    void settersWork() {
        AlertResponse response = new AlertResponse();
        response.setId("ALT-99");
        response.setType("gas");
        response.setLocation("B车间");
        response.setRiskLevel("critical");
        response.setStatus("escalated");
        response.setTime("2026-04-17T12:00:00");
        response.setDeviceId("DEV-099");
        response.setContent("气体泄漏");
        response.setAiAnalysis("紧急处理");

        assertEquals("ALT-99", response.getId());
        assertEquals("gas", response.getType());
        assertEquals("B车间", response.getLocation());
        assertEquals("critical", response.getRiskLevel());
        assertEquals("escalated", response.getStatus());
        assertEquals("2026-04-17T12:00:00", response.getTime());
        assertEquals("DEV-099", response.getDeviceId());
        assertEquals("气体泄漏", response.getContent());
        assertEquals("紧急处理", response.getAiAnalysis());
    }
}
