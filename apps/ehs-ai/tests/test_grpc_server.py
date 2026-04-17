"""gRPC Server 单元测试"""
import pytest


def test_health_check_returns_healthy():
    """HealthCheck 应返回 healthy=True"""
    from src.grpc_server import EhsAiServicer
    from src.infrastructure.grpc.proto import ehs_pb2

    servicer = EhsAiServicer()
    request = ehs_pb2.HealthCheckRequest(service="ehs-ai")
    context = None
    response = servicer.HealthCheck(request, context)

    assert response.healthy is True
    assert response.service == "ehs-ai"
    assert response.version == "2.0.0"
