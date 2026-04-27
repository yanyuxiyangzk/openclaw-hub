import { test, expect } from '@playwright/test'

// 未登录时访问受保护页面应跳转到登录
test.describe('受保护页面（未登录重定向）', () => {
  const protectedPages = [
    { path: '/orgs', name: '组织列表' },
    { path: '/settings', name: '设置' },
    { path: '/dashboard', name: '仪表盘' },
  ]

  protectedPages.forEach(({ path, name }) => {
    test(`${name}页面未登录时重定向到登录页`, async ({ page }) => {
      await page.goto(path)
      await page.waitForURL(/\/login/, { timeout: 5000 })
      expect(page.url()).toContain('/login')
    })
  })

  test('首页重定向到登录或组织列表', async ({ page }) => {
    await page.goto('/')
    await page.waitForURL(/\/(login|orgs)/, { timeout: 5000 })
    expect(page.url()).toMatch(/\/(login|orgs)/)
  })
})

// 公开页面测试
test.describe('公开页面', () => {
  test('邀请页面可访问', async ({ page }) => {
    // 不存在的 token 页面应该正常显示（只是报验证失败）
    await page.goto('/invite/nonexistent-token')
    // 页面应该正常渲染，显示验证中或错误信息
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })
})
