import { test, expect } from '@playwright/test'

test.describe('执行历史列表页 (/executions)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/executions')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('执行详情页 (/executions/:id)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/executions/test-id')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('调度器页 (/scheduler)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/scheduler')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('工作流列表页 (/workflows)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/workflows')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('工作流详情页 (/workflows/:id)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/workflows/test-id')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('活动动态页 (/activities)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/activities')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})
