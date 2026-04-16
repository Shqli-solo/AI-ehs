/**
 * Playwright E2E 测试配置
 *
 * 配置说明：
 * - 使用 Chromium 进行测试
 * - 支持 headed/headless 模式
 * - 包含重试机制和视频录制
 */

import { defineConfig, devices } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173';
const CI = !!process.env.CI;

export default defineConfig({
  // 测试目录
  testDir: './',

  // 测试文件匹配模式
  testMatch: '**/*.spec.ts',

  // 每个测试超时时间
  timeout: 30 * 1000,

  // 单个期望超时
  expect: {
    timeout: 5000,
  },

  // 失败后重试次数
  retries: CI ? 2 : 0,

  // 并行执行的工作数
  workers: CI ? 1 : undefined,

  // 报告器
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
  ],

  // 共享配置
  use: {
    // 基础 URL
    baseURL: BASE_URL,

    // 浏览器操作超时
    actionTimeout: 10000,

    // 导航超时
    navigationTimeout: 30000,

    // 收集追踪信息（用于调试）
    trace: 'retain-on-failure',

    // 失败时录制视频
    video: 'retain-on-failure',

    // 截图模式
    screenshot: 'only-on-failure',

    // 浏览器上下文选项
    viewport: { width: 1280, height: 720 },
  },

  // 项目配置
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // 禁用字体平滑，确保截图一致性
        fontScale: 1,
      },
    },
  ],

  // Web 服务器配置（可选，用于自动启动开发服务器）
  // webServer: {
  //   command: 'npm run dev',
  //   url: BASE_URL,
  //   reuseExistingServer: !CI,
  //   timeout: 120000,
  // },
});
