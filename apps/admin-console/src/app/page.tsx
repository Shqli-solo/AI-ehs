"use client";

import * as React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useAlerts, useAlertStats } from "@/hooks/use-alerts";
import {
  AlertTriangle,
  Clock,
  CheckCircle,
  Shield,
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { data: alerts, loading: alertsLoading } = useAlerts({ fallbackToMock: true, pageSize: 5 });
  const { data: stats, loading: statsLoading } = useAlertStats(true);

  const loading = alertsLoading || statsLoading;
  const recentAlerts = alerts?.slice(0, 5) ?? [];
  const todayStats = stats ?? { total: 0, pending: 0, processing: 0, resolved: 0, change: '+0 起' };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

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
            <div className="text-2xl font-bold">{todayStats.total}</div>
            <p className="text-xs text-muted-foreground">
              较昨日 {todayStats.change}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">待处理</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayStats.pending}</div>
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
                  <p className="font-medium text-sm">{alert.type} - {alert.location}</p>
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
