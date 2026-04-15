'use client';

import * as React from 'react';
import { Button } from '@/components/ui/button';
import { riskLevelConfig, alertStatusConfig } from '@/lib/utils';

/**
 * Mock 数据 - 今日告警统计
 */
const mockTodayStats = {
  total: 12,
  pending: 5,
  processing: 3,
  resolved: 4,
  change: '+2 起',
};

/**
 * Mock 数据 - 设备在线率
 */
const mockDeviceOnlineRate = 98.5;

/**
 * Mock 数据 - 安全运行天数
 */
const mockSafeDays = 45;

/**
 * Mock 数据 - 最近告警列表
 */
const mockRecentAlerts = [
  {
    id: 'ALT-2026041501',
    type: '气体泄漏',
    location: 'A 车间 - 东区 -2 层',
    riskLevel: 'high' as const,
    status: 'pending' as const,
    time: '2026-04-15 10:30:00',
  },
  {
    id: 'ALT-2026041502',
    type: '温度异常',
    location: 'B 车间 - 西区 -1 层',
    riskLevel: 'medium' as const,
    status: 'processing' as const,
    time: '2026-04-15 09:15:00',
  },
  {
    id: 'ALT-2026041503',
    type: '入侵检测',
    location: 'C 仓库 - 北侧',
    riskLevel: 'low' as const,
    status: 'resolved' as const,
    time: '2026-04-15 08:00:00',
  },
];

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
function AlertList({ alerts }: { alerts: typeof mockRecentAlerts }) {
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
function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="bg-card rounded-card shadow-card border border-border p-12 text-center">
      <div className="text-6xl mb-4">⚠️</div>
      <h3 className="text-title font-semibold text-foreground mb-2">
        加载失败
      </h3>
      <p className="text-body text-muted-foreground mb-4">
        无法连接到服务器，请检查网络连接后重试
      </p>
      <div className="flex gap-2 justify-center">
        <Button onClick={onRetry}>重试</Button>
        <Button variant="outline">联系技术支持</Button>
      </div>
    </div>
  );
}

/**
 * Dashboard 首页组件
 */
export default function DashboardPage() {
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [stats, setStats] = React.useState<typeof mockTodayStats | null>(null);

  // 模拟数据加载
  React.useEffect(() => {
    const timer = setTimeout(() => {
      // 模拟加载成功
      setStats(mockTodayStats);
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const handleRetry = () => {
    setIsLoading(true);
    setError(null);
    setTimeout(() => {
      setStats(mockTodayStats);
      setIsLoading(false);
    }, 1000);
  };

  if (error) {
    return <ErrorState onRetry={handleRetry} />;
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
          {isLoading ? (
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
                value={`${mockDeviceOnlineRate}%`}
                subtitle="🟢 正常"
                icon="📊"
              />
              <StatCard
                title="安全运行天数"
                value={mockSafeDays}
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
          {isLoading ? (
            <div className="bg-card rounded-card shadow-card border border-border p-6 animate-pulse">
              <div className="h-6 bg-muted rounded w-32 mb-4"></div>
              <div className="space-y-3">
                <div className="h-16 bg-muted rounded"></div>
                <div className="h-16 bg-muted rounded"></div>
                <div className="h-16 bg-muted rounded"></div>
              </div>
            </div>
          ) : (
            <AlertList alerts={mockRecentAlerts} />
          )}
        </div>
      </main>
    </div>
  );
}
