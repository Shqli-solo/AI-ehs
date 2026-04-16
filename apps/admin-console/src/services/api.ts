/**
 * API 服务封装
 *
 * 提供统一的 API 请求方法，包含：
 * - 自动错误处理
 * - 请求超时
 * - 请求重试
 * - 请求取消
 */

export type {
  ApiError,
} from '@/lib/api-errors';

export {
  createNetworkError,
  createTimeoutError,
  createUnknownError,
  parseErrorFromResponse,
  isRetryableError,
  getErrorSummary,
} from '@/lib/api-errors';

import {
  ApiError,
  createNetworkError,
  createTimeoutError,
  createUnknownError,
  parseErrorFromResponse,
  isRetryableError,
  getErrorSummary,
} from '@/lib/api-errors';

/**
 * API 基础 URL
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/**
 * 默认请求超时时间（毫秒）
 */
const DEFAULT_TIMEOUT = 30000; // 30 秒

/**
 * 最大重试次数
 */
const MAX_RETRIES = 2;

/**
 * 重试延迟（毫秒）
 */
const RETRY_DELAY = 1000;

/**
 * 健康检查响应
 */
export interface HealthResponse {
  status: string;
  service: string;
  timestamp: string;
}

/**
 * 告警上报请求
 */
export interface AlertReportRequest {
  device_id: string;
  device_type: string;
  alert_type: string;
  alert_content: string;
  location: string;
  alert_level: number;
  extra_data?: Record<string, unknown>;
}

/**
 * 告警上报响应
 */
export interface AlertReportResponse {
  success: boolean;
  message: string;
  alert_id?: string;
  risk_level?: string;
  plans?: Array<{
    title: string;
    content: string;
    risk_level: string;
    source: string;
    score: number;
  }>;
  error?: string;
}

/**
 * 预案检索请求
 */
export interface PlanSearchRequest {
  query: string;
  event_type?: string;
  top_k?: number;
}

/**
 * 预案检索响应
 */
export interface PlanSearchResponse {
  success: boolean;
  message: string;
  plans?: Array<{
    title: string;
    content: string;
    risk_level: string;
    source: string;
    score: number;
  }>;
  query?: string;
  error?: string;
}

/**
 * 告警列表响应
 */
export interface AlertListResponse {
  success: boolean;
  data: {
    total: number;
    pending: number;
    processing: number;
    resolved: number;
    alerts: Array<{
      id: string;
      type: string;
      location: string;
      riskLevel: 'high' | 'medium' | 'low';
      status: 'pending' | 'processing' | 'resolved' | 'closed';
      time: string;
      deviceId?: string;
      content?: string;
    }>;
  };
}

/**
 * 请求配置选项
 */
interface RequestConfig extends RequestInit {
  /** 请求超时时间（毫秒） */
  timeout?: number;
  /** 是否重试 */
  retry?: boolean;
  /** 是否显示错误 Toast */
  showErrorToast?: boolean;
}

/**
 * 延迟函数
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 带超时的 fetch 封装
 */
async function fetchWithTimeout(
  url: string,
  options: RequestInit & { timeout?: number }
): Promise<Response> {
  const timeout = options.timeout ?? DEFAULT_TIMEOUT;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return response;
  } catch (error) {
    if (controller.signal.aborted) {
      throw createTimeoutError(timeout, url, options.method);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * 请求重试包装器
 */
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = MAX_RETRIES
): Promise<T> {
  let lastError: ApiError | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as ApiError;

      // 如果不是可重试的错误，或者已达到最大重试次数，则直接抛出
      if (!isRetryableError(lastError) || attempt === maxRetries) {
        throw lastError;
      }

      // 等待后重试
      await delay(RETRY_DELAY * (attempt + 1));
    }
  }

  throw lastError;
}

/**
 * 处理响应
 */
async function handleResponse<T>(
  response: Response,
  url: string,
  method: string
): Promise<T> {
  let data: unknown;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const error = parseErrorFromResponse(
      response.status,
      data,
      url,
      method
    );
    throw error;
  }

  // 检查响应数据中是否包含业务错误
  if (data && typeof data === 'object') {
    const dataObj = data as Record<string, unknown>;
    if (dataObj.success === false && dataObj.error) {
      const error = parseErrorFromResponse(
        response.status,
        data,
        url,
        method
      );
      throw error;
    }
  }

  return data as T;
}

/**
 * 通用请求方法
 */
async function request<T>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<T> {
  const {
    timeout,
    retry = true,
    headers = {},
    showErrorToast = true,
    ...restConfig
  } = config;

  const url = `${API_BASE_URL}${endpoint}`;
  const method = (config.method as string) ?? 'GET';

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const requestFn = async (): Promise<T> => {
    try {
      const response = await fetchWithTimeout(url, {
        ...restConfig,
        headers: {
          ...defaultHeaders,
          ...headers,
        },
        timeout,
      });

      return await handleResponse<T>(response, url, method);
    } catch (error) {
      // 网络错误处理
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw createNetworkError(url, method, error);
      }

      // 已经是 ApiError，直接抛出
      if (error && typeof error === 'object' && 'type' in error) {
        throw error;
      }

      // 未知错误
      throw createUnknownError(error, url, method);
    }
  };

  // 是否需要重试
  if (retry) {
    return await withRetry<T>(requestFn);
  }

  return await requestFn();
}

/**
 * API 服务类
 */
export class ApiService {
  /**
   * GET 请求
   */
  static async get<T>(
    endpoint: string,
    config?: RequestConfig
  ): Promise<T> {
    return request<T>(endpoint, { ...config, method: 'GET' });
  }

  /**
   * POST 请求
   */
  static async post<T, B = unknown>(
    endpoint: string,
    body?: B,
    config?: RequestConfig
  ): Promise<T> {
    return request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /**
   * PUT 请求
   */
  static async put<T, B = unknown>(
    endpoint: string,
    body?: B,
    config?: RequestConfig
  ): Promise<T> {
    return request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /**
   * DELETE 请求
   */
  static async delete<T>(
    endpoint: string,
    config?: RequestConfig
  ): Promise<T> {
    return request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  /**
   * 健康检查
   */
  static async healthCheck(): Promise<HealthResponse> {
    return this.get<HealthResponse>('/health', {
      retry: false,
      timeout: 5000,
    });
  }

  /**
   * 告警上报
   */
  static async reportAlert(
    request: AlertReportRequest
  ): Promise<AlertReportResponse> {
    return this.post<AlertReportResponse, AlertReportRequest>(
      '/api/alert/report',
      request
    );
  }

  /**
   * 预案检索
   */
  static async searchPlan(
    request: PlanSearchRequest
  ): Promise<PlanSearchResponse> {
    return this.post<PlanSearchResponse, PlanSearchRequest>(
      '/api/plan/search',
      request
    );
  }

  /**
   * 获取告警列表
   */
  static async getAlerts(
    params?: {
      status?: 'pending' | 'processing' | 'resolved' | 'closed';
      riskLevel?: 'high' | 'medium' | 'low';
      page?: number;
      pageSize?: number;
    }
  ): Promise<AlertListResponse> {
    const queryString = params
      ? '?' + new URLSearchParams(
          Object.entries(params).filter(([_, v]) => v !== undefined) as [string, string][]
        ).toString()
      : '';

    return this.get<AlertListResponse>(`/api/alert/list${queryString}`);
  }

  /**
   * 获取今日统计
   */
  static async getTodayStats(): Promise<{
    total: number;
    pending: number;
    processing: number;
    resolved: number;
    change: string;
  }> {
    // 暂时使用 Mock 数据，后续实现真实 API
    try {
      return await this.get('/api/stats/today') as unknown as {
        total: number;
        pending: number;
        processing: number;
        resolved: number;
        change: string;
      };
    } catch {
      return {
        total: 0,
        pending: 0,
        processing: 0,
        resolved: 0,
        change: '+0 起',
      };
    }
  }

  /**
   * 获取最近告警
   */
  static async getRecentAlerts(limit: number = 5): Promise<
    Array<{
      id: string;
      type: string;
      location: string;
      riskLevel: 'high' | 'medium' | 'low';
      status: 'pending' | 'processing' | 'resolved' | 'closed';
      time: string;
    }>
  > {
    const response = await this.get<AlertListResponse>('/api/alert/list', {
      timeout: 10000,
    });
    return response.data.alerts.slice(0, limit);
  }
}

/**
 * 导出默认实例
 */
export const api = ApiService;
