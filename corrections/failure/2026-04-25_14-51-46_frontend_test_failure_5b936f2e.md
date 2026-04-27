# Correction: FAILURE - FRONTEND 测试失败

## 任务
实现 Phase3 任务：T-322: GET /api/agents/{id}/tasks/count** - 获取任务计数

## 失败类型
test_failure: frontend 测试未通过

## 重试次数
2

## 测试输出
```

> openclawhub-frontend@0.1.0 test:unit
> vitest --run


[7m[1m[36m RUN [39m[22m[27m [36mv1.6.1[39m [90mD:/project/aicoding/OpenClawHub/frontend[39m

 [32m✓[39m src/views/__tests__/InvitationView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 59[2mms[22m[39m
 [32m✓[39m src/views/__tests__/OrgListView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 72[2mms[22m[39m
 [32m✓[39m src/views/__tests__/OrgDetailView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 76[2mms[22m[39m
 [32m✓[39m src/views/__tests__/MemberManageView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 82[2mms[22m[39m
 [32m✓[39m src/views/__tests__/SettingsView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 85[2mms[22m[39m
 [32m✓[39m src/views/__tests__/RegisterView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 128[2mms[22m[39m
 [33m❯[39m src/views/__tests__/LoginView.spec.ts [2m ([22m[2m2 tests[22m [2m|[22m [31m2 failed[39m[2m)[22m[33m 403[2mms[22m[39m
[31m   [33m❯[31m src/views/__tests__/LoginView.spec.ts[2m > [22mLoginView[2m > [22mrenders login form[39m
[31m     → expected 'OpenClawHub' to be 'OpenClawHub 登录' // Object.is equality[39m
[31m   [33m❯[31m src/views/__tests__/LoginView.spec.ts[2m > [22mLoginView[2m > [22mshows register link[39m
[31m     → expected '注册新账号' to be '注册' // Object.is equality[39m

[2m Test Files [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m6 passed[39m[22m[90m (7)[39m
[2m      Tests [22m [1m[31m2 failed[39m[22m[2m | [22m[1m[32m12 passed[39m[22m[90m (14)[39m
[2m   Start at [22m 14:51:42
[2m   Duration [22m 3.81s[2m (transform 2.20s, setup 3ms, collect 6.20s, tests 905ms, environment 12.30s, prepare 2.66s)[22m

[90mstderr[2m | src/views/__tests__/OrgListView.spec.ts[2m > [22m[2mOrgListView[2m > [22m[2mrenders org list header with create button[22m[39m
[Vue Router warn]: No match found for location with path "/"

[90mstderr[2m | src/views
```

## 根因分析
[LLM 分析失败原因]

## 教训
[从测试失败中学习的教训]

## 来源
harness_run.py 测试失败重试机制自动生成
