# apps/ehs-ai/src/adapters/primary/rest_api.py
"""FastAPI REST API - Primary Adapter"""
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from functools import wraps

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from src.container import Container
from src.adapters.primary.auth import JWTBearer, create_jwt_token


# 依赖注入容器
container = Container()


def get_current_user_optional(request: Request, credentials: Optional[dict] = Depends(JWTBearer(auto_error=False, required=False))):
    """获取当前用户（可选认证）"""
    return credentials


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
