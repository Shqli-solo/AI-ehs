package com.ehs.business;

import com.ehs.business.interfaces.dto.AlertRequest;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

/**
 * AlertRequest DTO 验证测试
 *
 * 使用 Hibernate Validator 手动验证 Bean Validation 注解
 */
class AlertRequestTest {

    private static Validator validator;

    @BeforeAll
    static void setUp() {
        ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
        validator = factory.getValidator();
    }

    @Test
    @DisplayName("完整有效的请求 - 无验证错误")
    void validRequest() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setLocation("A栋3楼");
        request.setAlertLevel(3);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertTrue(violations.isEmpty());
    }

    @Test
    @DisplayName("deviceId 为空 - 验证失败")
    void deviceIdBlank() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(2);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
        assertTrue(hasMessageContaining(violations, "设备 ID"));
    }

    @Test
    @DisplayName("deviceId 超过 50 字符 - 验证失败")
    void deviceIdTooLong() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("A".repeat(51));
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(2);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
    }

    @Test
    @DisplayName("deviceType 为空 - 验证失败")
    void deviceTypeBlank() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("   ");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(2);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
        assertTrue(hasMessageContaining(violations, "设备类型"));
    }

    @Test
    @DisplayName("alertType 为空 - 验证失败")
    void alertTypeBlank() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType(null);
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(2);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
        assertTrue(hasMessageContaining(violations, "告警类型"));
    }

    @Test
    @DisplayName("alertContent 为空 - 验证失败")
    void alertContentBlank() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("");
        request.setAlertLevel(2);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
        assertTrue(hasMessageContaining(violations, "告警内容"));
    }

    @Test
    @DisplayName("alertContent 超过 2000 字符 - 验证失败")
    void alertContentTooLong() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("A".repeat(2001));
        request.setAlertLevel(2);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
    }

    @Test
    @DisplayName("alertLevel 为 0 - 验证失败")
    void alertLevelTooLow() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(0);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
        assertTrue(hasMessageContaining(violations, "告警级别"));
    }

    @Test
    @DisplayName("alertLevel 为 5 - 验证失败")
    void alertLevelTooHigh() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(5);

        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
        assertTrue(hasMessageContaining(violations, "告警级别"));
    }

    @Test
    @DisplayName("alertLevel 边界值 - 1 和 4 均有效")
    void alertLevelBoundaryValid() {
        AlertRequest req1 = createValidRequest();
        req1.setAlertLevel(1);
        assertTrue(validator.validate(req1).isEmpty());

        AlertRequest req4 = createValidRequest();
        req4.setAlertLevel(4);
        assertTrue(validator.validate(req4).isEmpty());
    }

    @Test
    @DisplayName("location 为可选字段 - null 有效")
    void locationOptional() {
        AlertRequest request = createValidRequest();
        request.setLocation(null);
        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertTrue(violations.isEmpty());
    }

    @Test
    @DisplayName("location 超过 200 字符 - 验证失败")
    void locationTooLong() {
        AlertRequest request = createValidRequest();
        request.setLocation("A".repeat(201));
        Set<ConstraintViolation<AlertRequest>> violations = validator.validate(request);
        assertFalse(violations.isEmpty());
    }

    @Test
    @DisplayName("getter/setter 正常工作")
    void gettersAndSetters() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("烟雾报警");
        request.setLocation("A栋");
        request.setAlertLevel(3);

        assertEquals("DEV-001", request.getDeviceId());
        assertEquals("smoke_detector", request.getDeviceType());
        assertEquals("FIRE", request.getAlertType());
        assertEquals("烟雾报警", request.getAlertContent());
        assertEquals("A栋", request.getLocation());
        assertEquals(3, request.getAlertLevel());
    }

    private AlertRequest createValidRequest() {
        AlertRequest request = new AlertRequest();
        request.setDeviceId("DEV-001");
        request.setDeviceType("smoke_detector");
        request.setAlertType("FIRE");
        request.setAlertContent("检测到烟雾");
        request.setAlertLevel(2);
        return request;
    }

    private boolean hasMessageContaining(Set<ConstraintViolation<AlertRequest>> violations, String keyword) {
        return violations.stream()
            .anyMatch(v -> v.getMessage().contains(keyword));
    }
}
