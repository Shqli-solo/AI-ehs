package com.ehs.business.infrastructure.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 告警 Spring Data JPA Repository
 */
@Repository
public interface AlertRepository extends JpaRepository<JpaAlertEntity, Long>,
                                          JpaSpecificationExecutor<JpaAlertEntity> {
    List<JpaAlertEntity> findByLevel(String level);
    long countByStatus(JpaAlertEntity.AlertStatus status);
}
