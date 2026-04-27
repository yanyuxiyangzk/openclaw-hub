# Correction: FAILURE - FRONTEND 测试失败

## 任务
实现 Phase3 任务：T-323: GET /api/orgs/{id}/agents/usage** - 获取组织用量

## 失败类型
test_failure: frontend 测试未通过

## 重试次数
2

## 测试输出
```

> openclawhub-frontend@0.1.0 test:unit
> vitest --run


[7m[1m[36m RUN [39m[22m[27m [36mv1.6.1[39m [90mD:/project/aicoding/OpenClawHub/frontend[39m

 [32m✓[39m src/views/__tests__/InvitationView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 63[2mms[22m[39m
 [32m✓[39m src/views/__tests__/OrgDetailView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 79[2mms[22m[39m
 [32m✓[39m src/views/__tests__/MemberManageView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 90[2mms[22m[39m
 [32m✓[39m src/views/__tests__/OrgListView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 87[2mms[22m[39m
 [32m✓[39m src/views/__tests__/SettingsView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 98[2mms[22m[39m
 [32m✓[39m src/views/__tests__/RegisterView.spec.ts [2m ([22m[2m2 tests[22m[2m)[22m[90m 147[2mms[22m[39m
 [33m❯[39m src/views/__tests__/LoginView.spec.ts [2m ([22m[2m2 tests[22m [2m|[22m [31m2 failed[39m[2m)[22m[33m 547[2mms[22m[39m
[31m   [33m❯[31m src/views/__tests__/LoginView.spec.ts[2m > [22mLoginView[2m > [22mrenders login form[39m
[31m     → expected 'OpenClawHub' to be 'OpenClawHub 登录' // Object.is equality[39m
[31m   [33m❯[31m src/views/__tests__/LoginView.spec.ts[2m > [22mLoginView[2m > [22mshows register link[39m
[31m     → expected '注册新账号' to be '注册' // Object.is equality[39m

[2m Test Files [22m [1m[31m1 failed[39m[22m[2m | [22m[1m[32m6 passed[39m[22m[90m (7)[39m
[2m      Tests [22m [1m[31m2 failed[39m[22m[2m | [22m[1m[32m12 passed[39m[22m[90m (14)[39m
[2m   Start at [22m 15:01:45
[2m   Duration [22m 4.04s[2m (transform 2.54s, setup 1ms, collect 6.39s, tests 1.11s, environment 12.85s, prepare 2.59s)[22m

[90mstderr[2m | src/views/__tests__/OrgDetailView.spec.ts[2m > [22m[2mOrgDetailView[2m > [22m[2mrenders org detail header[22m[39m
[Vue Router warn]: No match found for location with path "/"

[90mstderr[2m | src/views/__tests__/Me
```

## 根因分析
[LLM 分析失败原因]

## 教训
[从测试失败中学习的教训]

## 来源
harness_run.py 测试失败重试机制自动生成
