package com.ehs.business.interfaces.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Size;

/**
 * 告警请求 DTO
 */
public class AlertRequest {
    @NotBlank(message = "设备 ID 不能为空")
    @Size(max = 50, message = "设备 ID 长度不能超过 50")
    private String deviceId;

    @NotBlank(message = "设备类型不能为空")
    @Size(max = 50, message = "设备类型长度不能超过 50")
    private String deviceType;

    @NotBlank(message = "告警类型不能为空")
    @Size(max = 50, message = "告警类型长度不能超过 50")
    private String alertType;

    @NotBlank(message = "告警内容不能为空")
    @Size(max = 2000, message = "告警内容长度不能超过 2000")
    private String alertContent;

    @Size(max = 200, message = "位置长度不能超过 200")
    private String location;

    @Min(value = 1, message = "告警级别必须在 1-4 之间")
    @Max(value = 4, message = "告警级别必须在 1-4 之间")
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
