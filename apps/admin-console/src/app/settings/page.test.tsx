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

import SettingsPage from './page';

describe('SettingsPage', () => {
  it('应该显示页面标题', () => {
    render(<SettingsPage />);
    expect(screen.getByText('系统设置')).toBeInTheDocument();
  });

  it('应该显示所有Tab', () => {
    render(<SettingsPage />);
    expect(screen.getByRole('tab', { name: '基本信息' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '告警配置' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '通知设置' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'API 管理' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: '操作日志' })).toBeInTheDocument();
  });

  it('应该显示基本信息Tab面板内容', () => {
    render(<SettingsPage />);
    // Default tab is "basic"
    expect(screen.getAllByText('基本信息').length).toBeGreaterThan(0);
    expect(screen.getByText('系统名称')).toBeInTheDocument();
    expect(screen.getByText('系统地址')).toBeInTheDocument();
    expect(screen.getByText('管理员邮箱')).toBeInTheDocument();
  });

  it('应该显示默认表单值', () => {
    render(<SettingsPage />);
    const siteNameInput = screen.getByDisplayValue('EHS 智能安保决策中台');
    expect(siteNameInput).toBeInTheDocument();
    const siteUrlInput = screen.getByDisplayValue('http://localhost:3000');
    expect(siteUrlInput).toBeInTheDocument();
    const adminEmailInput = screen.getByDisplayValue('admin@ehs.com');
    expect(adminEmailInput).toBeInTheDocument();
  });

  it('应该显示保存设置按钮', () => {
    render(<SettingsPage />);
    expect(screen.getByText('保存设置')).toBeInTheDocument();
  });

  it('点击保存应该调用toast.success', async () => {
    const { toast } = await import('sonner');
    const user = userEvent.setup();
    render(<SettingsPage />);
    const saveButton = screen.getByText('保存设置');
    await user.click(saveButton);

    expect(vi.mocked(toast.success)).toHaveBeenCalledWith('保存成功');
  });
});

describe('SettingsPage - Tab 切换', () => {
  it('点击Tab应该切换选中状态', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    // 基本信息 tab should be active initially
    const basicTab = screen.getByRole('tab', { name: '基本信息' });
    expect(basicTab).toHaveAttribute('aria-selected', 'true');

    // Click 告警配置 tab
    const alertConfigTab = screen.getByRole('tab', { name: '告警配置' });
    await user.click(alertConfigTab);

    // 告警配置 tab should now be active
    expect(alertConfigTab).toHaveAttribute('aria-selected', 'true');
    expect(basicTab).toHaveAttribute('aria-selected', 'false');
  });

  it('切换到告警配置Tab后基本信息Tab应该变为非选中', async () => {
    const user = userEvent.setup();
    render(<SettingsPage />);

    const basicTab = screen.getByRole('tab', { name: '基本信息' });
    const alertConfigTab = screen.getByRole('tab', { name: '告警配置' });
    expect(basicTab).toHaveAttribute('aria-selected', 'true');

    await user.click(alertConfigTab);

    expect(basicTab).toHaveAttribute('aria-selected', 'false');
    expect(alertConfigTab).toHaveAttribute('aria-selected', 'true');
  });
});
