import { test, expect } from '@playwright/test'

test.describe('任务看板页 (/projects/:id/kanban)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/kanban')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('任务列表页 (/projects/:id/tasks)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/tasks')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('任务时间线页 (/projects/:id/timeline)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/projects/test-id/timeline')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('任务详情页 (/tasks/:id)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/tasks/test-id')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('任务编辑页 (/tasks/:id/edit)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/tasks/test-id/edit')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})

test.describe('到期提醒页 (/tasks/due-soon)', () => {
  test('访问重定向到登录（未认证）', async ({ page }) => {
    await page.goto('/tasks/due-soon')
    await page.waitForURL(/\/login/, { timeout: 5000 })
    expect(page.url()).toContain('/login')
  })
})
