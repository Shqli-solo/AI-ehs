import * as React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockAlerts = [
  { id: '1', type: 'fire' as const, title: '烟感报警', content: 'A栋3楼烟感', riskLevel: 'high' as const, status: 'pending' as const, location: 'A栋3楼', deviceId: 'DEV-001', createdAt: '2026-04-17T08:30:00Z' },
  { id: '2', type: 'gas_leak' as const, title: '气体泄漏', content: 'B车间气体泄漏', riskLevel: 'medium' as const, status: 'processing' as const, location: 'B车间', deviceId: 'DEV-002', createdAt: '2026-04-17T09:00:00Z' },
  { id: '3', type: 'intrusion' as const, title: '入侵检测', content: 'C区域', riskLevel: 'low' as const, status: 'resolved' as const, location: 'C区域', deviceId: 'DEV-003', createdAt: '2026-04-17T10:00:00Z' },
];

vi.mock('@/hooks/use-alerts', () => ({
  useAlerts: vi.fn(() => ({
    data: mockAlerts,
    loading: false,
    error: null,
    load: vi.fn(),
    refresh: vi.fn(),
  })),
  useAlertStats: vi.fn(() => ({
    data: { total: 0, pending: 0, processing: 0, resolved: 0, change: '+0 起' },
    loading: false,
    error: null,
    refresh: vi.fn(),
  })),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), warning: vi.fn(), error: vi.fn() },
}));

import AlertsPage from './page';

describe('AlertsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该显示页面标题', () => {
    render(<AlertsPage />);
    expect(screen.getByText('告警管理')).toBeInTheDocument();
  });

  it('应该显示状态筛选器', () => {
    render(<AlertsPage />);
    expect(screen.getByText('全部状态')).toBeInTheDocument();
  });

  it('应该显示等级筛选器', () => {
    render(<AlertsPage />);
    expect(screen.getByText('全部等级')).toBeInTheDocument();
  });

  it('应该显示刷新按钮', () => {
    render(<AlertsPage />);
    expect(screen.getByText('刷新')).toBeInTheDocument();
  });

  it('应该显示告警表格列头', () => {
    render(<AlertsPage />);
    expect(screen.getByText('ID')).toBeInTheDocument();
    expect(screen.getByText('类型')).toBeInTheDocument();
    expect(screen.getByText('标题')).toBeInTheDocument();
    expect(screen.getByText('等级')).toBeInTheDocument();
    expect(screen.getByText('状态')).toBeInTheDocument();
    expect(screen.getByText('位置')).toBeInTheDocument();
    expect(screen.getByText('时间')).toBeInTheDocument();
  });

  it('应该显示告警行数据', () => {
    render(<AlertsPage />);
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('烟感报警')).toBeInTheDocument();
    expect(screen.getByText('A栋3楼')).toBeInTheDocument();
  });

  it('应该显示告警类型中文标签', () => {
    render(<AlertsPage />);
    const gasLeakLabels = screen.getAllByText('气体泄漏');
    expect(gasLeakLabels.length).toBeGreaterThan(0);
    const fireLabels = screen.getAllByText('火灾');
    expect(fireLabels.length).toBeGreaterThan(0);
    const intrusionLabels = screen.getAllByText('入侵检测');
    expect(intrusionLabels.length).toBeGreaterThan(0);
  });

  it('应该显示风险等级徽章', () => {
    render(<AlertsPage />);
    expect(screen.getByText('高')).toBeInTheDocument();
    expect(screen.getByText('中')).toBeInTheDocument();
    expect(screen.getByText('低')).toBeInTheDocument();
  });

  it('应该显示状态徽章', () => {
    render(<AlertsPage />);
    expect(screen.getByText('待处理')).toBeInTheDocument();
    expect(screen.getByText('处理中')).toBeInTheDocument();
    // "已解决" also appears, but may have duplicates from StatusBadge
    const resolved = screen.getAllByText('已解决');
    expect(resolved.length).toBeGreaterThan(0);
  });
});

describe('AlertsPage - Empty State', () => {
  it('应该显示空状态当无数据', async () => {
    const { useAlerts } = await import('@/hooks/use-alerts');
    vi.mocked(useAlerts).mockReturnValueOnce({
      data: [],
      loading: false,
      error: null,
      load: vi.fn(),
      refresh: vi.fn(),
    });

    render(<AlertsPage />);
    expect(screen.getByText('暂无告警数据')).toBeInTheDocument();
  });
});
