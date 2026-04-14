import React, { useState } from 'react';
import { Card, Button, Input, Select, Space, message } from 'antd';
import { FireOutlined, WarningOutlined, LineChartOutlined, AlertOutlined, SendOutlined } from '@ant-design/icons';
import { PRESET_SCENARIOS, AlertType, ALERT_TYPE_MAP } from '@/types/alert';

const { TextArea } = Input;
const { Option } = Select;

interface SimulateAlertProps {
  onSubmit?: (data: { alertType: AlertType; content: string }) => Promise<void>;
  onSuccess?: () => void;
}

/**
 * 模拟告警上报组件
 *
 * 功能特性：
 * - 预设场景按钮（火灾、气体泄漏、温度异常、入侵检测）
 * - 告警类型下拉选择
 * - 告警内容文本域
 * - 提交按钮（带 loading 状态）
 * - 成功后 Toast 提示
 *
 * UI 状态：
 * - Loading 状态 - 提交按钮显示 loading spinner
 * - Error 状态 - Toast 错误消息 + 重试能力
 */
export const SimulateAlert: React.FC<SimulateAlertProps> = ({ onSubmit, onSuccess }) => {
  const [selectedType, setSelectedType] = useState<AlertType>(AlertType.FIRE);
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [messageApi, messageContextHolder] = message.useMessage();

  /**
   * 处理预设场景点击
   */
  const handlePresetClick = (scenario: (typeof PRESET_SCENARIOS)[0]) => {
    setSelectedType(scenario.alertType);
    setContent(scenario.alertContent);
  };

  /**
   * 处理提交
   */
  const handleSubmit = async () => {
    if (!content.trim()) {
      messageApi.error('请输入告警内容');
      return;
    }

    setLoading(true);
    try {
      if (onSubmit) {
        await onSubmit({
          alertType: selectedType,
          content: content.trim(),
        });
      }

      // 阶段 1 使用 Mock，直接显示成功
      messageApi.success('告警上报成功！已启动应急预案检索');

      // 清空表单
      setContent('');

      // 通知父组件刷新列表
      onSuccess?.();
    } catch (error) {
      messageApi.error({
        content: '告警上报失败，请重试',
        duration: 3,
      });
      console.error('告警上报失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {messageContextHolder}
      <Card
        title="模拟告警上报"
        className="mb-6"
        bordered={false}
      >
        {/* 预设场景按钮 */}
        <div className="mb-4">
          <div className="text-sm text-gray-500 mb-2">快速选择预设场景</div>
          <Space wrap>
            {PRESET_SCENARIOS.map((scenario) => (
              <Button
                key={scenario.alertType}
                icon={
                  scenario.alertType === AlertType.FIRE ? <FireOutlined /> :
                  scenario.alertType === AlertType.GAS_LEAK ? <WarningOutlined /> :
                  scenario.alertType === AlertType.TEMPERATURE_ABNORMAL ? <LineChartOutlined /> :
                  <AlertOutlined />
                }
                onClick={() => handlePresetClick(scenario)}
                size="middle"
              >
                {scenario.icon} {scenario.name}
              </Button>
            ))}
          </Space>
        </div>

        {/* 告警类型选择 */}
        <div className="mb-4">
          <div className="text-sm text-gray-500 mb-2">告警类型</div>
          <Select
            value={selectedType}
            onChange={(value) => setSelectedType(value)}
            className="w-full"
            size="large"
          >
            {Object.entries(ALERT_TYPE_MAP).map(([value, label]) => (
              <Option key={value} value={value}>
                {label}
              </Option>
            ))}
          </Select>
        </div>

        {/* 告警内容 */}
        <div className="mb-4">
          <div className="text-sm text-gray-500 mb-2">告警内容</div>
          <TextArea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="请输入详细的告警内容描述..."
            rows={4}
            size="large"
            showCount
            maxLength={500}
          />
        </div>

        {/* 提交按钮 */}
        <Button
          type="primary"
          size="large"
          icon={<SendOutlined />}
          onClick={handleSubmit}
          loading={loading}
          block
        >
          {loading ? '上报中...' : '提交告警'}
        </Button>
      </Card>
    </>
  );
};

export default SimulateAlert;
