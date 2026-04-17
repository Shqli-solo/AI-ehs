// apps/admin-console/tests/e2e/plans.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Plans Management', () => {
  test('should display plans as cards', async ({ page }) => {
    await page.goto('/plans');

    // 验证页面标题
    await expect(page.getByText('预案管理')).toBeVisible();

    // 验证卡片网格存在
    const cards = page.locator('.grid.gap-4 .border');
    await expect(cards.count()).toBeGreaterThan(0);
  });

  test('should filter plans by category', async ({ page }) => {
    await page.goto('/plans');

    // 点击分类筛选下拉框
    const categoryTrigger = page.locator('select').first();
    await categoryTrigger.click();

    // 选择一个分类
    await page.getByRole('option').first().click();

    // 验证筛选生效 - 卡片仍然可见
    await expect(page.locator('.grid.gap-4')).toBeVisible();
  });

  test('should open plan preview dialog', async ({ page }) => {
    await page.goto('/plans');

    // 点击第一个卡片的预览按钮
    const firstCard = page.locator('.grid.gap-4 > .border').first();
    await firstCard.getByRole('button', { name: '预览' }).click();

    // 验证对话框打开
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // 验证对话框包含预案标题
    await expect(dialog.locator('[id*="radix"]')).toBeVisible();
  });
});
