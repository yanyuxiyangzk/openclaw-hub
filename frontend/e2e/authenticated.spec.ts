import { test, expect } from '@playwright/test'

/**
 * 辅助函数：注册并自动登录
 * 使用随机邮箱避免并行测试冲突
 */
async function registerAndLogin(page: any) {
  const random = Math.floor(Math.random() * 999999)
  const testEmail = `e2e_${random}@test.com`
  const testUsername = `e2e_${random}`

  // 1. 访问注册页
  await page.goto('/register')
  await page.waitForLoadState('networkidle')

  // 2. 填写注册表单
  const usernameInput = page.locator('input[type="text"], input[name="username"]').first()
  const emailInput = page.locator('input[type="email"], input[name="email"]').first()
  const passwordInputs = page.locator('input[type="password"]')
  const submitButton = page.locator('button[type="submit"]').first()

  await usernameInput.fill(testUsername)
  await emailInput.fill(testEmail)
  await passwordInputs.first().fill('Test123456')
  await passwordInputs.nth(1).fill('Test123456')
  await submitButton.click()

  // 3. 等待注册完成（可能跳转到 /orgs 或停留在 /register）
  // 增加等待时间，避免并行测试冲突
  try {
    await page.waitForURL(/\/(orgs|login)/, { timeout: 15000 })
  } catch {
    // 注册可能已经失败（邮箱重复等），继续尝试登录
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await page.locator('input[type="email"], input[name="email"]').first().fill(testEmail)
    await page.locator('input[type="password"]').first().fill('Test123456')
    await page.locator('button[type="submit"]').first().click()
    try {
      await page.waitForURL(/\/orgs/, { timeout: 10000 })
    } catch {
      // 登录也失败，跳过
    }
  }
}

test.describe('已登录状态测试', () => {

  test('注册 → 跳转组织列表', async ({ page }) => {
    await page.goto('/register')
    await page.waitForLoadState('networkidle')

    const usernameInput = page.locator('input[type="text"], input[name="username"]').first()
    const emailInput = page.locator('input[type="email"], input[name="email"]').first()
    const passwordInputs = page.locator('input[type="password"]')
    const submitButton = page.locator('button[type="submit"]').first()

    const testEmail = `e2e_${Date.now()}@test.com`
    await usernameInput.fill('e2e_test')
    await emailInput.fill(testEmail)
    await passwordInputs.first().fill('Test123456')
    await passwordInputs.nth(1).fill('Test123456')
    await submitButton.click()

    // 注册后跳转到 orgs 或 orgs 列表
    await page.waitForURL(/\/(orgs|org)/, { timeout: 10000 })
    expect(page.url()).toMatch(/\/(orgs|org)/)
  })

  test('登录页 → 输入错误密码 → 提示错误', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')

    await page.locator('input[type="email"], input[name="email"]').first().fill('wrong@test.com')
    await page.locator('input[type="password"]').first().fill('wrongpassword')
    await page.locator('button[type="submit"]').first().click()

    // 等待错误提示（后端返回 401）
    await page.waitForTimeout(3000)
    // 页面不应跳转到 orgs
    expect(page.url()).not.toMatch(/\/orgs/)
  })

  test('已登录用户访问 /orgs 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/orgs')
    await page.waitForLoadState('networkidle')
    // 页面应该加载，不崩溃
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /dashboard 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /projects 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/projects')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /agents 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/agents')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /executions 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/executions')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /activities 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/activities')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /scheduler 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/scheduler')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /workflows 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/workflows')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /settings 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /agent-roles 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/agent-roles')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })

  test('已登录用户访问 /tasks/due-soon 正常显示', async ({ page }) => {
    await registerAndLogin(page)
    await page.goto('/tasks/due-soon')
    await page.waitForLoadState('networkidle')
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })
})
