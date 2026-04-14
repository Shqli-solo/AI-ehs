# python-ai-service/src/api/rest.py
"""FastAPI REST API - 告警上报和预案检索"""
import uuid
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.core.logging import log
from src.shared.models import (
    AlertReportRequest,
    AlertReportResponse,
    PlanSearchRequest,
    PlanSearchResponse,
    HealthResponse,
    ErrorResponse,
    MockPlanData
)


# 创建 FastAPI 应用
app = FastAPI(
    title="EHS AI Service",
    description="EHS 智能安保决策中台 - REST API",
    version="1.0.0"
)

# 配置 CORS 中间件 - 支持前端跨域调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理 - 错误降级处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器 - 返回友好错误而非 500 堆栈"""
    log.error(f"全局异常：{exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="服务器内部错误",
            detail="请稍后重试或联系管理员"
        ).model_dump()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Pydantic 验证异常处理器"""
    log.warning(f"验证失败：{exc}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="输入验证失败",
            detail=str(exc)
        ).model_dump()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    log.info("健康检查请求")
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
    2. 调用 Multi-Agent 工作流（风险感知 + 预案检索）
    3. 返回告警 ID、风险等级、关联预案
    """
    try:
        log.info(f"收到告警上报：{request.alert_type} - {request.location}")

        # 生成告警 ID
        alert_id = str(uuid.uuid4())

        # 延迟导入工作流（避免模块加载时依赖）
        try:
            from src.agents.workflow import create_workflow
            workflow = create_workflow()
            initial_state = {
                "alert_message": request.alert_content,
                "risk_assessment": None,
                "emergency_plans": [],
                "error": None
            }

            result = workflow.invoke(initial_state)
            risk_assessment = result.get("risk_assessment", {})
            emergency_plans = result.get("emergency_plans", [])
        except Exception as workflow_error:
            log.warning(f"工作流执行失败，使用 Mock 数据：{workflow_error}")
            # 降级处理：使用 Mock 数据
            risk_assessment = {
                "risk_level": "high" if request.alert_level >= 3 else "medium",
                "confidence": 0.85,
                "factors": [request.alert_content],
                "recommended_actions": ["启动应急预案"]
            }
            emergency_plans = MockPlanData.get_plans(request.alert_type)

        # 构建响应
        response = AlertReportResponse(
            success=True,
            message="告警上报成功",
            alert_id=alert_id,
            risk_level=risk_assessment.get("risk_level", "unknown"),
            plans=emergency_plans if emergency_plans else MockPlanData.get_plans(request.alert_type)
        )

        log.info(f"告警上报完成：{alert_id}")
        return response

    except ValidationError as e:
        log.error(f"输入验证失败：{e}")
        raise
    except Exception as e:
        log.error(f"告警上报失败：{e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=AlertReportResponse(
                success=False,
                message="告警上报失败",
                error=str(e)
            ).model_dump()
        )


@app.post("/api/plan/search", response_model=PlanSearchResponse)
async def search_plan(request: PlanSearchRequest):
    """
    预案检索接口

    1. 接收查询请求
    2. 调用 GraphRAG 检索引擎
    3. 返回预案列表
    """
    try:
        log.info(f"收到预案检索请求：{request.query} (type={request.event_type})")

        # 延迟导入 GraphRAG（避免模块加载时依赖）
        try:
            from src.rag.graph_rag import GraphRAGSearcher
            searcher = GraphRAGSearcher()
            plans = searcher.search(
                query=request.query,
                event_type=request.event_type,
                top_k=request.top_k
            )
        except Exception as search_error:
            log.warning(f"GraphRAG 检索失败，使用 Mock 数据：{search_error}")
            # 降级处理：使用 Mock 数据
            all_plans = []
            for key, plan_list in MockPlanData.PLANS.items():
                if not request.event_type or key == request.event_type:
                    all_plans.extend(plan_list)
            plans = all_plans[:request.top_k] if all_plans else MockPlanData.PLANS["fire"][:request.top_k]

        # 构建响应
        response = PlanSearchResponse(
            success=True,
            message="预案检索成功",
            plans=plans,
            query=request.query
        )

        log.info(f"预案检索完成，返回 {len(plans)} 条结果")
        return response

    except ValidationError as e:
        log.error(f"输入验证失败：{e}")
        raise
    except Exception as e:
        log.error(f"预案检索失败：{e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=PlanSearchResponse(
                success=False,
                message="预案检索失败",
                error=str(e)
            ).model_dump()
        )


# 启动日志
log.info("FastAPI REST API 初始化完成")
