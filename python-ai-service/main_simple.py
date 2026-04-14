"""EHS AI Service - 简化版（Mock 数据但走真实 API 流程）"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# 创建 FastAPI 应用
app = FastAPI(title="EHS AI Service", description="EHS 智能安保决策中台", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock 预案数据
MOCK_PLANS = {
    "fire": [
        {"title": "火灾事故专项应急预案", "content": "1. 立即启动消防泵 2. 疏散现场人员 3. 通知消防队", "risk_level": "high", "score": 0.95},
        {"title": "消防设备操作指南", "content": "消防泵启动步骤：1. 检查电源 2. 打开阀门 3. 启动按钮", "risk_level": "medium", "score": 0.85},
    ],
    "gas_leak": [
        {"title": "化学品泄漏应急处置预案", "content": "1. 立即疏散人员 2. 关闭泄漏源阀门 3. 启动排风系统", "risk_level": "high", "score": 0.93},
    ],
    "temperature_abnormal": [
        {"title": "机房温度异常处置预案", "content": "1. 检查空调系统 2. 增加临时散热设备 3. 减少设备负载", "risk_level": "medium", "score": 0.90},
    ],
    "intrusion": [
        {"title": "安防入侵应急处置预案", "content": "1. 确认入侵位置 2. 通知保安巡逻 3. 锁定相关区域", "risk_level": "high", "score": 0.92},
    ],
}

# 风险评估映射
RISK_LEVEL_MAP = {
    "fire": "high",
    "gas_leak": "high",
    "temperature_abnormal": "medium",
    "intrusion": "high",
}

# 内存存储告警列表
ALERTS_STORE: List[Dict[str, Any]] = [
    {
        "id": "ALT-20260414-001",
        "type": "fire",
        "typeLabel": "火灾",
        "content": "生产车间检测到浓烟，能见度低于 5 米",
        "level": "critical",
        "location": "生产车间 A 区",
        "timestamp": "2026-04-14T18:30:00",
        "status": "processing",
        "statusLabel": "处理中",
        "planName": "《火灾事故专项应急预案》"
    },
    {
        "id": "ALT-20260414-002",
        "type": "gas_leak",
        "typeLabel": "气体泄漏",
        "content": "甲烷浓度超标 50ppm",
        "level": "high",
        "location": "化学品仓库",
        "timestamp": "2026-04-14T17:15:00",
        "status": "resolved",
        "statusLabel": "已解决",
        "planName": "《化学品泄漏应急处置预案》"
    }
]

# 告警类型映射
ALERT_TYPE_LABEL_MAP = {
    "fire": "火灾",
    "gas_leak": "气体泄漏",
    "temperature_abnormal": "温度异常",
    "intrusion": "入侵检测",
}

# 告警级别映射
ALERT_LEVEL_MAP = {
    "fire": "critical",
    "gas_leak": "high",
    "temperature_abnormal": "medium",
    "intrusion": "high",
}


class AlertReportRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=50)
    device_type: str = Field(..., min_length=1, max_length=50)
    alert_type: str = Field(..., min_length=1, max_length=50)
    alert_content: str = Field(..., min_length=1, max_length=2000)
    location: str = Field(..., min_length=1, max_length=200)
    alert_level: int = Field(..., ge=1, le=4)
    extra_data: Optional[Dict[str, Any]] = None


class AlertReportResponse(BaseModel):
    success: bool
    message: str
    alert_id: str
    risk_level: str
    plans: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        service="ehs-ai-service",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/alert/report", response_model=AlertReportResponse)
async def report_alert(request: AlertReportRequest):
    """告警上报接口"""
    print(f"\n{'='*60}")
    print(f"收到告警上报：{request.alert_type} - {request.location}")
    print(f"{'='*60}")

    # 生成告警 ID
    alert_id = str(uuid.uuid4())
    alert_num = len(ALERTS_STORE) + 1
    alert_timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    # 步骤 1: RiskAgent 风险评估
    print(f"\n[RiskAgent] 开始风险评估...")
    risk_level = RISK_LEVEL_MAP.get(request.alert_type, "medium")
    print(f"   风险等级：{risk_level}")
    print(f"   置信度：0.92")
    print(f"   风险因素：[{request.alert_content}]")
    print(f"   建议操作：[启动应急预案，通知相关人员]")

    # 步骤 2: SearchAgent 预案检索
    print(f"\n[SearchAgent] 检索应急预案...")
    plans = MOCK_PLANS.get(request.alert_type, MOCK_PLANS["fire"])
    print(f"   找到 {len(plans)} 条关联预案:")
    for plan in plans:
        print(f"      - {plan['title']} (匹配度：{plan['score']})")

    # 获取第一条预案名称
    plan_name = plans[0]["title"] if plans else "未知预案"

    # 步骤 3: 存储告警到内存
    new_alert = {
        "id": f"ALT-{alert_timestamp}",
        "type": request.alert_type,
        "typeLabel": ALERT_TYPE_LABEL_MAP.get(request.alert_type, request.alert_type),
        "content": request.alert_content,
        "level": ALERT_LEVEL_MAP.get(request.alert_type, "medium"),
        "location": request.location,
        "timestamp": datetime.now().isoformat(),
        "status": "pending",
        "statusLabel": "待处理",
        "planName": f"《{plan_name}》"
    }
    ALERTS_STORE.insert(0, new_alert)
    print(f"\n[Storage] 告警已存储：{new_alert['id']}")

    print(f"\n{'='*60}")
    print(f"告警上报完成：{alert_id}")
    print(f"{'='*60}\n")

    return AlertReportResponse(
        success=True,
        message="告警上报成功！已启动应急预案检索",
        alert_id=f"ALT-{alert_timestamp}",
        risk_level=risk_level,
        plans=plans
    )


@app.get("/api/alert/list")
async def list_alerts():
    """获取告警列表（支持动态添加）"""
    return {
        "alerts": ALERTS_STORE
    }


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EHS AI Service 启动中...")
    print("="*60)
    print("API 地址：http://localhost:8000")
    print("健康检查：http://localhost:8000/health")
    print("告警上报：POST http://localhost:8000/api/alert/report")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
