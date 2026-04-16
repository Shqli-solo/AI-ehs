# EHS AI Service API 使用示例

本文档提供 EHS AI Service REST API 的使用示例，包括 curl 命令和 Python SDK。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 版本**: 2.0.0
- **认证方式**: Bearer Token (JWT)

## 健康检查

### curl 示例

```bash
curl -X GET http://localhost:8000/health
```

### Python SDK 示例

```python
import httpx

response = httpx.get("http://localhost:8000/health")
print(response.json())
```

### 响应示例

```json
{
  "status": "healthy",
  "service": "ehs-ai-service",
  "timestamp": "2026-04-16T10:00:00Z"
}
```

---

## 告警上报

### 功能说明

接收 AIoT 设备告警，调用 Multi-Agent 工作流进行：
1. 风险感知（RiskAgent 评估风险等级）
2. 预案检索（SearchAgent 检索应急预案）

### curl 示例

#### 火灾告警

```bash
curl -X POST http://localhost:8000/api/alert/report \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEV-001",
    "device_type": "烟雾探测器",
    "alert_type": "fire",
    "alert_content": "3 号楼 2 层检测到浓烟",
    "location": "3 号楼 2 层",
    "alert_level": 3
  }'
```

#### 气体泄漏告警

```bash
curl -X POST http://localhost:8000/api/alert/report \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "DEV-002",
    "device_type": "气体传感器",
    "alert_type": "gas_leak",
    "alert_content": "地下室甲烷浓度超标",
    "location": "地下室",
    "alert_level": 4
  }'
```

### Python SDK 示例

```python
import httpx
from typing import Optional, Dict, Any


class EHSClient:
    """EHS AI Service 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)

    def report_alert(
        self,
        device_id: str,
        device_type: str,
        alert_type: str,
        alert_content: str,
        location: str,
        alert_level: int,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上报告警

        Args:
            device_id: 设备 ID
            device_type: 设备类型
            alert_type: 告警类型
            alert_content: 告警内容
            location: 告警位置
            alert_level: 告警级别（1-4）
            extra_data: 额外数据

        Returns:
            告警响应
        """
        payload = {
            "device_id": device_id,
            "device_type": device_type,
            "alert_type": alert_type,
            "alert_content": alert_content,
            "location": location,
            "alert_level": alert_level,
        }
        if extra_data:
            payload["extra_data"] = extra_data

        response = self.client.post("/api/alert/report", json=payload)
        response.raise_for_status()
        return response.json()


# 使用示例
if __name__ == "__main__":
    client = EHSClient()

    # 上报火灾告警
    result = client.report_alert(
        device_id="DEV-001",
        device_type="烟雾探测器",
        alert_type="fire",
        alert_content="3 号楼 2 层检测到浓烟",
        location="3 号楼 2 层",
        alert_level=3
    )

    print(f"告警 ID: {result['alert_id']}")
    print(f"风险等级：{result['risk_level']}")
    print(f"关联预案：{len(result.get('plans', []))} 条")
```

### 响应示例

```json
{
  "success": true,
  "message": "告警上报成功",
  "alert_id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_level": "high",
  "plans": [
    {
      "title": "火灾事故专项应急预案",
      "content": "1. 立即启动消防泵 2. 疏散现场人员 3. 通知消防队",
      "risk_level": "high",
      "source": "ES",
      "score": 0.95
    }
  ]
}
```

---

## 预案检索

### 功能说明

使用 GraphRAG 检索引擎搜索应急预案：
1. ES BM25 文本检索
2. Milvus 向量相似度检索
3. 合并去重
4. BGE-Reranker 重排序

### curl 示例

#### 检索火灾预案

```bash
curl -X POST http://localhost:8000/api/plan/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "火灾应急处置",
    "event_type": "fire",
    "top_k": 5
  }'
```

#### 通用检索

```bash
curl -X POST http://localhost:8000/api/plan/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "化学品泄漏应急预案",
    "top_k": 10
  }'
```

### Python SDK 示例

```python
from typing import Optional, List, Dict, Any


class EHSClient:
    # ... 上面已定义 report_alert 方法 ...

    def search_plans(
        self,
        query: str,
        event_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索应急预案

        Args:
            query: 查询文本
            event_type: 事件类型（可选）
            top_k: 返回结果数量

        Returns:
            预案列表
        """
        payload = {
            "query": query,
            "top_k": top_k
        }
        if event_type:
            payload["event_type"] = event_type

        response = self.client.post("/api/plan/search", json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("plans", [])


# 使用示例
if __name__ == "__main__":
    client = EHSClient()

    # 检索火灾预案
    plans = client.search_plans(
        query="火灾应急处置",
        event_type="fire",
        top_k=5
    )

    for plan in plans:
        print(f"标题：{plan.get('title')}")
        print(f"内容：{plan.get('content')[:50]}...")
        print(f"相似度：{plan.get('score')}")
        print("---")
```

### 响应示例

```json
{
  "success": true,
  "message": "预案检索成功",
  "plans": [
    {
      "id": "plan-001",
      "title": "火灾事故专项应急预案",
      "content": "1. 立即启动消防泵 2. 疏散现场人员 3. 通知消防队 4. 切断电源 5. 使用灭火器初期灭火",
      "risk_level": "high",
      "source": "ES",
      "score": 0.95,
      "metadata": {
        "category": "火灾",
        "version": "2024-v1"
      }
    },
    {
      "id": "plan-002",
      "title": "消防设备操作指南",
      "content": "消防泵启动步骤：1. 检查电源 2. 打开阀门 3. 启动按钮 4. 检查压力表",
      "risk_level": "medium",
      "source": "Milvus",
      "score": 0.85
    }
  ],
  "query": "火灾应急处置"
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "message": "错误消息",
  "detail": "详细错误信息（可选）"
}
```

### 常见错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 422 | 输入验证失败 |
| 500 | 服务器内部错误 |

### Python 错误处理示例

```python
import httpx
from httpx import HTTPStatusError, RequestError


def call_api_with_error_handling():
    client = EHSClient()

    try:
        result = client.report_alert(
            device_id="DEV-001",
            device_type="烟雾探测器",
            alert_type="fire",
            alert_content="测试告警",
            location="测试位置",
            alert_level=2
        )
        print(f"成功：{result}")

    except HTTPStatusError as e:
        # HTTP 错误（4xx, 5xx）
        print(f"HTTP 错误：{e.response.status_code}")
        print(f"错误详情：{e.response.json()}")

    except RequestError as e:
        # 网络错误
        print(f"网络错误：{e}")

    except Exception as e:
        # 其他错误
        print(f"未知错误：{e}")
```

---

## 异步 Python 示例

```python
import asyncio
import httpx


class AsyncEHSClient:
    """异步 EHS 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def close(self):
        await self.client.aclose()

    async def report_alert(
        self,
        device_id: str,
        device_type: str,
        alert_type: str,
        alert_content: str,
        location: str,
        alert_level: int
    ) -> dict:
        payload = {
            "device_id": device_id,
            "device_type": device_type,
            "alert_type": alert_type,
            "alert_content": alert_content,
            "location": location,
            "alert_level": alert_level,
        }
        response = await self.client.post("/api/alert/report", json=payload)
        response.raise_for_status()
        return response.json()

    async def search_plans(
        self,
        query: str,
        event_type: str = None,
        top_k: int = 5
    ) -> list:
        payload = {"query": query, "top_k": top_k}
        if event_type:
            payload["event_type"] = event_type
        response = await self.client.post("/api/plan/search", json=payload)
        response.raise_for_status()
        result = await response.json()
        return result.get("plans", [])


# 异步使用示例
async def main():
    client = AsyncEHSClient()

    try:
        # 并发上报告警和检索预案
        alert_task = client.report_alert(
            device_id="DEV-001",
            device_type="烟雾探测器",
            alert_type="fire",
            alert_content="3 号楼 2 层检测到浓烟",
            location="3 号楼 2 层",
            alert_level=3
        )

        plan_task = client.search_plans(
            query="火灾应急处置",
            event_type="fire",
            top_k=5
        )

        # 并发执行
        alert_result, plans = await asyncio.gather(alert_task, plan_task)

        print(f"告警 ID: {alert_result['alert_id']}")
        print(f"风险等级：{alert_result['risk_level']}")
        print(f"检索到 {len(plans)} 条预案")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## OpenAPI 规范

完整的 OpenAPI 规范文件位于：
- `docs/api/openapi.yaml`

可以使用 Swagger UI 查看：
```bash
# 启动服务后访问
http://localhost:8000/docs
```

或使用 Redoc：
```bash
http://localhost:8000/redoc
```
