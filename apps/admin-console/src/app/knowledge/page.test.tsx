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

import KnowledgePage from './page';

describe('KnowledgePage', () => {
  it('应该显示页面标题', () => {
    render(<KnowledgePage />);
    expect(screen.getByText('知识库管理')).toBeInTheDocument();
  });

  it('应该显示Tab列表', () => {
    render(<KnowledgePage />);
    expect(screen.getByRole('tab', { name: '文档管理' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '上传文档' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '检索测试' })).toBeInTheDocument();
  });

  it('应该显示已上传文档列表（默认Tab）', () => {
    render(<KnowledgePage />);
    expect(screen.getByText('已上传文档')).toBeInTheDocument();
    expect(screen.getByText('火灾应急预案.pdf')).toBeInTheDocument();
    expect(screen.getByText('气体泄漏处置流程.docx')).toBeInTheDocument();
    expect(screen.getByText('安全生产管理制度.pdf')).toBeInTheDocument();
  });

  it('应该显示文档大小和日期', () => {
    render(<KnowledgePage />);
    expect(screen.getByText('2.3 MB · 2026-04-10')).toBeInTheDocument();
    expect(screen.getByText('1.1 MB · 2026-04-08')).toBeInTheDocument();
    expect(screen.getByText('3.5 MB · 2026-04-05')).toBeInTheDocument();
  });

  it('应该显示文档索引状态', () => {
    render(<KnowledgePage />);
    expect(screen.getAllByText('已索引').length).toBeGreaterThan(0);
    expect(screen.getAllByText('向量化中').length).toBeGreaterThan(0);
  });

  it('默认文档管理Tab应该是选中状态', () => {
    render(<KnowledgePage />);
    const docsTab = screen.getByRole('tab', { name: '文档管理' });
    expect(docsTab).toHaveAttribute('aria-selected', 'true');
  });
});

describe('KnowledgePage - Tab 切换', () => {
  it('点击上传文档Tab应该切换选中状态', async () => {
    const user = userEvent.setup();
    render(<KnowledgePage />);

    const docsTab = screen.getByRole('tab', { name: '文档管理' });
    const uploadTab = screen.getByRole('tab', { name: '上传文档' });
    expect(docsTab).toHaveAttribute('aria-selected', 'true');

    await user.click(uploadTab);

    expect(uploadTab).toHaveAttribute('aria-selected', 'true');
    expect(docsTab).toHaveAttribute('aria-selected', 'false');
  });

  it('点击检索测试Tab应该切换选中状态', async () => {
    const user = userEvent.setup();
    render(<KnowledgePage />);

    const searchTab = screen.getByRole('tab', { name: '检索测试' });
    await user.click(searchTab);

    expect(searchTab).toHaveAttribute('aria-selected', 'true');
  });
});
