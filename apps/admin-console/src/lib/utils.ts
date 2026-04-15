import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * 合并类名工具函数
 * 支持条件性类名、数组、对象等
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 格式化日期
 */
export function formatDate(date: Date | string | number): string {
  const d = new Date(date);
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
}

/**
 * 格式化相对时间
 */
export function formatRelativeTime(date: Date | string | number): string {
  const d = new Date(date);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000);

  if (diffInSeconds < 60) {
    return '刚刚';
  }

  const diffInMinute = Math.floor(diffInSeconds / 60);
  if (diffInMinute < 60) {
    return `${diffInMinute} 分钟前`;
  }

  const diffInHour = Math.floor(diffInMinute / 60);
  if (diffInHour < 24) {
    return `${diffInHour} 小时前`;
  }

  const diffInDay = Math.floor(diffInHour / 24);
  if (diffInDay < 7) {
    return `${diffInDay} 天前`;
  }

  return formatDate(d);
}

/**
 * 风险等级映射
 */
export const riskLevelConfig = {
  high: {
    label: '高风险',
    className: 'bg-error text-white',
  },
  medium: {
    label: '中风险',
    className: 'bg-warning text-white',
  },
  low: {
    label: '低风险',
    className: 'bg-success text-white',
  },
};

/**
 * 告警状态映射
 */
export const alertStatusConfig = {
  pending: {
    label: '待处理',
    className: 'bg-warning/10 text-warning',
  },
  processing: {
    label: '处理中',
    className: 'bg-primary/10 text-primary',
  },
  resolved: {
    label: '已解决',
    className: 'bg-success/10 text-success',
  },
  closed: {
    label: '已关闭',
    className: 'bg-muted/10 text-muted-foreground',
  },
};
