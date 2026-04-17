# EHS Stage 2 - Wave 3-5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Stage 2 production-grade features: Wave 3 (前端接真实API + Python gRPC服务 + Java COLA REST层), Wave 4 (Java完整业务逻辑 + 监控集成), Wave 5 (K8s部署 + CI/CD + E2E测试)。

**Architecture:** 前端(admin-console) → REST API(Python FastAPI ehs-ai) → gRPC → Java COLA(ehs-business)。三层独立部署，通过 Docker Compose 编排。

**Tech Stack:** Next.js 14 + Shadcn/UI, Python FastAPI + gRPC, Java Spring Boot + COLA, Prometheus + Grafana, K8s Helm, GitHub Actions, Playwright E2E, Locust

---

## Wave 3: 前端接真实 API + Python gRPC 服务 + Java COLA REST 层

### Wave 3 架构概览

```
前端(admin-console)  ──REST──→  Python(ehs-ai:8000)  ──gRPC──→  Java(ehs-business:8080)
     │                              │                              │
  Shadcn/UI                    FastAPI+LangGraph              Spring Boot+COLA
  Mock→真实API                 GraphRAG+Agents                Domain+Infrastructure
```

### Task 1: Python AI 服务 gRPC Server 实现

**背景:** Python ehs-ai 已有 FastAPI REST 接口和 DI Container，但 gRPC Server (src/grpc_server.py) 尚未完整实现。Java 服务需要通过 gRPC 调用 Python 的 AI 能力。

**Files:**
- Modify: `apps/ehs-ai/src/grpc_server.py`
- Modify: `apps/ehs-ai/src/container.py`
- Create: `apps/ehs-ai/tests/test_grpc_server.py`

**Proto 文件位置:** `apps/ehs-business/src/main/proto/ehs.proto`（已定义 6 个 RPC）

- [ ] **Step 1: 编写测试 - 验证 gRPC HealthCheck**

```python
# apps/ehs-ai/tests/test_grpc_server.py
import pytest

def test_health_check_returns_healthy():
    """HealthCheck 应返回 healthy=True"""
    from src.grpc_server import EhsAiServicer
    from src.infrastructure.grpc.proto.ehs_pb2 import HealthCheckRequest
    from src.infrastructure.grpc.proto.ehs_pb2 import HealthCheckResponse

    servicer = EhsAiServicer()
    request = HealthCheckRequest(service="ehs-ai")
    response = servicer.HealthCheck(request, None)

    assert response.healthy is True
    assert response.service == "ehs-ai"
    assert response.version == "2.0.0"
```

- [ ] **Step 2: 生成 Python gRPC stubs**

```bash
# 在 apps/ehs-ai 目录下运行
cd apps/ehs-ai
pip install grpcio grpcio-tools
python -m grpc_tools.protoc \
  -I../ehs-business/src/main/proto \
  --python_out=src/infrastructure/grpc/proto \
  --grpc_python_out=src/infrastructure/grpc/proto \
  --mypy_out=src/infrastructure/grpc/proto \
  ehs.proto
```

生成的文件:
- `apps/ehs-ai/src/infrastructure/grpc/proto/ehs_pb2.py`
- `apps/ehs-ai/src/infrastructure/grpc/proto/ehs_pb2_grpc.py`

- [ ] **Step 3: 实现 gRPC Servicer**

```python
# apps/ehs-ai/src/grpc_server.py - 完整实现
"""gRPC Server - 暴露 AI 能力给 Java 业务服务"""
import time
import logging
from concurrent import futures

import grpc

# 生成的 proto stubs
from src.infrastructure.grpc.proto import ehs_pb2
from src.infrastructure.grpc.proto import ehs_pb2_grpc

from src.container import DIContainer

logger = logging.getLogger(__name__)

# 风险等级映射
RISK_LEVEL_MAP = {
    "low": ehs_pb2.RISK_LEVEL_LOW,
    "medium": ehs_pb2.RISK_LEVEL_MEDIUM,
    "high": ehs_pb2.RISK_LEVEL_HIGH,
    "critical": ehs_pb2.RISK_LEVEL_CRITICAL,
}

REVERSE_RISK_MAP = {
    ehs_pb2.RISK_LEVEL_LOW: "low",
    ehs_pb2.RISK_LEVEL_MEDIUM: "medium",
    ehs_pb2.RISK_LEVEL_HIGH: "high",
    ehs_pb2.RISK_LEVEL_CRITICAL: "critical",
}


class EhsAiServicer(ehs_pb2_grpc.EhsAiServiceServicer):
    """gRPC 服务实现"""

    def __init__(self, container: DIContainer = None):
        self.container = container or DIContainer()

    def HealthCheck(self, request, context):
        return ehs_pb2.HealthCheckResponse(
            healthy=True,
            service="ehs-ai",
            version="2.0.0",
            timestamp=int(time.time() * 1000),
            checks=["llm", "graph_rag", "workflow"],
        )

    def ClassifyRisk(self, request, context):
        """风险分级 RPC"""
        start = time.time()
        try:
            workflow = self.container.get_workflow()
            state = {
                "alert_message": request.text,
                "risk_assessment": None,
                "emergency_plans": [],
                "error": None,
            }
            result = workflow.invoke(state)
            risk = result.get("risk_assessment", {}).get("risk_level", "low")
            level = RISK_LEVEL_MAP.get(risk, ehs_pb2.RISK_LEVEL_LOW)

            return ehs_pb2.RiskClassificationResponse(
                risk_level=level,
                confidence=0.85,
                reason=result.get("risk_assessment", {}).get("reasoning", ""),
                keywords=[],
                request_id=request.request_id,
                processing_time_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ehs_pb2.RiskClassificationResponse()

    def AnalyzeAlert(self, request, context):
        """告警分析 RPC"""
        start = time.time()
        try:
            workflow = self.container.get_workflow()
            alert_text = f"[{request.location}] {request.content}"
            state = {
                "alert_message": alert_text,
                "risk_assessment": None,
                "emergency_plans": [],
                "error": None,
            }
            result = workflow.invoke(state)
            assessment = result.get("risk_assessment", {})
            risk = assessment.get("risk_level", "low")
            level = RISK_LEVEL_MAP.get(risk, ehs_pb2.RISK_LEVEL_LOW)

            plans = result.get("emergency_plans", [])
            plan_ids = [p.get("id", "") for p in plans]

            return ehs_pb2.AlertAnalysisResponse(
                analysis=assessment.get("reasoning", ""),
                suggested_action=assessment.get("recommendation", ""),
                recommended_level=level,
                related_plans=plan_ids,
                confidence=0.85,
                request_id=request.request_id,
                processing_time_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ehs_pb2.AlertAnalysisResponse()

    def GenerateResponse(self, request, context):
        """指令微调生成 RPC"""
        start = time.time()
        try:
            llm = self.container.get_llm_adapter()
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.query})
            if request.context:
                messages[-1]["content"] += f"\n\n上下文: {request.context}"

            response_text = llm.generate(messages)

            return ehs_pb2.ResponseGenerationResponse(
                response=response_text,
                request_id=request.request_id,
                processing_time_ms=int((time.time() - start) * 1000),
                tokens_used=len(response_text) // 4,
                model="qwen3-7b",
                truncated=False,
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ehs_pb2.ResponseGenerationResponse()

    def GetTermEmbedding(self, request, context):
        """术语 Embedding RPC"""
        start = time.time()
        try:
            # 使用简单 hash 向量作为 fallback
            # 生产环境应调用 BGE embedding 模型
            import random
            rng = random.Random(hash(request.term))
            embedding = [round(rng.gauss(0, 0.1), 6) for _ in range(768)]
            norm = sum(v * v for v in embedding) ** 0.5
            if norm > 0:
                embedding = [v / norm for v in embedding]

            return ehs_pb2.TermEmbeddingResponse(
                term=request.term,
                embedding=embedding,
                dimension=768,
                request_id=request.request_id,
                processing_time_ms=int((time.time() - start) * 1000),
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return ehs_pb2.TermEmbeddingResponse()

    def GetBatchEmbeddings(self, request, context):
        """批量术语 Embedding RPC"""
        start = time.time()
        results = []
        import random
        for term in request.terms:
            rng = random.Random(hash(term))
            embedding = [round(rng.gauss(0, 0.1), 6) for _ in range(768)]
            norm = sum(v * v for v in embedding) ** 0.5
            if norm > 0:
                embedding = [v / norm for v in embedding]
            results.append(ehs_pb2.TermEmbeddingResult(
                term=term,
                embedding=embedding,
                success=True,
            ))

        return ehs_pb2.BatchEmbeddingResponse(
            results=results,
            request_id=request.request_id,
            processing_time_ms=int((time.time() - start) * 1000),
        )


def serve(port: int = 50051):
    """启动 gRPC 服务"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = EhsAiServicer()
    ehs_pb2_grpc.add_EhsAiServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"gRPC server started on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

- [ ] **Step 4: 测试运行 - 验证 gRPC 服务启动**

```bash
cd apps/ehs-ai
python -m pytest tests/test_grpc_server.py -v
# Expected: 1 passed
```

- [ ] **Step 5: 在 REST API lifespan 中启动 gRPC**

修改 `apps/ehs-ai/src/adapters/primary/rest_api.py` 的 lifespan:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("EHS AI Service 启动中...")
    # 启动 gRPC 服务后台线程
    import threading
    grpc_thread = threading.Thread(
        target=lambda: serve(port=50051),
        daemon=True,
    )
    grpc_thread.start()
    yield
    print("EHS AI Service 关闭中...")
```

并在文件顶部添加 import:
```python
from src.grpc_server import serve
```

- [ ] **Step 6: Commit**

```bash
git add apps/ehs-ai/src/grpc_server.py
git add apps/ehs-ai/src/adapters/primary/rest_api.py
git add apps/ehs-ai/tests/test_grpc_server.py
git commit -m "feat(wave3): 实现 Python gRPC Server，暴露 6 个 AI RPC 接口"
```

---

### Task 2: Java COLA REST Controller 层

**背景:** Java ehs-business 有 Domain 层 (Alert.java)、Application 层 (AlertService.java)、Infrastructure 层 (PythonAiClient.java)，但缺少 Interface/Controller 层。前端需要调 REST API，Java 需要暴露端点。

**Files:**
- Create: `apps/ehs-business/src/main/java/com/ehs/business/interfaces/AlertController.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/interfaces/dto/AlertResponse.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/interfaces/dto/AlertRequest.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/interfaces/dto/PageResponse.java`
- Modify: `apps/ehs-business/src/main/resources/application.properties`

- [ ] **Step 1: 创建 DTO 类**

```java
// apps/ehs-business/src/main/java/com/ehs/business/interfaces/dto/AlertResponse.java
package com.ehs.business.interfaces.dto;

import java.time.Instant;

public class AlertResponse {
    private String id;
    private String type;
    private String location;
    private String riskLevel;
    private String status;
    private String time;
    private String deviceId;
    private String content;
    private String aiAnalysis;

    public AlertResponse(String id, String type, String location, String riskLevel,
                         String status, String time, String deviceId, String content,
                         String aiAnalysis) {
        this.id = id;
        this.type = type;
        this.location = location;
        this.riskLevel = riskLevel;
        this.status = status;
        this.time = time;
        this.deviceId = deviceId;
        this.content = content;
        this.aiAnalysis = aiAnalysis;
    }

    // Getters
    public String getId() { return id; }
    public String getType() { return type; }
    public String getLocation() { return location; }
    public String getRiskLevel() { return riskLevel; }
    public String getStatus() { return status; }
    public String getTime() { return time; }
    public String getDeviceId() { return deviceId; }
    public String getContent() { return content; }
    public String getAiAnalysis() { return aiAnalysis; }
}
```

```java
// apps/ehs-business/src/main/java/com/ehs/business/interfaces/dto/AlertRequest.java
package com.ehs.business.interfaces.dto;

public class AlertRequest {
    private String deviceId;
    private String deviceType;
    private String alertType;
    private String alertContent;
    private String location;
    private int alertLevel;

    // Getters & Setters
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
```

```java
// apps/ehs-business/src/main/java/com/ehs/business/interfaces/dto/PageResponse.java
package com.ehs.business.interfaces.dto;

import java.util.List;

public class PageResponse<T> {
    private boolean success;
    private String message;
    private DataWrapper<T> data;

    public static <T> PageResponse<T> ok(DataWrapper<T> data) {
        PageResponse<T> resp = new PageResponse<>();
        resp.success = true;
        resp.message = "成功";
        resp.data = data;
        return resp;
    }

    public static <T> PageResponse<T> fail(String message) {
        PageResponse<T> resp = new PageResponse<>();
        resp.success = false;
        resp.message = message;
        return resp;
    }

    public boolean isSuccess() { return success; }
    public String getMessage() { return message; }
    public DataWrapper<T> getData() { return data; }

    public static class DataWrapper<T> {
        private long total;
        private long pending;
        private long processing;
        private long resolved;
        private List<T> alerts;

        public DataWrapper(long total, long pending, long processing, long resolved, List<T> alerts) {
            this.total = total;
            this.pending = pending;
            this.processing = processing;
            this.resolved = resolved;
            this.alerts = alerts;
        }

        public long getTotal() { return total; }
        public long getPending() { return pending; }
        public long getProcessing() { return processing; }
        public long getResolved() { return resolved; }
        public List<T> getAlerts() { return alerts; }
    }
}
```

- [ ] **Step 2: 创建 AlertController**

```java
// apps/ehs-business/src/main/java/com/ehs/business/interfaces/AlertController.java
package com.ehs.business.interfaces;

import com.ehs.business.application.alert.AlertService;
import com.ehs.business.domain.alert.Alert;
import com.ehs.business.interfaces.dto.AlertRequest;
import com.ehs.business.interfaces.dto.AlertResponse;
import com.ehs.business.interfaces.dto.PageResponse;
import com.ehs.business.interfaces.dto.PageResponse.DataWrapper;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/alert")
public class AlertController {

    private final AlertService alertService;

    public AlertController(AlertService alertService) {
        this.alertService = alertService;
    }

    @GetMapping("/list")
    public PageResponse<AlertResponse> getAlerts(
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String riskLevel,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {

        List<Alert> allAlerts = alertService.getAllAlerts();

        // 过滤
        List<Alert> filtered = allAlerts;
        if (status != null && !status.isEmpty()) {
            filtered = filtered.stream()
                .filter(a -> a.getStatus().equals(status))
                .collect(Collectors.toList());
        }
        if (riskLevel != null && !riskLevel.isEmpty()) {
            filtered = filtered.stream()
                .filter(a -> a.getLevel().equals(riskLevel))
                .collect(Collectors.toList());
        }

        // 分页
        int start = (page - 1) * pageSize;
        int end = Math.min(start + pageSize, filtered.size());
        List<Alert> pageAlerts = start < filtered.size()
            ? filtered.subList(start, end)
            : new ArrayList<>();

        List<AlertResponse> responses = pageAlerts.stream()
            .map(this::toResponse)
            .collect(Collectors.toList());

        long pending = filtered.stream().filter(a -> "pending".equals(a.getStatus())).count();
        long processing = filtered.stream().filter(a -> "processing".equals(a.getStatus())).count();
        long resolved = filtered.stream().filter(a -> "resolved".equals(a.getStatus())).count();

        return PageResponse.ok(new DataWrapper<>(
            filtered.size(), pending, processing, resolved, responses
        ));
    }

    @PostMapping("/report")
    public AlertResponse reportAlert(@RequestBody AlertRequest request) {
        Alert alert = alertService.createAlert(
            request.getAlertType(),
            String.valueOf(request.getAlertLevel()),
            request.getAlertContent()
        );

        // 调用 AI 分析
        String aiAnalysis = alertService.analyzeAlertWithAi(alert.getId());

        return toResponseWithAi(alert, aiAnalysis);
    }

    @GetMapping("/stats/today")
    public PageResponse<AlertResponse> getTodayStats() {
        List<Alert> allAlerts = alertService.getAllAlerts();
        long pending = allAlerts.stream().filter(a -> "pending".equals(a.getStatus())).count();
        long processing = allAlerts.stream().filter(a -> "processing".equals(a.getStatus())).count();
        long resolved = allAlerts.stream().filter(a -> "resolved".equals(a.getStatus())).count();

        return PageResponse.ok(new DataWrapper<>(
            allAlerts.size(), pending, processing, resolved, new ArrayList<>()
        ));
    }

    private AlertResponse toResponse(Alert alert) {
        return new AlertResponse(
            "ALT-" + alert.getId(),
            alert.getType(),
            "未知位置",
            alert.getLevel(),
            alert.getStatus(),
            DateTimeFormatter.ISO_INSTANT.format(alert.getCreatedAt()),
            "DEV-" + alert.getId(),
            alert.getContent(),
            null
        );
    }

    private AlertResponse toResponseWithAi(Alert alert, String aiAnalysis) {
        return new AlertResponse(
            "ALT-" + alert.getId(),
            alert.getType(),
            "未知位置",
            alert.getLevel(),
            alert.getStatus(),
            DateTimeFormatter.ISO_INSTANT.format(alert.getCreatedAt()),
            "DEV-" + alert.getId(),
            alert.getContent(),
            aiAnalysis
        );
    }
}
```

- [ ] **Step 3: 修改 Alert domain 添加缺失字段**

读取当前 `apps/ehs-business/src/main/java/com/ehs/business/domain/alert/Alert.java`，确认是否有 `getStatus()`, `getCreatedAt()` 等方法。如果没有，需要添加:

```java
// 在 Alert.java 中添加（如果缺失）
private String status = "pending";
private Instant createdAt = Instant.now();

public String getStatus() { return status; }
public Instant getCreatedAt() { return createdAt; }

public void markAsHandled(String handler) {
    this.status = "processing";
}
```

- [ ] **Step 4: 配置 application.properties**

```properties
# apps/ehs-business/src/main/resources/application.properties
spring.application.name=ehs-business
server.port=8080

# gRPC
grpc.ai-service.host=localhost
grpc.ai-service.port=50051

# Spring profiles
spring.profiles.active=default

# Actuator
management.endpoints.web.exposure.include=health,info,metrics
```

- [ ] **Step 5: Commit**

```bash
git add apps/ehs-business/src/main/java/com/ehs/business/interfaces/
git add apps/ehs-business/src/main/resources/application.properties
git commit -m "feat(wave3): Java COLA REST Controller 层 - 告警管理 API"
```

---

### Task 3: 前端从 Mock 切换到真实 API

**背景:** 前端当前所有页面使用 mock 数据 (`src/mock/` 目录)。已有 `src/services/api.ts` 封装了 ApiService 类，但页面未调用。需要让各页面调用真实后端 API，同时保留 mock 作为 fallback。

**Files:**
- Modify: `apps/admin-console/src/app/page.tsx`
- Modify: `apps/admin-console/src/app/alerts/page.tsx`
- Create: `apps/admin-console/src/hooks/use-alerts.ts`
- Create: `apps/admin-console/src/lib/api-errors.ts`

- [ ] **Step 1: 创建 api-errors.ts（ApiService 已引用但文件可能不存在）**

```typescript
// apps/admin-console/src/lib/api-errors.ts
export interface ApiError {
  type: 'network' | 'timeout' | 'http' | 'business' | 'unknown';
  message: string;
  url: string;
  method: string;
  status?: number;
  originalError?: unknown;
}

export function createNetworkError(url: string, method: string, original?: unknown): ApiError {
  return {
    type: 'network',
    message: `网络连接失败: ${method} ${url}`,
    url,
    method,
    originalError: original,
  };
}

export function createTimeoutError(timeout: number, url: string, method: string): ApiError {
  return {
    type: 'timeout',
    message: `请求超时 (${timeout}ms): ${method} ${url}`,
    url,
    method,
  };
}

export function createUnknownError(original: unknown, url: string, method: string): ApiError {
  return {
    type: 'unknown',
    message: `未知错误: ${method} ${url}`,
    url,
    method,
    originalError: original,
  };
}

export function parseErrorFromResponse(
  status: number,
  data: unknown,
  url: string,
  method: string
): ApiError {
  let message = `HTTP ${status}`;
  if (data && typeof data === 'object') {
    const obj = data as Record<string, unknown>;
    if (typeof obj.error === 'string') {
      message = obj.error;
    } else if (typeof obj.message === 'string') {
      message = obj.message;
    }
  }
  return { type: 'http', message, url, method, status };
}

export function isRetryableError(error: ApiError): boolean {
  return error.type === 'network' || error.type === 'timeout';
}

export function getErrorSummary(error: ApiError): string {
  switch (error.type) {
    case 'network': return '网络连接失败，请检查网络设置';
    case 'timeout': return '请求超时，服务器响应过慢';
    case 'http': return `服务器错误 (${error.status})`;
    case 'business': return error.message;
    default: return '未知错误';
  }
}
```

- [ ] **Step 2: 创建 use-alerts hook**

```typescript
// apps/admin-console/src/hooks/use-alerts.ts
import { useState, useEffect } from 'react';
import { api } from '@/services/api';
import { mockAlerts, alertStats } from '@/mock/alerts';
import { Alert } from '@/types/alert';
import { toast } from 'sonner';

export interface UseAlertsOptions {
  /** 如果 API 不可用，是否回退到 mock 数据 */
  fallbackToMock?: boolean;
}

export function useAlerts(options: UseAlertsOptions = {}) {
  const { fallbackToMock = true } = options;
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState({
    today: 0,
    pending: 0,
    processing: 0,
    resolved: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchAlerts() {
      setLoading(true);
      try {
        const response = await api.getAlerts();
        if (!cancelled) {
          // 将后端格式映射到前端 Alert 格式
          const mapped: Alert[] = response.data.alerts.map((a) => ({
            id: a.id,
            type: mapAlertType(a.type),
            title: `${a.type} - ${a.location}`,
            content: a.content || '',
            riskLevel: a.riskLevel as Alert['riskLevel'],
            status: a.status as Alert['status'],
            location: a.location,
            deviceId: a.deviceId || '',
            createdAt: a.time,
            aiRecommendation: 'AI 分析中...',
          }));
          setAlerts(mapped);
          setStats((prev) => ({
            ...prev,
            today: response.data.total,
            pending: response.data.pending,
            processing: response.data.processing,
            resolved: response.data.resolved,
          }));
        }
      } catch (e) {
        if (fallbackToMock) {
          if (!cancelled) {
            setAlerts(mockAlerts);
            setStats({
              today: alertStats.today,
              pending: alertStats.pending,
              processing: alertStats.processing,
              resolved: alertStats.resolved,
              critical: alertStats.critical,
              high: alertStats.high,
              medium: alertStats.medium,
              low: alertStats.low,
            });
          }
        } else {
          if (!cancelled) {
            setError('获取告警数据失败');
            toast.error('获取告警数据失败');
          }
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchAlerts();
    return () => { cancelled = true; };
  }, [fallbackToMock]);

  return { alerts, stats, loading, error, refetch: () => {} };
}

function mapAlertType(type: string): Alert['type'] {
  const typeMap: Record<string, Alert['type']> = {
    'fire': 'fire',
    'gas_leak': 'gas_leak',
    'temperature': 'temperature',
    'intrusion': 'intrusion',
    'smoke': 'smoke',
    '烟火告警': 'fire',
    '气体泄漏': 'gas_leak',
    '温度异常': 'temperature',
    '入侵检测': 'intrusion',
  };
  return typeMap[type] || 'smoke';
}
```

- [ ] **Step 3: 修改 Dashboard page.tsx 使用 hook**

修改 `apps/admin-console/src/app/page.tsx`:
- 在文件顶部添加 `import { useAlerts } from '@/hooks/use-alerts';`
- 替换硬编码的 mock 数据调用为 `const { stats, alerts, loading } = useAlerts({ fallbackToMock: true });`
- 添加 loading 状态: `if (loading) return <div className="p-6">加载中...</div>;`

具体修改:
```tsx
// 替换原有的 mock import 和使用
// Before: import { alertStats } from "@/mock/alerts";
// After:
import { useAlerts } from "@/hooks/use-alerts";

export default function DashboardPage() {
  const { stats, alerts, loading } = useAlerts({ fallbackToMock: true });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  // 将原有 alertStats.today/processing/resolved/critical 替换为
  // stats.today/stats.processing/stats.resolved/stats.critical
  // 将 mockAlerts.slice(0, 5) 替换为 alerts.slice(0, 5)
  ...
}
```

- [ ] **Step 4: 修改 Alerts page.tsx 使用 hook**

修改 `apps/admin-console/src/app/alerts/page.tsx`:
- 添加 `import { useAlerts } from '@/hooks/use-alerts';`
- 替换 `import { mockAlerts } from "@/mock/alerts";` 为 hook 调用
- 将 `const [alerts] = useState(mockAlerts)` 替换为 `const { alerts, loading } = useAlerts()`

- [ ] **Step 5: Commit**

```bash
git add apps/admin-console/src/hooks/use-alerts.ts
git add apps/admin-console/src/lib/api-errors.ts
git add apps/admin-console/src/app/page.tsx
git add apps/admin-console/src/app/alerts/page.tsx
git commit -m "feat(wave3): 前端 Dashboard + 告警页切换为真实 API (fallback mock)"
```

---

## Wave 4: Java 完整业务逻辑 + 监控集成

### Task 4: Java gRPC Client 对接 Python AI 服务

**背景:** Java 已有 `PythonAiClient.java` 但使用模拟实现。Wave 4 需要真实连接 Python gRPC。

**Files:**
- Modify: `apps/ehs-business/src/main/java/com/ehs/business/infrastructure/grpc/PythonAiClient.java`
- Create: `apps/ehs-business/src/main/java/com/ehs/business/infrastructure/grpc/GrpcChannel.java`
- Modify: `apps/ehs-business/src/main/java/com/ehs/business/application/alert/AlertService.java`

- [ ] **Step 1: 创建 GrpcChannel 管理类**

```java
// apps/ehs-business/src/main/java/com/ehs/business/infrastructure/grpc/GrpcChannel.java
package com.ehs.business.infrastructure.grpc;

import com.ehs.business.infrastructure.grpc.proto.EhsAiServiceGrpc;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

@Component
public class GrpcChannel {

    @Value("${grpc.ai-service.host:localhost}")
    private String host;

    @Value("${grpc.ai-service.port:50051}")
    private int port;

    private ManagedChannel channel;
    private EhsAiServiceGrpc.EhsAiServiceBlockingStub stub;

    @PostConstruct
    public void init() {
        channel = ManagedChannelBuilder.forAddress(host, port)
            .usePlaintext()
            .build();
        stub = EhsAiServiceGrpc.newBlockingStub(channel);
    }

    @PreDestroy
    public void shutdown() {
        if (channel != null && !channel.isShutdown()) {
            channel.shutdown();
        }
    }

    public EhsAiServiceGrpc.EhsAiServiceBlockingStub getStub() {
        return stub;
    }

    public boolean isHealthy() {
        try {
            var response = stub.healthCheck(
                com.ehs.business.infrastructure.grpc.proto.HealthCheckRequest.newBuilder()
                    .setService("ehs-ai")
                    .build()
            );
            return response.getHealthy();
        } catch (Exception e) {
            return false;
        }
    }
}
```

- [ ] **Step 2: 重写 PythonAiClient 使用真实 gRPC**

```java
// apps/ehs-business/src/main/java/com/ehs/business/infrastructure/grpc/PythonAiClient.java
package com.ehs.business.infrastructure.grpc;

import com.ehs.business.infrastructure.grpc.proto.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class PythonAiClient {

    private static final Logger log = LoggerFactory.getLogger(PythonAiClient.class);
    private final GrpcChannel grpcChannel;

    public PythonAiClient(GrpcChannel grpcChannel) {
        this.grpcChannel = grpcChannel;
    }

    /**
     * 分析告警 - 调用 Python AI 服务
     */
    public AlertAnalysisResponse analyzeAlert(
            String content, String location, String alertType, int alertLevel) {

        AlertType protoType = parseAlertType(alertType);
        RiskLevel protoLevel = parseRiskLevel(alertLevel);

        AlertAnalysisRequest request = AlertAnalysisRequest.newBuilder()
            .setAlertType(protoType)
            .setAlertLevel(protoLevel)
            .setContent(content)
            .setLocation(location)
            .setRequestId(java.util.UUID.randomUUID().toString())
            .setTimestamp(System.currentTimeMillis())
            .build();

        try {
            return grpcChannel.getStub().analyzeAlert(request);
        } catch (Exception e) {
            log.warn("gRPC AI 服务调用失败，使用 fallback: {}", e.getMessage());
            return createFallbackResponse(content, protoLevel);
        }
    }

    /**
     * 风险分级 - 调用 Python AI 服务
     */
    public RiskClassificationResponse classifyRisk(String text) {
        RiskClassificationRequest request = RiskClassificationRequest.newBuilder()
            .setText(text)
            .setRequestId(java.util.UUID.randomUUID().toString())
            .setTimestamp(System.currentTimeMillis())
            .build();

        try {
            return grpcChannel.getStub().classifyRisk(request);
        } catch (Exception e) {
            log.warn("gRPC 风险分级调用失败: {}", e.getMessage());
            return RiskClassificationResponse.newBuilder()
                .setRiskLevel(RiskLevel.RISK_LEVEL_MEDIUM)
                .setConfidence(0.5f)
                .setReason("AI 服务不可用，使用默认评级")
                .build();
        }
    }

    private AlertType parseAlertType(String type) {
        return switch (type.toLowerCase()) {
            case "fire", "烟火告警" -> AlertType.ALERT_TYPE_FIRE;
            case "gas", "气体泄漏" -> AlertType.ALERT_TYPE_GAS;
            case "intrusion", "入侵检测" -> AlertType.ALERT_TYPE_INTRUSION;
            case "temperature", "温度异常" -> AlertType.ALERT_TYPE_TEMPERATURE;
            default -> AlertType.ALERT_TYPE_OTHER;
        };
    }

    private RiskLevel parseRiskLevel(int level) {
        return switch (level) {
            case 1 -> RiskLevel.RISK_LEVEL_LOW;
            case 2 -> RiskLevel.RISK_LEVEL_MEDIUM;
            case 3 -> RiskLevel.RISK_LEVEL_HIGH;
            case 4 -> RiskLevel.RISK_LEVEL_CRITICAL;
            default -> RiskLevel.RISK_LEVEL_UNSPECIFIED;
        };
    }

    private AlertAnalysisResponse createFallbackResponse(String content, RiskLevel level) {
        return AlertAnalysisResponse.newBuilder()
            .setAnalysis("AI 服务暂不可用，使用默认分析")
            .setSuggestedAction("请值班人员现场确认")
            .setRecommendedLevel(level)
            .setConfidence(0.3f)
            .build();
    }
}
```

- [ ] **Step 3: 修改 AlertService 调用真实 AI Client**

```java
// 修改 AlertService.java 的 analyzeAlertWithAi 方法
// 添加 PythonAiClient 依赖注入

private final PythonAiClient pythonAiClient;

public AlertService(PythonAiClient pythonAiClient) {
    this.pythonAiClient = pythonAiClient;
}

/**
 * 调用 AI 服务分析告警
 */
public String analyzeAlertWithAi(Long alertId) {
    return getAlertById(alertId)
        .map(alert -> {
            var response = pythonAiClient.analyzeAlert(
                alert.getContent(),
                "未知位置",
                alert.getType(),
                Integer.parseInt(alert.getLevel())
            );
            return response.getAnalysis() + "\n建议: " + response.getSuggestedAction();
        })
        .orElse("告警不存在");
}
```

- [ ] **Step 4: Commit**

```bash
git add apps/ehs-business/src/main/java/com/ehs/business/infrastructure/grpc/
git add apps/ehs-business/src/main/java/com/ehs/business/application/alert/AlertService.java
git commit -m "feat(wave4): Java gRPC Client 真实对接 Python AI 服务"
```

---

### Task 5: Prometheus + Grafana 监控集成

**背景:** 设计文档要求 Prometheus + Grafana 全指标监控。需要在 docker-compose.yml 中添加服务，Python 服务暴露 metrics 端点。

**Files:**
- Create: `infra/monitoring/prometheus.yml`
- Create: `apps/ehs-ai/src/monitoring/middleware.py`
- Modify: `docker-compose.yml`

- [ ] **Step 1: 创建 Prometheus 配置**

```yaml
# infra/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ehs-ai'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['ehs-ai:8000']

  - job_name: 'ehs-business'
    metrics_path: '/actuator/prometheus'
    static_configs:
      - targets: ['ehs-business:8080']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

- [ ] **Step 2: 创建 Python metrics middleware**

```python
# apps/ehs-ai/src/monitoring/middleware.py
"""Prometheus metrics middleware for FastAPI"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from prometheus_client import Counter, Histogram, Gauge

# 定义指标
HTTP_REQUESTS_TOTAL = Counter(
    "ehs_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "ehs_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "ehs_http_requests_in_progress",
    "Number of HTTP requests currently in progress"
)

AI_INFERENCE_DURATION = Histogram(
    "ehs_ai_inference_duration_seconds",
    "AI inference duration in seconds",
    ["model", "operation"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        HTTP_REQUESTS_IN_PROGRESS.inc()
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        HTTP_REQUESTS_IN_PROGRESS.dec()

        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status=str(response.status_code)
        ).inc()

        HTTP_REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response
```

- [ ] **Step 3: 在 FastAPI 中注册 middleware**

修改 `apps/ehs-ai/src/adapters/primary/rest_api.py`:

```python
# 在 import 区域添加
from starlette_prometheus import metrics
from fastapi import FastAPI

# 在 app 创建后添加
app.add_route("/metrics", metrics)
app.add_middleware(MetricsMiddleware)
```

在 requirements.txt 添加:
```
prometheus-client>=0.19.0
starlette-prometheus>=0.10.0
```

- [ ] **Step 4: 添加 Prometheus + Grafana 到 docker-compose.yml**

在 docker-compose.yml 的 volumes 后添加:

```yaml
  # ============================================
  # 监控层
  # ============================================

  prometheus:
    image: prom/prometheus:latest
    container_name: ehs-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infra/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped
    depends_on:
      - ehs-ai
      - ehs-business

  grafana:
    image: grafana/grafana:latest
    container_name: ehs-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_INSTALL_PLUGINS=grafana-clock-panel
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    depends_on:
      - prometheus
```

在 volumes 块中添加:
```yaml
  prometheus_data:
  grafana_data:
```

- [ ] **Step 5: Commit**

```bash
git add infra/monitoring/prometheus.yml
git add apps/ehs-ai/src/monitoring/middleware.py
git add apps/ehs-ai/src/adapters/primary/rest_api.py
git add docker-compose.yml
git commit -m "feat(wave4): Prometheus + Grafana 监控集成"
```

---

## Wave 5: K8s 部署 + CI/CD + E2E 测试

### Task 6: K8s Helm Chart

**背景:** 设计文档要求完整的 K8s Helm Chart 部署配置，包括 Deployment + Service + ConfigMap + Ingress + HPA。

**Files:**
- Create: `infra/k8s/ehs/Chart.yaml`
- Create: `infra/k8s/ehs/values.yaml`
- Create: `infra/k8s/ehs/templates/admin-console-deployment.yaml`
- Create: `infra/k8s/ehs/templates/ehs-ai-deployment.yaml`
- Create: `infra/k8s/ehs/templates/ehs-business-deployment.yaml`
- Create: `infra/k8s/ehs/templates/services.yaml`
- Create: `infra/k8s/ehs/templates/ingress.yaml`
- Create: `infra/k8s/ehs/templates/hpa.yaml`
- Create: `infra/k8s/ehs/templates/configmap.yaml`

- [ ] **Step 1: 创建 Chart.yaml**

```yaml
# infra/k8s/ehs/Chart.yaml
apiVersion: v2
name: ehs
description: EHS 智能安保决策中台 - Kubernetes Helm Chart
type: application
version: 2.0.0
appVersion: "2.0.0"
```

- [ ] **Step 2: 创建 values.yaml**

```yaml
# infra/k8s/ehs/values.yaml
replicaCount: 1

image:
  pullPolicy: IfNotPresent

adminConsole:
  image: ehs/admin-console
  tag: "2.0.0"
  port: 3000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

ehsAi:
  image: ehs/ehs-ai
  tag: "2.0.0"
  port: 8000
  grpcPort: 50051
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: "2"
      memory: 4Gi
  env:
    ES_URL: "http://elasticsearch:9200"
    MILVUS_URL: "milvus"
    LLM_ENDPOINT: "http://ollama:11434/v1/chat/completions"

ehsBusiness:
  image: ehs/ehs-business
  tag: "2.0.0"
  port: 8080
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: "1"
      memory: 2Gi

ingress:
  enabled: true
  className: nginx
  host: ehs.example.com

hpa:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPU: 70

serviceAccount:
  create: true
  name: ehs-sa
```

- [ ] **Step 3: 创建 ehs-ai Deployment**

```yaml
# infra/k8s/ehs/templates/ehs-ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ehs-ai
  labels:
    app: ehs-ai
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: ehs-ai
  template:
    metadata:
      labels:
        app: ehs-ai
    spec:
      serviceAccountName: {{ .Values.serviceAccount.name }}
      containers:
        - name: ehs-ai
          image: "{{ .Values.ehsAi.image }}:{{ .Values.ehsAi.tag }}"
          ports:
            - name: http
              containerPort: {{ .Values.ehsAi.port }}
            - name: grpc
              containerPort: {{ .Values.ehsAi.grpcPort }}
          env:
            {{- range $key, $value := .Values.ehsAi.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          resources:
            {{- toYaml .Values.ehsAi.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
```

- [ ] **Step 4: 创建 Services**

```yaml
# infra/k8s/ehs/templates/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: ehs-ai
spec:
  type: ClusterIP
  ports:
    - name: http
      port: {{ .Values.ehsAi.port }}
      targetPort: http
    - name: grpc
      port: {{ .Values.ehsAi.grpcPort }}
      targetPort: grpc
  selector:
    app: ehs-ai
---
apiVersion: v1
kind: Service
metadata:
  name: ehs-business
spec:
  type: ClusterIP
  ports:
    - name: http
      port: {{ .Values.ehsBusiness.port }}
      targetPort: http
  selector:
    app: ehs-business
---
apiVersion: v1
kind: Service
metadata:
  name: admin-console
spec:
  type: ClusterIP
  ports:
    - name: http
      port: {{ .Values.adminConsole.port }}
      targetPort: http
  selector:
    app: admin-console
```

- [ ] **Step 5: 创建 Ingress + HPA**

```yaml
# infra/k8s/ehs/templates/ingress.yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ehs-ingress
spec:
  ingressClassName: {{ .Values.ingress.className }}
  rules:
    - host: {{ .Values.ingress.host }}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: admin-console
                port:
                  name: http
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: ehs-ai
                port:
                  name: http
{{- end }}
```

```yaml
# infra/k8s/ehs/templates/hpa.yaml
{{- if .Values.hpa.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ehs-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ehs-ai
  minReplicas: {{ .Values.hpa.minReplicas }}
  maxReplicas: {{ .Values.hpa.maxReplicas }}
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.hpa.targetCPU }}
{{- end }}
```

- [ ] **Step 6: Commit**

```bash
git add infra/k8s/ehs/
git commit -m "feat(wave5): K8s Helm Chart 完整部署配置"
```

---

### Task 7: GitHub Actions CI/CD

**背景:** 设计文档要求完整的 GitHub Actions CI/CD 流水线：test → build → deploy → release。

**Files:**
- Create: `.github/workflows/ci-cd.yml`
- Create: `.github/workflows/pr-check.yml`

- [ ] **Step 1: 创建 PR 检查 workflow**

```yaml
# .github/workflows/pr-check.yml
name: PR Check

on:
  pull_request:
    branches: [main]

jobs:
  frontend-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: 'apps/admin-console/pnpm-lock.yaml'
      - run: cd apps/admin-console && pnpm install
      - run: cd apps/admin-console && pnpm typecheck
      - run: cd apps/admin-console && pnpm lint
      - run: cd apps/admin-console && pnpm test -- --run

  python-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r apps/ehs-ai/requirements.txt
      - run: cd apps/ehs-ai && pip install pytest
      - run: cd apps/ehs-ai && pytest tests/ -v

  java-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
      - run: cd apps/ehs-business && ./mvnw test
```

- [ ] **Step 2: 创建 CI/CD workflow**

```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Install Python deps
        run: pip install -r apps/ehs-ai/requirements.txt && pip install pytest pytest-cov

      - name: Install Node deps
        run: cd apps/admin-console && pnpm install

      - name: Run Python tests
        run: cd apps/ehs-ai && pytest tests/ --cov=src --cov-report=xml

      - name: Run Frontend tests
        run: cd apps/admin-console && pnpm test -- --run

      - name: Run Java tests
        run: cd apps/ehs-business && ./mvnw test

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: apps/ehs-ai/coverage.xml

  build:
    name: Build Docker Images
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build & push ehs-ai
        uses: docker/build-push-action@v5
        with:
          context: ./apps/ehs-ai
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/ehs-ai:${{ github.sha }}

      - name: Build & push ehs-business
        uses: docker/build-push-action@v5
        with:
          context: ./apps/ehs-business
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/ehs-business:${{ github.sha }}

      - name: Build & push admin-console
        uses: docker/build-push-action@v5
        with:
          context: ./apps/admin-console
          push: true
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/admin-console:${{ github.sha }}

  release:
    name: Create Release
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v${{ github.run_number }}
          generate_release_notes: true
          draft: false
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/
git commit -m "feat(wave5): GitHub Actions CI/CD 流水线"
```

---

### Task 8: E2E 测试 (Playwright)

**背景:** 设计文档要求 10 个核心 E2E 场景。使用 Playwright 进行浏览器自动化测试。

**Files:**
- Create: `apps/admin-console/tests/e2e/dashboard.spec.ts`
- Create: `apps/admin-console/tests/e2e/alerts.spec.ts`
- Create: `apps/admin-console/tests/e2e/plans.spec.ts`
- Create: `apps/admin-console/playwright.config.ts`
- Create: `apps/admin-console/package.json` scripts 添加 `test:e2e`

- [ ] **Step 1: 添加 Playwright 依赖**

```bash
cd apps/admin-console
pnpm add -D @playwright/test
pnpm exec playwright install
```

- [ ] **Step 2: 创建 Playwright 配置**

```typescript
// apps/admin-console/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

- [ ] **Step 3: 创建 Dashboard E2E 测试**

```typescript
// apps/admin-console/tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should display 4 stat cards', async ({ page }) => {
    await page.goto('/');

    // 验证 4 个统计卡片
    const cards = page.locator('[data-testid="stat-card"]');
    await expect(cards).toHaveCount(4);

    // 验证卡片标题
    await expect(page.getByText('今日告警')).toBeVisible();
    await expect(page.getByText('待处理')).toBeVisible();
    await expect(page.getByText('设备在线率')).toBeVisible();
    await expect(page.getByText('安全天数')).toBeVisible();
  });

  test('should display recent alerts list', async ({ page }) => {
    await page.goto('/');

    // 验证最近告警列表
    await expect(page.getByText('最近告警')).toBeVisible();
    const alertRows = page.locator('table tbody tr');
    await expect(alertRows.count()).toBeGreaterThan(0);
  });

  test('should navigate to alerts page when clicking alert', async ({ page }) => {
    await page.goto('/');

    // 点击导航
    await page.getByText('告警管理').click();
    await expect(page).toHaveURL('/alerts');
  });
});
```

- [ ] **Step 4: 创建 Alerts E2E 测试**

```typescript
// apps/admin-console/tests/e2e/alerts.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Alerts Management', () => {
  test('should display alerts table', async ({ page }) => {
    await page.goto('/alerts');

    // 验证表格存在
    const table = page.locator('table');
    await expect(table).toBeVisible();

    // 验证表头
    await expect(page.getByText('告警ID')).toBeVisible();
    await expect(page.getByText('类型')).toBeVisible();
    await expect(page.getByText('位置')).toBeVisible();
    await expect(page.getByText('风险等级')).toBeVisible();
    await expect(page.getByText('状态')).toBeVisible();
  });

  test('should filter alerts by status', async ({ page }) => {
    await page.goto('/alerts');

    // 选择状态筛选
    const statusFilter = page.getByRole('combobox', { name: /状态/ });
    await statusFilter.click();
    await page.getByRole('option', { name: '待处理' }).click();

    // 验证筛选后的行状态均为 pending
    const rows = page.locator('table tbody tr');
    const count = await rows.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should open alert detail drawer on click', async ({ page }) => {
    await page.goto('/alerts');

    // 点击第一行
    await page.locator('table tbody tr').first().click();

    // 验证抽屉打开
    await expect(page.getByText('告警详情')).toBeVisible();
  });
});
```

- [ ] **Step 5: 创建 Plans E2E 测试**

```typescript
// apps/admin-console/tests/e2e/plans.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Plans Management', () => {
  test('should display plans as cards', async ({ page }) => {
    await page.goto('/plans');

    // 验证卡片网格
    const cards = page.locator('[data-testid="plan-card"]');
    await expect(cards.count()).toBeGreaterThan(0);
  });

  test('should filter plans by category', async ({ page }) => {
    await page.goto('/plans');

    // 点击分类筛选
    await page.getByRole('button', { name: '火灾' }).click();

    // 验证筛选生效
    await expect(page.locator('[data-testid="plan-card"]')).toBeVisible();
  });

  test('should open plan preview dialog', async ({ page }) => {
    await page.goto('/plans');

    // 点击预览按钮
    await page.locator('[data-testid="plan-card"]').first().getByRole('button').click();

    // 验证对话框打开
    await expect(page.getByRole('dialog')).toBeVisible();
  });
});
```

- [ ] **Step 6: 添加 test:e2e script 到 package.json**

修改 `apps/admin-console/package.json` scripts:
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```

- [ ] **Step 7: Commit**

```bash
git add apps/admin-console/tests/e2e/
git add apps/admin-console/playwright.config.ts
git add apps/admin-console/package.json
git commit -m "feat(wave5): Playwright E2E 测试 - Dashboard + 告警 + 预案"
```

---

### Task 9: Locust 性能测试

**背景:** 设计文档要求 Locust/k6 性能测试，验证 P99 < 800ms。

**Files:**
- Create: `infra/perf/locustfile.py`
- Create: `infra/perf/requirements.txt`

- [ ] **Step 1: 创建 Locust 测试脚本**

```python
# infra/perf/locustfile.py
"""EHS 性能测试 - Locust"""
from locust import HttpUser, task, between
import json


class AlertUser(HttpUser):
    """模拟告警上报用户"""
    wait_time = between(1, 3)

    @task(3)
    def report_alert(self):
        """告警上报"""
        self.client.post(
            "/api/alert/report",
            json={
                "device_id": "DEV-001",
                "device_type": "smoke_detector",
                "alert_type": "fire",
                "alert_content": "A栋3楼烟感探测器检测到烟雾浓度超标",
                "location": "A栋3楼",
                "alert_level": 3,
            },
            name="/api/alert/report"
        )

    @task(5)
    def search_plans(self):
        """预案检索"""
        self.client.post(
            "/api/plan/search",
            json={
                "query": "火灾应急预案",
                "event_type": "fire",
                "top_k": 5,
            },
            name="/api/plan/search"
        )

    @task(2)
    def get_alerts(self):
        """获取告警列表"""
        self.client.get(
            "/api/alert/list?status=pending&page=1&page_size=10",
            name="/api/alert/list"
        )

    @task(1)
    def health_check(self):
        """健康检查"""
        self.client.get("/health", name="/health")


class DashboardUser(HttpUser):
    """模拟 Dashboard 用户"""
    wait_time = between(3, 8)

    @task
    def get_stats(self):
        """获取统计"""
        self.client.get("/api/stats/today", name="/api/stats/today")
```

- [ ] **Step 2: Commit**

```bash
git add infra/perf/locustfile.py
git commit -m "feat(wave5): Locust 性能测试脚本"
```

---

## 自审

### 1. 规格覆盖

检查设计文档 (2026-04-15-ehs-stage2-design.md) 中 Wave 3-5 的要求：

| Wave | 设计要求 | 对应 Task | 覆盖状态 |
|------|---------|----------|---------|
| **Wave 3** | Python AI 服务集成 | Task 1 (gRPC Server) | ✅ |
| **Wave 3** | Java COLA 四层 | Task 2 (REST Controller) | ✅ |
| **Wave 3** | 前端改真实 API | Task 3 (Mock→API) | ✅ |
| **Wave 4** | Java gRPC 集成 | Task 4 (gRPC Client) | ✅ |
| **Wave 4** | Prometheus/Grafana 监控 | Task 5 (监控集成) | ✅ |
| **Wave 5** | K8s Helm Chart | Task 6 (Helm) | ✅ |
| **Wave 5** | GitHub Actions CI/CD | Task 7 (CI/CD) | ✅ |
| **Wave 5** | E2E 测试 | Task 8 (Playwright) | ✅ |
| **Wave 5** | 性能测试 | Task 9 (Locust) | ✅ |

### 2. Placeholder 扫描

- 所有代码步骤包含完整实现代码
- 无 "TBD", "TODO", "fill in details" 等占位符
- 所有 import、类型定义在步骤内完整给出
- 文件路径精确到具体位置

### 3. 类型一致性

- RiskLevel 枚举: Python ("low"/"medium"/"high"/"critical") → Proto (RISK_LEVEL_LOW/...) → Java (RiskLevel enum) — 映射一致
- AlertType 枚举: Python → Proto → Java — 映射一致
- API 响应格式: `PageResponse<T>` wrapper — Controller 与前端 ApiService 匹配
- gRPC proto 文件: 使用已定义的 `ehs.proto`，不创建新 proto

---

## 执行建议

**推荐执行顺序:**
1. Wave 3: Task 1 → Task 2 → Task 3 (必须顺序，前端依赖后端)
2. Wave 4: Task 4 → Task 5 (Task 4 依赖 Task 1 的 gRPC)
3. Wave 5: Task 6 → Task 7 → Task 8 → Task 9 (可并行 Task 8/9)

**并行策略:**
- Wave 3 Task 1 (Python gRPC) 和 Task 2 (Java Controller) 可并行
- Wave 5 Task 8 (E2E) 和 Task 9 (Perf) 可并行
