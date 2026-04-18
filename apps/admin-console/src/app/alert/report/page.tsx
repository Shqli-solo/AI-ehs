'use client';

import * as React from 'react';
import { api } from '@/services/api';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

/** 告警等级配置 */
const ALERT_LEVELS = [
  { value: 1, label: '低', color: 'bg-blue-500', desc: '低风险，常规关注' },
  { value: 2, label: '中', color: 'bg-yellow-500', desc: '中等风险，需要处理' },
  { value: 3, label: '高', color: 'bg-orange-500', desc: '高风险，紧急处理' },
  { value: 4, label: '严重', color: 'bg-red-500', desc: '严重风险，立即响应' },
];

/** 风险等级显示 */
function RiskBadge({ level }: { level: string }) {
  const config: Record<string, { color: string; label: string }> = {
    low: { color: 'bg-blue-100 text-blue-800', label: '低风险' },
    medium: { color: 'bg-yellow-100 text-yellow-800', label: '中风险' },
    high: { color: 'bg-orange-100 text-orange-800', label: '高风险' },
    critical: { color: 'bg-red-100 text-red-800', label: '严重风险' },
    unknown: { color: 'bg-gray-100 text-gray-800', label: '未知' },
  };
  const c = config[level] || config.unknown;
  return <span className={`px-3 py-1 rounded-full text-sm font-medium ${c.color}`}>{c.label}</span>;
}

interface ReportResult {
  alert_id: string;
  risk_level: string;
  plans: Array<{ title: string; content: string; risk_level: string }>;
  image_url?: string;
}

export default function AlertReportPage() {
  const [deviceId, setDeviceId] = React.useState('');
  const [deviceType, setDeviceType] = React.useState('烟雾传感器');
  const [alertType, setAlertType] = React.useState('烟火告警');
  const [location, setLocation] = React.useState('');
  const [alertLevel, setAlertLevel] = React.useState(2);
  const [alertContent, setAlertContent] = React.useState('');
  const [sensorData, setSensorData] = React.useState('');
  const [uploadedFile, setUploadedFile] = React.useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [result, setResult] = React.useState<ReportResult | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  // 图片预览
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  // 提交表单
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let response: unknown;

      if (uploadedFile) {
        // 多模态上报
        const formData = new FormData();
        formData.append('alert_text', alertContent);
        formData.append('device_id', deviceId);
        formData.append('location', location);
        formData.append('image', uploadedFile);
        if (sensorData) formData.append('sensor_data', sensorData);

        const resp = await fetch(`${API_BASE}/api/alert/report/multimodal`, {
          method: 'POST',
          body: formData,
        });
        response = await resp.json();
      } else {
        // 文本上报
        response = await api.reportAlert({
          device_id: deviceId,
          device_type: deviceType,
          alert_type: alertType,
          alert_content: alertContent,
          location,
          alert_level: alertLevel,
          extra_data: sensorData ? JSON.parse(sensorData) : undefined,
        });
      }

      const data = response as Record<string, unknown>;
      if (data.success) {
        setResult({
          alert_id: (data.alert_id as string) || '',
          risk_level: (data.risk_level as string) || 'unknown',
          plans: (data.plans as Array<{ title: string; content: string; risk_level: string }>) || [],
        });
      } else {
        setError((data.error as string) || '上报失败');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '网络请求失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-10">
        <div className="flex items-center justify-between h-16 px-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">📋</span>
            <h1 className="text-title font-semibold text-foreground">
              告警上报
            </h1>
          </div>
        </div>
      </header>

      <main className="p-6 max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 设备信息 */}
          <div className="bg-card rounded-card shadow-card border border-border p-6">
            <h2 className="text-title font-semibold text-foreground mb-4">设备信息</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">设备 ID</label>
                <input
                  type="text"
                  value={deviceId}
                  onChange={(e) => setDeviceId(e.target.value)}
                  placeholder="DEV-001"
                  required
                  className="w-full h-10 px-3 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">设备类型</label>
                <select
                  value={deviceType}
                  onChange={(e) => setDeviceType(e.target.value)}
                  className="w-full h-10 px-3 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="烟雾传感器">烟雾传感器</option>
                  <option value="温度传感器">温度传感器</option>
                  <option value="燃气传感器">燃气传感器</option>
                  <option value="红外移动传感器">红外移动传感器</option>
                  <option value="视频监控AI">视频监控AI</option>
                  <option value="化学传感器">化学传感器</option>
                  <option value="门禁系统">门禁系统</option>
                  <option value="电力监控">电力监控</option>
                </select>
              </div>
            </div>
          </div>

          {/* 告警信息 */}
          <div className="bg-card rounded-card shadow-card border border-border p-6">
            <h2 className="text-title font-semibold text-foreground mb-4">告警信息</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">告警类型</label>
                  <select
                    value={alertType}
                    onChange={(e) => setAlertType(e.target.value)}
                    className="w-full h-10 px-3 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="烟火告警">烟火告警</option>
                    <option value="入侵检测">入侵检测</option>
                    <option value="燃气泄漏">燃气泄漏</option>
                    <option value="温度异常">温度异常</option>
                    <option value="积水告警">积水告警</option>
                    <option value="设备故障">设备故障</option>
                    <option value="化学品泄漏">化学品泄漏</option>
                    <option value="自然灾害">自然灾害</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">位置</label>
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="A栋3楼办公区"
                    required
                    className="w-full h-10 px-3 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">告警等级</label>
                <div className="flex gap-3">
                  {ALERT_LEVELS.map((level) => (
                    <button
                      key={level.value}
                      type="button"
                      onClick={() => setAlertLevel(level.value)}
                      className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                        alertLevel === level.value
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-muted-foreground'
                      }`}
                    >
                      <div className={`w-6 h-6 rounded-full mx-auto mb-1 ${level.color}`} />
                      <div className="text-center text-sm font-medium text-foreground">{level.label}</div>
                      <div className="text-center text-xs text-muted-foreground">{level.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">告警内容</label>
                <textarea
                  value={alertContent}
                  onChange={(e) => setAlertContent(e.target.value)}
                  placeholder="描述告警详情..."
                  rows={4}
                  className="w-full px-3 py-2 rounded-input border border-border bg-background text-body focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">传感器数据（JSON，可选）</label>
                <textarea
                  value={sensorData}
                  onChange={(e) => setSensorData(e.target.value)}
                  placeholder='{"temperature": 38, "smoke_density": "high"}'
                  rows={2}
                  className="w-full px-3 py-2 rounded-input border border-border bg-background text-body font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                />
              </div>
            </div>
          </div>

          {/* 图片上传 */}
          <div className="bg-card rounded-card shadow-card border border-border p-6">
            <h2 className="text-title font-semibold text-foreground mb-4">图片上传（可选）</h2>
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                previewUrl
                  ? 'border-primary bg-primary/5'
                  : 'border-border hover:border-primary'
              }`}
              onClick={() => document.getElementById('file-upload')?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const file = e.dataTransfer.files[0];
                if (file) {
                  setUploadedFile(file);
                  setPreviewUrl(URL.createObjectURL(file));
                }
              }}
            >
              {previewUrl ? (
                <div>
                  <img src={previewUrl} alt="预览" className="max-h-48 mx-auto rounded" />
                  <p className="text-sm text-muted-foreground mt-2">{uploadedFile?.name}</p>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setUploadedFile(null);
                      setPreviewUrl(null);
                    }}
                    className="text-sm text-error mt-1 hover:underline"
                  >
                    移除图片
                  </button>
                </div>
              ) : (
                <div>
                  <p className="text-3xl mb-2">📷</p>
                  <p className="text-body text-muted-foreground">
                    点击或拖拽上传图片
                  </p>
                  <p className="text-caption text-muted-foreground mt-1">
                    支持监控截图、现场照片等
                  </p>
                </div>
              )}
              <input
                id="file-upload"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>

          {/* 提交按钮 */}
          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={() => {
                setDeviceId('');
                setAlertContent('');
                setLocation('');
                setSensorData('');
                setUploadedFile(null);
                setPreviewUrl(null);
                setResult(null);
                setError(null);
              }}
              className="h-10 px-6 rounded-input border border-border bg-background text-sm hover:bg-muted"
            >
              重置
            </button>
            <button
              type="submit"
              disabled={loading || !alertContent || !deviceId || !location}
              className={`h-10 px-6 rounded-input text-sm font-medium text-white transition-colors ${
                loading || !alertContent || !deviceId || !location
                  ? 'bg-primary/50 cursor-not-allowed'
                  : 'bg-primary hover:bg-primary/90'
              }`}
            >
              {loading ? 'AI 分析中...' : '提交告警'}
            </button>
          </div>
        </form>

        {/* 错误提示 */}
        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-card p-4">
            <p className="text-red-800 font-medium">⚠️ {error}</p>
          </div>
        )}

        {/* AI 分析结果 */}
        {result && (
          <div className="mt-6 space-y-6">
            <div className="bg-card rounded-card shadow-card border border-border p-6">
              <h2 className="text-title font-semibold text-foreground mb-4">AI 分析结果</h2>
              <div className="flex items-center gap-4 mb-4">
                <div>
                  <span className="text-sm text-muted-foreground">告警 ID</span>
                  <p className="font-mono text-sm">{result.alert_id}</p>
                </div>
                <div>
                  <span className="text-sm text-muted-foreground">风险等级</span>
                  <div className="mt-1"><RiskBadge level={result.risk_level} /></div>
                </div>
              </div>
            </div>

            {result.plans && result.plans.length > 0 && (
              <div className="bg-card rounded-card shadow-card border border-border p-6">
                <h2 className="text-title font-semibold text-foreground mb-4">关联预案</h2>
                <div className="space-y-3">
                  {result.plans.map((plan, i) => {
                    const title = typeof plan === 'object' ? plan.title : String(plan);
                    const content = typeof plan === 'object' ? plan.content : '';
                    const riskLevel = typeof plan === 'object' ? plan.risk_level : '';
                    return (
                      <div key={i} className="border border-border rounded p-4">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium text-foreground">{title}</h3>
                          {riskLevel && <RiskBadge level={riskLevel} />}
                        </div>
                        {content && (
                          <p className="text-sm text-muted-foreground whitespace-pre-line">{content}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
