# Phase 4 Task: Task Kanban Module

## Overview

Implement Phase 4: Task Kanban with collaboration features - core workflow for agents and users working together on tasks.

## Task Scope

### Database Models (3 tables)

**tasks table (add fields)**
- parent_id: UUID (FK, nullable) - parent task for subtasks
- root_id: UUID (FK, nullable) - root task for cross-level
- position: INT - kanban order
- estimated_hours: FLOAT
- actual_hours: FLOAT
- priority: ENUM('low', 'medium', 'high', 'urgent')
- tags: JSON - tag array
- reminder_at: DATETIME (nullable)

**task_comments table**
- id: UUID (PK)
- task_id: UUID (FK)
- user_id: UUID (FK)
- content: TEXT
- created_at, updated_at

**task_attachments table**
- id: UUID (PK)
- task_id: UUID (FK)
- filename: VARCHAR(256)
- file_url: VARCHAR(512)
- file_size: INT
- uploaded_by: UUID (FK)
- uploaded_at

### Backend APIs (25 APIs)

#### Task CRUD (8 APIs)
- T-401: POST /api/tasks - Create task
- T-402: GET /api/tasks - List tasks (filter: status, assignee, project)
- T-403: GET /api/tasks/{id} - Get task
- T-404: PUT /api/tasks/{id} - Update task
- T-405: DELETE /api/tasks/{id} - Delete task
- T-406: POST /api/tasks/bulk - Bulk create
- T-407: PUT /api/tasks/bulk/status - Bulk status update
- T-408: GET /api/tasks/export - Export tasks (CSV/JSON)

#### Task Collaboration (8 APIs)
- T-410: POST /api/tasks/{id}/assign - Assign task
- T-411: POST /api/tasks/{id}/claim - Claim task
- T-412: POST /api/tasks/{id}/complete - Complete task
- T-413: POST /api/tasks/{id}/comment - Add comment
- T-414: GET /api/tasks/{id}/comments - List comments
- T-415: POST /api/tasks/{id}/subtasks - Create subtask
- T-416: GET /api/tasks/{id}/subtasks - List subtasks
- T-417: POST /api/tasks/{id}/attachments - Upload attachment

#### Kanban Views (6 APIs)
- T-420: GET /api/projects/{id}/kanban - Kanban data
- T-421: GET /api/projects/{id}/tasks/by-status - By status
- T-422: GET /api/projects/{id}/tasks/by-assignee - By assignee
- T-423: GET /api/projects/{id}/tasks/timeline - Timeline view
- T-424: POST /api/tasks/{id}/move - Move task (drag-drop)
- T-425: GET /api/tasks/{id}/activity - Activity history

#### Reminders (3 APIs)
- T-430: POST /api/tasks/{id}/remind - Set reminder
- T-431: GET /api/tasks/due-soon - Tasks due soon
- T-432: POST /api/tasks/{id}/snooze - Snooze reminder

### Frontend Pages (6 pages)

- T-440: /projects/:id/kanban - Kanban board
- T-441: /projects/:id/tasks - Task list view
- T-442: /projects/:id/timeline - Timeline view
- T-443: /tasks/:id - Task detail drawer
- T-444: /tasks/:id/edit - Task edit page
- T-445: /tasks/due-soon - Due soon page

### Frontend Components

- KanbanBoard.vue - Main kanban
- KanbanColumn.vue - Kanban column
- TaskCard.vue - Draggable task card
- TaskDetailDrawer.vue - Task detail drawer
- CommentThread.vue - Comments
- SubtaskList.vue - Subtask list
- DueDatePicker.vue - Due date picker
- TaskFilter.vue - Filter component

## Tech Stack

- Backend: Python FastAPI + SQLAlchemy
- Frontend: Vue 3 + TypeScript + TailwindCSS
- Drag-drop: @vueuse/integrations + sortablejs

## Reference

- Phase 2: backend/routers/projects.py, agents.py
- Phase 3: backend/routers/phase3.py

## Acceptance Criteria

- [ ] 3 database tables with migrations
- [ ] 25 APIs implemented
- [ ] 6 frontend pages
- [ ] Kanban drag-drop works
- [ ] All tests pass

## Start!
