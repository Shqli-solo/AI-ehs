package com.ehs.business;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * EHS 智能安保决策中台 - 业务服务启动类
 *
 * 基于 Spring Boot 3 + COLA 4.x 架构
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@SpringBootApplication
public class EhsBusinessApplication {

    public static void main(String[] args) {
        SpringApplication.run(EhsBusinessApplication.class, args);
    }
}
