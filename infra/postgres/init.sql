-- EHS 智能安保决策中台 - PostgreSQL 初始化脚本
-- 在 docker-entrypoint-initdb.d/ 中自动执行

-- ============================================
-- 启用 pgvector 扩展 (向量存储)
-- ============================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- Python AI 服务 Schema (ehs_ai)
-- ============================================
CREATE SCHEMA IF NOT EXISTS ehs_ai;

-- 告警表
CREATE TABLE IF NOT EXISTS ehs_ai.alerts (
    id SERIAL PRIMARY KEY,
    alert_id UUID UNIQUE NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    alert_content TEXT NOT NULL,
    location VARCHAR(200) NOT NULL,
    alert_level INTEGER NOT NULL CHECK (alert_level BETWEEN 1 AND 4),
    risk_level VARCHAR(20) NOT NULL DEFAULT 'unknown',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    plans JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 告警表索引
CREATE INDEX IF NOT EXISTS idx_alerts_status ON ehs_ai.alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_risk_level ON ehs_ai.alerts(risk_level);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON ehs_ai.alerts(created_at DESC);

-- 预案向量表 (pgvector)
CREATE TABLE IF NOT EXISTS ehs_ai.plans (
    id SERIAL PRIMARY KEY,
    plan_id UUID UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    event_type VARCHAR(50),
    risk_level VARCHAR(20),
    embedding vector(384),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 向量索引 (IVFFlat - 余弦相似度)
CREATE INDEX IF NOT EXISTS idx_plans_embedding
    ON ehs_ai.plans USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================
-- Java 业务服务 Schema (ehs_business)
-- ============================================
CREATE SCHEMA IF NOT EXISTS ehs_business;

-- 告警表 (JPA 管理)
CREATE TABLE IF NOT EXISTS ehs_business.alerts (
    id BIGSERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    location VARCHAR(200),
    device_id VARCHAR(50),
    handled_by VARCHAR(100),
    handled_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
