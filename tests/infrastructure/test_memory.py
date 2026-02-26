"""
Memory 单元测试
验证 LocalMemory 的各种功能
"""
import asyncio
import pytest
from datetime import datetime, timedelta
from src.infrastructure.memory.local_memory import LocalMemory
from src.core.types import MemoryScope


@pytest.fixture
def local_memory():
    """创建 LocalMemory 实例"""
    return LocalMemory()


@pytest.mark.asyncio
async def test_store_and_retrieve_ephemeral(local_memory):
    """测试在 EPHEMERAL scope 下存储和检索数据"""
    key = "test_key"
    value = {"data": "ephemeral_test"}
    
    # 存储数据
    await local_memory.store(key, value, MemoryScope.EPHEMERAL)
    
    # 检索数据
    retrieved_value = await local_memory.retrieve(key, MemoryScope.EPHEMERAL)
    
    assert retrieved_value == value


@pytest.mark.asyncio
async def test_store_and_retrieve_session(local_memory):
    """测试在 SESSION scope 下存储和检索数据"""
    key = "session_key"
    value = {"data": "session_test"}
    
    # 存储数据
    await local_memory.store(key, value, MemoryScope.SESSION)
    
    # 检索数据
    retrieved_value = await local_memory.retrieve(key, MemoryScope.SESSION)
    
    assert retrieved_value == value


@pytest.mark.asyncio
async def test_store_and_retrieve_global(local_memory):
    """测试在 GLOBAL scope 下存储和检索数据"""
    key = "global_key"
    value = {"data": "global_test"}
    
    # 存储数据
    await local_memory.store(key, value, MemoryScope.GLOBAL)
    
    # 检索数据
    retrieved_value = await local_memory.retrieve(key, MemoryScope.GLOBAL)
    
    assert retrieved_value == value


@pytest.mark.asyncio
async def test_different_scopes_isolation(local_memory):
    """测试不同 scope 的数据隔离"""
    key = "isolation_test"
    ephemeral_value = {"scope": "ephemeral"}
    session_value = {"scope": "session"}
    global_value = {"scope": "global"}
    
    # 在不同 scope 存储相同 key 的不同值
    await local_memory.store(key, ephemeral_value, MemoryScope.EPHEMERAL)
    await local_memory.store(key, session_value, MemoryScope.SESSION)
    await local_memory.store(key, global_value, MemoryScope.GLOBAL)
    
    # 验证每个 scope 返回正确的值
    assert await local_memory.retrieve(key, MemoryScope.EPHEMERAL) == ephemeral_value
    assert await local_memory.retrieve(key, MemoryScope.SESSION) == session_value
    assert await local_memory.retrieve(key, MemoryScope.GLOBAL) == global_value


@pytest.mark.asyncio
async def test_search_functionality(local_memory):
    """测试 search() 方法能返回匹配的结果"""
    # 存储一些测试数据
    await local_memory.store("task_1", {"title": "User Registration", "status": "completed"}, MemoryScope.SESSION)
    await local_memory.store("task_2", {"title": "Data Processing", "status": "running"}, MemoryScope.SESSION)
    await local_memory.store("task_3", {"title": "User Profile Update", "status": "pending"}, MemoryScope.SESSION)
    
    # 搜索包含 "User" 的数据
    results = await local_memory.search("User", MemoryScope.SESSION)
    
    # 应该找到两个结果
    assert len(results) == 2
    titles = [item["title"] for item in results]
    assert "User Registration" in titles
    assert "User Profile Update" in titles


@pytest.mark.asyncio
async def test_record_failure_pattern(local_memory):
    """测试 record_failure_pattern() 正确记录失败模式"""
    failure_pattern = {
        "error_type": "ConnectionError",
        "tool_name": "api_call",
        "frequency": 5,
        "context": "network_issue"
    }
    
    # 记录失败模式
    await local_memory.record_failure_pattern(failure_pattern)
    
    # 检查失败模式是否被记录（注意：LocalMemory 没有公开获取失败模式的方法，
    # 所以我们只能验证它没有抛出异常）
    assert len(local_memory._failure_patterns) == 1
    recorded = local_memory._failure_patterns[0]
    assert recorded["error_type"] == "ConnectionError"
    assert "timestamp" in recorded


@pytest.mark.asyncio
async def test_data_expiration(local_memory):
    """测试数据过期机制"""
    key = "expiring_key"
    value = {"data": "will_expire"}
    
    # 手动设置一个已过期的数据
    expire_time = datetime.now() - timedelta(seconds=1)  # 1秒前过期
    local_memory._memory_store[MemoryScope.EPHEMERAL][key] = (value, expire_time)
    
    # 尝试检索，应该返回 None（因为已过期并被删除）
    retrieved_value = await local_memory.retrieve(key, MemoryScope.EPHEMERAL)
    
    assert retrieved_value is None
    assert key not in local_memory._memory_store[MemoryScope.EPHEMERAL]


@pytest.mark.asyncio
async def test_store_complex_data_structure(local_memory):
    """测试存储复杂数据结构"""
    key = "complex_data"
    value = {
        "nested": {
            "list": [1, 2, {"inner": "value"}],
            "dict": {"deep": {"deeper": "data"}}
        },
        "array": [{"id": 1}, {"id": 2}],
        "simple": "values"
    }
    
    # 存储复杂数据
    await local_memory.store(key, value, MemoryScope.GLOBAL)
    
    # 检索复杂数据
    retrieved_value = await local_memory.retrieve(key, MemoryScope.GLOBAL)
    
    assert retrieved_value == value


@pytest.mark.asyncio
async def test_search_case_insensitive(local_memory):
    """测试搜索功能大小写不敏感"""
    await local_memory.store("case_test", {"description": "This is a Mixed Case Test"}, MemoryScope.SESSION)
    
    # 使用小写查询应该能找到大写内容
    results = await local_memory.search("mixed", MemoryScope.SESSION)
    assert len(results) == 1
    
    # 使用大写查询应该能找到小写内容
    results = await local_memory.search("THIS", MemoryScope.SESSION)
    assert len(results) == 1


@pytest.mark.asyncio
async def test_cleanup_expired_called_during_operations(local_memory):
    """测试在各种操作中都会调用过期清理"""
    # 添加一个过期的数据项
    expired_key = "expired_item"
    valid_key = "valid_item"
    expired_value = {"status": "should_be_removed"}
    valid_value = {"status": "should_remain"}
    
    # 设置一个已过期的项和一个有效项
    expired_time = datetime.now() - timedelta(seconds=1)
    valid_time = datetime.now() + timedelta(hours=1)
    
    local_memory._memory_store[MemoryScope.SESSION][expired_key] = (expired_value, expired_time)
    local_memory._memory_store[MemoryScope.SESSION][valid_key] = (valid_value, valid_time)
    
    # 执行检索操作，这应该触发过期清理
    result = await local_memory.retrieve(valid_key, MemoryScope.SESSION)
    
    # 验证有效的数据仍然存在，过期的数据已被清理
    assert result == valid_value
    assert expired_key not in local_memory._memory_store[MemoryScope.SESSION]
    assert valid_key in local_memory._memory_store[MemoryScope.SESSION]