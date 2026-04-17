package com.ehs.business.interfaces;

import com.ehs.business.application.alert.AlertService;
import com.ehs.business.domain.alert.Alert;
import com.ehs.business.domain.alert.Alert.AlertStatus;
import com.ehs.business.interfaces.dto.AlertRequest;
import com.ehs.business.interfaces.dto.AlertResponse;
import com.ehs.business.interfaces.dto.PageResponse;
import com.ehs.business.interfaces.dto.PageResponse.DataWrapper;
import org.springframework.web.bind.annotation.*;

import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 告警管理 REST Controller - Interface 层
 *
 * 提供告警查询、上报、统计等 REST API
 *
 * @author EHS Team
 * @since 2026-04-17
 */
@RestController
@RequestMapping("/api/alert")
public class AlertController {

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    /**
     * 获取告警列表（支持分页和过滤）
     * GET /api/alert/list?status=&riskLevel=&page=&pageSize=
     */
    @GetMapping("/list")
    public PageResponse<AlertResponse> getAlerts(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String riskLevel,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {

        List<Alert> allAlerts = alertService.getAllAlerts();

        // 按状态过滤
        List<Alert> filtered = allAlerts.stream()
            .filter(a -> status == null || status.isEmpty() || statusMatches(a, status))
            .filter(a -> riskLevel == null || riskLevel.isEmpty() ||
                         a.getLevel().equalsIgnoreCase(riskLevel))
            .collect(Collectors.toList());

        // 分页
        int start = Math.max(0, (page - 1) * pageSize);
        int end = Math.min(start + pageSize, filtered.size());
        List<Alert> pageAlerts = start < filtered.size()
            ? filtered.subList(start, end)
            : new ArrayList<>();

        List<AlertResponse> responses = pageAlerts.stream()
            .map(this::toResponse)
            .collect(Collectors.toList());

        long pending = filtered.stream().filter(a -> a.getStatus() == AlertStatus.PENDING).count();
        long processing = filtered.stream().filter(a -> a.getStatus() == AlertStatus.ESCALATED).count();
        long resolved = filtered.stream().filter(a -> a.getStatus() == AlertStatus.HANDLED).count();

        return PageResponse.ok(new DataWrapper<>(
            filtered.size(), pending, processing, resolved, responses
        ));
    }

    /**
     * 上报告警
     * POST /api/alert/report
     */
    @PostMapping("/report")
    public AlertResponse reportAlert(@RequestBody AlertRequest request) {
        String level = levelFromInt(request.getAlertLevel());
        Alert alert = alertService.createAlert(
            request.getAlertType(),
            level,
            request.getAlertContent()
        );

        String aiAnalysis = alertService.analyzeAlertWithAi(alert.getId());

        return toResponseWithAi(alert, aiAnalysis);
    }

    /**
     * 获取今日统计
     * GET /api/stats/today
     */
    @GetMapping("/stats/today")
    public PageResponse<AlertResponse> getTodayStats() {
        List<Alert> allAlerts = alertService.getAllAlerts();
        long pending = allAlerts.stream().filter(a -> a.getStatus() == AlertStatus.PENDING).count();
        long processing = allAlerts.stream().filter(a -> a.getStatus() == AlertStatus.ESCALATED).count();
        long resolved = allAlerts.stream().filter(a -> a.getStatus() == AlertStatus.HANDLED).count();

        return PageResponse.ok(new DataWrapper<>(
            allAlerts.size(), pending, processing, resolved, new ArrayList<>()
        ));
    }

    /**
     * 判断告警状态是否匹配前端传入的 status 参数
     * 前端使用 "pending"/"processing"/"resolved"，领域使用枚举
     */
    private boolean statusMatches(Alert alert, String status) {
        switch (status.toLowerCase()) {
            case "pending":
                return alert.getStatus() == AlertStatus.PENDING;
            case "processing":
                return alert.getStatus() == AlertStatus.ESCALATED;
            case "resolved":
                return alert.getStatus() == AlertStatus.HANDLED;
            default:
                return true;
        }
    }

    /**
     * 将前端传入的整数告警级别转换为领域级别字符串
     */
    private String levelFromInt(int level) {
        switch (level) {
            case 1: return "LOW";
            case 2: return "MEDIUM";
            case 3: return "HIGH";
            case 4: return "CRITICAL";
            default: return "MEDIUM";
        }
    }

    /**
     * 将领域对象转换为响应 DTO
     */
    private AlertResponse toResponse(Alert alert) {
        return new AlertResponse(
            "ALT-" + alert.getId(),
            alert.getType(),
            alert.getLocation(),
            alert.getLevel().toLowerCase(),
            alert.getStatus().name().toLowerCase(),
            DateTimeFormatter.ISO_LOCAL_DATE_TIME.format(alert.getCreatedAt()),
            alert.getDeviceId(),
            alert.getContent(),
            null
        );
    }

    /**
     * 将领域对象转换为带 AI 分析的响应 DTO
     */
    private AlertResponse toResponseWithAi(Alert alert, String aiAnalysis) {
        return new AlertResponse(
            "ALT-" + alert.getId(),
            alert.getType(),
            alert.getLocation(),
            alert.getLevel().toLowerCase(),
            alert.getStatus().name().toLowerCase(),
            DateTimeFormatter.ISO_LOCAL_DATE_TIME.format(alert.getCreatedAt()),
            alert.getDeviceId(),
            alert.getContent(),
            aiAnalysis
        );
    }
}
