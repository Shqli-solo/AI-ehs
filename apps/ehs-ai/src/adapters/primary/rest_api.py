# apps/ehs-ai/src/adapters/primary/rest_api.py
"""FastAPI REST API - Primary Adapter"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from functools import wraps
import threading

from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.container import DIContainer
from src.adapters.primary.auth import JWTBearer, create_jwt_token
from src.adapters.secondary.minio import MinIOAdapter
from src.grpc_server import serve


# 依赖注入容器
container = DIContainer()


def get_current_user_optional(request: Request, credentials: Optional[dict] = Depends(JWTBearer(auto_error=False, required=False))):
    """获取当前用户（可选认证）"""
    return credentials


# Pydantic 数据模型
class AlertReportRequest(BaseModel):
    """告警上报请求"""
    device_id: str = Field(..., min_length=1, max_length=50)
    device_type: str = Field(..., min_length=1, max_length=50)
    alert_type: str = Field(..., min_length=1, max_length=50)
    alert_content: str = Field(..., min_length=1, max_length=2000)
    location: str = Field(..., min_length=1, max_length=200)
    alert_level: int = Field(..., ge=1, le=4)
    extra_data: Dict[str, Any] = None

    @field_validator('alert_content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("告警内容不能为空")
        return v.strip()


class AlertReportResponse(BaseModel):
    """告警上报响应"""
    success: bool
    message: str
    alert_id: str = None
    risk_level: str = None
    plans: List[Dict[str, Any]] = None
    error: str = None


class PlanSearchRequest(BaseModel):
    """预案检索请求"""
    query: str = Field(..., min_length=1, max_length=500)
    event_type: str = None
    top_k: int = Field(default=5, ge=1, le=20)


class PlanSearchResponse(BaseModel):
    """预案检索响应"""
    success: bool
    message: str
    plans: List[Dict[str, Any]] = None
    query: str = None
    error: str = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    service: str
    timestamp: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("EHS AI Service 启动中...")
    grpc_thread = threading.Thread(
        target=lambda: serve(port=50051),
        daemon=True,
    )
    grpc_thread.start()
    yield
    # 关闭时清理
    print("EHS AI Service 关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="EHS AI Service",
    description="EHS 智能安保决策中台 - REST API（六边形架构）",
    version="2.0.0",
    lifespan=lifespan
)

# 配置 CORS - 使用环境变量管理生产环境来源
# 限制 HTTP 方法为最小集，仅允许 API 需要的方法
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 限制为具体方法
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],  # 明确声明需要的 headers
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口（公开）"""
    return HealthResponse(
        status="healthy",
        service="ehs-ai-service",
        timestamp=datetime.now().isoformat()
    )


@app.post("/auth/login", tags=["认证"])
async def login(username: str, password: str):
    """
    用户登录接口

    开发环境：任意用户名密码都返回 token
    生产环境：需对接真实用户系统
    """
    # TODO: 对接真实用户认证系统
    # 开发环境模拟登录
    token = create_jwt_token(
        subject=username,
        extra_data={"username": username, "role": "admin"}
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_MINUTES * 60
    }


@app.post("/auth/refresh", tags=["认证"])
async def refresh_token(current_user: Optional[dict] = Depends(JWTBearer(auto_error=False, required=False))):
    """刷新 Token"""
    if not current_user:
        raise HTTPException(status_code=401, detail="未认证")

    new_token = create_jwt_token(
        subject=current_user.get("sub"),
        extra_data={"username": current_user.get("username")}
    )
    return {
        "access_token": new_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRATION_MINUTES * 60
    }


@app.post("/api/alert/report", response_model=AlertReportResponse)
async def report_alert(
    request: AlertReportRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    告警上报接口

    1. 接收 AIoT 设备告警
    2. 调用 Multi-Agent 工作流
    3. 返回告警 ID、风险等级、关联预案

    认证：可选（开发环境允许匿名）
    """
    try:
        # 生成告警 ID
        alert_id = str(uuid.uuid4())

        # 从容器获取工作流
        workflow = container.get_workflow()

        # 执行工作流
        initial_state = {
            "alert_message": request.alert_content,
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }

        result = workflow.invoke(initial_state)

        return AlertReportResponse(
            success=True,
            message="告警上报成功",
            alert_id=alert_id,
            risk_level=result.get("risk_assessment", {}).get("risk_level", "unknown"),
            plans=result.get("emergency_plans", [])
        )

    except Exception as e:
        return AlertReportResponse(
            success=False,
            message="告警上报失败",
            alert_id=str(uuid.uuid4()),
            error=str(e)
        )


@app.post("/api/plan/search", response_model=PlanSearchResponse)
async def search_plan(
    request: PlanSearchRequest,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    预案检索接口

    1. 接收查询请求
    2. 调用 GraphRAG 检索
    3. 返回预案列表

    认证：可选（开发环境允许匿名）
    """
    try:
        # 从容器获取 GraphRAG
        graph_rag = container.get_graph_rag()

        plans = graph_rag.search(
            query=request.query,
            event_type=request.event_type,
            top_k=request.top_k
        )

        return PlanSearchResponse(
            success=True,
            message="预案检索成功",
            plans=plans,
            query=request.query
        )

    except Exception as e:
        return PlanSearchResponse(
            success=False,
            message="预案检索失败",
            query=request.query,
            error=str(e)
        )


@app.get("/api/alert/list", tags=["告警管理"])
async def get_alert_list(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """
    获取告警列表（Mock 数据）

    TODO: 对接真实告警数据源
    """
    # Mock 告警数据
    mock_alerts = [
        {
            "id": "ALT-001",
            "type": "烟火告警",
            "location": "A 栋 1 楼大厅",
            "riskLevel": "high",
            "status": "pending",
            "time": "2026-04-16T10:30:00Z",
            "deviceId": "DEV-001",
            "content": "红外传感器检测到异常高温"
        },
        {
            "id": "ALT-002",
            "type": "入侵检测",
            "location": "B 栋 3 楼走廊",
            "riskLevel": "medium",
            "status": "processing",
            "time": "2026-04-16T09:15:00Z",
            "deviceId": "DEV-002",
            "content": "移动传感器触发告警"
        },
        {
            "id": "ALT-003",
            "type": "设备故障",
            "location": "C 栋地下室",
            "riskLevel": "low",
            "status": "resolved",
            "time": "2026-04-16T08:00:00Z",
            "deviceId": "DEV-003",
            "content": "水泵压力异常"
        }
    ]

    # 过滤
    filtered = mock_alerts
    if status:
        filtered = [a for a in filtered if a["status"] == status]
    if risk_level:
        filtered = [a for a in filtered if a["riskLevel"] == risk_level]

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]

    return {
        "success": True,
        "data": {
            "total": len(filtered),
            "pending": len([a for a in mock_alerts if a["status"] == "pending"]),
            "processing": len([a for a in mock_alerts if a["status"] == "processing"]),
            "resolved": len([a for a in mock_alerts if a["status"] == "resolved"]),
            "alerts": paginated
        }
    }


@app.get("/api/stats/today", tags=["统计"])
async def get_today_stats():
    """
    获取今日统计（Mock 数据）

    TODO: 对接真实统计数据
    """
    return {
        "success": True,
        "data": {
            "total": 12,
            "pending": 2,
            "processing": 1,
            "resolved": 9,
            "change": "+3 起"
        }
    }


@app.get("/api/graph", tags=["知识图谱"])
async def get_knowledge_graph(query: Optional[str] = None):
    """
    获取知识图谱数据（用于前端可视化）

    可选查询参数：
    - query: 如果提供，返回与该查询相关的子图
    - 不提供：返回完整图谱
    """
    try:
        graph_rag = container.get_graph_rag()

        if query:
            # 返回相关子图
            insights = graph_rag.get_graph_insights(query)
            return {
                "success": True,
                "data": insights,
                "query": query,
            }

        # 返回完整图谱
        kg = graph_rag._knowledge_graph
        if not kg:
            return {
                "success": False,
                "error": "知识图谱未加载",
            }

        # 转换为前端可视化格式
        nodes = []
        edges = []

        for node_id, node_data in kg._graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": node_data.get("name", node_id),
                "type": node_data.get("type", ""),
                "properties": node_data.get("properties", {}),
            })

        for source, target, edge_data in kg._graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "label": edge_data.get("type", ""),
                "description": edge_data.get("properties", {}).get("description", ""),
            })

        return {
            "success": True,
            "data": {
                "nodes": nodes,
                "edges": edges,
                "stats": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                },
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@app.get("/api/graph/buildings/{building_name}/connected", tags=["知识图谱"])
async def get_connected_buildings(building_name: str):
    """
    获取与指定建筑相连/相邻的建筑

    用于演示 GraphRAG 的价值：发现隐含的关联风险
    """
    try:
        graph_rag = container.get_graph_rag()
        kg = graph_rag._knowledge_graph

        if not kg:
            return {"success": False, "error": "知识图谱未加载"}

        connected = kg.get_connected_buildings(building_name)

        return {
            "success": True,
            "data": {
                "building": building_name,
                "connected_buildings": connected,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


class MultimodalAlertRequest(BaseModel):
    """多模态告警上报请求"""
    alert_text: str = Field(..., min_length=1, max_length=2000)
    sensor_data: Optional[str] = None
    device_id: Optional[str] = None
    location: Optional[str] = None


from fastapi import Form


@app.post("/api/alert/report/multimodal", response_model=AlertReportResponse, tags=["多模态"])
async def report_alert_multimodal(
    image: Optional[UploadFile] = File(None, description="监控截图"),
    alert_text: str = Form(..., description="文本告警描述"),
    sensor_data: Optional[str] = Form(None, description="传感器数据 JSON"),
    device_id: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
):
    """
    多模态告警上报接口

    1. 上传图片到 MinIO 存储
    2. 用多模态 LLM 分析图片（识别火焰、烟雾等）
    3. 合并图片分析结果 + 文本告警 → RiskAgent
    4. 返回风险评估 + 预案

    认证：可选
    """
    try:
        alert_id = str(uuid.uuid4())
        image_url = ""

        # 1. 上传图片到 MinIO
        if image and image.file:
            minio = MinIOAdapter(
                endpoint=getattr(settings, "MINIO_ENDPOINT", "localhost:9000"),
                access_key=getattr(settings, "MINIO_ACCESS_KEY", "minioadmin"),
                secret_key=getattr(settings, "MINIO_SECRET_KEY", "minioadmin"),
            )
            image_bytes = await image.read()
            image_url = minio.upload_image(
                object_name=f"alerts/{alert_id}/{image.filename}",
                data=image_bytes,
                content_type=image.content_type or "image/png",
            )

        # 2. 构建增强告警内容
        enhanced_content = alert_text
        if image_url:
            enhanced_content += f"\n[分析图片: {image_url}]"
        if sensor_data:
            enhanced_content += f"\n传感器数据: {sensor_data}"

        # 3. 调用工作流
        workflow = container.get_workflow()
        initial_state = {
            "alert_message": enhanced_content,
            "risk_assessment": None,
            "emergency_plans": [],
            "error": None
        }
        result = workflow.invoke(initial_state)

        return AlertReportResponse(
            success=True,
            message="多模态告警上报成功",
            alert_id=alert_id,
            risk_level=result.get("risk_assessment", {}).get("risk_level", "unknown"),
            plans=result.get("emergency_plans", [])
        )

    except Exception as e:
        return AlertReportResponse(
            success=False,
            message="多模态告警上报失败",
            alert_id=str(uuid.uuid4()),
            error=str(e)
        )
