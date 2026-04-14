# python-ai-service/src/shared/models.py
"""Pydantic 数据模型 - 用于 API 输入验证"""
import html
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


def validate_not_empty(v: str, field_name: str = "field") -> str:
    """验证字段不为空"""
    if not v or not v.strip():
        raise ValueError(f"{field_name} 不能为空")
    return v.strip()


def validate_content(v: str, max_length: int = 2000) -> str:
    """验证内容长度并防止 XSS 注入"""
    if not v:
        raise ValueError("内容不能为空")
    if len(v) > max_length:
        raise ValueError(f"内容长度不能超过 {max_length} 字符")
    # 使用 html.escape() 进行 XSS 防护（审查修复）
    v = html.escape(v.strip())
    return v


def validate_level(v: int) -> int:
    """验证告警级别（1-4）"""
    if not isinstance(v, int) or v < 1 or v > 4:
        raise ValueError("告警级别必须是 1-4 之间的整数")
    return v


class AlertReportRequest(BaseModel):
    """告警上报请求模型"""
    device_id: str = Field(..., description="设备 ID", min_length=1, max_length=50)
    device_type: str = Field(..., description="设备类型", min_length=1, max_length=50)
    alert_type: str = Field(..., description="告警类型", min_length=1, max_length=50)
    alert_content: str = Field(..., description="告警内容", min_length=1, max_length=2000)
    location: str = Field(..., description="告警位置", min_length=1, max_length=200)
    alert_level: int = Field(..., description="告警级别（1-4）", ge=1, le=4)
    extra_data: Optional[Dict[str, Any]] = Field(default=None, description="额外数据")

    @field_validator('device_id')
    @classmethod
    def _validate_device_id(cls, v: str) -> str:
        return validate_not_empty(v, "设备 ID")

    @field_validator('device_type')
    @classmethod
    def _validate_device_type(cls, v: str) -> str:
        return validate_not_empty(v, "设备类型")

    @field_validator('alert_type')
    @classmethod
    def _validate_alert_type(cls, v: str) -> str:
        return validate_not_empty(v, "告警类型")

    @field_validator('location')
    @classmethod
    def _validate_location(cls, v: str) -> str:
        return validate_not_empty(v, "告警位置")

    @field_validator('alert_content')
    @classmethod
    def _validate_alert_content(cls, v: str) -> str:
        return validate_content(v, 2000)

    @field_validator('alert_level')
    @classmethod
    def _validate_alert_level(cls, v: int) -> int:
        return validate_level(v)


class AlertReportResponse(BaseModel):
    """告警上报响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    alert_id: Optional[str] = Field(default=None, description="告警 ID")
    risk_level: Optional[str] = Field(default=None, description="风险等级")
    plans: Optional[List[Dict[str, Any]]] = Field(default=None, description="关联预案")
    error: Optional[str] = Field(default=None, description="错误信息（如有）")


class PlanSearchRequest(BaseModel):
    """预案检索请求模型"""
    query: str = Field(..., description="查询文本", min_length=1, max_length=500)
    event_type: Optional[str] = Field(default=None, description="事件类型", max_length=50)
    top_k: int = Field(default=5, description="返回结果数量", ge=1, le=20)

    @field_validator('query')
    @classmethod
    def _validate_query(cls, v: str) -> str:
        return validate_content(v, 500)

    @field_validator('top_k')
    @classmethod
    def _validate_top_k(cls, v: int) -> int:
        return min(v, 20)


class PlanSearchResponse(BaseModel):
    """预案检索响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    plans: Optional[List[Dict[str, Any]]] = Field(default=None, description="预案列表")
    query: Optional[str] = Field(default=None, description="查询文本")
    error: Optional[str] = Field(default=None, description="错误信息（如有）")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    service: str = Field(..., description="服务名称")
    timestamp: str = Field(..., description="时间戳")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(default=None, description="详细信息")


class MockPlanData:
    """Mock 预案数据（用于演示）"""

    PLANS = {
        "fire": [
            {
                "title": "火灾事故专项应急预案",
                "content": "1. 立即启动消防泵 2. 疏散现场人员 3. 通知消防队 4. 切断电源 5. 使用灭火器初期灭火",
                "risk_level": "high",
                "source": "ES",
                "score": 0.95
            },
            {
                "title": "消防设备操作指南",
                "content": "消防泵启动步骤：1. 检查电源 2. 打开阀门 3. 启动按钮 4. 检查压力表",
                "risk_level": "medium",
                "source": "Milvus",
                "score": 0.85
            }
        ],
        "gas_leak": [
            {
                "title": "化学品泄漏应急处置预案",
                "content": "1. 立即疏散人员 2. 关闭泄漏源阀门 3. 启动排风系统 4. 佩戴防护装备 5. 通知专业人员处理",
                "risk_level": "high",
                "source": "ES",
                "score": 0.93
            },
            {
                "title": "气体检测报警处置流程",
                "content": "气体报警响应：1. 确认报警真实性 2. 检测浓度 3. 启动应急预案 4. 持续监测",
                "risk_level": "medium",
                "source": "Milvus",
                "score": 0.82
            }
        ],
        "temperature_abnormal": [
            {
                "title": "机房温度异常处置预案",
                "content": "1. 检查空调系统 2. 增加临时散热设备 3. 减少设备负载 4. 通知维修人员",
                "risk_level": "medium",
                "source": "ES",
                "score": 0.90
            }
        ],
        "intrusion": [
            {
                "title": "安防入侵应急处置预案",
                "content": "1. 确认入侵位置 2. 通知保安巡逻 3. 锁定相关区域 4. 调取监控录像 5. 必要时报警",
                "risk_level": "high",
                "source": "ES",
                "score": 0.92
            }
        ]
    }

    @classmethod
    def get_plans(cls, alert_type: str) -> List[Dict[str, Any]]:
        """根据告警类型返回预案"""
        return cls.PLANS.get(alert_type, cls.PLANS["fire"])
