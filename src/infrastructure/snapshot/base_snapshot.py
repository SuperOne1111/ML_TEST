"""
快照管理器抽象基类
提供快照创建和恢复的基础接口定义
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.core.models import ExecutionContext


class BaseSnapshotManager(ABC):
    """
    快照管理器抽象基类，定义了快照的基本操作接口
    """
    
    @abstractmethod
    async def create_snapshot(
        self,
        execution_context: ExecutionContext,
        label: str,
    ) -> str:
        """
        创建快照
        
        Args:
            execution_context: 执行上下文
            label: 快照标签
            
        Returns:
            str: 快照ID
        """
        pass

    @abstractmethod
    async def restore_snapshot(
        self,
        snapshot_id: str,
    ) -> ExecutionContext:
        """
        恢复快照
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            ExecutionContext: 恢复的执行上下文
        """
        pass