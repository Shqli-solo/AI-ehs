'use client';

import * as React from 'react';
import { api } from '@/services/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/** 节点类型对应的颜色 */
const TYPE_COLORS: Record<string, string> = {
  Building: '#3b82f6',
  Floor: '#60a5fa',
  Room: '#8b5cf6',
  Equipment: '#10b981',
  Hazard: '#ef4444',
  Plan: '#f59e0b',
};

/** 节点类型对应的中文 */
const TYPE_LABELS: Record<string, string> = {
  Building: '建筑',
  Floor: '楼层',
  Room: '房间',
  Equipment: '设备',
  Hazard: '危险源',
  Plan: '预案',
};

interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
}

interface GraphEdge {
  source: string;
  target: string;
  label: string;
  description: string;
}

interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  stats: { total_nodes: number; total_edges: number };
}

export default function GraphPage() {
  const [graphData, setGraphData] = React.useState<GraphData | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedNode, setSelectedNode] = React.useState<GraphNode | null>(null);
  const svgRef = React.useRef<SVGSVGElement>(null);

  // 加载完整图谱
  const loadGraph = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/api/graph`);
      const data = await resp.json();
      if (data.success) {
        setGraphData(data.data);
      } else {
        setError(data.error || '加载失败');
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '网络请求失败');
    } finally {
      setLoading(false);
    }
  }, []);

  // 搜索相关子图
  const searchGraph = React.useCallback(async (query: string) => {
    if (!query.trim()) {
      loadGraph();
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/api/graph?query=${encodeURIComponent(query)}`);
      const data = await resp.json();
      if (data.success && data.data.subgraph) {
        // 将子图数据转换为可视化格式
        const nodes: GraphNode[] = [];
        const edges: GraphEdge[] = [];
        const seenNodes = new Set<string>();

        for (const node of data.data.subgraph) {
          if (!seenNodes.has(node.entity_id)) {
            seenNodes.add(node.entity_id);
            nodes.push({
              id: node.entity_id,
              label: node.name,
              type: node.type,
              properties: node.properties || {},
            });
          }
          for (const rel of (node.relations || [])) {
            if (!seenNodes.has(rel.to_entity)) {
              seenNodes.add(rel.to_entity);
              nodes.push({
                id: rel.to_entity,
                label: rel.to_name,
                type: rel.to_type,
                properties: {},
              });
            }
            edges.push({
              source: rel.from_entity,
              target: rel.to_entity,
              label: rel.relation_type,
              description: rel.description || '',
            });
          }
        }

        setGraphData({ nodes, edges, stats: { total_nodes: nodes.length, total_edges: edges.length } });
      } else if (data.success) {
        setError('未找到相关子图');
      } else {
        setError(data.error || '搜索失败');
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : '网络请求失败');
    } finally {
      setLoading(false);
    }
  }, [loadGraph]);

  React.useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  // 简单的力导向图布局（使用 Canvas 渲染）
  React.useEffect(() => {
    if (!graphData || !svgRef.current || graphData.nodes.length === 0) return;

    const svg = svgRef.current;
    const width = svg.clientWidth || 1200;
    const height = svg.clientHeight || 600;
    const { nodes, edges } = graphData;

    // 初始化节点位置（圆形布局）
    const positions: Record<string, { x: number; y: number }> = {};
    const radius = Math.min(width, height) * 0.35;
    const cx = width / 2;
    const cy = height / 2;

    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      positions[node.id] = {
        x: cx + radius * Math.cos(angle),
        y: cy + radius * Math.sin(angle),
      };
    });

    // 简单力导向模拟（50 次迭代）
    for (let iter = 0; iter < 50; iter++) {
      const forces: Record<string, { fx: number; fy: number }> = {};
      nodes.forEach(n => { forces[n.id] = { fx: 0, fy: 0 }; });

      // 斥力（节点间）
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = positions[nodes[i].id];
          const b = positions[nodes[j].id];
          let dx = b.x - a.x;
          let dy = b.y - a.y;
          let dist = Math.sqrt(dx * dx + dy * dy) || 1;
          let force = 5000 / (dist * dist);
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          forces[nodes[i].id].fx -= fx;
          forces[nodes[i].id].fy -= fy;
          forces[nodes[j].id].fx += fx;
          forces[nodes[j].id].fy += fy;
        }
      }

      // 引力（边连接）
      for (const edge of edges) {
        if (!positions[edge.source] || !positions[edge.target]) continue;
        const a = positions[edge.source];
        const b = positions[edge.target];
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        let dist = Math.sqrt(dx * dx + dy * dy) || 1;
        let force = (dist - 120) * 0.01;
        let fx = (dx / dist) * force;
        let fy = (dy / dist) * force;
        forces[edge.source].fx += fx;
        forces[edge.source].fy += fy;
        forces[edge.target].fx -= fx;
        forces[edge.target].fy -= fy;
      }

      // 应用力
      const damping = 0.8;
      for (const node of nodes) {
        const f = forces[node.id];
        const p = positions[node.id];
        p.x = Math.max(50, Math.min(width - 50, p.x + f.fx * damping));
        p.y = Math.max(50, Math.min(height - 50, p.y + f.fy * damping));
      }
    }

    // 渲染 SVG
    const ns = 'http://www.w3.org/2000/svg';
    svg.innerHTML = '';

    // 绘制边
    for (const edge of edges) {
      const src = positions[edge.source];
      const tgt = positions[edge.target];
      if (!src || !tgt) continue;

      const line = document.createElementNS(ns, 'line');
      line.setAttribute('x1', String(src.x));
      line.setAttribute('y1', String(src.y));
      line.setAttribute('x2', String(tgt.x));
      line.setAttribute('y2', String(tgt.y));
      line.setAttribute('stroke', '#94a3b8');
      line.setAttribute('stroke-width', '1.5');
      line.setAttribute('stroke-opacity', '0.6');
      svg.appendChild(line);

      // 边标签
      if (edge.label) {
        const mx = (src.x + tgt.x) / 2;
        const my = (src.y + tgt.y) / 2;
        const text = document.createElementNS(ns, 'text');
        text.setAttribute('x', String(mx));
        text.setAttribute('y', String(my - 5));
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '10');
        text.setAttribute('fill', '#64748b');
        text.textContent = edge.label;
        svg.appendChild(text);
      }
    }

    // 绘制节点
    for (const node of nodes) {
      const pos = positions[node.id];
      if (!pos) continue;

      const g = document.createElementNS(ns, 'g');
      g.setAttribute('cursor', 'pointer');
      g.setAttribute('data-node-id', node.id);

      // 外圈（类型颜色）
      const circle = document.createElementNS(ns, 'circle');
      circle.setAttribute('cx', String(pos.x));
      circle.setAttribute('cy', String(pos.y));
      circle.setAttribute('r', '22');
      circle.setAttribute('fill', TYPE_COLORS[node.type] || '#94a3b8');
      circle.setAttribute('stroke', '#1e293b');
      circle.setAttribute('stroke-width', '2');
      g.appendChild(circle);

      // 内圈
      const inner = document.createElementNS(ns, 'circle');
      inner.setAttribute('cx', String(pos.x));
      inner.setAttribute('cy', String(pos.y));
      inner.setAttribute('r', '18');
      inner.setAttribute('fill', '#f8fafc');
      inner.setAttribute('opacity', '0.3');
      g.appendChild(inner);

      // 标签
      const text = document.createElementNS(ns, 'text');
      text.setAttribute('x', String(pos.x));
      text.setAttribute('y', String(pos.y + 35));
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', '11');
      text.setAttribute('fill', '#334155');
      text.setAttribute('font-weight', '500');
      text.textContent = node.label.length > 8 ? node.label.slice(0, 8) + '...' : node.label;
      g.appendChild(text);

      // 类型标签
      const typeText = document.createElementNS(ns, 'text');
      typeText.setAttribute('x', String(pos.x));
      typeText.setAttribute('y', String(pos.y + 48));
      typeText.setAttribute('text-anchor', 'middle');
      typeText.setAttribute('font-size', '9');
      typeText.setAttribute('fill', '#64748b');
      typeText.textContent = TYPE_LABELS[node.type] || node.type;
      g.appendChild(typeText);

      // 点击事件
      g.addEventListener('click', () => setSelectedNode(node));

      svg.appendChild(g);
    }
  }, [graphData]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-10">
        <div className="flex items-center justify-between h-16 px-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🕸️</span>
            <h1 className="text-title font-semibold text-foreground">
              知识图谱可视化 - GraphRAG
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                searchGraph(searchQuery);
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索实体或查询..."
                className="h-9 w-64 px-4 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                type="submit"
                className="h-9 px-4 rounded-input bg-primary text-white text-sm font-medium hover:bg-primary/90"
              >
                搜索
              </button>
              <button
                type="button"
                onClick={loadGraph}
                className="h-9 px-4 rounded-input border border-border bg-background text-sm hover:bg-muted"
              >
                重置
              </button>
            </form>
          </div>
        </div>
      </header>

      {/* Legend */}
      <div className="bg-card border-b border-border px-6 py-3">
        <div className="flex items-center gap-6 flex-wrap">
          <span className="text-sm font-medium text-foreground">图例：</span>
          {Object.entries(TYPE_LABELS).map(([type, label]) => (
            <div key={type} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: TYPE_COLORS[type] }}
              />
              <span className="text-sm text-muted-foreground">{label}</span>
            </div>
          ))}
          {graphData && (
            <span className="text-sm text-muted-foreground ml-auto">
              {graphData.stats.total_nodes} 个节点 · {graphData.stats.total_edges} 条边
            </span>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="flex gap-4 p-4" style={{ height: 'calc(100vh - 140px)' }}>
        {/* Graph Canvas */}
        <div className="flex-1 bg-card rounded-card shadow-card border border-border overflow-hidden">
          {loading && (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              加载中...
            </div>
          )}
          {error && !loading && (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <p className="text-error text-lg mb-2">⚠️ {error}</p>
                <button
                  onClick={loadGraph}
                  className="px-4 py-2 bg-primary text-white rounded hover:bg-primary/90"
                >
                  重新加载
                </button>
              </div>
            </div>
          )}
          {!loading && !error && graphData && graphData.nodes.length === 0 && (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              未找到相关数据
            </div>
          )}
          <svg
            ref={svgRef}
            className="w-full h-full"
            style={{ display: loading || error ? 'none' : 'block' }}
          />
        </div>

        {/* Node Detail Panel */}
        {selectedNode && (
          <div className="w-80 bg-card rounded-card shadow-card border border-border p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-title font-semibold text-foreground">节点详情</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-muted-foreground hover:text-foreground text-lg"
              >
                ✕
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground">名称</label>
                <p className="text-sm font-medium text-foreground">{selectedNode.label}</p>
              </div>
              <div>
                <label className="text-xs text-muted-foreground">类型</label>
                <p className="text-sm">
                  <span
                    className="px-2 py-0.5 rounded-full text-white text-xs"
                    style={{ backgroundColor: TYPE_COLORS[selectedNode.type] }}
                  >
                    {TYPE_LABELS[selectedNode.type] || selectedNode.type}
                  </span>
                </p>
              </div>
              {Object.keys(selectedNode.properties).length > 0 && (
                <div>
                  <label className="text-xs text-muted-foreground">属性</label>
                  <pre className="text-xs bg-muted p-2 rounded mt-1 overflow-x-auto">
                    {JSON.stringify(selectedNode.properties, null, 2)}
                  </pre>
                </div>
              )}
              <div>
                <label className="text-xs text-muted-foreground">ID</label>
                <p className="text-xs text-muted-foreground font-mono">{selectedNode.id}</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
