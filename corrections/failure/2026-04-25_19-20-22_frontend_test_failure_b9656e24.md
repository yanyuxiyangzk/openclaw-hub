# Correction: FAILURE - FRONTEND 测试失败

## 任务
实现 Phase4 任务：T-424: POST /api/tasks/{id}/move** - 移动任务

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
 [32m✓[39m src/views/__tests__/OrgListView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 75[2mms[22m[39m
 [32m✓[39m src/views/__tests__/OrgDetailView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 77[2mms[22m[39m
 [32m✓[39m src/views/__tests__/MemberManageView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 81[2mms[22m[39m
 [32m✓[39m src/views/__tests__/SettingsView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 84[2mms[22m[39m
 [32m✓[39m src/views/__tests__/RegisterView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 140[2mms[22m[39m
 [33m❯[39m src/views/__tests__/LoginView.spec.ts [2m ([22m[2m2 tests[22m [2m|[22m [31m2 failed[39m[2m)[22m[33m 417[2mms[22m[39m
[31m   [33m❯[31m src/views/__tests__/LoginView.spec.ts[2m > [22mLoginView[2m > [22mrenders login form[39m
[31m     → expected 'OpenClawHub' to be 'OpenClawHub 登录' // Object.is equality[39m
[31m   [33m❯[31m src/views/__tests__/LoginView.spec.ts[2m > [22mLoginView[2m > [22mshows register link[39m
[31m     → expected '注册新账号' to be '注册' // Object.is equality[39m

[2m Test Files [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m6 passed[39m[22m[90m (7)[39m
[2m      Tests [22m [1m[31m2 failed[39m[22m[2m | [22m[1m[32m12 passed[39m[22m[90m (14)[39m
[2m   Start at [22m 19:20:18
[2m   Duration [22m 3.97s[2m (transform 2.77s, setup 3ms, collect 6.68s, tests 933ms, environment 12.31s, prepare 3.10s)[22m

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
