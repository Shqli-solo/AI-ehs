package com.ehs.business.interfaces;

import com.ehs.business.application.alert.AlertService;
import com.ehs.business.domain.alert.Alert;
import com.ehs.business.domain.alert.Alert.AlertStatus;
import com.ehs.business.interfaces.dto.AlertRequest;
import com.ehs.business.interfaces.dto.AlertResponse;
import com.ehs.business.interfaces.dto.PageResponse;
import com.ehs.business.interfaces.dto.PageResponse.DataWrapper;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
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
     *
     * 注意：当前使用内存数据分页，生产环境应改为数据库分页
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
            .filter(a -> status == null || status.isEmpty() || AlertAssembler.statusMatches(a, status))
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
            .map(AlertAssembler::toResponse)
            .collect(Collectors.toList());

        // 单次遍历统计各状态数量
        Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(filtered);

        return PageResponse.ok(new DataWrapper<>(
            filtered.size(),
            counts.getOrDefault(AlertStatus.PENDING, 0L),
            counts.getOrDefault(AlertStatus.ESCALATED, 0L),
            counts.getOrDefault(AlertStatus.HANDLED, 0L),
            responses
        ));
    }

    /**
     * 上报告警
     * POST /api/alert/report
     */
    @PostMapping("/report")
    public AlertResponse reportAlert(@Valid @RequestBody AlertRequest request) {
        String level = AlertAssembler.levelFromInt(request.getAlertLevel());
        Alert alert = alertService.createAlert(
            request.getAlertType(),
            level,
            request.getAlertContent()
        );
        alert.setLocation(request.getLocation() != null ? request.getLocation() : "未知位置");
        alert.setDeviceId(request.getDeviceId() != null ? request.getDeviceId() : "");

        String aiAnalysis = alertService.analyzeAlertWithAi(alert.getId());

        return AlertAssembler.toResponseWithAi(alert, aiAnalysis);
    }

    /**
     * 获取今日统计
     * GET /api/stats/today
     */
    @GetMapping("/stats/today")
    public PageResponse<AlertResponse> getTodayStats() {
        List<Alert> allAlerts = alertService.getAllAlerts();
        Map<AlertStatus, Long> counts = AlertAssembler.countByStatus(allAlerts);

        return PageResponse.ok(new DataWrapper<>(
            allAlerts.size(),
            counts.getOrDefault(AlertStatus.PENDING, 0L),
            counts.getOrDefault(AlertStatus.ESCALATED, 0L),
            counts.getOrDefault(AlertStatus.HANDLED, 0L),
            new ArrayList<>()
        ));
    }
}
