package com.ehs.business.interfaces.dto;

/**
 * 告警请求 DTO
 */
public class AlertRequest {
    private String deviceId;
    private String deviceType;
    private String alertType;
    private String alertContent;
    private String location;
    private int alertLevel;

    public String getDeviceId() { return deviceId; }
    public void setDeviceId(String deviceId) { this.deviceId = deviceId; }
    public String getDeviceType() { return deviceType; }
    public void setDeviceType(String deviceType) { this.deviceType = deviceType; }
    public String getAlertType() { return alertType; }
    public void setAlertType(String alertType) { this.alertType = alertType; }
    public String getAlertContent() { return alertContent; }
    public void setAlertContent(String alertContent) { this.alertContent = alertContent; }
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    public int getAlertLevel() { return alertLevel; }
    public void setAlertLevel(int alertLevel) { this.alertLevel = alertLevel; }
}
