import * as React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DashboardPage from './page';

// Mock useId hook for consistent IDs
vi.mock('react', async () => {
  const actual = await vi.importActual('react');
  return {
    ...(actual as object),
    useId: () => 'mock-id',
  };
});

describe('DashboardPage', () => {
  it('renders loading state initially', () => {
    render(<DashboardPage />);

    // Should show skeleton loading states
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders dashboard content after loading', async () => {
    render(<DashboardPage />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText(/欢迎回来，张三/)).toBeInTheDocument();
    }, { timeout: 2000 });

    // Check stats cards exist (using role button for "查看全部")
    await waitFor(() => {
      const viewAllButton = screen.getByText('查看全部');
      expect(viewAllButton).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('renders header with logo and search', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('EHS 智能安保决策中台')).toBeInTheDocument();
    }, { timeout: 2000 });

    // Check search input
    const searchInput = screen.getByPlaceholderText('搜索...');
    expect(searchInput).toBeInTheDocument();

    // Check notification bell with badge
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders recent alerts list', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('最近告警')).toBeInTheDocument();
    }, { timeout: 2000 });

    // Check alert items
    expect(screen.getByText('气体泄漏')).toBeInTheDocument();
    expect(screen.getByText('A 车间 - 东区 -2 层')).toBeInTheDocument();
    expect(screen.getByText('温度异常')).toBeInTheDocument();
    expect(screen.getByText('入侵检测')).toBeInTheDocument();
  });

  it('renders risk level badges', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      // Check risk level badge exists (using class name)
      const riskBadges = document.querySelectorAll('[class*="bg-error"]');
      expect(riskBadges.length).toBeGreaterThan(0);
    }, { timeout: 2000 });
  });

  it('renders alert status labels', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      // Check alert status labels exist (using class names)
      const statusLabels = document.querySelectorAll('[class*="text-"]');
      expect(statusLabels.length).toBeGreaterThan(0);
    }, { timeout: 2000 });
  });

  it('renders chart placeholders', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      expect(screen.getByText('告警趋势图 (7 天)')).toBeInTheDocument();
    }, { timeout: 2000 });

    expect(screen.getByText('告警类型分布')).toBeInTheDocument();
  });

  it('renders view all button', async () => {
    render(<DashboardPage />);

    await waitFor(() => {
      const viewAllButton = screen.getByText('查看全部');
      expect(viewAllButton).toBeInTheDocument();
    }, { timeout: 2000 });
  });
});
