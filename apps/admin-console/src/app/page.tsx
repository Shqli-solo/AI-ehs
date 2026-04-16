'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { Toaster } from '@/components/ui/toaster';
import { useToast } from '@/hooks/use-toast';
import { riskLevelConfig, alertStatusConfig } from '@/lib/utils';
import { api, ApiError, getErrorSummary } from '@/services/api';
import {
  useAlertStats,
  useAlerts,
  useDeviceOnlineRate,
  useSafeDays,
  type Alert,
} from '@/hooks/use-alerts';

/**
 * 统计卡片组件
 */
function StatCard({
  title,
  value,
  subtitle,
  icon,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="bg-card rounded-card shadow-card p-6 border border-border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-caption text-muted-foreground mb-1">{title}</p>
          <p className="text-3xl font-bold text-foreground">{value}</p>
          {subtitle && (
            <p className="text-caption text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
        {icon && <div className="text-2xl">{icon}</div>}
      </div>
    </div>
  );
}

/**
 * 告警列表组件
 */
function AlertList({ alerts }: { alerts: Alert[] }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="bg-card rounded-card shadow-card border border-border p-12 text-center">
        <div className="text-6xl mb-4">📭</div>
        <h3 className="text-title font-semibold text-foreground mb-2">
          暂无告警
        </h3>
        <p className="text-body text-muted-foreground">
          所有系统运行正常
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-card shadow-card border border-border">
      <div className="p-4 border-b border-border">
        <h3 className="text-title font-semibold text-foreground">最近告警</h3>
      </div>
      <div className="divide-y divide-border">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="p-4 hover:bg-muted/50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-body font-medium text-foreground">
                    {alert.type}
                  </span>
                  <span
                    className={`text-xs px-2 py-0.5 rounded-badge ${riskLevelConfig[alert.riskLevel].className}`}
                  >
                    {riskLevelConfig[alert.riskLevel].label}
                  </span>
                </div>
                <p className="text-caption text-muted-foreground">
                  {alert.location}
                </p>
              </div>
              <div className="text-right">
                <p className="text-caption text-muted-foreground mb-1">
                  {alert.time}
                </p>
                <span
                  className={`text-xs font-medium ${alertStatusConfig[alert.status].className}`}
                >
                  {alertStatusConfig[alert.status].label}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t border-border">
        <Button variant="ghost" className="w-full text-primary">
          查看全部
          <svg
            className="w-4 h-4 ml-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </Button>
      </div>
    </div>
  );
}

/**
 * 骨架屏加载组件
 */
function StatCardSkeleton() {
  return (
    <div className="bg-card rounded-card shadow-card p-6 border border-border animate-pulse">
      <div className="h-4 bg-muted rounded w-24 mb-3"></div>
      <div className="h-8 bg-muted rounded w-16 mb-2"></div>
      <div className="h-3 bg-muted rounded w-20"></div>
    </div>
  );
}

/**
 * 空状态组件
 */
function EmptyState() {
  return (
    <div className="bg-card rounded-card shadow-card border border-border p-12 text-center">
      <div className="text-6xl mb-4">🎉</div>
      <h3 className="text-title font-semibold text-foreground mb-2">
        一切正常
      </h3>
      <p className="text-body text-muted-foreground">
        所有系统运行正常，继续保持良好的监控状态
      </p>
    </div>
  );
}

/**
 * 错误状态组件
 */
function ErrorState({
  error,
  onRetry
}: {
  error: ApiError;
  onRetry: () => void;
}) {
  return (
    <div className="bg-card rounded-card shadow-card border border-border p-12 text-center">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-title font-semibold text-foreground mb-2">
        {error.title}
      </h3>
      <p className="text-body text-muted-foreground mb-4">
        {error.message}
      </p>
      <div className="flex gap-2 justify-center">
        <Button onClick={onRetry}>重试</Button>
        <Button variant="outline">联系技术支持</Button>
      </div>
    </div>
  );
}

/**
 * 健康检查指示器
 */
function HealthIndicator({
  healthy,
  onCheck
}: {
  healthy: boolean | null;
  onCheck: () => void;
}) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className={`inline-block w-2 h-2 rounded-full ${healthy ? 'bg-success' : 'bg-error'}`} />
      <span className="text-muted-foreground">
        {healthy ? '后端服务正常' : '后端服务离线'}
      </span>
      <Button variant="link" className="h-auto p-0 text-primary" onClick={onCheck}>
        检查
      </Button>
    </div>
  );
}

/**
 * Dashboard 首页组件
 */
export default function DashboardPage() {
  const { toast } = useToast();

  // 使用真实 API Hook
  const { data: stats, loading: statsLoading, error: statsError, refresh: refreshStats } = useAlertStats();
  const { data: alerts, loading: alertsLoading, error: alertsError, refresh: refreshAlerts } = useAlerts({
    autoLoad: true,
    pageSize: 5,
  });
  const { rate: deviceOnlineRate, loading: deviceLoading } = useDeviceOnlineRate();
  const { days: safeDays } = useSafeDays();

  // 后端健康检查状态
  const [backendHealthy, setBackendHealthy] = React.useState<boolean | null>(null);

  // 检查后端健康状态
  const checkHealth = React.useCallback(async () => {
    try {
      await api.healthCheck();
      setBackendHealthy(true);
    } catch {
      setBackendHealthy(false);
    }
  }, []);

  // 初始健康检查
  React.useEffect(() => {
    checkHealth();
  }, [checkHealth]);

  // 显示错误 Toast
  React.useEffect(() => {
    if (statsError) {
      toast({
        variant: "destructive",
        title: statsError.title,
        description: getErrorSummary(statsError),
      });
    }
  }, [statsError, toast]);

  React.useEffect(() => {
    if (alertsError) {
      toast({
        variant: "destructive",
        title: alertsError.title,
        description: getErrorSummary(alertsError),
      });
    }
  }, [alertsError, toast]);

  // 合并加载和错误状态
  const loading = statsLoading || alertsLoading || deviceLoading;
  const error = statsError || alertsError;

  const handleRetry = () => {
    refreshStats();
    refreshAlerts();
  };

  const handleShowSuccessToast = () => {
    toast({
      variant: "success",
      title: "操作成功",
      description: "数据已成功保存",
    });
  };

  const handleShowErrorToast = () => {
    toast({
      variant: "destructive",
      title: "操作失败",
      description: "保存数据时发生错误",
    });
  };

  const handleShowInfoToast = () => {
    toast({
      variant: "info",
      title: "提示信息",
      description: "系统正在运行中",
    });
  };

  const handleShowWarningToast = () => {
    toast({
      variant: "warning",
      title: "警告提示",
      description: "请注意潜在风险",
    });
  };

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <header className="bg-card border-b border-border sticky top-0 z-10">
          <div className="flex items-center justify-between h-16 px-6">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🚨</span>
              <h1 className="text-title font-semibold text-foreground">
                EHS 智能安保决策中台
              </h1>
            </div>
            <HealthIndicator healthy={backendHealthy} onCheck={checkHealth} />
          </div>
        </header>
        <main className="p-6">
          <ErrorState error={error} onRetry={handleRetry} />
        </main>
        <Toaster />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-10">
        <div className="flex items-center justify-between h-16 px-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🚨</span>
            <h1 className="text-title font-semibold text-foreground">
              EHS 智能安保决策中台
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <HealthIndicator healthy={backendHealthy} onCheck={checkHealth} />
            <div className="relative">
              <input
                type="text"
                placeholder="搜索..."
                className="h-9 w-64 px-4 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            <button className="relative text-muted-foreground hover:text-foreground">
              🔔
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-error text-white text-xs rounded-full flex items-center justify-center">
                3
              </span>
            </button>
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-white">
              👤
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        {/* Welcome Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-title-lg font-semibold text-foreground">
                欢迎回来，张三
              </h2>
              <p className="text-body text-muted-foreground mt-1">
                {new Date().toLocaleDateString('zh-CN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  weekday: 'long',
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {(statsLoading || deviceLoading) ? (
            <>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : stats ? (
            <>
              <StatCard
                title="今日告警"
                value={stats.total}
                subtitle={stats.change}
                icon="🚨"
              />
              <StatCard
                title="待处理"
                value={stats.pending}
                subtitle={`${stats.processing} 处理中`}
                icon="⏳"
              />
              <StatCard
                title="设备在线率"
                value={`${deviceOnlineRate ?? 0}%`}
                subtitle="🟢 正常"
                icon="📊"
              />
              <StatCard
                title="安全运行天数"
                value={safeDays}
                subtitle="天"
                icon="🛡️"
              />
            </>
          ) : (
            <div className="col-span-full">
              <EmptyState />
            </div>
          )}
        </div>

        {/* Charts Section - Placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-card rounded-card shadow-card border border-border p-6">
            <h3 className="text-title font-semibold text-foreground mb-4">
              告警趋势图 (7 天)
            </h3>
            <div className="h-48 bg-muted/30 rounded flex items-center justify-center text-muted-foreground">
              📈 图表占位区域
            </div>
          </div>
          <div className="bg-card rounded-card shadow-card border border-border p-6">
            <h3 className="text-title font-semibold text-foreground mb-4">
              告警类型分布
            </h3>
            <div className="h-48 bg-muted/30 rounded flex items-center justify-center text-muted-foreground">
              🥧 图表占位区域
            </div>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="mb-6">
          {alertsLoading ? (
            <div className="bg-card rounded-card shadow-card border border-border p-6 animate-pulse">
              <div className="h-6 bg-muted rounded w-32 mb-4"></div>
              <div className="space-y-3">
                <div className="h-16 bg-muted rounded"></div>
                <div className="h-16 bg-muted rounded"></div>
                <div className="h-16 bg-muted rounded"></div>
              </div>
            </div>
          ) : (
            <AlertList alerts={alerts ?? []} />
          )}
        </div>

        {/* Toast 演示区域 */}
        <div className="bg-card rounded-card shadow-card border border-border p-6">
          <h3 className="text-title font-semibold text-foreground mb-4">
            Toast 组件演示
          </h3>
          <div className="flex flex-wrap gap-3">
            <Button onClick={handleShowSuccessToast} variant="default">
              ✅ 成功 Toast
            </Button>
            <Button onClick={handleShowErrorToast} variant="destructive">
              ❌ 错误 Toast
            </Button>
            <Button onClick={handleShowInfoToast} variant="outline">
              ℹ️ 信息 Toast
            </Button>
            <Button onClick={handleShowWarningToast} variant="warning">
              ⚠️ 警告 Toast
            </Button>
          </div>
          <p className="text-caption text-muted-foreground mt-4">
            点击按钮查看不同类型的 Toast 通知，3 秒后自动消失
          </p>
        </div>
      </main>
      <Toaster />
    </div>
  );
}
