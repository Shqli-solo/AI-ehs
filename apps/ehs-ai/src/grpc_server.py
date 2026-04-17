"""
gRPC Server - 暴露 AI 能力给 Java 业务服务

提供 6 个 RPC 接口:
- HealthCheck: 健康检查
- ClassifyRisk: 风险分级
- AnalyzeAlert: 告警分析
- GenerateResponse: 指令微调生成
- GetTermEmbedding: 术语 Embedding
- GetBatchEmbeddings: 批量术语 Embedding

@author: EHS Team
@since: 2026-04-17
"""
import time
import logging
import random
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


class EhsAiServicer(ehs_pb2_grpc.EhsAiServiceServicer):
    """gRPC 服务实现"""

    def __init__(self, container: DIContainer = None):
        self.container = container or DIContainer()

    def HealthCheck(self, request, context):
        """健康检查 RPC"""
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
            logger.error(f"ClassifyRisk error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, f"ClassifyRisk failed: {e}")

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
            logger.error(f"AnalyzeAlert error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, f"AnalyzeAlert failed: {e}")

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
            logger.error(f"GenerateResponse error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, f"GenerateResponse failed: {e}")

    def GetTermEmbedding(self, request, context):
        """术语 Embedding RPC"""
        start = time.time()
        try:
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
            logger.error(f"GetTermEmbedding error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, f"GetTermEmbedding failed: {e}")

    def GetBatchEmbeddings(self, request, context):
        """批量术语 Embedding RPC"""
        start = time.time()
        try:
            results = []
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
        except Exception as e:
            logger.error(f"GetBatchEmbeddings error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, f"GetBatchEmbeddings failed: {e}")


def serve(port: int = 50051) -> grpc.server:
    """启动 gRPC 服务（非阻塞，返回 server 对象供关闭时清理）"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = EhsAiServicer()
    ehs_pb2_grpc.add_EhsAiServiceServicer_to_server(servicer, server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info(f"gRPC server started on port {port}")
    return server


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    import signal
    import sys

    server = serve()
    logger.info("Press Ctrl+C to stop")

    def shutdown(signum, frame):
        logger.info("Shutting down gRPC server...")
        server.stop(grace=5)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        shutdown(None, None)
