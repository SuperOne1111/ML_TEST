"""
快照管理器单元测试
测试JSON快照管理器的各项功能
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock

from src.core.models import ExecutionContext
from src.infrastructure.snapshot.json_snapshot import JsonSnapshotManager


@pytest.fixture
def temp_storage_path(tmp_path):
    """创建临时存储路径"""
    return tmp_path / "snapshots"


@pytest.fixture
def snapshot_manager(temp_storage_path):
    """创建快照管理器实例"""
    manager = JsonSnapshotManager(str(temp_storage_path))
    return manager


@pytest.fixture
def sample_execution_context():
    """创建示例执行上下文"""
    return ExecutionContext(
        current_plan=None,
        active_steps={},
        current_batch_id=None,
        replan_scope=None,
        intermediate_results={"key": "value"},
        errors=[],
        snapshot_id=None
    )


@pytest.mark.asyncio
async def test_create_snapshot(snapshot_manager, sample_execution_context):
    """测试创建快照功能"""
    label = "test_label"
    snapshot_id = await snapshot_manager.create_snapshot(sample_execution_context, label)
    
    # 验证返回的快照ID不为空
    assert snapshot_id is not None
    assert len(snapshot_id) > 0
    
    # 验证快照文件已创建
    snapshot_file = snapshot_manager.storage_path / f"{snapshot_id}.json"
    assert snapshot_file.exists()


@pytest.mark.asyncio
async def test_restore_snapshot(snapshot_manager, sample_execution_context):
    """测试恢复快照功能"""
    # 创建快照
    label = "restore_test"
    snapshot_id = await snapshot_manager.create_snapshot(sample_execution_context, label)
    
    # 恢复快照
    restored_context = await snapshot_manager.restore_snapshot(snapshot_id)
    
    # 验证恢复的上下文与原始上下文一致
    assert restored_context.intermediate_results == sample_execution_context.intermediate_results
    assert restored_context.errors == sample_execution_context.errors


@pytest.mark.asyncio
async def test_list_snapshots(snapshot_manager, sample_execution_context):
    """测试列出快照功能"""
    # 创建多个快照
    await snapshot_manager.create_snapshot(sample_execution_context, "test1")
    await snapshot_manager.create_snapshot(sample_execution_context, "test2")
    
    # 获取快照列表
    snapshots = await snapshot_manager.list_snapshots()
    
    # 验证快照列表包含创建的快照
    assert len(snapshots) == 2
    labels = [s["label"] for s in snapshots]
    assert "test1" in labels
    assert "test2" in labels


@pytest.mark.asyncio
async def test_delete_snapshot(snapshot_manager, sample_execution_context):
    """测试删除快照功能"""
    # 创建快照
    snapshot_id = await snapshot_manager.create_snapshot(sample_execution_context, "delete_test")
    
    # 验证快照存在
    snapshot_file = snapshot_manager.storage_path / f"{snapshot_id}.json"
    assert snapshot_file.exists()
    
    # 删除快照
    result = await snapshot_manager.delete(snapshot_id)
    assert result is True
    
    # 验证快照文件已被删除
    assert not snapshot_file.exists()


@pytest.mark.asyncio
async def test_delete_nonexistent_snapshot(snapshot_manager):
    """测试删除不存在的快照"""
    result = await snapshot_manager.delete("nonexistent_id")
    assert result is False


@pytest.mark.asyncio
async def test_restore_nonexistent_snapshot(snapshot_manager):
    """测试恢复不存在的快照"""
    with pytest.raises(FileNotFoundError):
        await snapshot_manager.restore_snapshot("nonexistent_id")


@pytest.mark.asyncio
async def test_expired_snapshot(snapshot_manager, sample_execution_context):
    """测试过期快照"""
    # 创建一个带有过去过期时间的快照数据
    snapshot_id = "expired_test"
    snapshot_file = snapshot_manager.storage_path / f"{snapshot_id}.json"
    
    expired_data = {
        "id": snapshot_id,
        "label": "expired",
        "timestamp": datetime.now().isoformat(),
        "execution_context": sample_execution_context.model_dump(),
        "expires_at": (datetime.now() - timedelta(hours=1)).isoformat()  # 已过期
    }
    
    with open(snapshot_file, 'w') as f:
        import json
        json.dump(expired_data, f)
    
    # 尝试恢复过期快照应该抛出异常
    with pytest.raises(ValueError, match="has expired"):
        await snapshot_manager.restore_snapshot(snapshot_id)


@pytest.mark.asyncio
async def test_snapshot_persistence(snapshot_manager, sample_execution_context):
    """测试快照持久化功能"""
    # 创建快照
    label = "persistence_test"
    snapshot_id = await snapshot_manager.create_snapshot(sample_execution_context, label)
    
    # 创建新的快照管理器实例（模拟重启）
    new_manager = JsonSnapshotManager(str(snapshot_manager.storage_path))
    
    # 从新实例恢复快照
    restored_context = await new_manager.restore_snapshot(snapshot_id)
    
    # 验证数据保持不变
    assert restored_context.intermediate_results == sample_execution_context.intermediate_results