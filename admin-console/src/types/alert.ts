/**
 * 告警类型枚举
 */
export enum AlertType {
  FIRE = 'fire',
  GAS_LEAK = 'gas_leak',
  TEMPERATURE_ABNORMAL = 'temperature_abnormal',
  INTRUSION = 'intrusion',
}

/**
 * 告警级别枚举
 */
export enum AlertLevel {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4,
}

/**
 * 告警状态枚举
 */
export enum AlertStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}

/**
 * 告警数据类型
 */
export interface Alert {
  id: string;
  type: AlertType;
  content: string;
  level: AlertLevel;
  location: string;
  timestamp: string;
  status: AlertStatus;
  planName?: string;
}

/**
 * 预设场景配置
 */
export interface PresetScenario {
  name: string;
  icon: string;
  alertType: AlertType;
  alertContent: string;
  location: string;
  level: AlertLevel;
}

/**
 * 预设场景列表
 */
export const PRESET_SCENARIOS: PresetScenario[] = [
  {
    name: '火灾告警',
    icon: '🔥',
    alertType: AlertType.FIRE,
    alertContent: '生产车间检测到浓烟，能见度低于 5 米',
    location: '生产车间 A 区',
    level: AlertLevel.CRITICAL,
  },
  {
    name: '气体泄漏',
    icon: '☣️',
    alertType: AlertType.GAS_LEAK,
    alertContent: '甲烷浓度超标 50ppm',
    location: '化学品仓库',
    level: AlertLevel.HIGH,
  },
  {
    name: '温度异常',
    icon: '🌡️',
    alertType: AlertType.TEMPERATURE_ABNORMAL,
    alertContent: '机房温度 45°C，超过安全阈值',
    location: '数据中心机房',
    level: AlertLevel.MEDIUM,
  },
  {
    name: '入侵检测',
    icon: '🚨',
    alertType: AlertType.INTRUSION,
    alertContent: '周界红外传感器触发',
    location: '厂区北侧围墙',
    level: AlertLevel.HIGH,
  },
];

/**
 * 告警类型映射
 */
export const ALERT_TYPE_MAP: Record<AlertType, string> = {
  [AlertType.FIRE]: '火灾',
  [AlertType.GAS_LEAK]: '气体泄漏',
  [AlertType.TEMPERATURE_ABNORMAL]: '温度异常',
  [AlertType.INTRUSION]: '入侵检测',
};

/**
 * 告警级别映射
 */
export const ALERT_LEVEL_MAP: Record<AlertLevel, string> = {
  [AlertLevel.LOW]: '低',
  [AlertLevel.MEDIUM]: '中',
  [AlertLevel.HIGH]: '高',
  [AlertLevel.CRITICAL]: '严重',
};

/**
 * 告警状态映射
 */
export const ALERT_STATUS_MAP: Record<AlertStatus, string> = {
  [AlertStatus.PENDING]: '待处理',
  [AlertStatus.PROCESSING]: '处理中',
  [AlertStatus.RESOLVED]: '已解决',
  [AlertStatus.CLOSED]: '已关闭',
};

/**
 * Mock 告警数据
 */
export const MOCK_ALERTS: Alert[] = [
  {
    id: 'ALT-20260414-001',
    type: AlertType.FIRE,
    content: '生产车间检测到浓烟，能见度低于 5 米',
    level: AlertLevel.CRITICAL,
    location: '生产车间 A 区',
    timestamp: '2026-04-14T10:30:00Z',
    status: AlertStatus.PROCESSING,
    planName: '《火灾事故专项应急预案》',
  },
  {
    id: 'ALT-20260414-002',
    type: AlertType.GAS_LEAK,
    content: '甲烷浓度超标 50ppm',
    level: AlertLevel.HIGH,
    location: '化学品仓库',
    timestamp: '2026-04-14T09:15:00Z',
    status: AlertStatus.RESOLVED,
    planName: '《化学品泄漏应急处置预案》',
  },
];
