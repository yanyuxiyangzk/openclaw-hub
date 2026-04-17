"""
OpenClawHub Phase 0: Hermes Agent 实例管理器

负责：
1. 启动/停止 Hermes Agent 实例
2. 管理实例生命周期
3. 监控实例健康状态
4. 处理实例通信（通过 subprocess 或 HTTP）
"""

import os
import json
import subprocess
import signal
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass, field

from .tenant_isolation import TenantIsolation, get_hermes_env_for_tenant


# Hermes Agent 源码中的入口脚本
HERMES_ENTRY = "hermes-agent/cli.py"


@dataclass
class HermesInstance:
    """Hermes Agent 实例"""
    id: str                          # 实例 ID
    tenant_id: str                   # 所属租户
    agent_id: str                    # 对应的数字员工 ID
    process: Optional[subprocess.Popen] = None  # subprocess 进程
    port: Optional[int] = None       # HTTP 端口（如果有）
    status: str = "stopped"         # stopped / starting / running / error / stopping
    started_at: Optional[str] = None
    error: Optional[str] = None
    env: dict = field(default_factory=dict)  # 环境变量


class HermesInstanceManager:
    """
    Hermes Agent 实例管理器
    
    支持两种运行模式：
    1. subprocess 模式：直接在进程内运行（开发/测试用）
    2. 进程隔离模式：每个租户一个独立进程（生产用）
    """

    def __init__(self, hermes_src: Path, tenants_root: Path):
        self.hermes_src = hermes_src
        self.tenants_root = tenants_root
        self.tenant_isolation = TenantIsolation(tenants_root)
        
        # 实例注册表：instance_id → HermesInstance
        self._instances: dict[str, HermesInstance] = {}
        
        # 锁，保证线程安全
        self._lock = threading.Lock()

    # ─── 实例生命周期 ───────────────────────────────────────────

    def start_instance(
        self,
        tenant_id: str,
        agent_id: str,
        mode: str = "subprocess",
        on_output: Optional[Callable[[str], None]] = None,
    ) -> HermesInstance:
        """
        启动 Hermes Agent 实例
        
        Args:
            tenant_id: 租户 ID
            agent_id: 数字员工 ID
            mode: 启动模式
                - "subprocess": 子进程模式（开发用）
                - "detached": 分离进程（生产用）
            on_output: 输出回调函数
            
        Returns:
            HermesInstance 对象
        """
        with self._lock:
            instance_id = f"{tenant_id}/{agent_id}"
            
            # 检查是否已存在
            if instance_id in self._instances:
                existing = self._instances[instance_id]
                if existing.status == "running":
                    return existing
                elif existing.status in ("starting",):
                    return existing
            
            # 获取租户环境变量
            env = get_hermes_env_for_tenant(tenant_id)
            env["HERMES_AGENT_ID"] = agent_id
            env["HERMES_INSTANCE_ID"] = instance_id
            
            # 读取 agent 配置
            agent_config = self._load_agent_config(tenant_id, agent_id)
            
            instance = HermesInstance(
                id=instance_id,
                tenant_id=tenant_id,
                agent_id=agent_id,
                status="starting",
                env=env,
            )
            self._instances[instance_id] = instance
            
            if mode == "subprocess":
                self._start_subprocess(instance, agent_config, on_output)
            elif mode == "detached":
                self._start_detached(instance, agent_config)
            else:
                raise ValueError(f"Unknown mode: {mode}")
            
            instance.status = "running"
            instance.started_at = datetime.now().isoformat()
            return instance

    def stop_instance(self, tenant_id: str, agent_id: str) -> dict:
        """停止 Hermes Agent 实例"""
        instance_id = f"{tenant_id}/{agent_id}"
        
        with self._lock:
            if instance_id not in self._instances:
                raise ValueError(f"实例 {instance_id} 不存在")
            
            instance = self._instances[instance_id]
            instance.status = "stopping"
        
        if instance.process:
            # 发送 SIGTERM（Linux）/ Ctrl+C（Windows）
            try:
                instance.process.terminate()
                instance.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                instance.process.kill()
            except Exception as e:
                instance.error = str(e)
        
        with self._lock:
            instance.status = "stopped"
            self._instances.pop(instance_id, None)
        
        return {
            "instance_id": instance_id,
            "stopped": True,
            "stopped_at": datetime.now().isoformat(),
        }

    def get_instance(self, tenant_id: str, agent_id: str) -> Optional[HermesInstance]:
        """获取实例状态"""
        instance_id = f"{tenant_id}/{agent_id}"
        return self._instances.get(instance_id)

    def list_instances(self, tenant_id: Optional[str] = None) -> list:
        """列出租户的所有实例，或所有实例"""
        instances = []
        for instance_id, inst in self._instances.items():
            if tenant_id is None or inst.tenant_id == tenant_id:
                instances.append({
                    "id": inst.id,
                    "tenant_id": inst.tenant_id,
                    "agent_id": inst.agent_id,
                    "status": inst.status,
                    "started_at": inst.started_at,
                    "error": inst.error,
                })
        return instances

    def stop_all(self, tenant_id: str) -> list:
        """停止租户的所有实例"""
        instances = self.list_instances(tenant_id)
        results = []
        for inst in instances:
            try:
                result = self.stop_instance(inst["tenant_id"], inst["agent_id"])
                results.append(result)
            except Exception as e:
                results.append({
                    "id": inst["id"],
                    "error": str(e),
                })
        return results

    # ─── 内部方法 ───────────────────────────────────────────────

    def _start_subprocess(
        self,
        instance: HermesInstance,
        agent_config: dict,
        on_output: Optional[Callable[[str], None]],
    ):
        """以子进程模式启动"""
        # 构造启动命令
        cmd = [
            "python",
            str(self.hermes_src / "cli.py"),
            "--chat",
            # 可以添加更多参数，如 --model, --system-prompt 等
        ]
        
        instance.process = subprocess.Popen(
            cmd,
            env={**os.environ, **instance.env},
            cwd=str(self.hermes_src),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # 启动输出读取线程
        if on_output:
            def read_output(stream, prefix):
                for line in iter(stream.readline, ""):
                    if line:
                        on_output(f"[{prefix}] {line}")
            
            stdout_thread = threading.Thread(
                target=read_output,
                args=(instance.process.stdout, "OUT"),
                daemon=True,
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(instance.process.stderr, "ERR"),
                daemon=True,
            )
            stdout_thread.start()
            stderr_thread.start()

    def _start_detached(self, instance: HermesInstance, agent_config: dict):
        """以分离进程模式启动（生产用）"""
        # TODO: 实现进程隔离，启动独立 Python 进程
        raise NotImplementedError("detached mode 尚未实现")

    def _load_agent_config(self, tenant_id: str, agent_id: str) -> dict:
        """加载 agent 配置"""
        agent_yaml = self.tenants_root / tenant_id / "agents" / agent_id / "agent.yaml"
        if not agent_yaml.exists():
            return {}
        
        # 简单 YAML 解析（实际应使用 pyyaml）
        config = {}
        for line in agent_yaml.read_text(encoding="utf-8").splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                config[key.strip()] = value.strip().strip('"')
        return config
