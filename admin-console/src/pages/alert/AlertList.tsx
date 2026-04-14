import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Space, Typography, Empty, Button, Spin } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  Alert,
  AlertType,
  AlertLevel,
  AlertStatus,
  ALERT_TYPE_MAP,
  ALERT_LEVEL_MAP,
  ALERT_STATUS_MAP,
  MOCK_ALERTS,
} from '@/types/alert';

const { Text } = Typography;

interface AlertListProps {
  refreshTrigger?: number; // 用于接收刷新信号
  onRefresh?: () => void;
}

/**
 * 告警列表组件
 *
 * 功能特性：
 * - 告警列表表格（ID、类型、内容、级别、位置、时间、状态、关联预案）
 * - 使用 Mock 数据（阶段 1 不连接真实 API）
 * - 支持新增告警后刷新列表
 *
 * UI 状态：
 * - Loading 状态 - 表格显示 loading spinner
 * - Empty 状态 - 空列表时显示"暂无告警"引导
 * - Error 状态 - 显示错误提示 + 重试按钮
 */
export const AlertList: React.FC<AlertListProps> = ({ refreshTrigger, onRefresh }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  /**
   * 加载告警数据
   */
  const loadAlerts = async () => {
    setLoading(true);
    setError(false);
    try {
      // 阶段 1 使用 Mock 数据，模拟 API 延迟
      await new Promise((resolve) => setTimeout(resolve, 500));
      setAlerts(MOCK_ALERTS);
    } catch (err) {
      setError(true);
      console.error('加载告警数据失败:', err);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 监听刷新信号
   */
  useEffect(() => {
    loadAlerts();
  }, []);

  useEffect(() => {
    if (refreshTrigger !== undefined) {
      loadAlerts();
    }
  }, [refreshTrigger]);

  /**
   * 获取告警级别颜色
   */
  const getLevelColor = (level: AlertLevel): string => {
    switch (level) {
      case AlertLevel.CRITICAL:
        return 'red';
      case AlertLevel.HIGH:
        return 'orange';
      case AlertLevel.MEDIUM:
        return 'blue';
      case AlertLevel.LOW:
        return 'green';
      default:
        return 'default';
    }
  };

  /**
   * 表格列定义
   */
  const columns: ColumnsType<Alert> = [
    {
      title: '告警 ID',
      dataIndex: 'id',
      key: 'id',
      width: 160,
      fixed: 'left',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: AlertType) => (
        <Text strong>{ALERT_TYPE_MAP[type]}</Text>
      ),
    },
    {
      title: '告警内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: { showTitle: false },
      render: (content: string) => (
        <Text type="secondary" className="truncate block max-w-[200px]">
          {content}
        </Text>
      ),
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      width: 80,
      render: (level: AlertLevel) => (
        <Tag color={getLevelColor(level)}>{ALERT_LEVEL_MAP[level]}</Tag>
      ),
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 150,
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: string) => (
        <Text type="secondary">
          {new Date(timestamp).toLocaleString('zh-CN')}
        </Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: AlertStatus) => {
        let color = 'default';
        if (status === AlertStatus.PENDING) color = 'orange';
        if (status === AlertStatus.PROCESSING) color = 'blue';
        if (status === AlertStatus.RESOLVED) color = 'green';
        if (status === AlertStatus.CLOSED) color = 'gray';
        return <Tag color={color}>{ALERT_STATUS_MAP[status]}</Tag>;
      },
    },
    {
      title: '关联预案',
      dataIndex: 'planName',
      key: 'planName',
      width: 200,
      render: (planName?: string) =>
        planName ? (
          <Text type="primary" className="cursor-pointer hover:underline">
            {planName}
          </Text>
        ) : (
          <Text type="secondary">-</Text>
        ),
    },
  ];

  /**
   * 空状态渲染
   */
  const renderEmpty = () => (
    <Empty
      description="暂无告警"
      image={Empty.PRESENTED_IMAGE_SIMPLE}
    >
      <Button type="primary" onClick={loadAlerts} icon={<ReloadOutlined />}>
        刷新列表
      </Button>
    </Empty>
  );

  return (
    <Card
      title="告警列表"
      bordered={false}
      extra={
        <Button
          icon={<ReloadOutlined />}
          onClick={loadAlerts}
          loading={loading}
        >
          刷新
        </Button>
      }
    >
      {/* Error 状态 */}
      {error && (
        <Card className="mb-4 bg-red-50 border-red-200">
          <Space direction="vertical" size="small" className="w-full">
            <Text type="danger">加载告警数据失败，请检查网络连接后重试</Text>
            <Button type="primary" danger onClick={loadAlerts} loading={loading}>
              重试
            </Button>
          </Space>
        </Card>
      )}

      {/* 表格 - 包含 Loading 和 Empty 状态 */}
      <Table
        columns={columns}
        dataSource={alerts}
        rowKey="id"
        loading={loading}
        locale={{
          emptyText: renderEmpty(),
        }}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条告警`,
        }}
        scroll={{ x: 1200 }}
      />
    </Card>
  );
};

export default AlertList;
