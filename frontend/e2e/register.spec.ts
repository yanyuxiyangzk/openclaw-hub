import { test, expect } from '@playwright/test'

test.describe('注册页面', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/register')
  })

  test('注册表单元素完整', async ({ page }) => {
    // 用户名输入框
    const usernameInput = page.locator('input[type="text"], input[name="username"]').first()
    await expect(usernameInput).toBeVisible()

    // 邮箱输入框
    const emailInput = page.locator('input[type="email"], input[name="email"]').first()
    await expect(emailInput).toBeVisible()

    // 密码输入框
    const passwordInputs = page.locator('input[type="password"]')
    await expect(passwordInputs.first()).toBeVisible()
    // 确认密码
    await expect(passwordInputs.nth(1)).toBeVisible()

    // 注册按钮
    const submitButton = page.locator('button[type="submit"]').first()
    await expect(submitButton).toBeVisible()
    await expect(submitButton).toContainText(/注册/)
  })

  test('显示登录链接', async ({ page }) => {
    const loginLink = page.locator('a[href*="login"], a:has-text("登录")').first()
    await expect(loginLink).toBeVisible()
  })

  test('页面无崩溃', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', err => {
      errors.push(err.message)
    })
    await page.waitForTimeout(2000)
    expect(errors.filter(e => !e.includes('Failed to fetch'))).toHaveLength(0)
  })
})
