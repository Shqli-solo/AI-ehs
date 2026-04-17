package com.ehs.business;

import com.ehs.business.domain.alert.Alert;
import com.ehs.business.domain.alert.Alert.AlertStatus;
import com.ehs.business.interfaces.AlertAssembler;
import com.ehs.business.interfaces.dto.AlertResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * AlertAssembler 独立单元测试
 *
 * 测试覆盖：
 * - statusMatches 各分支（pending/processing/resolved/default）
 * - levelFromInt 各值（1-4 + 默认值）
 * - toResponse / toResponseWithAi 字段映射
 * - countByStatus 统计
 */
class AlertAssemblerTest {

    // ============== statusMatches ==============

    @Nested
    @DisplayName("statusMatches - 状态匹配")
    class StatusMatchesTests {

        @Test
        @DisplayName("pending 匹配 PENDING 状态")
        void pendingMatchesPending() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            assertTrue(AlertAssembler.statusMatches(alert, "pending"));
        }

        @Test
        @DisplayName("pending 不匹配 HANDLED 状态")
        void pendingNotMatchHandled() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.markAsHandled("张三");
            assertFalse(AlertAssembler.statusMatches(alert, "pending"));
        }

        @Test
        @DisplayName("processing 匹配 ESCALATED 状态")
        void processingMatchesEscalated() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.escalate();
            assertTrue(AlertAssembler.statusMatches(alert, "processing"));
        }

        @Test
        @DisplayName("processing 不匹配 PENDING 状态")
        void processingNotMatchPending() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            assertFalse(AlertAssembler.statusMatches(alert, "processing"));
        }

        @Test
        @DisplayName("resolved 匹配 HANDLED 状态")
        void resolvedMatchesHandled() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.markAsHandled("张三");
            assertTrue(AlertAssembler.statusMatches(alert, "resolved"));
        }

        @Test
        @DisplayName("resolved 不匹配 PENDING 状态")
        void resolvedNotMatchPending() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            assertFalse(AlertAssembler.statusMatches(alert, "resolved"));
        }

        @Test
        @DisplayName("未知状态返回 true（默认分支）")
        void unknownStatusReturnsTrue() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            assertTrue(AlertAssembler.statusMatches(alert, "unknown_status"));
        }

        @Test
        @DisplayName("状态参数大小写不敏感")
        void caseInsensitiveStatus() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            assertTrue(AlertAssembler.statusMatches(alert, "PENDING"));
            assertTrue(AlertAssembler.statusMatches(alert, "Pending"));
        }
    }

    // ============== levelFromInt ==============

    @Nested
    @DisplayName("levelFromInt - 级别映射")
    class LevelFromIntTests {

        @Test
        @DisplayName("1 -> LOW")
        void level1() {
            assertEquals("LOW", AlertAssembler.levelFromInt(1));
        }

        @Test
        @DisplayName("2 -> MEDIUM")
        void level2() {
            assertEquals("MEDIUM", AlertAssembler.levelFromInt(2));
        }

        @Test
        @DisplayName("3 -> HIGH")
        void level3() {
            assertEquals("HIGH", AlertAssembler.levelFromInt(3));
        }

        @Test
        @DisplayName("4 -> CRITICAL")
        void level4() {
            assertEquals("CRITICAL", AlertAssembler.levelFromInt(4));
        }

        @Test
        @DisplayName("0 -> MEDIUM（默认值）")
        void level0Default() {
            assertEquals("MEDIUM", AlertAssembler.levelFromInt(0));
        }

        @Test
        @DisplayName("5 -> MEDIUM（默认值）")
        void level5Default() {
            assertEquals("MEDIUM", AlertAssembler.levelFromInt(5));
        }

        @Test
        @DisplayName("负数 -> MEDIUM（默认值）")
        void negativeLevelDefault() {
            assertEquals("MEDIUM", AlertAssembler.levelFromInt(-1));
        }
    }

    // ============== toResponse ==============

    @Nested
    @DisplayName("toResponse - 领域转响应 DTO")
    class ToResponseTests {

        @Test
        @DisplayName("ID 格式为 ALT-{id}")
        void idFormat() {
            Alert alert = new Alert(42L, "fire", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("ALT-42", response.getId());
        }

        @Test
        @DisplayName("type 字段正确映射")
        void typeMapping() {
            Alert alert = new Alert(1L, "gas_leak", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("gas_leak", response.getType());
        }

        @Test
        @DisplayName("location 字段正确映射")
        void locationMapping() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.setLocation("A栋3楼");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("A栋3楼", response.getLocation());
        }

        @Test
        @DisplayName("riskLevel 转为小写")
        void riskLevelLowerCase() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("high", response.getRiskLevel());
        }

        @Test
        @DisplayName("status 转为小写")
        void statusLowerCase() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.escalate();
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("escalated", response.getStatus());
        }

        @Test
        @DisplayName("deviceId 字段正确映射")
        void deviceIdMapping() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.setDeviceId("DEV-001");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("DEV-001", response.getDeviceId());
        }

        @Test
        @DisplayName("content 字段正确映射")
        void contentMapping() {
            Alert alert = new Alert(1L, "fire", "HIGH", "烟感报警");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertEquals("烟感报警", response.getContent());
        }

        @Test
        @DisplayName("aiAnalysis 为 null")
        void aiAnalysisNull() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertNull(response.getAiAnalysis());
        }

        @Test
        @DisplayName("time 字段为 ISO 格式字符串")
        void timeIsoFormat() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponse(alert);
            assertNotNull(response.getTime());
            // Should be a valid ISO local date-time string
            assertDoesNotThrow(() -> java.time.LocalDateTime.parse(response.getTime()));
        }
    }

    // ============== toResponseWithAi ==============

    @Nested
    @DisplayName("toResponseWithAi - 带 AI 分析的转换")
    class ToResponseWithAiTests {

        @Test
        @DisplayName("aiAnalysis 字段正确设置")
        void aiAnalysisSet() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponseWithAi(alert, "AI 分析结果");
            assertEquals("AI 分析结果", response.getAiAnalysis());
        }

        @Test
        @DisplayName("其他字段与 toResponse 一致")
        void otherFieldsSame() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            alert.setLocation("A栋");
            alert.setDeviceId("DEV-001");

            AlertResponse response = AlertAssembler.toResponseWithAi(alert, "分析");

            assertEquals("ALT-1", response.getId());
            assertEquals("fire", response.getType());
            assertEquals("A栋", response.getLocation());
            assertEquals("high", response.getRiskLevel());
            assertEquals("DEV-001", response.getDeviceId());
        }

        @Test
        @DisplayName("aiAnalysis 为 null 时正确处理")
        void aiAnalysisNull() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            AlertResponse response = AlertAssembler.toResponseWithAi(alert, null);
            assertNull(response.getAiAnalysis());
        }
    }

    // ============== countByStatus ==============

    @Nested
    @DisplayName("countByStatus - 按状态统计")
    class CountByStatusTests {

        @Test
        @DisplayName("空列表返回空 Map")
        void emptyList() {
            Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(List.of());
            assertTrue(counts.isEmpty());
        }

        @Test
        @DisplayName("单元素列表统计正确")
        void singleElement() {
            Alert alert = new Alert(1L, "fire", "HIGH", "test");
            Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(List.of(alert));
            assertEquals(1L, counts.get(AlertStatus.PENDING));
        }

        @Test
        @DisplayName("多状态混合统计正确")
        void mixedStatuses() {
            Alert a1 = new Alert(1L, "fire", "HIGH", "test");
            Alert a2 = new Alert(2L, "gas", "MEDIUM", "test");
            a2.markAsHandled("张三");
            Alert a3 = new Alert(3L, "intrusion", "LOW", "test");
            a3.escalate();
            Alert a4 = new Alert(4L, "temp", "HIGH", "test");
            a4.escalate();

            Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(List.of(a1, a2, a3, a4));

            assertEquals(1L, counts.get(AlertStatus.PENDING));
            assertEquals(1L, counts.get(AlertStatus.HANDLED));
            assertEquals(2L, counts.get(AlertStatus.ESCALATED));
            assertEquals(3, counts.size());
        }

        @Test
        @DisplayName("全部相同状态统计正确")
        void allSameStatus() {
            Alert a1 = new Alert(1L, "fire", "HIGH", "test");
            Alert a2 = new Alert(2L, "gas", "MEDIUM", "test");
            Alert a3 = new Alert(3L, "intrusion", "LOW", "test");

            Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(List.of(a1, a2, a3));

            assertEquals(3L, counts.get(AlertStatus.PENDING));
            assertEquals(1, counts.size());
        }
    }
}
