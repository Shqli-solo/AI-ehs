# apps/ehs-ai/src/adapters/primary/rest_api.py
"""FastAPI REST API - Primary Adapter"""
import uuid
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.container import Container


# 依赖注入容器
container = Container()


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

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse(
        status="healthy",
        service="ehs-ai-service",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/alert/report", response_model=AlertReportResponse)
async def report_alert(request: AlertReportRequest):
    """
    告警上报接口

    1. 接收 AIoT 设备告警
    2. 调用 Multi-Agent 工作流
    3. 返回告警 ID、风险等级、关联预案
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
async def search_plan(request: PlanSearchRequest):
    """
    预案检索接口

    1. 接收查询请求
    2. 调用 GraphRAG 检索
    3. 返回预案列表
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
