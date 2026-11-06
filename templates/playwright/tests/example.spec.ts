import { test, expect } from '@playwright/test';

test('replace with a matrix-backed case', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/.*/);
});
