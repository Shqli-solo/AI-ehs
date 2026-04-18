# apps/ehs-ai/src/adapters/primary/rest_api.py
"""FastAPI REST API - Primary Adapter"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from functools import wraps
import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.container import DIContainer
from src.adapters.primary.auth import JWTBearer, create_jwt_token
from src.adapters.secondary.minio import MinIOAdapter
from src.grpc_server import serve
from src.monitoring.metrics import MetricsMiddleware


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
    logger.info("EHS AI Service 启动中...")
    grpc_server = serve(port=50051)

    # 初始化种子数据
    _seed_alerts_if_empty()

    yield
    # 关闭时清理
    logger.info("EHS AI Service 关闭中，停止 gRPC 服务...")
    grpc_server.stop(grace=5)


def _seed_alerts_if_empty():
    """如果数据库为空，插入种子数据"""
    try:
        alert_repo = container.get_alert_repository()
    except Exception as e:
        logger.warning(f"种子数据初始化失败: {e}")
        return

    if alert_repo.count_alerts() > 0:
        return

    seed_data = [
        {
            "alert_id": "a1b2c3d4-0001-4000-8000-000000000001",
            "device_id": "DEV-001",
            "device_type": "烟雾传感器",
            "alert_type": "烟火告警",
            "alert_content": "红外传感器检测到A栋1楼大厅温度异常升高，疑似火情",
            "location": "A栋1楼大厅",
            "alert_level": 4,
            "risk_level": "high",
            "status": "pending",
            "plans": [{"title": "火灾应急预案", "content": "1. 确认火情\n2. 启动消防系统\n3. 疏散人员", "risk_level": "high"}],
        },
        {
            "alert_id": "a1b2c3d4-0002-4000-8000-000000000002",
            "device_id": "DEV-002",
            "device_type": "红外移动传感器",
            "alert_type": "入侵检测",
            "alert_content": "夜间B栋3楼走廊移动传感器触发告警",
            "location": "B栋3楼走廊",
            "alert_level": 2,
            "risk_level": "medium",
            "status": "processing",
            "plans": [],
        },
        {
            "alert_id": "a1b2c3d4-0003-4000-8000-000000000003",
            "device_id": "DEV-003",
            "device_type": "水压传感器",
            "alert_type": "设备故障",
            "alert_content": "C栋地下室水泵压力异常，低于正常值30%",
            "location": "C栋地下室",
            "alert_level": 1,
            "risk_level": "low",
            "status": "resolved",
            "plans": [],
        },
        {
            "alert_id": "a1b2c3d4-0004-4000-8000-000000000004",
            "device_id": "DEV-004",
            "device_type": "燃气传感器",
            "alert_type": "燃气泄漏",
            "alert_content": "食堂燃气管道检测到轻微泄漏，浓度超过阈值",
            "location": "D栋食堂",
            "alert_level": 3,
            "risk_level": "high",
            "status": "pending",
            "plans": [{"title": "燃气泄漏应急预案", "content": "1. 关闭燃气总阀\n2. 打开窗户通风\n3. 禁止明火", "risk_level": "high"}],
        },
        {
            "alert_id": "a1b2c3d4-0005-4000-8000-000000000005",
            "device_id": "DEV-005",
            "device_type": "温度传感器",
            "alert_type": "温度异常",
            "alert_content": "机房空调故障，温度持续上升至35°C",
            "location": "A栋5楼机房",
            "alert_level": 2,
            "risk_level": "medium",
            "status": "resolved",
            "plans": [],
        },
    ]

    for alert in seed_data:
        alert_repo.save_alert(alert)
    logger.info(f"种子数据初始化完成，插入 {len(seed_data)} 条告警")


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

# 注册 Prometheus metrics 端点和中间件
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.add_middleware(MetricsMiddleware)

@app.get("/health", tags=["系统"])
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

        # 调用 Multi-Agent 工作流
        risk_level = "unknown"
        plans = []
        workflow_error = None
        try:
            workflow = container.get_workflow()
            initial_state = {
                "alert_message": request.alert_content,
                "risk_assessment": None,
                "emergency_plans": [],
                "error": None
            }
            result = workflow.invoke(initial_state)
            risk_level = result.get("risk_assessment", {}).get("risk_level", "unknown")
            plans = result.get("emergency_plans", [])
            workflow_error = result.get("error")
        except Exception as e:
            workflow_error = str(e)
            logger.warning(f"工作流执行失败: {workflow_error}")

        # 保存到 PostgreSQL
        alert_repo = container.get_alert_repository()
        alert_repo.save_alert({
            "alert_id": alert_id,
            "device_id": request.device_id,
            "device_type": request.device_type,
            "alert_type": request.alert_type,
            "alert_content": request.alert_content,
            "location": request.location,
            "alert_level": request.alert_level,
            "risk_level": risk_level,
            "status": "pending",
            "plans": plans,
        })

        if workflow_error:
            return AlertReportResponse(
                success=True,
                message=f"告警已保存（AI 分析失败: {workflow_error[:50]}...）",
                alert_id=alert_id,
                risk_level=risk_level,
                plans=plans,
            )

        return AlertReportResponse(
            success=True,
            message="告警上报成功",
            alert_id=alert_id,
            risk_level=risk_level,
            plans=plans,
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
    """获取告警列表（PostgreSQL 真实数据）"""
    try:
        alert_repo = container.get_alert_repository()
        db_alerts = alert_repo.list_alerts(status=status, risk_level=risk_level, page=page, page_size=page_size)

        alerts = []
        for a in db_alerts:
            alerts.append({
                "id": a.get("alert_id", ""),
                "type": a.get("alert_type", ""),
                "location": a.get("location", ""),
                "riskLevel": a.get("risk_level", "unknown"),
                "status": a.get("status", "pending"),
                "time": a.get("created_at", ""),
                "deviceId": a.get("device_id", ""),
                "content": a.get("alert_content", ""),
            })

        # 获取总数用于分页
        total = alert_repo.count_alerts(status=status, risk_level=risk_level)

        return {
            "success": True,
            "data": {
                "total": total,
                "alerts": alerts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/today", tags=["统计"])
async def get_today_stats():
    """获取今日统计（PostgreSQL 真实数据）"""
    try:
        alert_repo = container.get_alert_repository()
        stats = alert_repo.get_stats()

        # 计算变化量（简化：较昨日固定值，后续可按日期统计）
        yesterday_count = max(0, stats.get("total", 0) - 1)

        return {
            "success": True,
            "data": {
                "total": stats.get("total", 0),
                "pending": stats.get("pending", 0),
                "processing": stats.get("processing", 0),
                "resolved": stats.get("resolved", 0),
                "change": f"+{yesterday_count} 起"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
