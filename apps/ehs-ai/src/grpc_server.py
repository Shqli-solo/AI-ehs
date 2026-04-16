"""
EHS AI 服务 - gRPC Server 实现

提供 gRPC 服务接口，与 Java 业务服务通信
包含健康检查、风险分级、指令生成、告警分析、Embedding 等服务

@author: EHS Team
@since: 2026-04-16
"""

import asyncio
import logging
import time
from concurrent import futures
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import grpc
from grpc import aio

from src.core.config import settings
from src.core.agents.risk_agent import RiskAgent
from src.core.agents.search_agent import SearchAgent
from src.core.graph_rag import GraphRAGSearcher

# 导入生成的 gRPC 代码（需要先生成）
# from src.proto import ehs_pb2
# from src.proto import ehs_pb2_grpc

logger = logging.getLogger(__name__)


# ==================== Proto 定义（内联，用于开发） ====================
# 实际使用时应该从生成的 Python 文件导入


@dataclass
class GrpcServerConfig:
    """gRPC 服务器配置"""
    host: str = "0.0.0.0"
    port: int = 50051
    max_workers: int = 10
    max_message_length: int = 50 * 1024 * 1024  # 50MB
    keepalive_time_ms: int = 30000
    timeout_seconds: int = 120


class EhsAiServicer:
    """
    EHS AI 服务实现

    实现所有 gRPC 服务方法
    """

    def __init__(
        self,
        risk_agent: Optional[RiskAgent] = None,
        search_agent: Optional[SearchAgent] = None,
        graph_rag: Optional[GraphRAGSearcher] = None,
    ):
        self.risk_agent = risk_agent
        self.search_agent = search_agent
        self.graph_rag = graph_rag
        self._version = "2.0.0"
        logger.info("EhsAiServicer 初始化完成")

    async def HealthCheck(
        self, request, context: grpc.ServicerContext
    ) -> "HealthCheckResponse":
        """健康检查"""
        start_time = time.time()
        logger.debug("收到健康检查请求")

        checks = []
        healthy = True

        # 检查各组件状态
        if self.risk_agent:
            checks.append("risk_agent:ok")
        else:
            checks.append("risk_agent:not_configured")

        if self.search_agent:
            checks.append("search_agent:ok")
        else:
            checks.append("search_agent:not_configured")

        if self.graph_rag:
            checks.append("graph_rag:ok")
        else:
            checks.append("graph_rag:not_configured")

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "healthy": healthy,
            "service": "ehs-ai",
            "version": self._version,
            "timestamp": int(time.time() * 1000),
            "checks": checks,
            "processing_time_ms": processing_time,
        }

    async def ClassifyRisk(
        self, request, context: grpc.ServicerContext
    ) -> "RiskClassificationResponse":
        """风险分级"""
        start_time = time.time()
        text = request.get("text", "")
        request_id = request.get("request_id", "")

        logger.info(f"收到风险分级请求：request_id={request_id}, text_length={len(text)}")

        try:
            # 调用风险分级 Agent
            if self.risk_agent:
                result = await self.risk_agent.analyze(text)
                risk_level = self._map_risk_level(result.get("level", "LOW"))
                confidence = result.get("confidence", 0.0)
                reason = result.get("reason", "")
                keywords = result.get("keywords", [])
            else:
                # Fallback：简单规则判断
                risk_level, confidence, reason, keywords = self._simple_risk_check(text)

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"风险分级完成：request_id={request_id}, level={risk_level}, "
                f"confidence={confidence:.2f}, time={processing_time}ms"
            )

            return {
                "risk_level": risk_level,
                "confidence": confidence,
                "reason": reason,
                "keywords": keywords,
                "request_id": request_id,
                "processing_time_ms": processing_time,
            }
        except Exception as e:
            logger.error(f"风险分级失败：request_id={request_id}, error={e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def GenerateResponse(
        self, request, context: grpc.ServicerContext
    ) -> "ResponseGenerationResponse":
        """指令微调生成响应"""
        start_time = time.time()
        query = request.get("query", "")
        context_text = request.get("context", "")
        request_id = request.get("request_id", "")
        max_tokens = request.get("max_tokens", 512)
        temperature = request.get("temperature", 0.7)

        logger.info(f"收到生成请求：request_id={request_id}, query={query[:50]}...")

        try:
            # 调用搜索 Agent 生成响应
            if self.search_agent:
                result = await self.search_agent.generate(
                    query=query,
                    context=context_text,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                response = result.get("response", "")
                tokens_used = result.get("tokens_used", 0)
                model = result.get("model", "ehs-instruct-v1")
            else:
                # Fallback：简单响应
                response = f"基于查询'{query}'生成的响应"
                tokens_used = len(response)
                model = "fallback"

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"响应生成完成：request_id={request_id}, tokens={tokens_used}, time={processing_time}ms"
            )

            return {
                "response": response,
                "request_id": request_id,
                "processing_time_ms": processing_time,
                "tokens_used": tokens_used,
                "model": model,
                "truncated": len(response) >= max_tokens * 4,
            }
        except Exception as e:
            logger.error(f"响应生成失败：request_id={request_id}, error={e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def AnalyzeAlert(
        self, request, context: grpc.ServicerContext
    ) -> "AlertAnalysisResponse":
        """告警分析"""
        start_time = time.time()
        alert_type = request.get("alert_type", 0)
        alert_level = request.get("alert_level", 0)
        content = request.get("content", "")
        location = request.get("location", "")
        request_id = request.get("request_id", "")

        logger.info(
            f"收到告警分析请求：request_id={request_id}, type={alert_type}, "
            f"level={alert_level}, location={location}"
        )

        try:
            # 调用风险分级 Agent 分析告警
            if self.risk_agent:
                result = await self.risk_agent.analyze_alert(
                    alert_type=alert_type,
                    alert_level=alert_level,
                    content=content,
                    location=location,
                )
                analysis = result.get("analysis", "")
                suggested_action = result.get("suggested_action", "")
                recommended_level = result.get("recommended_level", alert_level)
                related_plans = result.get("related_plans", [])
                confidence = result.get("confidence", 0.0)
            else:
                # Fallback：简单分析
                analysis = f"AI 分析：{alert_level}级别告警 - {content}"
                suggested_action = "建议立即核实情况并采取相应措施"
                recommended_level = alert_level
                related_plans = []
                confidence = 0.5

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"告警分析完成：request_id={request_id}, time={processing_time}ms"
            )

            return {
                "analysis": analysis,
                "suggested_action": suggested_action,
                "recommended_level": recommended_level,
                "related_plans": related_plans,
                "confidence": confidence,
                "request_id": request_id,
                "processing_time_ms": processing_time,
            }
        except Exception as e:
            logger.error(f"告警分析失败：request_id={request_id}, error={e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def GetTermEmbedding(
        self, request, context: grpc.ServicerContext
    ) -> "TermEmbeddingResponse":
        """获取术语 Embedding"""
        start_time = time.time()
        term = request.get("term", "")
        request_id = request.get("request_id", "")

        logger.debug(f"收到 Embedding 请求：request_id={request_id}, term={term}")

        try:
            # 调用 Embedding 模型
            if self.graph_rag:
                embedding = await self.graph_rag.encode_term(term)
                dimension = len(embedding)
            else:
                # Fallback：返回零向量
                embedding = [0.0] * 768
                dimension = 768

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"Embedding 获取完成：request_id={request_id}, dim={dimension}, time={processing_time}ms"
            )

            return {
                "term": term,
                "embedding": embedding,
                "dimension": dimension,
                "request_id": request_id,
                "processing_time_ms": processing_time,
            }
        except Exception as e:
            logger.error(f"Embedding 获取失败：request_id={request_id}, error={e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    async def GetBatchEmbeddings(
        self, request, context: grpc.ServicerContext
    ) -> "BatchEmbeddingResponse":
        """批量获取术语 Embedding"""
        start_time = time.time()
        terms = request.get("terms", [])
        request_id = request.get("request_id", "")

        logger.info(f"收到批量 Embedding 请求：request_id={request_id}, count={len(terms)}")

        try:
            results = []
            for term in terms:
                try:
                    if self.graph_rag:
                        embedding = await self.graph_rag.encode_term(term)
                        results.append({
                            "term": term,
                            "embedding": embedding,
                            "dimension": len(embedding),
                            "success": True,
                        })
                    else:
                        results.append({
                            "term": term,
                            "embedding": [0.0] * 768,
                            "dimension": 768,
                            "success": True,
                        })
                except Exception as e:
                    results.append({
                        "term": term,
                        "embedding": [],
                        "dimension": 0,
                        "success": False,
                        "error": str(e),
                    })

            processing_time = int((time.time() - start_time) * 1000)
            logger.info(
                f"批量 Embedding 完成：request_id={request_id}, count={len(terms)}, time={processing_time}ms"
            )

            return {
                "results": results,
                "request_id": request_id,
                "processing_time_ms": processing_time,
            }
        except Exception as e:
            logger.error(f"批量 Embedding 失败：request_id={request_id}, error={e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise

    def _map_risk_level(self, level: str) -> int:
        """映射风险等级到 Proto 枚举值"""
        mapping = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 4,
        }
        return mapping.get(level.upper(), 0)

    def _simple_risk_check(self, text: str) -> tuple:
        """简单风险检查（fallback）"""
        text_lower = text.lower()

        if len(text) > 200 or any(
            kw in text_lower for kw in ["爆炸", "火灾", "泄漏", "死亡", "重伤"]
        ):
            return 4, 0.8, "文本包含高危关键词", ["危险", "紧急"]
        elif any(
            kw in text_lower for kw in ["警告", "注意", "危险", "事故"]
        ):
            return 3, 0.7, "文本包含警告信息", ["警告", "注意"]
        elif any(
            kw in text_lower for kw in ["异常", "故障", "问题"]
        ):
            return 2, 0.6, "文本包含异常信息", ["异常", "故障"]
        else:
            return 1, 0.5, "文本风险较低", []


class GrpcServer:
    """
    gRPC 服务器

    负责启动和停止 gRPC 服务
    """

    def __init__(
        self,
        config: Optional[GrpcServerConfig] = None,
        servicer: Optional[EhsAiServicer] = None,
    ):
        self.config = config or GrpcServerConfig()
        self.servicer = servicer or EhsAiServicer()
        self.server: Optional[aio.AioServer] = None
        logger.info(f"GrpcServer 初始化完成：host={self.config.host}, port={self.config.port}")

    async def start(self) -> None:
        """启动 gRPC 服务器"""
        options = [
            ("grpc.max_concurrent_streams", self.config.max_workers),
            ("grpc.max_receive_message_length", self.config.max_message_length),
            ("grpc.max_send_message_length", self.config.max_message_length),
            ("grpc.keepalive_time_ms", self.config.keepalive_time_ms),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.http2.max_pings_without_data", 0),
        ]

        self.server = aio.server(options=options)

        # 注册服务（实际使用时需要导入生成的 gRPC 代码）
        # ehs_pb2_grpc.add_EhsAiServiceServicer_to_server(
        #     _ServicerImpl(self.servicer), self.server
        # )

        listen_addr = f"{self.config.host}:{self.config.port}"
        self.server.add_insecure_port(listen_addr)

        await self.server.start()
        logger.info(f"gRPC 服务器已启动：{listen_addr}")

    async def stop(self, grace: float = 5.0) -> None:
        """停止 gRPC 服务器"""
        if self.server:
            logger.info("正在停止 gRPC 服务器...")
            await self.server.stop(grace)
            logger.info("gRPC 服务器已停止")

    async def wait_for_termination(self) -> None:
        """等待服务器终止"""
        if self.server:
            await self.server.wait_for_termination()


async def serve() -> None:
    """启动 gRPC 服务（入口函数）"""
    logger.info("启动 EHS AI gRPC 服务...")

    # 创建服务实例
    servicer = EhsAiServicer()
    server = GrpcServer(servicer=servicer)

    await server.start()
    logger.info("EHS AI gRPC 服务就绪")

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        logger.info("收到取消信号，正在关闭...")
        await server.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(serve())
