package com.ehs.business.interfaces.dto;

import java.time.LocalDateTime;

/**
 * 告警响应 DTO
 */
public class AlertResponse {
    private String id;
    private String type;
    private String location;
    private String riskLevel;
    private String status;
    private String time;
    private String deviceId;
    private String content;
    private String aiAnalysis;

    public AlertResponse() {}

    public AlertResponse(String id, String type, String location, String riskLevel,
                         String status, String time, String deviceId, String content,
                         String aiAnalysis) {
        this.id = id;
        this.type = type;
        this.location = location;
        this.riskLevel = riskLevel;
        this.status = status;
        this.time = time;
        this.deviceId = deviceId;
        this.content = content;
        this.aiAnalysis = aiAnalysis;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getTime() { return time; }
    public void setTime(String time) { this.time = time; }
    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getAiAnalysis() { return aiAnalysis; }
    public void setAiAnalysis(String aiAnalysis) { this.aiAnalysis = aiAnalysis; }
}
