/**
 * 告警相关自定义 Hook
 *
 * 包含：
 * - useAlerts: 获取告警列表
 * - useAlertStats: 获取告警统计
 * - useReportAlert: 告警上报
 * - usePlanSearch: 预案检索
 */

import * as React from 'react';
import { api } from '@/services/api';
import { mockAlerts, alertStats } from '@/mock/alerts';
import { Alert } from '@/types/alert';
import type { ApiError, AlertReportRequest, PlanSearchRequest, AlertReportResponse, PlanSearchResponse } from '@/services/api';
import { toast } from 'sonner';

/**
 * 告警统计接口
 */
export interface AlertStats {
  total: number;
  pending: number;
  processing: number;
  resolved: number;
  change: string;
}

/**
 * Hook 状态接口
 */
interface HookState<T> {
  /** 数据 */
  data: T | null;
  /** 加载中 */
  loading: boolean;
  /** 错误信息 */
  error: ApiError | null;
}

/**
 * 告警列表 Hook 选项
 */
interface UseAlertsOptions {
  /** 是否自动加载 */
  autoLoad?: boolean;
  /** 告警状态过滤 */
  status?: 'pending' | 'processing' | 'resolved' | 'closed';
  /** 风险等级过滤 */
  riskLevel?: 'high' | 'medium' | 'low';
  /** 页面大小 */
  pageSize?: number;
  /** API 不可用时是否回退到 mock 数据 */
  fallbackToMock?: boolean;
}

/**
 * 告警列表 Hook 返回值
 */
interface UseAlertsReturn extends HookState<Alert[]> {
  /** 手动加载 */
  load: () => Promise<void>;
  /** 刷新 */
  refresh: () => Promise<void>;
}

/**
 * 告警列表 Hook
 *
 * @example
 * ```tsx
 * const { alerts, loading, error, load, refresh } = useAlerts();
 * ```
 */
export function useAlerts(options: UseAlertsOptions = {}): UseAlertsReturn {
  const {
    autoLoad = true,
    status,
    riskLevel,
    pageSize = 10,
    fallbackToMock = true,
  } = options;

  const [state, setState] = React.useState<HookState<Alert[]>>({
    data: null,
    loading: false,
    error: null,
  });

  const load = React.useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await api.getAlerts({
        status,
        riskLevel,
        pageSize,
      });
      const mapped: Alert[] = response.data.alerts.map((a) => ({
        id: a.id,
        type: mapAlertType(a.type),
        title: `${a.type} - ${a.location}`,
        content: a.content || "",
        riskLevel: a.riskLevel as Alert["riskLevel"],
        status: a.status as Alert["status"],
        location: a.location,
        deviceId: a.deviceId || "",
        createdAt: a.time,
      }));
      setState({
        data: mapped,
        loading: false,
        error: null,
      });
    } catch (error) {
      if (fallbackToMock) {
        setState({
          data: mockAlerts,
          loading: false,
          error: null,
        });
        toast.warning("后端服务不可用，已切换到演示数据");
      } else {
        setState({
          data: null,
          loading: false,
          error: error as ApiError,
        });
      }
    }
  }, [status, riskLevel, pageSize, fallbackToMock]);

  const refresh = React.useCallback(async () => {
    await load();
  }, [load]);

  React.useEffect(() => {
    if (autoLoad) {
      load();
    }
  }, [autoLoad, load]);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    load,
    refresh,
  };
}

/**
 * 告警统计 Hook 返回值
 */
interface UseAlertStatsReturn extends HookState<AlertStats> {
  /** 刷新 */
  refresh: () => Promise<void>;
}

/**
 * 告警统计 Hook
 *
 * @example
 * ```tsx
 * const { stats, loading, error, refresh } = useAlertStats();
 * ```
 */
export function useAlertStats(fallbackToMock: boolean = true): UseAlertStatsReturn {
  const [state, setState] = React.useState<HookState<AlertStats>>({
    data: null,
    loading: false,
    error: null,
  });

  const loadStats = React.useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await api.getTodayStats();
      setState({
        data,
        loading: false,
        error: null,
      });
    } catch (error) {
      if (fallbackToMock) {
        setState({
          data: {
            total: alertStats.today,
            pending: alertStats.pending,
            processing: alertStats.processing,
            resolved: alertStats.resolved,
            change: '+0 起',
          },
          loading: false,
          error: null,
        });
      } else {
        setState({
          data: null,
          loading: false,
          error: error as ApiError,
        });
      }
    }
  }, [fallbackToMock]);

  const refresh = React.useCallback(async () => {
    await loadStats();
  }, [loadStats]);

  React.useEffect(() => {
    loadStats();
  }, [loadStats]);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    refresh,
  };
}

/**
 * 告警上报 Hook 状态
 */
interface ReportAlertState {
  /** 提交中 */
  submitting: boolean;
  /** 提交成功 */
  success: boolean;
  /** 错误信息 */
  error: ApiError | null;
}

/**
 * 告警上报 Hook 返回值
 */
interface UseReportAlertReturn extends ReportAlertState {
  /** 提交函数 */
  report: (request: AlertReportRequest) => Promise<AlertReportResponse | null>;
  /** 重置状态 */
  reset: () => void;
}

/**
 * 告警上报 Hook
 *
 * @example
 * ```tsx
 * const { report, submitting, success, error, reset } = useReportAlert();
 * ```
 */
export function useReportAlert(): UseReportAlertReturn {
  const [state, setState] = React.useState<ReportAlertState>({
    submitting: false,
    success: false,
    error: null,
  });

  const report = React.useCallback(
    async (request: AlertReportRequest): Promise<AlertReportResponse | null> => {
      setState({
        submitting: true,
        success: false,
        error: null,
      });

      try {
        const response = await api.reportAlert(request);
        setState({
          submitting: false,
          success: response.success,
          error: null,
        });
        return response;
      } catch (error) {
        setState({
          submitting: false,
          success: false,
          error: error as ApiError,
        });
        return null;
      }
    },
    []
  );

  const reset = React.useCallback(() => {
    setState({
      submitting: false,
      success: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    report,
    reset,
  };
}

/**
 * 预案检索 Hook 状态
 */
interface PlanSearchState {
  /** 搜索中 */
  searching: boolean;
  /** 错误信息 */
  error: ApiError | null;
}

/**
 * 预案检索 Hook 返回值
 */
interface UsePlanSearchReturn extends PlanSearchState {
  /** 预案列表 */
  plans: Array<{
    title: string;
    content: string;
    risk_level: string;
    source: string;
    score: number;
  }> | null;
  /** 搜索函数 */
  search: (request: PlanSearchRequest) => Promise<PlanSearchResponse | null>;
  /** 重置 */
  reset: () => void;
}

/**
 * 预案检索 Hook
 *
 * @example
 * ```tsx
 * const { plans, searching, error, search, reset } = usePlanSearch();
 * ```
 */
export function usePlanSearch(): UsePlanSearchReturn {
  const [state, setState] = React.useState<PlanSearchState>({
    searching: false,
    error: null,
  });
  const [plans, setPlans] = React.useState<UsePlanSearchReturn['plans']>(null);

  const search = React.useCallback(
    async (request: PlanSearchRequest): Promise<PlanSearchResponse | null> => {
      setState({
        searching: true,
        error: null,
      });

      try {
        const response = await api.searchPlan(request);
        setPlans(response.plans ?? null);
        setState({
          searching: false,
          error: null,
        });
        return response;
      } catch (error) {
        setState({
          searching: false,
          error: error as ApiError,
        });
        setPlans(null);
        return null;
      }
    },
    []
  );

  const reset = React.useCallback(() => {
    setState({
      searching: false,
      error: null,
    });
    setPlans(null);
  }, []);

  return {
    ...state,
    plans,
    search,
    reset,
  };
}

/**
 * 设备在线率 Hook
 */
interface UseDeviceOnlineRateReturn {
  /** 在线率 */
  rate: number | null;
  /** 加载中 */
  loading: boolean;
  /** 错误 */
  error: ApiError | null;
  /** 刷新 */
  refresh: () => Promise<void>;
}

/**
 * 设备在线率 Hook（Mock 数据，后续实现真实 API）
 */
export function useDeviceOnlineRate(): UseDeviceOnlineRateReturn {
  const [state, setState] = React.useState({
    rate: null as number | null,
    loading: true,
    error: null as ApiError | null,
  });

  const load = React.useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    // TODO: 实现真实 API
    // const data = await api.getDeviceOnlineRate();

    // 模拟加载
    await new Promise(resolve => setTimeout(resolve, 500));
    setState({
      rate: 98.5,
      loading: false,
      error: null,
    });
  }, []);

  const refresh = React.useCallback(async () => {
    await load();
  }, [load]);

  React.useEffect(() => {
    load();
  }, [load]);

  return {
    rate: state.rate,
    loading: state.loading,
    error: state.error,
    refresh,
  };
}

/**
 * 安全运行天数 Hook
 */
interface UseSafeDaysReturn {
  /** 天数 */
  days: number;
  /** 加载中 */
  loading: boolean;
  /** 刷新 */
  refresh: () => Promise<void>;
}

/**
 * 安全运行天数 Hook（Mock 数据，后续实现真实 API）
 */
export function useSafeDays(): UseSafeDaysReturn {
  const [state, setState] = React.useState({
    days: 45,
    loading: false,
  });

  const refresh = React.useCallback(async () => {
    setState(prev => ({ ...prev, loading: true }));

    // TODO: 实现真实 API
    // const data = await api.getSafeDays();

    await new Promise(resolve => setTimeout(resolve, 300));
    setState({
      days: 45,
      loading: false,
    });
  }, []);

  return {
    days: state.days,
    loading: state.loading,
    refresh,
  };
}

/**
 * 将后端告警类型映射到前端类型
 */
function mapAlertType(type: string): Alert["type"] {
  const typeMap: Record<string, Alert["type"]> = {
    fire: "fire",
    gas_leak: "gas_leak",
    temperature: "temperature",
    intrusion: "intrusion",
    smoke: "smoke",
    烟火告警: "fire",
    气体泄漏: "gas_leak",
    温度异常: "temperature",
    入侵检测: "intrusion",
  };
  return typeMap[type] || "smoke";
}
