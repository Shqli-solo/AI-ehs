# apps/ehs-ai/src/core/graph_rag/__init__.py
"""GraphRAG 模块 - 知识图谱增强检索"""
from src.core.graph_rag.knowledge_graph import KnowledgeGraph
from src.core.graph_rag.core import GraphRAGCore

__all__ = ["KnowledgeGraph", "GraphRAGCore"]
