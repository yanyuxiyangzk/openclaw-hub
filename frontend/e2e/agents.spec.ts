import { test, expect } from '@playwright/test'

test.describe('Agent 列表页 (/agents)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agents')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('Agent 详情页 (/agents/:id)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agents/test-id')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('Agent 配置页 (/agents/:id/config)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agents/test-id/config')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('Agent 记忆页 (/agents/:id/memory)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agents/test-id/memory')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('Agent 指标页 (/agents/:id/metrics)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agents/test-id/metrics')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('Agent 角色列表页 (/agent-roles)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agent-roles')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('Agent 角色创建页 (/agent-roles/new)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/agent-roles/new')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})
