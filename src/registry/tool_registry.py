"""
工具注册中心
来源：《关键接口抽象框架.md》v2.0
"""
from typing import Dict, Optional

from src.core.interfaces import BaseTool


class ToolRegistry:
    """工具注册与查询中心"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        """通过名称获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        """列出所有已注册工具 (name -> version)"""
        return {name: tool.version for name, tool in self._tools.items()}

    def exists(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools