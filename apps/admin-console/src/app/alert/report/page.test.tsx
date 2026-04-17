import * as React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('@/hooks/use-alerts', () => ({
  useAlerts: vi.fn(),
  useAlertStats: vi.fn(),
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), warning: vi.fn(), error: vi.fn() },
}));

vi.mock('@/services/api', () => ({
  api: {
    reportAlert: vi.fn(),
  },
}));

// Mock URL.createObjectURL for file preview
global.URL.createObjectURL = vi.fn(() => 'mock://blob-url');

import AlertReportPage from './page';
import { api } from '@/services/api';

describe('AlertReportPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该显示页面标题', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('告警上报')).toBeInTheDocument();
  });

  it('应该显示设备信息区域', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('设备信息')).toBeInTheDocument();
    expect(screen.getByText('设备 ID')).toBeInTheDocument();
    expect(screen.getByText('设备类型')).toBeInTheDocument();
  });

  it('应该显示设备类型下拉选项', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('烟雾传感器')).toBeInTheDocument();
  });

  it('应该显示告警信息区域', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('告警信息')).toBeInTheDocument();
    expect(screen.getByText('告警类型')).toBeInTheDocument();
    expect(screen.getByText('位置')).toBeInTheDocument();
    expect(screen.getByText('告警等级')).toBeInTheDocument();
    expect(screen.getByText('告警内容')).toBeInTheDocument();
    expect(screen.getByText('传感器数据（JSON，可选）')).toBeInTheDocument();
  });

  it('应该显示所有告警等级选项', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('低')).toBeInTheDocument();
    expect(screen.getByText('中')).toBeInTheDocument();
    expect(screen.getByText('高')).toBeInTheDocument();
    expect(screen.getByText('严重')).toBeInTheDocument();
  });

  it('应该显示图片上传区域', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('图片上传（可选）')).toBeInTheDocument();
    expect(screen.getByText('点击或拖拽上传图片')).toBeInTheDocument();
    expect(screen.getByText('支持监控截图、现场照片等')).toBeInTheDocument();
  });

  it('应该显示提交和重置按钮', () => {
    render(<AlertReportPage />);
    expect(screen.getByText('提交告警')).toBeInTheDocument();
    expect(screen.getByText('重置')).toBeInTheDocument();
  });

  it('提交按钮在告警内容为空时应该被禁用', () => {
    render(<AlertReportPage />);
    const submitButton = screen.getByRole('button', { name: /提交告警/ });
    expect(submitButton).toBeDisabled();
  });

  it('输入告警内容后提交按钮应该可用', async () => {
    const user = userEvent.setup();
    render(<AlertReportPage />);
    const textarea = screen.getByPlaceholderText('描述告警详情...');
    await user.type(textarea, '测试告警内容');
    const submitButton = screen.getByRole('button', { name: /提交告警/ });
    expect(submitButton).toBeEnabled();
  });

  it('点击重置按钮应该清空表单', async () => {
    const user = userEvent.setup();
    render(<AlertReportPage />);
    const contentTextarea = screen.getByPlaceholderText('描述告警详情...');
    await user.type(contentTextarea, '一些内容');

    const resetButton = screen.getByText('重置');
    await user.click(resetButton);

    expect(contentTextarea).toHaveValue('');
  });
});

describe('AlertReportPage - 表单交互', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该能输入设备ID', async () => {
    const user = userEvent.setup();
    render(<AlertReportPage />);
    const deviceIdInput = screen.getByPlaceholderText('DEV-001');
    await user.type(deviceIdInput, 'DEV-999');
    expect(deviceIdInput).toHaveValue('DEV-999');
  });

  it('应该能输入位置', async () => {
    const user = userEvent.setup();
    render(<AlertReportPage />);
    const locationInput = screen.getByPlaceholderText('A栋3楼办公区');
    await user.type(locationInput, 'B栋5楼');
    expect(locationInput).toHaveValue('B栋5楼');
  });

  it('应该能输入传感器数据', () => {
    render(<AlertReportPage />);
    const sensorTextarea = screen.getByPlaceholderText('{"temperature": 38, "smoke_density": "high"}');
    fireEvent.change(sensorTextarea, { target: { value: '{"temp": 40}' } });
    expect(sensorTextarea).toHaveValue('{"temp": 40}');
  });
});

describe('AlertReportPage - 提交', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('提交成功应该显示AI分析结果', async () => {
    vi.mocked(api.reportAlert).mockResolvedValueOnce({
      success: true,
      message: 'ok',
      alert_id: 'ALT-001',
      risk_level: 'high',
      plans: [{ title: '火灾预案', content: '执行预案', risk_level: 'high', source: 'rag', score: 0.9 }],
    });

    const user = userEvent.setup();
    render(<AlertReportPage />);

    const textarea = screen.getByPlaceholderText('描述告警详情...');
    await user.type(textarea, '测试告警');

    const submitButton = screen.getByRole('button', { name: /提交告警/ });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('AI 分析结果')).toBeInTheDocument();
    });

    expect(screen.getByText('ALT-001')).toBeInTheDocument();
  });

  it('提交失败应该显示错误提示', async () => {
    vi.mocked(api.reportAlert).mockResolvedValueOnce({
      success: false,
      message: 'error',
      error: '上报失败，请重试',
    });

    const user = userEvent.setup();
    render(<AlertReportPage />);

    const textarea = screen.getByPlaceholderText('描述告警详情...');
    await user.type(textarea, '测试告警');

    await user.click(screen.getByRole('button', { name: /提交告警/ }));

    await waitFor(() => {
      expect(screen.getByText(/上报失败/)).toBeInTheDocument();
    });
  });
});
