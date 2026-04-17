package com.ehs.business;

import com.ehs.business.domain.alert.Alert;
import com.ehs.business.domain.alert.Alert.AlertStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Alert 领域对象单元测试
 *
 * 测试覆盖：
 * - 构造与字段初始化
 * - 告警级别校验
 * - 状态转换（markAsHandled, escalate）
 * - 边界场景（重复处理、非法状态转换）
 * - toString 输出
 */
class AlertTest {

    // ============== 构造函数与初始化 ==============

    @Test
    @DisplayName("构造函数 - 正确初始化字段")
    void testConstructorInitialization() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");

        assertEquals(1L, alert.getId());
        assertEquals("fire", alert.getType());
        assertEquals("HIGH", alert.getLevel());
        assertEquals("烟感报警", alert.getContent());
        assertEquals(AlertStatus.PENDING, alert.getStatus());
        assertNotNull(alert.getCreatedAt());
    }

    @Test
    @DisplayName("构造函数 - 告警级别自动转大写")
    void testConstructorUpperCasesLevel() {
        Alert alert = new Alert(1L, "fire", "high", "测试");
        assertEquals("HIGH", alert.getLevel());
    }

    @Nested
    @DisplayName("告警级别校验")
    class LevelValidation {

        @Test
        @DisplayName("有效级别 - LOW")
        void validLevelLow() {
            Alert alert = new Alert(1L, "TEST", "low", "内容");
            assertEquals("LOW", alert.getLevel());
        }

        @Test
        @DisplayName("有效级别 - MEDIUM")
        void validLevelMedium() {
            Alert alert = new Alert(1L, "TEST", "MEDIUM", "内容");
            assertEquals("MEDIUM", alert.getLevel());
        }

        @Test
        @DisplayName("有效级别 - HIGH")
        void validLevelHigh() {
            Alert alert = new Alert(1L, "TEST", "high", "内容");
            assertEquals("HIGH", alert.getLevel());
        }

        @Test
        @DisplayName("有效级别 - CRITICAL")
        void validLevelCritical() {
            Alert alert = new Alert(1L, "TEST", "Critical", "内容");
            assertEquals("CRITICAL", alert.getLevel());
        }

        @Test
        @DisplayName("无效级别 - 空字符串")
        void invalidLevelEmpty() {
            assertThrows(IllegalArgumentException.class, () ->
                new Alert(1L, "TEST", "", "内容")
            );
        }

        @Test
        @DisplayName("无效级别 - null")
        void invalidLevelNull() {
            assertThrows(IllegalArgumentException.class, () ->
                new Alert(1L, "TEST", null, "内容")
            );
        }

        @Test
        @DisplayName("无效级别 - 未知值")
        void invalidLevelUnknown() {
            assertThrows(IllegalArgumentException.class, () ->
                new Alert(1L, "TEST", "URGENT", "内容")
            );
        }

        @Test
        @DisplayName("无效级别 - 纯空格")
        void invalidLevelWhitespace() {
            assertThrows(IllegalArgumentException.class, () ->
                new Alert(1L, "TEST", "   ", "内容")
            );
        }
    }

    // ============== markAsHandled ==============

    @Test
    @DisplayName("标记已处理 - PENDING 状态下成功")
    void testMarkAsHandledFromPending() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.markAsHandled("张三");

        assertEquals(AlertStatus.HANDLED, alert.getStatus());
        assertEquals("张三", alert.getHandledBy());
        assertNotNull(alert.getHandledAt());
    }

    @Test
    @DisplayName("标记已处理 - HANDLED 状态不允许重复处理")
    void testMarkAsHandledAlreadyHandled() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.markAsHandled("张三");

        assertThrows(IllegalStateException.class, () ->
            alert.markAsHandled("李四")
        );
    }

    @Test
    @DisplayName("标记已处理 - ESCALATED 状态不允许处理")
    void testMarkAsHandledFromEscalated() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.escalate();

        assertThrows(IllegalStateException.class, () ->
            alert.markAsHandled("张三")
        );
    }

    // ============== escalate ==============

    @Test
    @DisplayName("升级 - PENDING 状态下成功")
    void testEscalateFromPending() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.escalate();

        assertEquals(AlertStatus.ESCALATED, alert.getStatus());
    }

    @Test
    @DisplayName("升级 - HANDLED 状态不允许升级")
    void testEscalateFromHandled() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.markAsHandled("张三");

        assertThrows(IllegalStateException.class, () ->
            alert.escalate()
        );
    }

    @Test
    @DisplayName("升级 - ESCALATED 状态幂等（不抛出异常）")
    void testEscalateAlreadyEscalated() {
        Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
        alert.escalate();

        // 已升级的告警再次升级应幂等（不抛异常，状态仍为 ESCALATED）
        assertDoesNotThrow(() -> alert.escalate());
        assertEquals(AlertStatus.ESCALATED, alert.getStatus());
    }

    // ============== Location and DeviceId ==============

    @Test
    @DisplayName("设置位置 - 默认值为未知位置")
    void testDefaultLocation() {
        Alert alert = new Alert(1L, "fire", "HIGH", "内容");
        assertEquals("未知位置", alert.getLocation());
    }

    @Test
    @DisplayName("设置位置 - 可以修改")
    void testSetLocation() {
        Alert alert = new Alert(1L, "fire", "HIGH", "内容");
        alert.setLocation("A栋3楼");
        assertEquals("A栋3楼", alert.getLocation());
    }

    @Test
    @DisplayName("设置设备ID - 默认值为空字符串")
    void testDefaultDeviceId() {
        Alert alert = new Alert(1L, "fire", "HIGH", "内容");
        assertEquals("", alert.getDeviceId());
    }

    @Test
    @DisplayName("设置设备ID - 可以修改")
    void testSetDeviceId() {
        Alert alert = new Alert(1L, "fire", "HIGH", "内容");
        alert.setDeviceId("DEV-001");
        assertEquals("DEV-001", alert.getDeviceId());
    }

    // ============== toString ==============

    @Test
    @DisplayName("toString - 包含关键字段")
    void testToStringContainsKeyFields() {
        Alert alert = new Alert(42L, "fire", "HIGH", "烟感报警");
        String str = alert.toString();

        assertTrue(str.contains("42"));
        assertTrue(str.contains("fire"));
        assertTrue(str.contains("HIGH"));
        assertTrue(str.contains("PENDING"));
    }

    @Test
    @DisplayName("toString - 格式正确")
    void testToStringFormat() {
        Alert alert = new Alert(1L, "gas", "LOW", "气体泄漏");
        String str = alert.toString();

        assertTrue(str.startsWith("Alert{"));
        assertTrue(str.endsWith("}"));
        assertTrue(str.contains("id=1"));
        assertTrue(str.contains("type='gas'"));
    }
}
