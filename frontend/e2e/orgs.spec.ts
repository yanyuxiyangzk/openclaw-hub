import { test, expect } from '@playwright/test'

test.describe('组织列表页 (/orgs)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/orgs')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('组织详情页 (/orgs/:id)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/orgs/test-id')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('成员管理页 (/orgs/:id/members)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/orgs/test-id/members')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('设置页 (/settings)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})
