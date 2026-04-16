/**
 * API 服务测试
 *
 * 测试覆盖：
 * - 错误处理
 * - 请求重试
 * - 超时处理
 * - 响应解析
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ApiService } from './api';
import {
  HTTP_STATUS_MAP,
  BUSINESS_ERROR_MAP,
  createHttpError,
  createBusinessError,
  createNetworkError,
  createTimeoutError,
  parseErrorFromResponse,
  isRetryableError,
  getErrorSummary,
} from '@/lib/api-errors';

// Mock fetch
global.fetch = vi.fn();

/**
 * 创建 mock 响应辅助函数
 */
function createMockResponse(data: unknown, status = 200, ok = true): Response {
  return {
    ok,
    status,
    json: async () => data,
    headers: new Headers(),
    statusText: '',
    type: 'basic' as ResponseType,
    url: '',
    redirected: false,
    body: null,
    bodyUsed: false,
    arrayBuffer: async () => new ArrayBuffer(0),
    blob: async () => new Blob(),
    formData: async () => new FormData(),
    text: async () => '',
    clone: () => createMockResponse(data, status, ok),
  } as Response;
}

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('错误处理', () => {
    it('应该正确处理 HTTP 400 错误', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse({ message: 'Bad Request' }, 400, false)
      );

      await expect(ApiService.get('/api/test')).rejects.toMatchObject({
        type: 'HTTP_ERROR',
        code: 400,
      });
    });

    it('应该正确处理 HTTP 500 错误', async () => {
      // Mock 三次响应（初始 + 2 次重试）
      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse({ message: 'Internal Server Error' }, 500, false)
      );
      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse({ message: 'Internal Server Error' }, 500, false)
      );
      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse({ message: 'Internal Server Error' }, 500, false)
      );

      await expect(ApiService.get('/api/test')).rejects.toMatchObject({
        type: 'HTTP_ERROR',
        code: 500,
      });
    });

    it('应该正确处理网络错误', async () => {
      vi.mocked(global.fetch).mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      // 由于重试机制，需要 mock 多次失败
      vi.mocked(global.fetch).mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      vi.mocked(global.fetch).mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      await expect(ApiService.get('/api/test', { retry: false })).rejects.toMatchObject({
        type: 'NETWORK_ERROR',
        code: 'NETWORK_ERROR',
      });
    });

    it('应该正确处理业务错误', async () => {
      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse({ success: false, error: 'ALERT_NOT_FOUND' }, 200, true)
      );

      await expect(ApiService.get('/api/alert/invalid')).rejects.toMatchObject({
        type: 'BUSINESS_ERROR',
        code: 'ALERT_NOT_FOUND',
      });
    });
  });

  describe('健康检查', () => {
    it('应该返回健康状态', async () => {
      const responseData = {
        status: 'healthy',
        service: 'ehs-ai-service',
        timestamp: '2026-04-16T10:00:00.000Z',
      };

      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse(responseData, 200, true)
      );

      const result = await ApiService.healthCheck();

      expect(result).toEqual(responseData);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/health',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });
  });

  describe('告警上报', () => {
    it('应该成功上报告警', async () => {
      const mockRequest = {
        device_id: 'DEV-001',
        device_type: '烟雾传感器',
        alert_type: '气体泄漏',
        alert_content: '检测到气体浓度异常',
        location: 'A 车间 - 东区',
        alert_level: 3,
      };

      const responseData = {
        success: true,
        message: '告警上报成功',
        alert_id: 'ALT-2026041601',
        risk_level: 'high',
        plans: [
          {
            title: '化学品泄漏应急预案',
            content: '1. 疏散人员 2. 关闭泄漏源',
            risk_level: 'high',
            source: 'ES',
            score: 0.95,
          },
        ],
      };

      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse(responseData, 200, true)
      );

      const result = await ApiService.reportAlert(mockRequest);

      expect(result).toEqual(responseData);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/alert/report',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(mockRequest),
        })
      );
    });

    it('应该处理上报失败', async () => {
      const mockRequest = {
        device_id: 'DEV-999',  // 不存在的设备
        device_type: '烟雾传感器',
        alert_type: '气体泄漏',
        alert_content: '检测到气体浓度异常',
        location: 'A 车间 - 东区',
        alert_level: 3,
      };

      // 使用已知的业务错误码
      const responseData = {
        success: false,
        message: '告警上报失败',
        error: 'INVALID_DEVICE',  // 业务错误码
      };

      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse(responseData, 200, true)
      );

      await expect(ApiService.reportAlert(mockRequest)).rejects.toMatchObject({
        type: 'BUSINESS_ERROR',
        code: 'INVALID_DEVICE',
      });
    });
  });

  describe('预案检索', () => {
    it('应该成功检索预案', async () => {
      const mockRequest = {
        query: '气体泄漏',
        event_type: '气体泄漏',
        top_k: 5,
      };

      const responseData = {
        success: true,
        message: '预案检索成功',
        plans: [
          {
            title: '化学品泄漏应急处置预案',
            content: '1. 立即疏散人员 2. 关闭泄漏源阀门',
            risk_level: 'high',
            source: 'ES',
            score: 0.93,
          },
        ],
        query: '气体泄漏',
      };

      vi.mocked(global.fetch).mockResolvedValueOnce(
        createMockResponse(responseData, 200, true)
      );

      const result = await ApiService.searchPlan(mockRequest);

      expect(result).toEqual(responseData);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/plan/search',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(mockRequest),
        })
      );
    });
  });
});

describe('错误处理工具函数', () => {
  describe('createHttpError', () => {
    it('应该创建正确的 HTTP 错误', () => {
      const error = createHttpError(500);

      expect(error).toMatchObject({
        type: 'HTTP_ERROR',
        code: 500,
        title: '服务器错误',
      });
      expect(error.message).toContain('服务器内部发生错误');
    });

    it('应该为未知状态码创建默认错误', () => {
      const error = createHttpError(999);

      expect(error).toMatchObject({
        type: 'HTTP_ERROR',
        code: 999,
        title: '未知错误',
      });
    });
  });

  describe('createBusinessError', () => {
    it('应该创建正确的业务错误', () => {
      const error = createBusinessError('ALERT_NOT_FOUND');

      expect(error).toMatchObject({
        type: 'BUSINESS_ERROR',
        code: 'ALERT_NOT_FOUND',
        title: '告警不存在',
      });
      expect(error.message).toContain('指定的告警记录不存在');
    });

    it('应该为未知错误码创建默认错误', () => {
      const error = createBusinessError('UNKNOWN_CODE');

      expect(error).toMatchObject({
        type: 'BUSINESS_ERROR',
        code: 'UNKNOWN_CODE',
        title: '业务错误',
      });
    });
  });

  describe('createNetworkError', () => {
    it('应该创建正确的网络错误', () => {
      const error = createNetworkError('http://localhost:8000/api/test', 'GET');

      expect(error).toMatchObject({
        type: 'NETWORK_ERROR',
        code: 'NETWORK_ERROR',
        title: '网络连接失败',
      });
      expect(error.message).toContain('无法连接到后端服务器');
    });
  });

  describe('createTimeoutError', () => {
    it('应该创建正确的超时错误', () => {
      const error = createTimeoutError(5000);

      expect(error).toMatchObject({
        type: 'TIMEOUT_ERROR',
        code: 'TIMEOUT',
        title: '请求超时',
      });
      expect(error.message).toContain('5000ms');
    });
  });

  describe('parseErrorFromResponse', () => {
    it('应该从响应中解析业务错误码', () => {
      const error = parseErrorFromResponse(
        400,
        { error_code: 'ALERT_NOT_FOUND', message: '告警不存在' },
        '/api/alert/123',
        'GET'
      );

      expect(error).toMatchObject({
        type: 'BUSINESS_ERROR',
        code: 'ALERT_NOT_FOUND',
        title: '告警不存在',
      });
    });

    it('应该从响应中解析错误字段', () => {
      const error = parseErrorFromResponse(
        400,
        { error: 'INVALID_DEVICE', message: '设备无效' },
        '/api/alert/report',
        'POST'
      );

      expect(error).toMatchObject({
        type: 'BUSINESS_ERROR',
        code: 'INVALID_DEVICE',
        title: '设备无效',
      });
    });

    it('应该回退到 HTTP 状态码映射', () => {
      const error = parseErrorFromResponse(
        500,
        { message: '未知错误' },
        '/api/test',
        'GET'
      );

      expect(error).toMatchObject({
        type: 'HTTP_ERROR',
        code: 500,
        title: '服务器错误',
      });
    });
  });

  describe('isRetryableError', () => {
    it('应该识别网络错误为可重试', () => {
      const error = createNetworkError();
      expect(isRetryableError(error)).toBe(true);
    });

    it('应该识别超时错误为可重试', () => {
      const error = createTimeoutError(5000);
      expect(isRetryableError(error)).toBe(true);
    });

    it('应该识别 5xx 错误为可重试', () => {
      const error = createHttpError(503);
      expect(isRetryableError(error)).toBe(true);
    });

    it('应该识别 429 为可重试', () => {
      const error = createHttpError(429);
      expect(isRetryableError(error)).toBe(true);
    });

    it('应该识别 4xx 错误为不可重试', () => {
      const error = createHttpError(400);
      expect(isRetryableError(error)).toBe(false);
    });
  });

  describe('getErrorSummary', () => {
    it('应该生成错误摘要', () => {
      const error = createHttpError(500);
      const summary = getErrorSummary(error);

      // 摘要格式为 "标题：问题"
      expect(summary).toContain('服务器错误');
    });

    it('应该生成简洁的错误摘要', () => {
      const error = createNetworkError();
      const summary = getErrorSummary(error);

      expect(summary).toContain('网络连接失败');
    });
  });
});
