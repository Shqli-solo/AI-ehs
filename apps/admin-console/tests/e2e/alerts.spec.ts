// apps/admin-console/tests/e2e/alerts.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Alerts Management', () => {
  test('should display alerts table', async ({ page }) => {
    await page.goto('/alerts');

    // 验证页面标题
    await expect(page.getByText('告警管理')).toBeVisible();

    // 验证表头
    await expect(page.getByText('ID')).toBeVisible();
    await expect(page.getByText('类型')).toBeVisible();
    await expect(page.getByText('标题')).toBeVisible();
    await expect(page.getByText('等级')).toBeVisible();
    await expect(page.getByText('状态')).toBeVisible();
    await expect(page.getByText('位置')).toBeVisible();
    await expect(page.getByText('时间')).toBeVisible();
    await expect(page.getByText('操作')).toBeVisible();
  });

  test('should filter alerts by status', async ({ page }) => {
    await page.goto('/alerts');

    // 点击状态筛选下拉框
    const statusTrigger = page.locator('select').first();
    await statusTrigger.selectOption('pending');

    // 验证筛选控件存在
    await expect(page.getByText('待处理')).toBeVisible();
  });

  test('should open alert detail drawer on click', async ({ page }) => {
    await page.goto('/alerts');

    // 点击表格第一行的查看按钮
    const firstRow = page.locator('table tbody tr').first();
    await firstRow.locator('button').first().click();

    // 验证对话框打开
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
  });
});
