#!/usr/bin/env python3
"""
OpenClawHub hermes-runtime 管理工具

用法：
    python hermes_runtime_manager.py tenant create <tenant_id> <name>
    python hermes_runtime_manager.py tenant list
    python hermes_runtime_manager.py tenant delete <tenant_id>
    
    python hermes_runtime_manager.py agent create <tenant_id> <agent_id> <name> <role>
    python hermes_runtime_manager.py agent list <tenant_id>
    
    python hermes_runtime_manager.py instance start <tenant_id> <agent_id>
    python hermes_runtime_manager.py instance stop <tenant_id> <agent_id>
    python hermes_runtime_manager.py instance list [tenant_id]
"""

import sys
import json
from pathlib import Path

# 添加 hermes-runtime 到 path
sys.path.insert(0, str(Path(__file__).parent))

from services import (
    TenantIsolation, TenantConfig, AgentConfig,
    HermesInstanceManager, get_hermes_env_for_tenant,
)


def cmd_tenant_create(args):
    config = TenantConfig(
        id=args.tenant_id,
        name=args.name,
        plan=args.plan,
    )
    ti = TenantIsolation()
    result = ti.create_tenant(config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_tenant_list(args):
    ti = TenantIsolation()
    tenants = ti.list_tenants()
    print(json.dumps(tenants, ensure_ascii=False, indent=2))


def cmd_tenant_delete(args):
    ti = TenantIsolation()
    result = ti.delete_tenant(args.tenant_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_tenant_info(args):
    ti = TenantIsolation()
    hermes_home = ti.get_tenant_hermes_home(args.tenant_id)
    env = ti.get_hermes_env(args.tenant_id)
    print(f"HERMES_HOME: {hermes_home}")
    print(f"环境变量:")
    for k, v in env.items():
        print(f"  {k}={v}")


def cmd_agent_create(args):
    config = AgentConfig(
        id=args.agent_id,
        tenant_id=args.tenant_id,
        name=args.name,
        role=args.role,
    )
    ti = TenantIsolation()
    result = ti.create_agent(config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_agent_list(args):
    ti = TenantIsolation()
    agents = ti.list_agents(args.tenant_id)
    print(json.dumps(agents, ensure_ascii=False, indent=2))


def cmd_instance_start(args):
    hermes_src = Path(__file__).parent.parent / "hermes-agent"
    manager = HermesInstanceManager(hermes_src=hermes_src, tenants_root=Path(__file__).parent / "tenants")
    instance = manager.start_instance(args.tenant_id, args.agent_id)
    print(json.dumps({
        "id": instance.id,
        "status": instance.status,
        "started_at": instance.started_at,
    }, ensure_ascii=False, indent=2))


def cmd_instance_stop(args):
    hermes_src = Path(__file__).parent.parent / "hermes-agent"
    manager = HermesInstanceManager(hermes_src=hermes_src, tenants_root=Path(__file__).parent / "tenants")
    result = manager.stop_instance(args.tenant_id, args.agent_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_instance_list(args):
    hermes_src = Path(__file__).parent.parent / "hermes-agent"
    manager = HermesInstanceManager(hermes_src=hermes_src, tenants_root=Path(__file__).parent / "tenants")
    instances = manager.list_instances(args.tenant_id if hasattr(args, "tenant_id") and args.tenant_id else None)
    print(json.dumps(instances, ensure_ascii=False, indent=2))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClawHub hermes-runtime 管理工具")
    subparsers = parser.add_subparsers(dest="command")
    
    # tenant 子命令
    p_tenant = subparsers.add_parser("tenant", help="租户管理")
    p_tenant_sub = p_tenant.add_subparsers(dest="subcommand")
    
    p_tenant_create = p_tenant_sub.add_parser("create", help="创建租户")
    p_tenant_create.add_argument("tenant_id")
    p_tenant_create.add_argument("name")
    p_tenant_create.add_argument("--plan", default="free")
    p_tenant_create.set_defaults(func=cmd_tenant_create)
    
    p_tenant_list = p_tenant_sub.add_parser("list", help="列出租户")
    p_tenant_list.set_defaults(func=cmd_tenant_list)
    
    p_tenant_delete = p_tenant_sub.add_parser("delete", help="删除租户")
    p_tenant_delete.add_argument("tenant_id")
    p_tenant_delete.set_defaults(func=cmd_tenant_delete)
    
    p_tenant_info = p_tenant_sub.add_parser("info", help="租户详情")
    p_tenant_info.add_argument("tenant_id")
    p_tenant_info.set_defaults(func=cmd_tenant_info)
    
    # agent 子命令
    p_agent = subparsers.add_parser("agent", help="数字员工管理")
    p_agent_sub = p_agent.add_subparsers(dest="subcommand")
    
    p_agent_create = p_agent_sub.add_parser("create", help="创建数字员工")
    p_agent_create.add_argument("tenant_id")
    p_agent_create.add_argument("agent_id")
    p_agent_create.add_argument("name")
    p_agent_create.add_argument("role")
    p_agent_create.set_defaults(func=cmd_agent_create)
    
    p_agent_list = p_agent_sub.add_parser("list", help="列出数字员工")
    p_agent_list.add_argument("tenant_id")
    p_agent_list.set_defaults(func=cmd_agent_list)
    
    # instance 子命令
    p_instance = subparsers.add_parser("instance", help="Hermes 实例管理")
    p_instance_sub = p_instance.add_subparsers(dest="subcommand")
    
    p_instance_start = p_instance_sub.add_parser("start", help="启动实例")
    p_instance_start.add_argument("tenant_id")
    p_instance_start.add_argument("agent_id")
    p_instance_start.set_defaults(func=cmd_instance_start)
    
    p_instance_stop = p_instance_sub.add_parser("stop", help="停止实例")
    p_instance_stop.add_argument("tenant_id")
    p_instance_stop.add_argument("agent_id")
    p_instance_stop.set_defaults(func=cmd_instance_stop)
    
    p_instance_list = p_instance_sub.add_parser("list", help="列出实例")
    p_instance_list.add_argument("tenant_id", nargs="?", default=None)
    p_instance_list.set_defaults(func=cmd_instance_list)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
