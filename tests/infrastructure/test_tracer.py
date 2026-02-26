"""
Tracer 模块单元测试
测试 ConsoleTracer 的各项功能
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.infrastructure.tracer.console_tracer import ConsoleTracer
from src.core.types import TraceEventType


@pytest.fixture
def tracer():
    """创建一个新的 ConsoleTracer 实例用于测试"""
    return ConsoleTracer()


@pytest.mark.asyncio
async def test_record_event_and_get_trace(tracer):
    """测试记录事件并获取追踪"""
    trace_id = "test-trace-id"
    event_type = TraceEventType.STATE_TRANSITION
    payload = {"state_from": "INIT", "state_to": "CONTEXT_BUILD"}
    
    # 记录事件
    await tracer.record_event(event_type, payload, trace_id)
    
    # 获取追踪
    events = await tracer.get_trace(trace_id)
    
    assert len(events) == 1
    event = events[0]
    assert event["trace_id"] == trace_id
    assert event["event_type"] == event_type.value
    assert event["payload"] == payload
    assert "timestamp" in event
    # 验证时间戳格式
    datetime.fromisoformat(event["timestamp"])


@pytest.mark.asyncio
async def test_multiple_events_same_trace_id(tracer):
    """测试同一追踪ID的多个事件"""
    trace_id = "test-trace-id-multi"
    
    # 记录多个事件
    await tracer.record_event(
        TraceEventType.AGENT_DECISION, 
        {"agent": "planner", "action": "generate_plan"}, 
        trace_id
    )
    await tracer.record_event(
        TraceEventType.TOOL_CALL_START, 
        {"tool": "search", "query": "python tutorial"}, 
        trace_id
    )
    await tracer.record_event(
        TraceEventType.STATE_TRANSITION, 
        {"state_from": "PLAN_GENERATION", "state_to": "PLAN_CHECK"}, 
        trace_id
    )
    
    # 获取追踪
    events = await tracer.get_trace(trace_id)
    
    assert len(events) == 3
    for event in events:
        assert event["trace_id"] == trace_id


@pytest.mark.asyncio
async def test_different_trace_ids_isolation(tracer):
    """测试不同追踪ID之间的隔离性"""
    trace_id_1 = "trace-id-1"
    trace_id_2 = "trace-id-2"
    
    # 为两个不同的追踪ID记录事件
    await tracer.record_event(
        TraceEventType.STATE_TRANSITION, 
        {"state_from": "INIT", "state_to": "CONTEXT_BUILD"}, 
        trace_id_1
    )
    await tracer.record_event(
        TraceEventType.AGENT_DECISION, 
        {"agent": "reviewer", "decision": "approve"}, 
        trace_id_2
    )
    await tracer.record_event(
        TraceEventType.STATE_TRANSITION, 
        {"state_from": "CONTEXT_BUILD", "state_to": "PLAN_GENERATION"}, 
        trace_id_1
    )
    
    # 获取第一个追踪ID的事件
    events_1 = await tracer.get_trace(trace_id_1)
    assert len(events_1) == 2
    for event in events_1:
        assert event["trace_id"] == trace_id_1
    
    # 获取第二个追踪ID的事件
    events_2 = await tracer.get_trace(trace_id_2)
    assert len(events_2) == 1
    assert events_2[0]["trace_id"] == trace_id_2


@pytest.mark.asyncio
async def test_all_trace_event_types(tracer):
    """测试所有 TraceEventType 类型都能被记录"""
    trace_id = "test-all-event-types"
    
    # 测试所有事件类型
    all_event_types = [
        TraceEventType.STATE_TRANSITION,
        TraceEventType.AGENT_DECISION,
        TraceEventType.TOOL_CALL_START,
        TraceEventType.TOOL_CALL_END,
        TraceEventType.POLICY_EVALUATION,
        TraceEventType.SNAPSHOT_CREATED,
        TraceEventType.SNAPSHOT_RESTORED,
        TraceEventType.HUMAN_INTERACTION,
        TraceEventType.ERROR_OCCURRED,
    ]
    
    for i, event_type in enumerate(all_event_types):
        await tracer.record_event(
            event_type,
            {"index": i, "type": event_type.value},
            trace_id
        )
    
    events = await tracer.get_trace(trace_id)
    assert len(events) == len(all_event_types)
    
    for i, event in enumerate(events):
        assert event["payload"]["index"] == i
        assert event["payload"]["type"] == all_event_types[i].value


@pytest.mark.asyncio
async def test_payload_any_dict_data(tracer):
    """测试 payload 支持任意字典数据"""
    trace_id = "test-payload-data"
    
    complex_payload = {
        "nested": {
            "data": [1, 2, 3],
            "value": "test"
        },
        "list_of_objects": [
            {"id": 1, "name": "item1"},
            {"id": 2, "name": "item2"}
        ],
        "simple_values": {
            "string": "hello",
            "number": 42,
            "boolean": True,
            "null_value": None
        }
    }
    
    await tracer.record_event(
        TraceEventType.AGENT_DECISION,
        complex_payload,
        trace_id
    )
    
    events = await tracer.get_trace(trace_id)
    assert len(events) == 1
    assert events[0]["payload"] == complex_payload


@pytest.mark.asyncio
async def test_events_ordered_by_time(tracer):
    """测试事件按时间顺序返回"""
    trace_id = "test-time-ordering"
    
    # 按顺序记录事件
    await tracer.record_event(
        TraceEventType.STATE_TRANSITION,
        {"state": "INIT"},
        trace_id
    )
    await asyncio.sleep(0.01)  # 确保时间戳不同
    await tracer.record_event(
        TraceEventType.STATE_TRANSITION,
        {"state": "CONTEXT_BUILD"},
        trace_id
    )
    await asyncio.sleep(0.01)  # 确保时间戳不同
    await tracer.record_event(
        TraceEventType.STATE_TRANSITION,
        {"state": "PLAN_GENERATION"},
        trace_id
    )
    
    events = await tracer.get_trace(trace_id)
    assert len(events) == 3
    
    # 验证时间戳是按顺序的
    timestamps = [event["timestamp"] for event in events]
    sorted_timestamps = sorted(timestamps)
    assert timestamps == sorted_timestamps, "Events should be ordered by timestamp"


@pytest.mark.asyncio
async def test_clear_events(tracer):
    """测试清除事件功能"""
    trace_id = "test-clear-events"
    
    # 添加一些事件
    await tracer.record_event(TraceEventType.STATE_TRANSITION, {"test": "data"}, trace_id)
    await tracer.record_event(TraceEventType.AGENT_DECISION, {"test": "data2"}, trace_id)
    
    # 验证事件存在
    events_before = await tracer.get_trace(trace_id)
    assert len(events_before) == 2
    
    # 清除事件
    tracer.clear_events()
    
    # 验证事件已清除
    events_after = await tracer.get_trace(trace_id)
    assert len(events_after) == 0


@pytest.mark.asyncio
async def test_get_all_events(tracer):
    """测试获取所有事件功能"""
    trace_id_1 = "trace-1"
    trace_id_2 = "trace-2"
    
    # 添加不同追踪ID的事件
    await tracer.record_event(TraceEventType.STATE_TRANSITION, {"test": "data1"}, trace_id_1)
    await tracer.record_event(TraceEventType.AGENT_DECISION, {"test": "data2"}, trace_id_2)
    await tracer.record_event(TraceEventType.TOOL_CALL_START, {"test": "data3"}, trace_id_1)
    
    # 获取所有事件
    all_events = tracer.get_all_events()
    assert len(all_events) == 3
    
    # 验证包含所有事件
    trace_ids = [event["trace_id"] for event in all_events]
    assert trace_ids.count(trace_id_1) == 2
    assert trace_ids.count(trace_id_2) == 1