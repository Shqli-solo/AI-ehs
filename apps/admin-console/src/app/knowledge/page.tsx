"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen, Upload, Search } from "lucide-react";

export default function KnowledgePage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">知识库管理</h2>

      <Tabs defaultValue="documents">
        <TabsList>
          <TabsTrigger value="documents">文档管理</TabsTrigger>
          <TabsTrigger value="upload">上传文档</TabsTrigger>
          <TabsTrigger value="search">检索测试</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>已上传文档</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "火灾应急预案.pdf", size: "2.3 MB", date: "2026-04-10", status: "已索引" },
                  { name: "气体泄漏处置流程.docx", size: "1.1 MB", date: "2026-04-08", status: "已索引" },
                  { name: "安全生产管理制度.pdf", size: "3.5 MB", date: "2026-04-05", status: "向量化中" },
                ].map((doc) => (
                  <div
                    key={doc.name}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <BookOpen className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium">{doc.name}</p>
                        <p className="text-xs text-gray-400">
                          {doc.size} · {doc.date}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        doc.status === "已索引"
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>上传文档</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-500">
                  拖拽文件到此处，或点击选择文件
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  支持 PDF, DOCX, TXT 格式
                </p>
                <Button className="mt-4">选择文件</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>RAG 检索测试</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input placeholder="输入测试问题..." />
                <Button>
                  <Search className="h-4 w-4 mr-1" />
                  检索
                </Button>
              </div>
              <div className="bg-gray-50 rounded-md p-4 text-sm text-gray-500">
                <p>检索结果将显示在这里</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
