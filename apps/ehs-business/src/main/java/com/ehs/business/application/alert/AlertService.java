package com.ehs.business.application.alert;

import com.ehs.business.domain.alert.Alert;
import com.ehs.business.infrastructure.repository.AlertRepository;
import com.ehs.business.infrastructure.repository.JpaAlertEntity;
import com.ehs.business.infrastructure.grpc.PythonAiClient;
import com.ehs.business.infrastructure.grpc.proto.AlertAnalysisResponse;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * 告警服务 - 应用层
 *
 * 使用 Spring Data JPA 持久化告警到 PostgreSQL
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@Service
public class AlertService {

    private final AlertRepository alertRepository;
    private final PythonAiClient pythonAiClient;

    public AlertService(AlertRepository alertRepository, PythonAiClient pythonAiClient) {
        this.alertRepository = alertRepository;
        this.pythonAiClient = pythonAiClient;
    }

    /**
     * 创建告警并持久化到数据库
     */
    public Alert createAlert(String type, String level, String content) {
        JpaAlertEntity entity = new JpaAlertEntity();
        entity.setType(type);
        entity.setLevel(level);
        entity.setContent(content);
        entity.setStatus(JpaAlertEntity.AlertStatus.PENDING);

        JpaAlertEntity saved = alertRepository.save(entity);
        return toDomain(saved);
    }

    /**
     * 根据 ID 获取告警
     */
    public Optional<Alert> getAlertById(Long id) {
        return alertRepository.findById(id).map(this::toDomain);
    }

    /**
     * 获取所有告警
     */
    public List<Alert> getAllAlerts() {
        return alertRepository.findAll().stream()
            .map(this::toDomain)
            .collect(Collectors.toList());
    }

    /**
     * 根据级别获取告警
     */
    public List<Alert> getAlertsByLevel(String level) {
        return alertRepository.findByLevel(level).stream()
            .map(this::toDomain)
            .collect(Collectors.toList());
    }

    /**
     * 处理告警（标记为已处理）
     */
    public Optional<Alert> handleAlert(Long id, String handler) {
        return alertRepository.findById(id)
            .map(entity -> {
                entity.setHandledBy(handler);
                entity.setStatus(JpaAlertEntity.AlertStatus.HANDLED);
                return toDomain(alertRepository.save(entity));
            });
    }

    /**
     * 删除告警
     */
    public boolean deleteAlert(Long id) {
        if (alertRepository.existsById(id)) {
            alertRepository.deleteById(id);
            return true;
        }
        return false;
    }

    /**
     * 更新告警状态
     */
    public Optional<Alert> updateAlertStatus(Long id, JpaAlertEntity.AlertStatus status) {
        return alertRepository.findById(id)
            .map(entity -> {
                entity.setStatus(status);
                return toDomain(alertRepository.save(entity));
            });
    }

    /**
     * 按状态统计告警数量
     */
    public long countByStatus(JpaAlertEntity.AlertStatus status) {
        return alertRepository.countByStatus(status);
    }

    /**
     * 调用 AI 服务分析告警
     */
    public String analyzeAlertWithAi(Long alertId) {
        return getAlertById(alertId)
            .map(alert -> {
                int levelInt = levelToInt(alert.getLevel());
                AlertAnalysisResponse response = pythonAiClient.analyzeAlert(
                    alert.getContent(),
                    alert.getLocation(),
                    alert.getType(),
                    levelInt
                );
                return response.getAnalysis() + "\n建议: " + response.getSuggestedAction();
            })
            .orElse("告警不存在");
    }

    /**
     * 告警级别字符串转整数
     */
    private int levelToInt(String level) {
        return switch (level.toUpperCase()) {
            case "LOW" -> 1;
            case "MEDIUM" -> 2;
            case "HIGH" -> 3;
            case "CRITICAL" -> 4;
            default -> 0;
        };
    }

    /**
     * JPA Entity → Domain Alert
     */
    private Alert toDomain(JpaAlertEntity entity) {
        Alert alert = new Alert(
            entity.getId(),
            entity.getType(),
            entity.getLevel(),
            entity.getContent()
        );
        alert.setLocation(entity.getLocation() != null ? entity.getLocation() : "未知位置");
        alert.setDeviceId(entity.getDeviceId() != null ? entity.getDeviceId() : "");
        return alert;
    }
}
