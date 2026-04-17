"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">系统设置</h2>

      <Tabs defaultValue="basic">
        <TabsList>
          <TabsTrigger value="basic">基本信息</TabsTrigger>
          <TabsTrigger value="alert-config">告警配置</TabsTrigger>
          <TabsTrigger value="notification">通知设置</TabsTrigger>
          <TabsTrigger value="api">API 管理</TabsTrigger>
          <TabsTrigger value="logs">操作日志</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>基本信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="site-name">系统名称</Label>
                <Input id="site-name" defaultValue="EHS 智能安保决策中台" />
              </div>
              <div>
                <Label htmlFor="site-url">系统地址</Label>
                <Input id="site-url" defaultValue="http://localhost:3000" />
              </div>
              <div>
                <Label htmlFor="admin-email">管理员邮箱</Label>
                <Input id="admin-email" defaultValue="admin@ehs.com" />
              </div>
              <Button onClick={() => toast.success("保存成功")}>
                保存设置
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alert-config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>告警阈值配置</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="gas-threshold">气体泄漏阈值 (ppm)</Label>
                <Input id="gas-threshold" type="number" defaultValue="50" />
              </div>
              <div>
                <Label htmlFor="temp-threshold">温度异常阈值 (°C)</Label>
                <Input id="temp-threshold" type="number" defaultValue="45" />
              </div>
              <Button onClick={() => toast.success("保存配置")}>
                保存配置
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notification" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>通知渠道</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-500">
                配置告警通知渠道（邮件、短信、钉钉等）
              </p>
              <div className="bg-gray-50 rounded-md p-4 text-sm text-gray-500">
                <p>通知配置将在接入真实服务后启用</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API Key 管理</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 text-center py-8">
                暂无 API Key
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>操作日志</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 text-center py-8">
                暂无操作日志
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
