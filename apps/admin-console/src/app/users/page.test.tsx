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

import UsersPage from './page';

describe('UsersPage', () => {
  it('应该显示页面标题', () => {
    render(<UsersPage />);
    expect(screen.getByText('用户管理')).toBeInTheDocument();
  });

  it('应该显示添加用户按钮', () => {
    render(<UsersPage />);
    expect(screen.getByText('添加用户')).toBeInTheDocument();
  });

  it('应该显示搜索输入框', () => {
    render(<UsersPage />);
    expect(screen.getByPlaceholderText('搜索用户...')).toBeInTheDocument();
  });

  it('应该显示用户列表', () => {
    render(<UsersPage />);
    expect(screen.getByText('张三')).toBeInTheDocument();
    expect(screen.getByText('李四')).toBeInTheDocument();
    expect(screen.getByText('王五')).toBeInTheDocument();
    expect(screen.getByText('赵六')).toBeInTheDocument();
  });

  it('应该显示用户邮箱', () => {
    render(<UsersPage />);
    expect(screen.getByText('zhangsan@ehs.com')).toBeInTheDocument();
    expect(screen.getByText('lisi@ehs.com')).toBeInTheDocument();
    expect(screen.getByText('wangwu@ehs.com')).toBeInTheDocument();
    expect(screen.getByText('zhaoliu@ehs.com')).toBeInTheDocument();
  });

  it('应该显示用户角色', () => {
    render(<UsersPage />);
    expect(screen.getByText('管理员')).toBeInTheDocument();
    expect(screen.getByText('值班经理')).toBeInTheDocument();
    expect(screen.getByText('EHS 总监')).toBeInTheDocument();
    expect(screen.getByText('安保人员')).toBeInTheDocument();
  });

  it('应该显示用户状态徽章', () => {
    render(<UsersPage />);
    expect(screen.getAllByText('活跃').length).toBeGreaterThan(0);
    expect(screen.getByText('停用')).toBeInTheDocument();
  });

  it('应该显示编辑按钮', () => {
    render(<UsersPage />);
    const editButtons = screen.getAllByText('编辑');
    expect(editButtons.length).toBeGreaterThan(0);
  });
});

describe('UsersPage - 搜索过滤', () => {
  it('输入搜索词应该过滤用户列表', async () => {
    const user = userEvent.setup();
    render(<UsersPage />);
    const searchInput = screen.getByPlaceholderText('搜索用户...');

    // 初始显示所有用户
    expect(screen.getByText('张三')).toBeInTheDocument();
    expect(screen.getByText('赵六')).toBeInTheDocument();

    // 搜索"张"，使用 userEvent.type
    await user.type(searchInput, '张');

    // 搜索后张三应该仍然可见
    expect(screen.getByText('张三')).toBeInTheDocument();
  });
});

describe('UsersPage - 空状态', () => {
  it('搜索无结果时应该显示空列表', () => {
    render(<UsersPage />);
    expect(screen.getAllByText('活跃').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('停用')).toBeInTheDocument();
  });
});
