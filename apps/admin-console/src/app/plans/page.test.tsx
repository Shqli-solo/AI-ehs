import * as React from 'react';
import { render, screen, within } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

vi.mock('@/hooks/use-alerts', () => ({
  useAlerts: vi.fn(),
  useAlertStats: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), warning: vi.fn(), error: vi.fn() },
}));

import PlansPage from './page';

describe('PlansPage', () => {
  it('应该显示页面标题', () => {
    render(<PlansPage />);
    expect(screen.getByText('预案管理')).toBeInTheDocument();
  });

  it('应该显示分类筛选器', () => {
    render(<PlansPage />);
    expect(screen.getByText('全部分类')).toBeInTheDocument();
  });

  it('应该显示预案卡片', () => {
    render(<PlansPage />);
    expect(screen.getByText('火灾应急预案')).toBeInTheDocument();
    expect(screen.getByText('气体泄漏应急预案')).toBeInTheDocument();
    expect(screen.getByText('温度异常处置预案')).toBeInTheDocument();
    expect(screen.getByText('入侵处置预案')).toBeInTheDocument();
  });

  it('应该显示预案分类和版本标签', () => {
    render(<PlansPage />);
    expect(screen.getByText('火灾')).toBeInTheDocument();
    expect(screen.getByText('v2.3')).toBeInTheDocument();
    expect(screen.getByText('v1.8')).toBeInTheDocument();
  });

  it('应该显示已发布状态徽章', () => {
    render(<PlansPage />);
    const publishedBadges = screen.getAllByText('已发布');
    expect(publishedBadges.length).toBeGreaterThan(0);
  });

  it('应该显示风险等级徽章', () => {
    render(<PlansPage />);
    expect(screen.getByText('严重')).toBeInTheDocument();
    const highBadges = screen.getAllByText('高');
    expect(highBadges.length).toBeGreaterThan(0);
    expect(screen.getByText('中')).toBeInTheDocument();
  });

  it('应该显示预案内容摘要', () => {
    render(<PlansPage />);
    expect(screen.getByText(/立即启动火灾报警系统/)).toBeInTheDocument();
  });

  it('应该显示作者和更新时间', () => {
    render(<PlansPage />);
    expect(screen.getByText(/2026-04-10 by 张三/)).toBeInTheDocument();
  });

  it('应该显示预览按钮', () => {
    render(<PlansPage />);
    const previewButtons = screen.getAllByText('预览');
    expect(previewButtons.length).toBeGreaterThan(0);
  });
});
