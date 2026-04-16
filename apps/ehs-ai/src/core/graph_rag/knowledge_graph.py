# apps/ehs-ai/src/core/graph_rag/knowledge_graph.py
"""
知识图谱 - GraphRAG 的核心组件

为什么用 GraphRAG 而不是传统 RAG？

传统 RAG 的局限：
- 只能检索独立文档片段，无法理解实体间的关系
- 例："A 栋 3 楼火灾" → 传统 RAG 只能找到包含这些词的文档
- 但无法回答："A 栋和 B 栋之间有连廊，火势会蔓延吗？需要疏散哪些区域？"

GraphRAG 的优势：
- 构建知识图谱：建筑 → 楼层 → 房间 → 设备 → 危险源 → 应急预案
- 查询时先检索相关子图，再结合子图上下文进行 RAG
- 能回答跨实体的关系查询，发现隐含风险

面试演示：
1. 传统 RAG："A 栋火灾" → 返回 A 栋的预案
2. GraphRAG："A 栋火灾" → 返回 A 栋预案 + "A 栋与 B 栋有连廊" +
   "B 栋有化学品仓库，需要额外疏散"
3. 这就是为什么用 GraphRAG
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple

import networkx as nx

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    轻量级知识图谱（基于 NetworkX，不依赖外部图数据库）

    实体类型：
    - Building（建筑）
    - Floor（楼层）
    - Room（房间）
    - Equipment（设备）
    - Hazard（危险源）
    - Plan（应急预案）

    关系类型：
    - part_of（属于）
    - located_on（位于某楼层）
    - located_in（位于某建筑）
    - installed_in（安装于）
    - serves（服务于）
    - protects（保护）
    - affects（影响）
    - mitigated_by（被...缓解）
    - located_at（位于某处）
    - originates_from（源自）
    - addresses（应对）
    - covers（覆盖）
    - connected_by_corridor（连廊连接）
    - adjacent_to（相邻）
    - near（附近）
    """

    def __init__(self, graph_data_path: Optional[str] = None):
        """
        初始化知识图谱

        Args:
            graph_data_path: 知识图谱 JSON 数据文件路径
        """
        self._graph = nx.MultiDiGraph()
        self._entity_index: Dict[str, Dict[str, Any]] = {}
        self._plan_index: Dict[str, Dict[str, Any]] = {}

        if graph_data_path:
            self.load_from_json(graph_data_path)

    def load_from_json(self, path: str):
        """从 JSON 文件加载知识图谱"""
        logger.info(f"加载知识图谱: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 构建图
        for entity in data.get("entities", []):
            entity_id = entity["id"]
            self._graph.add_node(
                entity_id,
                type=entity["type"],
                name=entity["name"],
                properties=entity.get("properties", {}),
            )
            # 建立索引
            if entity["type"] == "Plan":
                self._plan_index[entity_id] = entity
            self._entity_index[entity_id] = entity

        # 添加关系
        for relation in data.get("relations", []):
            self._graph.add_edge(
                relation["from"],
                relation["to"],
                type=relation["type"],
                properties=relation.get("properties", {}),
            )

        logger.info(
            f"知识图谱加载完成: "
            f"{self._graph.number_of_nodes()} 个节点, "
            f"{self._graph.number_of_edges()} 条边"
        )

    def retrieve_subgraph(
        self,
        query: str,
        top_k: int = 5,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        检索与查询相关的子图

        这是 GraphRAG 的核心：先找到与查询相关的实体节点，
        然后通过图遍历找到其邻居和关联节点，构建上下文。

        Args:
            query: 查询文本
            top_k: 返回的根节点数量
            max_depth: 图遍历最大深度

        Returns:
            相关子图上下文列表
        """
        # 1. 找到查询中提及的实体
        matched_entities = self._match_entities(query)

        if not matched_entities:
            return []

        # 2. 从匹配实体出发，遍历图找到相关节点
        subgraph_context = []
        visited: Set[str] = set()

        for entity_id, match_score in matched_entities[:top_k]:
            if entity_id in visited:
                continue
            visited.add(entity_id)

            # 获取节点信息
            if entity_id in self._graph:
                node_data = self._graph.nodes[entity_id]
                subgraph_context.append({
                    "entity_id": entity_id,
                    "type": node_data.get("type", ""),
                    "name": node_data.get("name", ""),
                    "properties": node_data.get("properties", {}),
                    "match_score": match_score,
                    "relations": [],
                })

                # BFS 遍历邻居节点
                self._traverse_neighbors(
                    entity_id,
                    subgraph_context,
                    visited,
                    max_depth=max_depth,
                    depth=0
                )

        return subgraph_context

    def get_related_plans(self, query: str) -> List[Dict[str, Any]]:
        """
        获取与查询相关的应急预案（通过图谱关联）

        Args:
            query: 查询文本

        Returns:
            相关预案列表，每个包含图谱关系说明
        """
        matched_entities = self._match_entities(query)
        related_plans = []
        seen_plans: Set[str] = set()

        for entity_id, match_score in matched_entities:
            # BFS 找到所有关联的 Plan 节点
            for neighbor in nx.bfs_tree(self._graph, entity_id, depth_limit=3):
                if neighbor in seen_plans:
                    continue

                if neighbor in self._plan_index:
                    seen_plans.add(neighbor)
                    plan = self._plan_index[neighbor]

                    # 找到从查询实体到该预案的路径
                    path = self._find_path_to_plan(entity_id, neighbor)

                    related_plans.append({
                        "id": plan.get("properties", {}).get("plan_id", neighbor),
                        "title": plan["name"],
                        "risk_level": plan.get("properties", {}).get("risk_level", "unknown"),
                        "relevance_path": path,
                        "match_score": match_score,
                    })

        # 按相关度排序
        related_plans.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return related_plans

    def enrich_query(self, query: str) -> str:
        """
        用图谱信息增强查询

        将图谱中发现的关联实体和关系注入查询，
        使后续的传统检索（BM25 / 向量）能利用图谱上下文。

        Args:
            query: 原始查询

        Returns:
            增强后的查询
        """
        subgraph = self.retrieve_subgraph(query, top_k=3, max_depth=2)

        if not subgraph:
            return query

        # 提取关键关联信息
        context_parts = []
        for node in subgraph:
            if node["type"] == "Hazard":
                context_parts.append(f"危险源: {node['name']}")
            elif node["type"] == "Building":
                # 查找该建筑的连接关系
                for rel in node.get("relations", []):
                    context_parts.append(rel.get("description", ""))
            elif node["type"] == "Plan":
                context_parts.append(f"相关预案: {node['name']}")

        if context_parts:
            context = "；".join(filter(None, context_parts))
            return f"{query}。相关上下文：{context}"

        return query

    def get_entity_info(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """获取实体信息"""
        for entity_id, entity in self._entity_index.items():
            if entity["name"] == entity_name:
                return entity
        return None

    def get_connected_buildings(self, building_name: str) -> List[str]:
        """获取与指定建筑相连的其他建筑（用于判断火灾蔓延风险）"""
        for entity_id, entity in self._entity_index.items():
            if entity["type"] == "Building" and entity["name"] == building_name:
                connected = []
                for neighbor in self._graph.neighbors(entity_id):
                    edge_data = self._graph[entity_id][neighbor]
                    for edge_key, edge_attrs in edge_data.items():
                        if edge_attrs.get("type") in (
                            "connected_by_corridor", "adjacent_to", "near"
                        ):
                            neighbor_data = self._graph.nodes[neighbor]
                            if neighbor_data.get("type") == "Building":
                                connected.append(neighbor_data["name"])
                return connected
        return []

    # ============================================
    # 私有方法
    # ============================================

    def _match_entities(self, query: str) -> List[Tuple[str, float]]:
        """
        匹配查询中提及的实体

        使用关键词匹配（生产环境可用 LLM 做 NER）
        """
        matches = []
        query_lower = query.lower()

        for entity_id, entity in self._entity_index.items():
            name = entity["name"].lower()
            # 精确匹配
            if name in query_lower:
                score = 1.0
                matches.append((entity_id, score))
            # 部分匹配
            elif any(word in query_lower for word in name if len(word) > 1):
                score = 0.5
                matches.append((entity_id, score))

        # 按分数排序
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _traverse_neighbors(
        self,
        entity_id: str,
        context: List[Dict],
        visited: Set[str],
        max_depth: int,
        depth: int
    ):
        """BFS 遍历邻居节点，构建子图上下文"""
        if depth >= max_depth:
            return

        for neighbor in self._graph.neighbors(entity_id):
            if neighbor in visited:
                continue
            visited.add(neighbor)

            if neighbor not in self._graph:
                continue

            neighbor_data = self._graph.nodes[neighbor]
            edge_data = self._graph[entity_id][neighbor]
            # 获取第一个 edge 的 type
            edge_type = ""
            edge_desc = ""
            for edge_key, edge_attrs in edge_data.items():
                edge_type = edge_attrs.get("type", "")
                edge_desc = edge_attrs.get("properties", {}).get("description", "")
                break

            relation_info = {
                "from_entity": entity_id,
                "to_entity": neighbor,
                "to_name": neighbor_data.get("name", ""),
                "to_type": neighbor_data.get("type", ""),
                "relation_type": edge_type,
                "description": edge_desc,
            }

            # 添加到上下文中最近匹配的节点的 relations 中
            for ctx_node in reversed(context):
                if ctx_node["entity_id"] == entity_id:
                    ctx_node["relations"].append(relation_info)
                    break

            # 如果是重要节点类型（Hazard, Plan, Building），也加入上下文
            if neighbor_data.get("type") in ("Hazard", "Plan", "Building", "Room"):
                context.append({
                    "entity_id": neighbor,
                    "type": neighbor_data.get("type", ""),
                    "name": neighbor_data.get("name", ""),
                    "properties": neighbor_data.get("properties", {}),
                    "match_score": 0.5 - depth * 0.15,
                    "relations": [],
                })

            # 继续遍历
            self._traverse_neighbors(
                neighbor, context, visited, max_depth, depth + 1
            )

    def _find_path_to_plan(self, entity_id: str, plan_id: str) -> str:
        """找到从实体到预案的路径"""
        try:
            path = nx.shortest_path(self._graph, entity_id, plan_id)
            path_names = []
            for node_id in path:
                if node_id in self._graph:
                    name = self._graph.nodes[node_id].get("name", node_id)
                    path_names.append(name)
            return " → ".join(path_names)
        except nx.NetworkXNoPath:
            return "间接关联"
        except nx.NodeNotFound:
            return "间接关联"
