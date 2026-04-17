import * as React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';

vi.mock('@/hooks/use-alerts', () => ({
  useAlerts: vi.fn(),
  useAlertStats: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), warning: vi.fn(), error: vi.fn() },
}));

import AgentsPage from './page';

describe('AgentsPage', () => {
  it('应该显示页面标题', () => {
    render(<AgentsPage />);
    expect(screen.getByText('Agent 编排')).toBeInTheDocument();
  });

  it('应该显示新建工作流按钮', () => {
    render(<AgentsPage />);
    expect(screen.getByText('新建工作流')).toBeInTheDocument();
  });

  it('应该显示Tab列表', () => {
    render(<AgentsPage />);
    expect(screen.getByRole('tab', { name: '工作流配置' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '节点管理' })).toBeInTheDocument();
  });

  it('应该显示默认工作流标题（默认Tab）', () => {
    render(<AgentsPage />);
    expect(screen.getByText('默认工作流')).toBeInTheDocument();
  });

  it('应该显示工作流中的RiskAgent节点', () => {
    render(<AgentsPage />);
    expect(screen.getByText('RiskAgent')).toBeInTheDocument();
    expect(screen.getByText('风险感知 - 分析告警内容')).toBeInTheDocument();
  });

  it('应该显示工作流中的SearchAgent节点', () => {
    render(<AgentsPage />);
    expect(screen.getByText('SearchAgent')).toBeInTheDocument();
    expect(screen.getByText('预案检索 - GraphRAG 匹配')).toBeInTheDocument();
  });

  it('应该显示输出节点', () => {
    render(<AgentsPage />);
    expect(screen.getByText('输出')).toBeInTheDocument();
    expect(screen.getByText('结构化响应')).toBeInTheDocument();
  });

  it('应该显示节点运行中状态', () => {
    render(<AgentsPage />);
    const runningBadges = screen.getAllByText('运行中');
    expect(runningBadges.length).toBeGreaterThanOrEqual(2);
  });

  it('应该显示测试运行和编辑按钮', () => {
    render(<AgentsPage />);
    expect(screen.getByText('测试运行')).toBeInTheDocument();
    expect(screen.getByText('编辑')).toBeInTheDocument();
  });

  it('默认工作流配置Tab应该是选中状态', () => {
    render(<AgentsPage />);
    const workflowTab = screen.getByRole('tab', { name: '工作流配置' });
    expect(workflowTab).toHaveAttribute('aria-selected', 'true');
  });
});

describe('AgentsPage - Tab 切换', () => {
  it('点击节点管理Tab应该切换选中状态', async () => {
    const user = userEvent.setup();
    render(<AgentsPage />);

    const workflowTab = screen.getByRole('tab', { name: '工作流配置' });
    const nodesTab = screen.getByRole('tab', { name: '节点管理' });
    expect(workflowTab).toHaveAttribute('aria-selected', 'true');

    await user.click(nodesTab);

    expect(nodesTab).toHaveAttribute('aria-selected', 'true');
    expect(workflowTab).toHaveAttribute('aria-selected', 'false');
  });
});
