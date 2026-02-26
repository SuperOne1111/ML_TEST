"""
Agent 注册中心
来源：《关键接口抽象框架.md》v2.0
"""
from typing import Dict

from src.core.interfaces import BaseAgent
from src.core.types import AgentRole


class AgentRegistry:
    """Agent 注册与路由中心"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """注册 Agent"""
        if agent.name in self._agents:
            raise ValueError(f"Agent {agent.name} already registered")
        self._agents[agent.name] = agent

    def get_by_role(self, role: AgentRole) -> BaseAgent:
        """通过角色获取 Agent，便于 Engine 调度"""
        for agent in self._agents.values():
            if agent.role == role:
                return agent
        raise ValueError(f"No agent found for role {role}")

    def get(self, name: str) -> BaseAgent:
        """通过名称获取 Agent"""
        return self._agents[name]

    def list_agents(self) -> Dict[str, AgentRole]:
        """列出所有已注册 Agent"""
        return {name: agent.role for name, agent in self._agents.items()}