"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/common/StatusBadge";
import { mockAlerts, alertStats } from "@/mock/alerts";
import {
  AlertTriangle,
  Clock,
  CheckCircle,
  Shield,
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const recentAlerts = mockAlerts.slice(0, 5);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">欢迎回来</h2>
        <p className="text-gray-500 mt-1">
          {new Date().toLocaleDateString("zh-CN")} | 所有系统运行正常
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">今日告警</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{alertStats.today}</div>
            <p className="text-xs text-muted-foreground">
              较昨日 +2
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">待处理</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{alertStats.pending}</div>
            <p className="text-xs text-muted-foreground">
              较昨日 -3
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">设备在线率</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.5%</div>
            <p className="text-xs text-green-600">正常</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">安全天数</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45</div>
            <p className="text-xs text-muted-foreground">天</p>
          </CardContent>
        </Card>
      </div>

      {/* 最近告警 */}
      <Card>
        <CardHeader>
          <CardTitle>最近告警</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div className="flex-1">
                  <p className="font-medium text-sm">{alert.title}</p>
                  <p className="text-xs text-gray-500">{alert.location}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge type="risk" value={alert.riskLevel} />
                  <StatusBadge type="status" value={alert.status} />
                  <span className="text-xs text-gray-400">
                    {alert.createdAt.slice(0, 16)}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <Link
            href="/alerts"
            className="text-sm text-blue-600 hover:text-blue-800 mt-4 inline-block"
          >
            查看全部 &rarr;
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
