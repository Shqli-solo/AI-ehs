package com.ehs.business.domain.alert;

import java.time.LocalDateTime;

/**
 * 告警领域对象 - 领域层
 *
 * EHS 告警实体，包含告警的核心业务逻辑
 *
 * @author EHS Team
 * @since 2026-04-16
 */
public class Alert {

    private final Long id;
    private final String type;
    private final String level;
    private final String content;
    private final LocalDateTime createdAt;
    private String location = "未知位置";
    private String deviceId = "";

    private String handledBy;
    private LocalDateTime handledAt;
    private AlertStatus status;

    /**
     * 告警状态枚举
     */
    public enum AlertStatus {
        PENDING,    // 待处理
        HANDLED,    // 已处理
        ESCALATED   // 已升级
    }

    public Alert(Long id, String type, String level, String content) {
        this.id = id;
        this.type = type;
        this.level = validateLevel(level);
        this.content = content;
        this.createdAt = LocalDateTime.now();
        this.status = AlertStatus.PENDING;
    }

    /**
     * 验证告警级别
     */
    private String validateLevel(String level) {
        if (level == null || level.trim().isEmpty()) {
            throw new IllegalArgumentException("告警级别不能为空");
        }
        String upperLevel = level.toUpperCase();
        if (!isValidLevel(upperLevel)) {
            throw new IllegalArgumentException("无效的告警级别：" + level);
        }
        return upperLevel;
    }

    /**
     * 判断是否为有效的告警级别
     */
    private boolean isValidLevel(String level) {
        return "LOW".equals(level) || "MEDIUM".equals(level) ||
               "HIGH".equals(level) || "CRITICAL".equals(level);
    }

    /**
     * 标记告警为已处理
     */
    public void markAsHandled(String handler) {
        if (this.status != AlertStatus.PENDING) {
            throw new IllegalStateException("只有待处理的告警才能被标记为已处理");
        }
        this.handledBy = handler;
        this.handledAt = LocalDateTime.now();
        this.status = AlertStatus.HANDLED;
    }

    /**
     * 升级告警
     */
    public void escalate() {
        if (this.status == AlertStatus.HANDLED) {
            throw new IllegalStateException("已处理的告警不能升级");
        }
        this.status = AlertStatus.ESCALATED;
    }

    // Getters
    public Long getId() { return id; }
    public String getType() { return type; }
    public String getLevel() { return level; }
    public String getContent() { return content; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public String getHandledBy() { return handledBy; }
    public LocalDateTime getHandledAt() { return handledAt; }
    public AlertStatus getStatus() { return status; }
    public String getLocation() { return location; }
    public String getDeviceId() { return deviceId; }

    public void setLocation(String location) { this.location = location; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }

    @Override
    public String toString() {
        return "Alert{" +
            "id=" + id +
            ", type='" + type + '\'' +
            ", level='" + level + '\'' +
            ", status=" + status +
            ", createdAt=" + createdAt +
            '}';
    }
}
