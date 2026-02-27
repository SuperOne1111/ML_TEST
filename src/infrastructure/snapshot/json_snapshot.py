"""
JSON快照管理器实现
基于JSON文件存储的快照管理器具体实现
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
import uuid

from src.core.models import ExecutionContext
from .base_snapshot import BaseSnapshotManager


class JsonSnapshotManager(BaseSnapshotManager):
    """
    JSON快照管理器实现，将快照以JSON格式存储在本地文件系统中
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化快照管理器
        
        Args:
            storage_path: 快照存储路径，默认为 ./snapshots/
        """
        self.storage_path = Path(storage_path or "./snapshots/")
        self.storage_path.mkdir(exist_ok=True)
        
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
        snapshot_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # 构建快照数据
        snapshot_data = {
            "id": snapshot_id,
            "label": label,
            "timestamp": timestamp.isoformat(),
            "execution_context": execution_context.model_dump(),
            "expires_at": (timestamp + timedelta(hours=24)).isoformat()  # 24小时后过期
        }
        
        # 保存快照到文件
        snapshot_file = self.storage_path / f"{snapshot_id}.json"
        async with asyncio.Lock():
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2, default=str)
                
        return snapshot_id

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
        snapshot_file = self.storage_path / f"{snapshot_id}.json"
        
        if not snapshot_file.exists():
            raise FileNotFoundError(f"Snapshot file not found: {snapshot_file}")
            
        # 读取快照文件
        async with asyncio.Lock():
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
        
        # 检查快照是否过期
        expires_at = datetime.fromisoformat(snapshot_data["expires_at"])
        if datetime.now() > expires_at:
            raise ValueError(f"Snapshot {snapshot_id} has expired")
        
        # 从快照数据重建ExecutionContext
        execution_context_dict = snapshot_data["execution_context"]
        return ExecutionContext(**execution_context_dict)
    
    async def list_snapshots(self) -> list:
        """
        列出所有快照
        
        Returns:
            list: 快照信息列表
        """
        snapshots = []
        for file_path in self.storage_path.glob("*.json"):
            async with asyncio.Lock():
                with open(file_path, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
                    
            # 检查快照是否过期
            expires_at = datetime.fromisoformat(snapshot_data["expires_at"])
            if datetime.now() <= expires_at:
                snapshots.append({
                    "id": snapshot_data["id"],
                    "label": snapshot_data["label"],
                    "timestamp": snapshot_data["timestamp"],
                    "expires_at": snapshot_data["expires_at"]
                })
                
        return snapshots
    
    async def delete(self, snapshot_id: str) -> bool:
        """
        删除指定快照
        
        Args:
            snapshot_id: 快照ID
            
        Returns:
            bool: 删除是否成功
        """
        snapshot_file = self.storage_path / f"{snapshot_id}.json"
        if snapshot_file.exists():
            snapshot_file.unlink()
            return True
        return False