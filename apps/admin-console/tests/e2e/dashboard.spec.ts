// apps/admin-console/tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should display 4 stat cards', async ({ page }) => {
    await page.goto('/');

    // 验证 4 个统计卡片
    const cards = page.locator('.grid.gap-4 > .border');
    await expect(cards).toHaveCount(4);

    // 验证卡片标题
    await expect(page.getByText('今日告警')).toBeVisible();
    await expect(page.getByText('待处理')).toBeVisible();
    await expect(page.getByText('设备在线率')).toBeVisible();
    await expect(page.getByText('安全天数')).toBeVisible();
  });

  test('should display recent alerts list', async ({ page }) => {
    await page.goto('/');

    // 验证最近告警列表标题
    await expect(page.getByText('最近告警')).toBeVisible();

    // 验证告警列表有内容
    const alertItems = page.locator('.space-y-3 > div');
    await expect(alertItems.count()).toBeGreaterThan(0);
  });

  test('should navigate to alerts page', async ({ page }) => {
    await page.goto('/');

    // 点击"查看全部"链接
    await page.getByText('查看全部').click();
    await expect(page).toHaveURL('/alerts');
  });
});
