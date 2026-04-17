import * as React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock hooks BEFORE any imports
vi.mock('@/hooks/use-alerts', () => ({
  useAlerts: vi.fn(() => ({
    data: [
      { id: '1', type: 'fire', title: '烟感报警', content: 'A栋3楼烟感', riskLevel: 'high', status: 'pending', location: 'A栋3楼', deviceId: 'DEV-001', createdAt: '2026-04-17T08:30:00Z' },
      { id: '2', type: 'gas_leak', title: '气体泄漏', content: 'B车间', riskLevel: 'medium', status: 'processing', location: 'B车间', deviceId: 'DEV-002', createdAt: '2026-04-17T09:00:00Z' },
    ],
    loading: false,
    error: null,
    load: vi.fn(),
    refresh: vi.fn(),
  })),
  useAlertStats: vi.fn(() => ({
    data: { total: 50, pending: 10, processing: 5, resolved: 35, change: '+5 起' },
    loading: false,
    error: null,
    refresh: vi.fn(),
  })),
}));

import DashboardPage from './page';

describe('DashboardPage', () => {
  it('应该显示欢迎标题', () => {
    render(<DashboardPage />);
    expect(screen.getByText('欢迎回来')).toBeInTheDocument();
  });

  it('应该显示今日告警统计卡片', () => {
    render(<DashboardPage />);
    expect(screen.getByText('今日告警')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
    const changeTexts = screen.getAllByText(/\+5 起/);
    expect(changeTexts.length).toBeGreaterThan(0);
  });

  it('应该显示待处理统计卡片', () => {
    render(<DashboardPage />);
    const pendingTitles = screen.getAllByText('待处理');
    expect(pendingTitles.length).toBeGreaterThan(0);
    const pendingCount = screen.getByText('10');
    expect(pendingCount).toBeInTheDocument();
  });

  it('应该显示设备在线率卡片', () => {
    render(<DashboardPage />);
    expect(screen.getByText('设备在线率')).toBeInTheDocument();
    expect(screen.getByText('98.5%')).toBeInTheDocument();
  });

  it('应该显示安全天数卡片', () => {
    render(<DashboardPage />);
    expect(screen.getByText('安全天数')).toBeInTheDocument();
    expect(screen.getByText('45')).toBeInTheDocument();
  });

  it('应该显示最近告警列表标题', () => {
    render(<DashboardPage />);
    expect(screen.getByText('最近告警')).toBeInTheDocument();
  });

  it('应该显示告警类型和位置', () => {
    render(<DashboardPage />);
    expect(screen.getByText('fire - A栋3楼')).toBeInTheDocument();
  });

  it('应该显示查看全部链接', () => {
    render(<DashboardPage />);
    const link = screen.getByText(/查看全部/);
    expect(link).toBeInTheDocument();
    expect(link.closest('a')).toHaveAttribute('href', '/alerts');
  });
});

describe('DashboardPage - Loading', () => {
  it('应该在加载时显示加载中', async () => {
    const { useAlerts, useAlertStats } = await import('@/hooks/use-alerts');
    vi.mocked(useAlerts).mockReturnValueOnce({
      data: null, loading: true, error: null, load: vi.fn(), refresh: vi.fn(),
    });
    vi.mocked(useAlertStats).mockReturnValueOnce({
      data: null, loading: true, error: null, refresh: vi.fn(),
    });

    render(<DashboardPage />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });
});
