# Phase 2 开发任务：项目管理 + Agent 管理

## 任务概述

根据 `TASK-Phase2-5_开发计划.md` 执行 Phase 2 的开发任务。

**Phase 2 包含：**
- 4 个数据库任务（T-201 到 T-204）
- 28 个后端 API 任务（T-210 到 T-243）
- 12 个前端任务（T-250 到 T-265）
- 8 个测试任务（T-270 到 T-277）

**执行顺序：**
1. 数据库任务（T-201 → T-202 → T-203 → T-204）
2. 项目管理 API（T-210 → T-211 → T-212 → T-213 → T-214 → T-215 → T-216 → T-217）
3. Agent 基础 API（T-220 → T-221 → T-222 → T-223 → T-224 → T-225 → T-226 → T-227 → T-228 → T-229）
4. 运行时管理 API（T-230 → T-231 → T-232 → T-233 → T-234 → T-235）
5. 项目-Agent 关联 API（T-240 → T-241 → T-242 → T-243）
6. 前端任务（T-250 到 T-265）
7. 测试任务（T-270 到 T-277）

---

## 项目信息

**项目路径：** `D:\project\aicoding\OpenClawHub`

**技术栈：**
- 后端：Python FastAPI + SQLAlchemy 2.0 + Alembic + SQLite
- 前端：Vue3 + Vite + TypeScript + TailwindCSS + Pinia
- 认证：JWT（Phase 1 已实现）

**Phase 1 参考：**
- 模型：`backend/models/user.py`, `backend/models/organization.py`
- 路由：`backend/routers/auth.py`, `backend/routers/orgs.py`
- Schema：`backend/schemas/user.py`, `backend/schemas/organization.py`

---

## 数据库任务

### T-201: 创建 projects 表

**文件：** `backend/models/project.py`

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    org_id = Column(UUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    settings = Column(JSON, nullable=True)  # 项目配置
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="projects")
    owner = relationship("User", back_populates="created_projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    project_agents = relationship("ProjectAgent", back_populates="project", cascade="all, delete-orphan")
```

**迁移文件：** `backend/alembic/versions/xxx_create_projects.py`

**验收标准：** 表创建成功

---

### T-202: 创建 agents 表

**文件：** `backend/models/agent.py`

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base
import enum

class AgentStatus(str, enum.Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ERROR = "error"

class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(32), default="hermes", nullable=False)  # 'hermes'
    config = Column(JSON, nullable=True)  # Agent 配置
    org_id = Column(UUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.OFFLINE, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="agents")
```

**迁移文件：** `backend/alembic/versions/xxx_create_agents.py`

**验收标准：** 表创建成功

---

### T-203: 创建 project_agents 表

**文件：** `backend/models/project_agent.py`

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base

class ProjectAgent(Base):
    __tablename__ = "project_agents"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="project_agents")
    agent = relationship("Agent", back_populates="project_agents")

    __table_args__ = (
        UniqueConstraint('project_id', 'agent_id', name='uq_project_agent'),
    )
```

**迁移文件：** `backend/alembic/versions/xxx_create_project_agents.py`

**验收标准：** 表创建成功，复合唯一索引

---

### T-204: 创建 project_members 表

**文件：** `backend/models/project_member.py`

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base

class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="member")  # owner, admin, member
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
```

**迁移文件：** `backend/alembic/versions/xxx_create_project_members.py`

**验收标准：** 表创建成功

---

## 后端 API 任务

### 项目管理 API（8 个）

路由文件：`backend/routers/projects.py`（新建）

Schema 文件：`backend/schemas/project.py`（新建）

Service 文件：`backend/services/project_service.py`（新建）

每个 API 的实现参考 Phase 1 的 `backend/routers/orgs.py` 和 `backend/routers/users.py`。

---

## 前端任务

### 页面任务（6 个）

参考 Phase 1 的前端结构：
- `frontend/src/views/` - 页面
- `frontend/src/components/` - 组件
- `frontend/src/api/` - API 调用

---

## 测试任务

每个模块完成后，编写对应的单元测试：
- `backend/tests/test_projects.py`
- `backend/tests/test_agents.py`
- `backend/tests/test_agent_runtime.py`

---

## 执行规则

1. **先阅读项目上下文：** `harness-context.md`
2. **参考 Phase 1 实现：** 复制模式到 Phase 2
3. **边开发边写测试：** 每个 API 完成后写测试
4. **代码和测试同时 commit**
5. **遇到问题查看 corrections/ 历史经验**

---

## 验收标准

- [ ] 4 个数据库表创建成功
- [ ] 28 个后端 API 实现并测试通过
- [ ] 12 个前端页面/组件完成
- [ ] 8 个测试文件编写
- [ ] Phase 1 认证功能不受影响

---

**开始执行！**
