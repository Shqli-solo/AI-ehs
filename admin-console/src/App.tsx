import React, { useState } from 'react';
import { ConfigProvider, Layout, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { SimulateAlert, AlertList } from '@/pages/alert';
import { AlertType } from '@/types/alert';

const { Header, Content } = Layout;

/**
 * 告警管理页面
 *
 * 整合 SimulateAlert 和 AlertList 组件
 * 实现完整的告警管理功能
 */
const AlertPage: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState<number>(0);

  /**
   * 处理告警上报
   */
  const handleSubmit = async (data: { alertType: AlertType; content: string }) => {
    // 阶段 1 使用 Mock，不实际调用 API
    console.log('告警上报:', data);

    // 模拟添加到列表
    const newAlert = {
      id: `ALT-${Date.now()}`,
      type: data.alertType,
      content: data.content,
      level: 4, // Critical
      location: '模拟位置',
      timestamp: new Date().toISOString(),
      status: 'pending' as const,
      planName: '《应急预案》',
    };

    // 这里应该会调用 API，然后刷新列表
    return Promise.resolve();
  };

  /**
   * 处理成功上报
   */
  const handleSuccess = () => {
    // 触发列表刷新
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <ConfigProvider locale={zhCN}>
      <Layout className="min-h-screen bg-gray-100">
        <Header className="bg-white shadow-md px-6 flex items-center">
          <h1 className="text-xl font-bold text-gray-800">EHS 智能安保决策中台 - 告警管理</h1>
        </Header>
        <Content className="p-6">
          <div className="max-w-7xl mx-auto">
            <SimulateAlert onSubmit={handleSubmit} onSuccess={handleSuccess} />
            <AlertList refreshTrigger={refreshTrigger} />
          </div>
        </Content>
      </Layout>
    </ConfigProvider>
  );
};

export default AlertPage;
