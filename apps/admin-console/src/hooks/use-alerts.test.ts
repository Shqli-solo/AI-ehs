/**
 * use-alerts.ts 单元测试
 *
 * 测试覆盖：
 * - useAlerts: 加载成功、加载失败 fallback、过滤条件、空数据
 * - useAlertStats: 加载成功、加载失败 fallback
 * - useReportAlert: 上报成功、上报失败、reset
 * - usePlanSearch: 搜索成功、搜索失败、reset
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import * as React from 'react';
import {
  useAlerts,
  useAlertStats,
  useReportAlert,
  usePlanSearch,
} from './use-alerts';
import { api } from '@/services/api';
import { mockAlerts } from '@/mock/alerts';

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    getAlerts: vi.fn(),
    getTodayStats: vi.fn(),
    reportAlert: vi.fn(),
    searchPlan: vi.fn(),
  },
}));

// Mock toast
vi.mock('sonner', () => ({
  toast: {
    warning: vi.fn(),
    error: vi.fn(),
    success: vi.fn(),
  },
}));

const { toast } = await import('sonner');

beforeEach(() => {
  vi.clearAllMocks();
});

// ============== useAlerts 测试 ==============

describe('useAlerts', () => {
  it('应该加载告警列表数据', async () => {
    const mockResponse = {
      data: {
        total: 2,
        pending: 1,
        processing: 1,
        resolved: 0,
        alerts: [
          {
            id: '1',
            type: 'fire',
            location: 'A栋3楼',
            riskLevel: 'HIGH',
            status: 'pending',
            time: '2026-04-17T08:30:00Z',
            deviceId: 'DEV-001',
            content: '烟感报警',
          },
        ],
      },
    };
    vi.mocked(api.getAlerts).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useAlerts({ autoLoad: true }));

    // 初始 loading
    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toHaveLength(1);
    expect(result.current.data?.[0].type).toBe('fire');
    expect(result.current.error).toBeNull();
  });

  it('应该在 API 失败时 fallback 到 mock 数据', async () => {
    vi.mocked(api.getAlerts).mockRejectedValueOnce(new Error('Network Error'));

    const { result } = renderHook(() => useAlerts({ fallbackToMock: true }));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockAlerts);
    expect(result.current.error).toBeNull();
    expect(toast.warning).toHaveBeenCalledWith('后端服务不可用，已切换到演示数据');
  });

  it('应该在 API 失败且 fallbackToMock=false 时返回 error', async () => {
    vi.mocked(api.getAlerts).mockRejectedValueOnce(new Error('Network Error'));

    const { result } = renderHook(() => useAlerts({ fallbackToMock: false }));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).not.toBeNull();
  });

  it('应该传递过滤参数到 API', async () => {
    vi.mocked(api.getAlerts).mockResolvedValueOnce({
      data: { total: 0, pending: 0, processing: 0, resolved: 0, alerts: [] },
    });

    renderHook(() => useAlerts({
      status: 'pending',
      riskLevel: 'high',
      pageSize: 20,
    }));

    await waitFor(() => {
      expect(api.getAlerts).toHaveBeenCalledWith({
        status: 'pending',
        riskLevel: 'high',
        pageSize: 20,
      });
    });
  });

  it('应该返回空的告警列表', async () => {
    vi.mocked(api.getAlerts).mockResolvedValueOnce({
      data: { total: 0, pending: 0, processing: 0, resolved: 0, alerts: [] },
    });

    const { result } = renderHook(() => useAlerts());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual([]);
  });

  it('应该支持手动 refresh', async () => {
    vi.mocked(api.getAlerts)
      .mockResolvedValueOnce({
        data: { total: 1, pending: 1, processing: 0, resolved: 0, alerts: [{ id: '1', type: 'fire', location: 'A', riskLevel: 'HIGH', status: 'pending', time: '2026-04-17T08:30:00Z' }] },
      })
      .mockResolvedValueOnce({
        data: { total: 2, pending: 2, processing: 0, resolved: 0, alerts: [{ id: '1', type: 'fire', location: 'A', riskLevel: 'HIGH', status: 'pending', time: '2026-04-17T08:30:00Z' }, { id: '2', type: 'gas_leak', location: 'B', riskLevel: 'MEDIUM', status: 'pending', time: '2026-04-17T09:00:00Z' }] },
      });

    const { result } = renderHook(() => useAlerts());

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toHaveLength(1);

    await result.current.refresh();

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toHaveLength(2);
  });
});

// ============== useAlertStats 测试 ==============

describe('useAlertStats', () => {
  it('应该加载统计数据', async () => {
    const mockStats = { total: 50, pending: 10, processing: 5, resolved: 35, change: '+5 起' };
    vi.mocked(api.getTodayStats).mockResolvedValueOnce(mockStats);

    const { result } = renderHook(() => useAlertStats(true));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockStats);
  });

  it('应该在 API 失败时 fallback 到 mock 数据', async () => {
    vi.mocked(api.getTodayStats).mockRejectedValueOnce(new Error('Network Error'));

    const { result } = renderHook(() => useAlertStats(true));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data?.total).toBe(12);
    expect(result.current.data?.pending).toBe(5);
  });

  it('应该在 API 失败且 fallbackToMock=false 时返回 error', async () => {
    vi.mocked(api.getTodayStats).mockRejectedValueOnce(new Error('Network Error'));

    const { result } = renderHook(() => useAlertStats(false));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toBeNull();
    expect(result.current.error).not.toBeNull();
  });
});

// ============== useReportAlert 测试 ==============

describe('useReportAlert', () => {
  it('应该成功上报告警', async () => {
    const mockResponse = { success: true, alert_id: 'ALT-123', risk_level: 'high' };
    vi.mocked(api.reportAlert).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => useReportAlert());

    const request = {
      device_id: 'DEV-001',
      device_type: 'smoke_detector',
      alert_type: 'fire',
      alert_content: '烟感报警',
      location: 'A栋3楼',
      alert_level: 3,
    };

    const response = await result.current.report(request);

    await waitFor(() => {
      expect(result.current.submitting).toBe(false);
    });

    expect(response?.success).toBe(true);
    expect(result.current.success).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it('应该处理上报失败', async () => {
    vi.mocked(api.reportAlert).mockRejectedValueOnce(new Error('API Error'));

    const { result } = renderHook(() => useReportAlert());

    const request = {
      device_id: 'DEV-999',
      device_type: 'smoke_detector',
      alert_type: 'fire',
      alert_content: '测试',
      location: 'A栋',
      alert_level: 1,
    };

    const response = await result.current.report(request);

    await waitFor(() => {
      expect(result.current.submitting).toBe(false);
    });

    expect(response).toBeNull();
    expect(result.current.success).toBe(false);
    expect(result.current.error).not.toBeNull();
  });

  it('应该支持 reset 重置状态', async () => {
    vi.mocked(api.reportAlert).mockRejectedValueOnce(new Error('API Error'));

    const { result } = renderHook(() => useReportAlert());

    await result.current.report({
      device_id: 'DEV-001',
      device_type: 'test',
      alert_type: 'test',
      alert_content: 'test',
      location: 'test',
      alert_level: 1,
    });

    await waitFor(() => {
      expect(result.current.submitting).toBe(false);
    });

    expect(result.current.success).toBe(false);
    expect(result.current.error).not.toBeNull();

    await act(async () => {
      result.current.reset();
    });

    expect(result.current.success).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.submitting).toBe(false);
  });
});

// ============== usePlanSearch 测试 ==============

describe('usePlanSearch', () => {
  it('应该成功搜索预案', async () => {
    const mockResponse = {
      success: true,
      plans: [
        { title: '火灾应急预案', content: '...', risk_level: 'high', source: 'ES', score: 0.95 },
      ],
      message: 'success',
    };
    vi.mocked(api.searchPlan).mockResolvedValueOnce(mockResponse);

    const { result } = renderHook(() => usePlanSearch());

    const response = await result.current.search({ query: '火灾', top_k: 5 });

    await waitFor(() => {
      expect(result.current.searching).toBe(false);
    });

    expect(response?.success).toBe(true);
    expect(result.current.plans).toHaveLength(1);
    expect(result.current.plans?.[0].title).toBe('火灾应急预案');
    expect(result.current.error).toBeNull();
  });

  it('应该处理搜索失败', async () => {
    vi.mocked(api.searchPlan).mockRejectedValueOnce(new Error('API Error'));

    const { result } = renderHook(() => usePlanSearch());

    const response = await result.current.search({ query: '测试' });

    await waitFor(() => {
      expect(result.current.searching).toBe(false);
    });

    expect(response).toBeNull();
    expect(result.current.plans).toBeNull();
    expect(result.current.error).not.toBeNull();
  });

  it('应该支持 reset 重置状态', async () => {
    vi.mocked(api.searchPlan).mockResolvedValueOnce({
      success: true,
      plans: [{ title: '预案', content: '...', risk_level: 'high', source: 'ES', score: 0.9 }],
      message: 'success',
    });

    const { result } = renderHook(() => usePlanSearch());

    await result.current.search({ query: '测试' });

    await waitFor(() => {
      expect(result.current.plans).not.toBeNull();
    });

    await act(async () => {
      result.current.reset();
    });

    expect(result.current.plans).toBeNull();
    expect(result.current.searching).toBe(false);
    expect(result.current.error).toBeNull();
  });
});
