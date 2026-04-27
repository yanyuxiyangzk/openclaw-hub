import { test, expect } from '@playwright/test'

test.describe('登录页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('页面标题存在', async ({ page }) => {
    await expect(page).toHaveTitle(/OpenClawHub/i)
  })

  test('登录表单元素完整', async ({ page }) => {
    // 邮箱输入框
    const emailInput = page.locator('input[type="email"], input[name="email"]').first()
    await expect(emailInput).toBeVisible()

    // 密码输入框
    const passwordInput = page.locator('input[type="password"]').first()
    await expect(passwordInput).toBeVisible()

    // 登录按钮
    const submitButton = page.locator('button[type="submit"]').first()
    await expect(submitButton).toBeVisible()
    await expect(submitButton).toContainText(/登录|登录/)
  })

  test('显示注册链接', async ({ page }) => {
    const registerLink = page.locator('a[href*="register"], a:has-text("注册")').first()
    await expect(registerLink).toBeVisible()
  })

  test('页面无控制台错误', async ({ page }) => {
    const errors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })
    await page.waitForTimeout(2000)
    // 过滤掉已知的网络错误（后端可能未启动）
    const criticalErrors = errors.filter(e => !e.includes('Failed to fetch') && !e.includes('NetworkError'))
    expect(criticalErrors).toHaveLength(0)
  })
})
