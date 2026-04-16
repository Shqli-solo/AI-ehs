package com.ehs.business.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import org.jose4j.jwt.JwtClaims;
import org.jose4j.jwt.NumericDate;

/**
 * JWT 认证过滤器 - 安全层
 *
 * 负责从 HTTP 请求中提取 JWT Token 并进行验证
 * 验证通过后将用户信息设置到 SecurityContext
 *
 * @author EHS Team
 * @since 2026-04-16
 */
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(JwtAuthFilter.class);
    private static final String AUTHORIZATION_HEADER = "Authorization";
    private static final String BEARER_PREFIX = "Bearer ";

    // JWT 密钥（生产环境应使用环境变量）
    private static final String JWT_SECRET = "ehs-jwt-secret-key-2026-production-change-me";
    private static final long JWT_EXPIRATION_MS = 1000 * 60 * 60 * 24; // 24 小时

    private final JwtTokenProvider tokenProvider;

    public JwtAuthFilter() {
        this.tokenProvider = new JwtTokenProvider();
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain
    ) throws ServletException, IOException {
        try {
            String jwt = getJwtFromRequest(request);

            if (StringUtils.hasText(jwt) && tokenProvider.validateToken(jwt)) {
                String username = tokenProvider.getUsernameFromToken(jwt);
                Map<String, Object> claims = tokenProvider.getClaimsFromToken(jwt);

                UserDetails userDetails = User.builder()
                    .username(username)
                    .password("")
                    .authorities(new ArrayList<>())
                    .build();

                UsernamePasswordAuthenticationToken authentication =
                    new UsernamePasswordAuthenticationToken(
                        userDetails,
                        null,
                        userDetails.getAuthorities()
                    );

                authentication.setDetails(
                    new WebAuthenticationDetailsSource().buildDetails(request)
                );

                SecurityContextHolder.getContext().setAuthentication(authentication);

                log.debug("用户认证成功：username={}", username);
            }
        } catch (Exception ex) {
            log.error("无法设置用户认证信息：{}", ex.getMessage());
        }

        filterChain.doFilter(request, response);
    }

    /**
     * 从请求头中提取 JWT Token
     */
    private String getJwtFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader(AUTHORIZATION_HEADER);

        if (StringUtils.hasText(bearerToken) && bearerToken.startsWith(BEARER_PREFIX)) {
            return bearerToken.substring(BEARER_PREFIX.length());
        }

        return null;
    }

    /**
     * JWT Token 提供者 - 内部类负责 Token 的生成和验证
     */
    @Component
    public static class JwtTokenProvider {

        /**
         * 生成 JWT Token
         */
        public String generateToken(String username, Map<String, Object> claims) {
            JwtClaims jwtClaims = new JwtClaims();
            jwtClaims.setSubject(username);
            jwtClaims.setIssuedAtToNow();
            jwtClaims.setExpirationTimeMinutesInTheFuture(24 * 60); // 24 小时
            jwtClaims.setClaim("claims", claims);
            return jwtClaims.toJson();
        }

        /**
         * 从 Token 中提取用户名
         */
        public String getUsernameFromToken(String token) {
            try {
                JwtClaims claims = JwtClaims.parse(token);
                return claims.getSubject();
            } catch (org.jose4j.jwt.consumer.InvalidJwtException | org.jose4j.jwt.MalformedClaimException e) {
                log.error("解析 Token 失败：{}", e.getMessage());
                return null;
            }
        }

        /**
         * 获取 Token 中的声明
         */
        public Map<String, Object> getClaimsFromToken(String token) {
            try {
                JwtClaims claims = JwtClaims.parse(token);
                Map<String, Object> result = new HashMap<>();
                claims.getClaimsMap().forEach((k, v) -> result.put(k, v));
                return result;
            } catch (org.jose4j.jwt.consumer.InvalidJwtException e) {
                log.error("解析 Token 声明失败：{}", e.getMessage());
                return new HashMap<>();
            }
        }

        /**
         * 验证 Token 是否有效
         */
        public boolean validateToken(String token) {
            try {
                JwtClaims claims = JwtClaims.parse(token);
                NumericDate expiration = claims.getExpirationTime();
                return expiration != null && expiration.getValue() > (System.currentTimeMillis() / 1000);
            } catch (org.jose4j.jwt.consumer.InvalidJwtException | org.jose4j.jwt.MalformedClaimException e) {
                log.error("Token 验证失败：{}", e.getMessage());
                return false;
            }
        }
    }
}
