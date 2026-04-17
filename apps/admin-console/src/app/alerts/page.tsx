"use client";

import * as React from 'react';
import { useAlerts } from "@/hooks/use-alerts";
import { Alert } from "@/types/alert";
import { AlertRow } from "./components/AlertRow";
import { AlertDrawer } from "./components/AlertDrawer";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { useState, useMemo } from "react";

export default function AlertsPage() {
  const { data: apiAlerts, loading, error, refresh } = useAlerts({ fallbackToMock: true });
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterRisk, setFilterRisk] = useState("all");

  const filtered = useMemo(() => {
    if (!apiAlerts) return [];
    return apiAlerts.filter((a) => {
      if (filterStatus !== "all" && a.status !== filterStatus) return false;
      if (filterRisk !== "all" && a.riskLevel !== filterRisk) return false;
      return true;
    });
  }, [apiAlerts, filterStatus, filterRisk]);

  const handleProcess = (alertId: string) => {
    toast.success("已开始处理告警");
    setDrawerOpen(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">告警管理</h2>

      {/* 筛选 */}
      <div className="flex gap-4">
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="全部状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部状态</SelectItem>
            <SelectItem value="pending">待处理</SelectItem>
            <SelectItem value="processing">处理中</SelectItem>
            <SelectItem value="resolved">已解决</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterRisk} onValueChange={setFilterRisk}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="全部等级" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部等级</SelectItem>
            <SelectItem value="critical">严重</SelectItem>
            <SelectItem value="high">高</SelectItem>
            <SelectItem value="medium">中</SelectItem>
            <SelectItem value="low">低</SelectItem>
          </SelectContent>
        </Select>

        <Button variant="outline" size="sm" onClick={refresh}>
          刷新
        </Button>
      </div>

      {/* 告警列表 */}
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">标题</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">等级</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">位置</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((alert) => (
              <AlertRow
                key={alert.id}
                alert={alert}
                onView={(a) => {
                  setSelectedAlert(a);
                  setDrawerOpen(true);
                }}
              />
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-4xl mb-4">{"\ud83c\udf89"}</p>
            <p>暂无告警数据</p>
            <p className="text-sm mt-2">所有系统运行正常，继续保持良好的监控状态</p>
          </div>
        )}
      </div>

      <AlertDrawer
        alert={selectedAlert}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onProcess={handleProcess}
      />
    </div>
  );
}
