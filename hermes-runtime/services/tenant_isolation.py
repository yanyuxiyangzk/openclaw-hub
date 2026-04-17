"""
OpenClawHub Phase 0: 多租户隔离服务

核心原理：Hermes Agent 使用 HERMES_HOME 环境变量确定所有数据存储位置。
通过为每个租户设置独立的 HERMES_HOME，实现完全隔离。

隔离资源：
- memories/     → MEMORY.md / USER.md
- sessions/     → SQLite 会话存储 (state.db)
- skills/       → 角色 Skills
- jobs.json     → Cron 定时任务
- config.yaml   → 租户级配置
"""

import shutil
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


# OpenClawHub 根目录（项目根）
OPENCLAWHUB_ROOT = Path(__file__).parent.parent.parent.resolve()

# Hermes Agent 源码目录
HERMES_SRC_DIR = OPENCLAWHUB_ROOT / "hermes-agent"

# 多租户运行时根目录
TENANTS_ROOT = OPENCLAWHUB_ROOT / "hermes-runtime" / "tenants"

# 共享 Skills 目录
SHARED_SKILLS_DIR = OPENCLAWHUB_ROOT / "hermes-runtime" / "shared_skills"

# 模板目录
TEMPLATE_DIR = TENANTS_ROOT / ".template"


@dataclass
class TenantConfig:
    """租户配置"""
    id: str
    name: str
    plan: str = "free"
    model: str = "minimax/MiniMax-M2.7"
    provider: str = "api.minimax.chat"
    base_url: str = "https://api.minimax.chat/v1"


@dataclass
class AgentConfig:
    """数字员工配置"""
    id: str
    tenant_id: str
    name: str
    role: str                      # backend-dev / frontend-dev / pm / architect / tester / ui-designer
    personality: str = ""
    model: Optional[str] = None    # None = 使用租户默认


class TenantIsolation:
    """
    租户隔离管理器
    
    负责：
    1. 创建租户目录结构
    2. 删除租户目录结构
    3. 获取租户 HERMES_HOME 路径
    4. 列出所有租户
    """

    def __init__(self, tenants_root: Path = TENANTS_ROOT):
        self.tenants_root = tenants_root
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保必要目录存在"""
        self.tenants_root.mkdir(parents=True, exist_ok=True)
        TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        SHARED_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    # ─── 租户管理 ───────────────────────────────────────────────

    def create_tenant(self, config: TenantConfig) -> dict:
        """
        创建新租户
        
        流程：
        1. 创建租户目录结构
        2. 从模板复制配置文件
        3. 初始化 hermes_home 目录
        4. 返回创建结果
        """
        tenant_id = config.id
        tenant_root = self.tenants_root / tenant_id
        
        if tenant_root.exists():
            raise ValueError(f"租户 {tenant_id} 已存在")
        
        created_at = datetime.now().isoformat()
        
        # 1. 创建目录结构
        hermes_home = tenant_root / "hermes_home"
        hermes_home.mkdir(parents=True, exist_ok=True)
        (hermes_home / "memories").mkdir(exist_ok=True)
        (hermes_home / "skills").mkdir(exist_ok=True)
        (hermes_home / "sessions").mkdir(exist_ok=True)
        (tenant_root / "agents").mkdir(exist_ok=True)
        
        # 2. 复制并填充模板
        self._render_template(
            TEMPLATE_DIR / "config.yaml",
            tenant_root / "config.yaml",
            {
                "{{TENANT_ID}}": tenant_id,
                "{{TENANT_NAME}}": config.name,
                "{{CREATED_AT}}": created_at,
            }
        )
        
        self._render_template(
            TEMPLATE_DIR / "hermes_home" / "memories" / "MEMORY.md",
            hermes_home / "memories" / "MEMORY.md",
            {
                "{{AGENT_NAME}}": f"{config.name} 的数字员工",
                "{{AGENT_ROLE}}": "general",
                "{{TENANT_ID}}": tenant_id,
                "{{CREATED_AT}}": created_at,
                "{{UPDATED_AT}}": created_at,
            }
        )
        
        self._render_template(
            TEMPLATE_DIR / "hermes_home" / "memories" / "USER.md",
            hermes_home / "memories" / "USER.md",
            {
                "{{USER_NAME}}": config.name,
                "{{UPDATED_AT}}": created_at,
            }
        )
        
        shutil.copy2(
            TEMPLATE_DIR / "hermes_home" / "jobs.json",
            hermes_home / "jobs.json"
        )
        
        return {
            "tenant_id": tenant_id,
            "tenant_root": str(tenant_root),
            "hermes_home": str(hermes_home),
            "created_at": created_at,
        }

    def delete_tenant(self, tenant_id: str) -> dict:
        """
        删除租户（危险操作！）
        
        流程：
        1. 停止所有运行中的 Agent 实例
        2. 删除租户目录
        """
        tenant_root = self.tenants_root / tenant_id
        
        if not tenant_root.exists():
            raise ValueError(f"租户 {tenant_id} 不存在")
        
        # TODO: 先停止所有运行中的 Agent 实例
        # hermes_instance_manager.stop_all(tenant_id)
        
        # 删除目录
        shutil.rmtree(tenant_root)
        
        return {
            "tenant_id": tenant_id,
            "deleted": True,
            "deleted_at": datetime.now().isoformat(),
        }

    def get_tenant_hermes_home(self, tenant_id: str) -> Path:
        """获取租户的 HERMES_HOME 路径"""
        hermes_home = self.tenants_root / tenant_id / "hermes_home"
        if not hermes_home.exists():
            raise ValueError(f"租户 {tenant_id} 的 hermes_home 不存在")
        return hermes_home

    def get_hermes_env(self, tenant_id: str) -> dict:
        """
        获取启动 Hermes Agent 所需的环境变量
        
        用于：
        1. subprocess 启动 Hermes 时传递
        2. Docker 容器启动时设置
        """
        hermes_home = self.get_tenant_hermes_home(tenant_id)
        return {
            "HERMES_HOME": str(hermes_home),
            # 共享 Skills 目录
            "HERMES_OPTIONAL_SKILLS": str(SHARED_SKILLS_DIR),
        }

    def list_tenants(self) -> list:
        """列出所有租户"""
        tenants = []
        for tenant_dir in self.tenants_root.iterdir():
            if tenant_dir.is_dir() and not tenant_dir.name.startswith("."):
                config_path = tenant_dir / "config.yaml"
                if config_path.exists():
                    tenants.append({
                        "id": tenant_dir.name,
                        "root": str(tenant_dir),
                    })
        return tenants

    # ─── 数字员工管理 ───────────────────────────────────────────

    def create_agent(self, config: AgentConfig) -> dict:
        """
        创建数字员工
        
        流程：
        1. 创建 agent.yaml 配置
        2. 初始化 agent 专属的 SOUL.md / IDENTITY.md
        """
        tenant_root = self.tenants_root / config.tenant_id
        agent_dir = tenant_root / "agents" / config.id
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        agent_yaml = f"""# 数字员工配置
# 租户：{config.tenant_id}
# 创建时间：{datetime.now().isoformat()}

agent:
  id: "{config.id}"
  name: "{config.name}"
  role: "{config.role}"
  personality: "{config.personality}"
  model: "{config.model or '租户默认'}"
  
  # 指向租户的 hermes_home
  hermes_home: "../hermes_home"
  
  # 状态：stopped / running / error
  status: "stopped"
  
  # 启用的 Skills（角色相关）
  skills:
    - "{config.role}-skill"
    
  # 资源限制
  limits:
    max_sessions_per_day: 100
    max_tool_calls_per_task: 500
"""
        (agent_dir / "agent.yaml").write_text(agent_yaml, encoding="utf-8")
        
        return {
            "agent_id": config.id,
            "tenant_id": config.tenant_id,
            "agent_dir": str(agent_dir),
            "created_at": datetime.now().isoformat(),
        }

    def list_agents(self, tenant_id: str) -> list:
        """列出租户的所有数字员工"""
        agents_dir = self.tenants_root / tenant_id / "agents"
        if not agents_dir.exists():
            return []
        
        agents = []
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir():
                agents.append({
                    "id": agent_dir.name,
                    "dir": str(agent_dir),
                })
        return agents

    # ─── 工具方法 ───────────────────────────────────────────────

    def _render_template(self, src: Path, dst: Path, variables: dict):
        """渲染模板文件，替换变量"""
        content = src.read_text(encoding="utf-8")
        for key, value in variables.items():
            content = content.replace(key, str(value))
        dst.write_text(content, encoding="utf-8")


# ─── 便捷函数 ──────────────────────────────────────────────────

def get_hermes_home_for_tenant(tenant_id: str) -> Path:
    """获取租户的 HERMES_HOME"""
    ti = TenantIsolation()
    return ti.get_tenant_hermes_home(tenant_id)


def get_hermes_env_for_tenant(tenant_id: str) -> dict:
    """获取启动 Hermes 的环境变量"""
    ti = TenantIsolation()
    return ti.get_hermes_env(tenant_id)
