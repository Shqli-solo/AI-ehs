"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Cpu, BarChart3, Download } from "lucide-react";

export default function ModelsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">模型管理</h2>

      <Tabs defaultValue="models">
        <TabsList>
          <TabsTrigger value="models">模型配置</TabsTrigger>
          <TabsTrigger value="fine-tune">微调记录</TabsTrigger>
          <TabsTrigger value="eval">评估报告</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>已部署模型</CardTitle>
            </CardHeader>
            <CardContent>
              {[
                {
                  name: "Qwen3-7B",
                  type: "LLM",
                  status: "运行中",
                  endpoint: "http://localhost:11434",
                },
                {
                  name: "BGE-Reranker",
                  type: "重排序",
                  status: "运行中",
                  endpoint: "http://localhost:6006",
                },
                {
                  name: "BERT-risk",
                  type: "风险分级",
                  status: "待部署",
                  endpoint: "-",
                },
              ].map((model) => (
                <div
                  key={model.name}
                  className="flex items-center justify-between py-3 border-b last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <Cpu className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">{model.name}</p>
                      <p className="text-xs text-gray-400">{model.type}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-400">
                      {model.endpoint}
                    </span>
                    <Badge
                      className={
                        model.status === "运行中"
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }
                    >
                      {model.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fine-tune" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>微调任务</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "指令微调 - Qwen7B", status: "待训练", samples: 500 },
                  { name: "风险分级 - BERT", status: "待训练", samples: 1000 },
                  { name: "合规检查 - RoBERTa", status: "待训练", samples: 300 },
                  { name: "术语Embedding - BGE", status: "待训练", samples: 2000 },
                ].map((task) => (
                  <div
                    key={task.name}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div>
                      <p className="text-sm font-medium">{task.name}</p>
                      <p className="text-xs text-gray-400">
                        训练样本：{task.samples}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className="bg-yellow-100 text-yellow-800">
                        {task.status}
                      </Badge>
                      <Button size="sm" variant="outline">
                        <Download className="h-3 w-3 mr-1" />
                        开始
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="eval" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>评估报告</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 text-center py-8">
                暂无评估报告。完成微调后自动生成评估。
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
