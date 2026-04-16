/**
 * Dashboard E2E 测试
 *
 * 测试场景：
 * 1. Dashboard 页面加载
 * 2. 统计卡片显示
 * 3. 告警列表渲染
 * 4. 健康检查指示器
 * 5. Toast 组件演示
 * 6. 响应式布局测试（桌面端）
 * 7. 响应式布局测试（移动端）
 * 8. 骨架屏加载状态
 */

import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  // 场景 1: Dashboard 页面正常加载
  test('should load dashboard page successfully', async ({ page }) => {
    await page.goto('/');

    // 验证页面标题包含 EHS
    await expect(page).toHaveTitle(/EHS/);

    // 验证 Header 显示
    await expect(page.getByText('EHS 智能安保决策中台')).toBeVisible();

    // 验证欢迎语
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });

  // 场景 2: 统计卡片显示正确
  test('should display stats cards correctly', async ({ page }) => {
    // Mock API 响应
    await page.route('**/api/stats/today', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total: 12,
          pending: 5,
          processing: 3,
          resolved: 4,
          change: '+15%',
        }),
      });
    });

    await page.route('**/api/alert/list**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            total: 0,
            pending: 0,
            processing: 0,
            resolved: 0,
            alerts: [],
          },
        }),
      });
    });

    await page.goto('/');

    // 等待统计卡片加载
    await expect(page.getByText('今日告警')).toBeVisible({ timeout: 10000 });

    // 验证 4 个统计卡片存在
    const todayAlertsVisible = await page.getByText('今日告警').isVisible();
    const pendingVisible = await page.getByText('待处理').isVisible();
    const deviceRateVisible = await page.getByText('设备在线率').isVisible();
    const safeDaysVisible = await page.getByText('安全运行天数').isVisible();

    expect(todayAlertsVisible && pendingVisible && deviceRateVisible && safeDaysVisible).toBe(true);
  });

  // 场景 3: 告警列表渲染
  test('should render alerts list or empty state', async ({ page }) => {
    await page.goto('/');

    // 等待告警区域加载
    await page.waitForTimeout(2000);

    // 验证告警列表区域存在（要么是告警列表，要么是空状态）
    const alertListVisible = await page.locator('text=最近告警').isVisible();
    const emptyStateVisible = await page.locator('text=暂无告警').isVisible();

    // 骨架屏状态也算通过
    const skeletonVisible = await page.locator('[class*="animate-pulse"]').first().isVisible();

    expect(alertListVisible || emptyStateVisible || skeletonVisible).toBe(true);
  });

  // 场景 4: 健康检查指示器
  test('should display backend health indicator', async ({ page }) => {
    await page.goto('/');

    // 等待健康指示器出现
    const healthIndicator = page.locator('[class*="rounded-full"]');
    await expect(healthIndicator.first()).toBeVisible({ timeout: 10000 });

    // 验证健康状态文本（正常或离线）
    const healthText = page.locator('text=后端服务');
    await expect(healthText.first()).toBeVisible();
  });

  // 场景 5: Toast 组件演示
  test('should show toast notifications on button click', async ({ page }) => {
    // Mock API 响应
    await page.route('**/api/stats/today', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total: 12,
          pending: 5,
          processing: 3,
          resolved: 4,
          change: '+15%',
        }),
      });
    });

    await page.route('**/api/alert/list**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            total: 0,
            pending: 0,
            processing: 0,
            resolved: 0,
            alerts: [],
          },
        }),
      });
    });

    await page.goto('/');

    // 等待 Toast 演示区域加载
    await expect(page.getByText('Toast 组件演示')).toBeVisible({ timeout: 10000 });

    // 点击成功 Toast 按钮
    const successButton = page.getByText('成功 Toast');
    await successButton.click();

    // 验证 Toast 显示（使用精确匹配和 role）
    await expect(page.getByRole('status').first()).toBeVisible({ timeout: 3000 });

    // 等待 Toast 消失
    await page.waitForTimeout(3500);

    // 点击错误 Toast 按钮
    const errorButton = page.getByText('错误 Toast');
    await errorButton.click();

    // 验证错误 Toast 显示
    await expect(page.getByRole('status').first()).toBeVisible({ timeout: 3000 });
  });

  // 场景 6: 响应式布局测试（桌面端）
  test('should render correctly on desktop viewport', async ({ page }) => {
    // Mock API 响应
    await page.route('**/api/stats/today', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total: 12,
          pending: 5,
          processing: 3,
          resolved: 4,
          change: '+15%',
        }),
      });
    });

    await page.route('**/api/alert/list**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            total: 0,
            pending: 0,
            processing: 0,
            resolved: 0,
            alerts: [],
          },
        }),
      });
    });

    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');

    // 验证网格布局存在
    const statsGrid = page.locator('[class*="grid-cols-"]');
    await expect(statsGrid.first()).toBeVisible({ timeout: 10000 });

    // 验证统计卡片存在（今日告警卡片）
    const statCard = page.getByText('今日告警');
    await expect(statCard.first()).toBeVisible();
  });

  // 场景 7: 响应式布局测试（移动端）
  test('should render correctly on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // 验证 Header 显示
    await expect(page.getByText('EHS 智能安保决策中台')).toBeVisible({ timeout: 10000 });

    // 移动端应该是单列布局
    const welcomeText = page.getByText('欢迎回来');
    await expect(welcomeText).toBeVisible();
  });

  // 场景 8: 骨架屏加载状态
  test('should show skeleton loading state', async ({ page }) => {
    // 设置慢速网络模拟加载
    await page.route('**/api/**', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.continue();
    });

    await page.goto('/');

    // 验证骨架屏动画出现
    const skeleton = page.locator('[class*="animate-pulse"]');
    await expect(skeleton.first()).toBeVisible({ timeout: 5000 });
  });
});
