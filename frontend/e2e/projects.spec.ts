import { test, expect } from '@playwright/test'

test.describe('项目列表页 (/projects)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('项目详情页 (/projects/:id)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('项目 Agents 页 (/projects/:id/agents)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/agents')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('项目 Feed 页 (/projects/:id/feed)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/feed')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('项目 Dashboard 页 (/projects/:id/dashboard)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/dashboard')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('项目 Schedule 页 (/projects/:id/schedule)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/schedule')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})
