package com.ehs.business.application.alert;

import com.ehs.business.domain.alert.Alert;
import com.ehs.business.infrastructure.grpc.PythonAiClient;
import com.ehs.business.infrastructure.grpc.proto.AlertAnalysisResponse;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 告警服务 - 应用层
 *
 * 负责告警业务的编排和协调
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@Service
public class AlertService {

    // 内存存储（演示用，生产环境应使用数据库）
    private final ConcurrentHashMap<Long, Alert> alertStore = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);
    private final PythonAiClient pythonAiClient;

    public AlertService(PythonAiClient pythonAiClient) {
        this.pythonAiClient = pythonAiClient;
    }

    /**
     * 创建告警
     */
    public Alert createAlert(String type, String level, String content) {
        Alert alert = new Alert(
            idGenerator.getAndIncrement(),
            type,
            level,
            content
        );
        alertStore.put(alert.getId(), alert);
        return alert;
    }

    /**
     * 根据 ID 获取告警
     */
    public Optional<Alert> getAlertById(Long id) {
        return Optional.ofNullable(alertStore.get(id));
    }

    /**
     * 获取所有告警
     */
    public List<Alert> getAllAlerts() {
        return new ArrayList<>(alertStore.values());
    }

    /**
     * 根据级别获取告警
     */
    public List<Alert> getAlertsByLevel(String level) {
        return alertStore.values().stream()
            .filter(alert -> level.equalsIgnoreCase(alert.getLevel()))
            .toList();
    }

    /**
     * 处理告警（标记为已处理）
     */
    public Optional<Alert> handleAlert(Long id, String handler) {
        return Optional.ofNullable(alertStore.get(id))
            .map(alert -> {
                alert.markAsHandled(handler);
                return alert;
            });
    }

    /**
     * 删除告警
     */
    public boolean deleteAlert(Long id) {
        return alertStore.remove(id) != null;
    }

    /**
     * 调用 AI 服务分析告警
     */
    public String analyzeAlertWithAi(Long alertId) {
        return getAlertById(alertId)
            .map(alert -> {
                AlertAnalysisResponse response = pythonAiClient.analyzeAlert(
                    alert.getContent(),
                    alert.getLocation(),
                    alert.getType(),
                    Integer.parseInt(alert.getLevel())
                );
                return response.getAnalysis() + "\n建议: " + response.getSuggestedAction();
            })
            .orElse("告警不存在");
    }
}
