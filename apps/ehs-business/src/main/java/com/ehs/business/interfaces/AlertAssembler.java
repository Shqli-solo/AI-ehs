package com.ehs.business.interfaces;

import com.ehs.business.domain.alert.Alert;
import com.ehs.business.domain.alert.Alert.AlertStatus;
import com.ehs.business.interfaces.dto.AlertResponse;

import java.time.format.DateTimeFormatter;
import java.util.Map;

/**
 * 告警 DTO 转换器 - Interface 层
 *
 * 负责领域对象与 DTO 之间的转换，以及前端/领域枚举的映射
 *
 * @author EHS Team
 * @since 2026-04-17
 */
public final class AlertAssembler {

    private AlertAssembler() {}

    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    /**
     * 前端 status 参数 → 领域枚举匹配
     */
    public static boolean statusMatches(Alert alert, String status) {
        return switch (status.toLowerCase()) {
            case "pending" -> alert.getStatus() == AlertStatus.PENDING;
            case "processing" -> alert.getStatus() == AlertStatus.ESCALATED;
            case "resolved" -> alert.getStatus() == AlertStatus.HANDLED;
            default -> true;
        };
    }

    /**
     * 前端整数告警级别 → 领域级别字符串
     */
    public static String levelFromInt(int level) {
        return switch (level) {
            case 1 -> "LOW";
            case 2 -> "MEDIUM";
            case 3 -> "HIGH";
            case 4 -> "CRITICAL";
            default -> "MEDIUM";
        };
    }

    /**
     * 领域对象 → 响应 DTO
     */
    public static AlertResponse toResponse(Alert alert) {
        return new AlertResponse(
            "ALT-" + alert.getId(),
            alert.getType(),
            alert.getLocation(),
            alert.getLevel().toLowerCase(),
            alert.getStatus().name().toLowerCase(),
            FORMATTER.format(alert.getCreatedAt()),
            alert.getDeviceId(),
            alert.getContent(),
            null
        );
    }

    /**
     * 领域对象 → 带 AI 分析的响应 DTO
     */
    public static AlertResponse toResponseWithAi(Alert alert, String aiAnalysis) {
        return new AlertResponse(
            "ALT-" + alert.getId(),
            alert.getType(),
            alert.getLocation(),
            alert.getLevel().toLowerCase(),
            alert.getStatus().name().toLowerCase(),
            FORMATTER.format(alert.getCreatedAt()),
            alert.getDeviceId(),
            alert.getContent(),
            aiAnalysis
        );
    }

    /**
     * 单次遍历计算各状态数量
     */
    public static Map<AlertStatus, Long> countByStatus(java.util.List<Alert> alerts) {
        return alerts.stream().collect(
            java.util.stream.Collectors.groupingBy(Alert::getStatus, java.util.stream.Collectors.counting())
        );
    }
}
