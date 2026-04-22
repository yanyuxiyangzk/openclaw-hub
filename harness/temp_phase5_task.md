## 任务：开发 OpenClawHub Phase 5 - 执行引擎集成

### 项目信息
- 项目路径：D:\project\aicoding\OpenClawHub
- 技术栈：Python FastAPI + SQLAlchemy + Vue 3 + TypeScript
- 参考：Phase 1-4 的实现模式

### Phase 5 任务内容

#### 1. 数据库模型（3个表）

**executions 表**
```python
- id: UUID (PK)
- task_id: UUID (FK)
- agent_id: UUID (FK)
- status: ENUM('pending', 'running', 'completed', 'failed', 'cancelled')
- input_data: JSON
- output_data: JSON
- error_message: TEXT
- started_at: DATETIME
- completed_at: DATETIME
- created_at
```

**scheduler_jobs 表**
```python
- id: UUID (PK)
- name: VARCHAR(128)
- task_template_id: UUID (FK)
- cron_expression: VARCHAR(64)
- agent_id: UUID (FK)
- enabled: BOOLEAN
- last_run_at: DATETIME
- next_run_at: DATETIME
- created_at
```

**workflows 表**
```python
- id: UUID (PK)
- name: VARCHAR(128)
- description: TEXT
- steps: JSON
- org_id: UUID (FK)
- created_by: UUID (FK)
- created_at, updated_at
```

#### 2. 后端 API（15个）

**执行引擎 (8个)**
- T-501: POST /api/tasks/{id}/execute - 触发任务执行
- T-502: POST /api/tasks/{id}/execute/batch - 批量执行
- T-503: GET /api/executions/{id} - 执行记录详情
- T-504: GET /api/tasks/{id}/executions - 任务执行历史
- T-505: POST /api/executions/{id}/cancel - 取消执行
- T-506: POST /api/executions/{id}/retry - 重试执行
- T-507: GET /api/executions/{id}/output - 执行输出
- T-508: GET /api/executions/active - 当前活跃执行

**Agent调度 (4个)**
- T-510: POST /api/scheduler/jobs - 创建定时任务
- T-511: GET /api/scheduler/jobs - 定时任务列表
- T-512: DELETE /api/scheduler/jobs/{id} - 删除定时任务
- T-513: GET /api/scheduler/jobs/{id}/runs - 执行记录

**工作流 (3个)**
- T-520: POST /api/workflows - 创建工作流
- T-521: GET /api/workflows/{id} - 工作流详情
- T-522: POST /api/workflows/{id}/execute - 执行工作流

#### 3. 前端页面（4个）
- T-530: /executions - 执行记录页
- T-531: /executions/:id - 执行详情页
- T-532: /scheduler - 定时任务管理页
- T-533: /workflows - 工作流编辑器页

### 开发要求

1. 先看 Phase 2-4 的代码模式，参考 backend/routers/ 和 frontend/src/pages/ 的结构
2. 数据库迁移使用 alembic
3. API 遵循 RESTful 规范
4. 前端使用 Vue 3 + TypeScript + TailwindCSS
5. 测试覆盖率 > 80%

### 执行步骤

1. 创建数据库模型文件：backend/models/phase5.py
2. 创建数据库迁移：alembic revision
3. 创建 API 路由文件：backend/routers/phase5.py
4. 实现 15 个 API
5. 创建前端页面组件
6. 运行测试验证

完成后报告完成情况。