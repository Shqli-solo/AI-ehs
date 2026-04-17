"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Workflow, ArrowRight, Play, Settings } from "lucide-react";

const agentNodes = [
  {
    id: "risk",
    name: "RiskAgent",
    desc: "风险感知 - 分析告警内容，评估风险等级",
    status: "active",
    input: "告警数据",
    output: "风险等级 + 处置建议",
  },
  {
    id: "search",
    name: "SearchAgent",
    desc: "预案检索 - 基于 GraphRAG 检索匹配预案",
    status: "active",
    input: "风险等级 + 关键词",
    output: "匹配预案列表",
  },
];

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Agent 编排</h2>
        <Button>
          <Workflow className="h-4 w-4 mr-1" />
          新建工作流
        </Button>
      </div>

      <Tabs defaultValue="workflow">
        <TabsList>
          <TabsTrigger value="workflow">工作流配置</TabsTrigger>
          <TabsTrigger value="nodes">节点管理</TabsTrigger>
        </TabsList>

        <TabsContent value="workflow" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>默认工作流</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 py-4">
                <div className="flex-1 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900">RiskAgent</h3>
                  <p className="text-xs text-blue-700 mt-1">
                    风险感知 - 分析告警内容
                  </p>
                  <Badge className="mt-2 bg-green-100 text-green-800">
                    运行中
                  </Badge>
                </div>
                <ArrowRight className="h-6 w-6 text-gray-400" />
                <div className="flex-1 bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-medium text-purple-900">SearchAgent</h3>
                  <p className="text-xs text-purple-700 mt-1">
                    预案检索 - GraphRAG 匹配
                  </p>
                  <Badge className="mt-2 bg-green-100 text-green-800">
                    运行中
                  </Badge>
                </div>
                <ArrowRight className="h-6 w-6 text-gray-400" />
                <div className="flex-1 bg-gray-50 border rounded-lg p-4">
                  <h3 className="font-medium text-gray-700">输出</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    结构化响应
                  </p>
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <Button size="sm">
                  <Play className="h-4 w-4 mr-1" />
                  测试运行
                </Button>
                <Button size="sm" variant="outline">
                  <Settings className="h-4 w-4 mr-1" />
                  编辑
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="nodes" className="space-y-4">
          {agentNodes.map((node) => (
            <Card key={node.id}>
              <CardHeader>
                <CardTitle className="text-lg">{node.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">{node.desc}</p>
                <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
                  <div>
                    <span className="text-gray-500">输入：</span>
                    {node.input}
                  </div>
                  <div>
                    <span className="text-gray-500">输出：</span>
                    {node.output}
                  </div>
                </div>
                <Badge className="mt-3 bg-green-100 text-green-800">
                  运行中
                </Badge>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
