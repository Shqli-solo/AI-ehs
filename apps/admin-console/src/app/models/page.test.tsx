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

import ModelsPage from './page';

describe('ModelsPage', () => {
  it('应该显示页面标题', () => {
    render(<ModelsPage />);
    expect(screen.getByText('模型管理')).toBeInTheDocument();
  });

  it('应该显示Tab列表', () => {
    render(<ModelsPage />);
    expect(screen.getByRole('tab', { name: '模型配置' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '微调记录' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '评估报告' })).toBeInTheDocument();
  });

  it('应该显示已部署模型列表（默认Tab）', () => {
    render(<ModelsPage />);
    expect(screen.getByText('已部署模型')).toBeInTheDocument();
    expect(screen.getByText('Qwen3-7B')).toBeInTheDocument();
    expect(screen.getByText('BGE-Reranker')).toBeInTheDocument();
    expect(screen.getByText('BERT-risk')).toBeInTheDocument();
  });

  it('应该显示模型类型', () => {
    render(<ModelsPage />);
    expect(screen.getByText('LLM')).toBeInTheDocument();
    expect(screen.getByText('重排序')).toBeInTheDocument();
    expect(screen.getByText('风险分级')).toBeInTheDocument();
  });

  it('应该显示模型运行状态', () => {
    render(<ModelsPage />);
    const runningBadges = screen.getAllByText('运行中');
    expect(runningBadges.length).toBeGreaterThan(0);
    expect(screen.getAllByText('待部署').length).toBeGreaterThan(0);
  });

  it('应该显示模型端点地址', () => {
    render(<ModelsPage />);
    expect(screen.getByText('http://localhost:11434')).toBeInTheDocument();
    expect(screen.getByText('http://localhost:6006')).toBeInTheDocument();
  });

  it('默认模型配置Tab应该是选中状态', () => {
    render(<ModelsPage />);
    const modelsTab = screen.getByRole('tab', { name: '模型配置' });
    expect(modelsTab).toHaveAttribute('aria-selected', 'true');
  });
});

describe('ModelsPage - Tab 切换', () => {
  it('点击微调记录Tab应该切换选中状态', async () => {
    const user = userEvent.setup();
    render(<ModelsPage />);

    const modelsTab = screen.getByRole('tab', { name: '模型配置' });
    const fineTuneTab = screen.getByRole('tab', { name: '微调记录' });
    expect(modelsTab).toHaveAttribute('aria-selected', 'true');

    await user.click(fineTuneTab);

    expect(fineTuneTab).toHaveAttribute('aria-selected', 'true');
    expect(modelsTab).toHaveAttribute('aria-selected', 'false');
  });

  it('点击评估报告Tab应该切换选中状态', async () => {
    const user = userEvent.setup();
    render(<ModelsPage />);

    const evalTab = screen.getByRole('tab', { name: '评估报告' });
    await user.click(evalTab);

    expect(evalTab).toHaveAttribute('aria-selected', 'true');
  });
});
