# GraphRAG 技术说明

## 为什么用 GraphRAG？

### 传统 RAG 的局限

传统 RAG（Retrieval-Augmented Generation）的工作流程：

```
查询 → 文本检索(BM25) + 向量检索 → 合并 → Rerank → LLM 生成
```

**问题：** 只能检索独立文档片段，无法理解实体间的关系。

**具体例子：**

查询："A 栋 3 楼火灾"

传统 RAG 返回：
- "A栋办公楼火灾应急预案" ✅
- "A栋3楼办公区烟雾报警应急预案" ✅
- ❌ 无法发现 "A栋与B栋有连廊相连，B栋地下室有化学品仓库"
- ❌ 无法回答 "火势会蔓延到哪些区域？需要疏散哪些建筑？"

### GraphRAG 的优势

GraphRAG 在传统 RAG 之上增加知识图谱层：

```
查询 → 知识图谱检索相关子图 → 增强查询 → 传统检索 → 附加图谱上下文
```

**同样的查询：** "A 栋 3 楼火灾"

GraphRAG 返回：
- "A栋办公楼火灾应急预案" ✅
- "A栋-B栋连廊火灾蔓延应急预案" ✅（传统 RAG 可能遗漏）
- 关联上下文："A栋与B栋通过二层连廊相连，B栋地下室有化学品仓库" ✅
- 建议："同时疏散A栋和B栋人员，重点关注B栋化学品区域" ✅

### 知识图谱结构

```
Building (A栋)
  ├── part_of → Floor (1楼, 2楼, 3楼, 地下一层)
  │     └── located_on → Room (办公区, 电梯)
  │           └── installed_in → Equipment (烟雾传感器, 喷淋系统)
  ├── connected_by_corridor → Building (B栋)
  │     └── located_on → Room (化学品仓库)
  │           └── has_hazard → Hazard (化学品泄漏)
  │                 └── addressed_by → Plan (化学品泄漏应急预案)
  ├── has_hazard → Hazard (火灾风险)
  │     └── mitigated_by → Equipment (消防喷淋)
  │     └── addressed_by → Plan (火灾应急预案)
  └── protects → Equipment (消防管网)
```

### 检索流程对比

| 步骤 | 传统 RAG | GraphRAG |
|------|----------|----------|
| 1 | 查询："A栋火灾" | 查询："A栋火灾" |
| 2 | BM25 匹配 "A栋" + "火灾" | 知识图谱匹配 "A栋" 实体 |
| 3 | 向量相似度匹配 | 遍历图谱找到关联节点 |
| 4 | 合并结果 | 发现 "A栋-B栋连廊" 关系 |
| 5 | Rerank 排序 | 增强查询："A栋火灾（与B栋连廊相连）" |
| 6 | 返回 Top-K 文档 | 用增强查询重新检索 + 附加图谱上下文 |
| 7 | ❌ 无关联风险信息 | ✅ 返回 "B栋化学品仓库需额外疏散" |

### 实现细节

#### 1. 实体匹配

使用关键词匹配查询中提及的实体（生产环境可用 LLM 做 NER）：

```python
def _match_entities(self, query: str):
    # "A栋火灾" → 匹配到 "A栋办公楼" (score=1.0) 和 "火灾风险" (score=0.5)
    matches = []
    for entity_id, entity in self._entity_index.items():
        if entity["name"].lower() in query.lower():
            matches.append((entity_id, 1.0))
    return sorted(matches, key=lambda x: x[1], reverse=True)
```

#### 2. 子图遍历

从匹配实体出发，BFS 遍历邻居节点构建子图上下文：

```python
def _traverse_neighbors(self, entity_id, context, visited, max_depth, depth):
    for neighbor in self._graph.neighbors(entity_id):
        # 重要节点类型（Hazard, Plan, Building）加入上下文
        if node_type in ("Hazard", "Plan", "Building"):
            context.append({
                "name": node_name,
                "type": node_type,
                "relations": [...],  # 关系描述
            })
```

#### 3. 查询增强

将图谱发现的关联信息注入查询：

```python
def enrich_query(self, query: str) -> str:
    # 原始查询: "A栋火灾"
    # 增强后: "A栋火灾。相关上下文：危险源: A栋火灾风险；
    #         相关预案: A栋-B栋连廊火灾蔓延应急预案"
    context_parts = []
    for node in subgraph:
        if node["type"] == "Hazard":
            context_parts.append(f"危险源: {node['name']}")
    return f"{query}。相关上下文：{'；'.join(context_parts)}"
```

### 前端可视化

`/api/graph` 端点返回图谱数据，前端使用 vis.js / D3.js 渲染：

```json
{
  "success": true,
  "data": {
    "nodes": [
      {"id": "building_a", "label": "A栋办公楼", "type": "Building"},
      {"id": "building_b", "label": "B栋仓储楼", "type": "Building"},
      {"id": "hazard_fire_a", "label": "A栋火灾风险", "type": "Hazard"}
    ],
    "edges": [
      {"source": "building_b", "target": "building_a", "label": "connected_by_corridor"}
    ]
  }
}
```

### 总结

GraphRAG 不是替代传统 RAG，而是在其基础上增加**关系理解**能力：

- **传统 RAG**：理解 "是什么"（关键词/语义匹配）
- **GraphRAG**：理解 "与什么相关"（实体关系推理）

在 EHS 安保场景中，这种关系理解能力至关重要——一个位置的事件往往会影响关联区域，这是传统 RAG 无法提供的。
