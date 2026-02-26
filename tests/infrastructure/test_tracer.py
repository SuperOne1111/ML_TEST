"""
Tracer 单元测试
"""
import asyncio
from datetime import datetime
from src.infrastructure.tracer.console_tracer import ConsoleTracer
from src.core.types import TraceEventType


class TestConsoleTracer:
    """ConsoleTracer 测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.tracer = ConsoleTracer()
        self.test_trace_id = "test-trace-id-123"
        self.another_trace_id = "another-trace-id-456"
    
    def test_record_and_get_trace_single_event(self):
        """测试记录单个事件并获取追踪"""
        payload = {"key": "value", "number": 42}
        
        # 记录事件
        asyncio.run(
            self.tracer.record_event(
                TraceEventType.AGENT_DECISION, 
                payload, 
                self.test_trace_id
            )
        )
        
        # 获取追踪
        events = asyncio.run(self.tracer.get_trace(self.test_trace_id))
        
        assert len(events) == 1
        event = events[0]
        
        assert event["event_type"] == TraceEventType.AGENT_DECISION.value
        assert event["payload"] == payload
        assert event["trace_id"] == self.test_trace_id
        
        # 验证时间戳格式
        timestamp = datetime.fromisoformat(event["timestamp"])
        assert isinstance(timestamp, datetime)
    
    def test_different_trace_ids_isolation(self):
        """测试不同 trace_id 的事件隔离"""
        payload1 = {"data": "trace1"}
        payload2 = {"data": "trace2"}
        
        # 记录两个不同 trace_id 的事件
        asyncio.run(
            self.tracer.record_event(
                TraceEventType.STATE_TRANSITION, 
                payload1, 
                self.test_trace_id
            )
        )
        asyncio.run(
            self.tracer.record_event(
                TraceEventType.TOOL_CALL_START, 
                payload2, 
                self.another_trace_id
            )
        )
        
        # 验证事件被正确隔离
        trace1_events = asyncio.run(self.tracer.get_trace(self.test_trace_id))
        trace2_events = asyncio.run(self.tracer.get_trace(self.another_trace_id))
        
        assert len(trace1_events) == 1
        assert len(trace2_events) == 1
        
        assert trace1_events[0]["payload"] == payload1
        assert trace2_events[0]["payload"] == payload2
        assert trace1_events[0]["trace_id"] == self.test_trace_id
        assert trace2_events[0]["trace_id"] == self.another_trace_id
    
    def test_multiple_events_same_trace_id_order(self):
        """测试同一 trace_id 的多个事件按时间顺序存储"""
        payloads = [
            {"step": 1, "action": "start"},
            {"step": 2, "action": "process"},
            {"step": 3, "action": "end"}
        ]
        
        # 按顺序记录多个事件
        for i, payload in enumerate(payloads):
            asyncio.run(
                self.tracer.record_event(
                    TraceEventType.AGENT_DECISION, 
                    payload, 
                    self.test_trace_id
                )
            )
            # 简单延迟以确保时间戳不同
            asyncio.run(asyncio.sleep(0.001))
        
        # 获取所有事件
        events = asyncio.run(self.tracer.get_trace(self.test_trace_id))
        
        assert len(events) == 3
        
        # 验证事件按时间顺序排列
        for i, event in enumerate(events):
            assert event["payload"] == payloads[i]
            assert event["event_type"] == TraceEventType.AGENT_DECISION.value
            assert event["trace_id"] == self.test_trace_id
            
            # 验证时间戳是递增的
            if i > 0:
                prev_timestamp = datetime.fromisoformat(events[i-1]["timestamp"])
                curr_timestamp = datetime.fromisoformat(event["timestamp"])
                assert curr_timestamp >= prev_timestamp
    
    def test_all_trace_event_types(self):
        """测试所有 TraceEventType 都能正常记录"""
        all_event_types = list(TraceEventType)
        test_payload = {"test": "event_type_coverage"}
        
        # 记录每种事件类型
        for event_type in all_event_types:
            asyncio.run(
                self.tracer.record_event(
                    event_type,
                    test_payload,
                    self.test_trace_id
                )
            )
        
        # 获取所有事件
        events = asyncio.run(self.tracer.get_trace(self.test_trace_id))
        
        assert len(events) == len(all_event_types)
        
        # 验证每种事件类型都被正确记录
        recorded_types = [event["event_type"] for event in events]
        expected_types = [event_type.value for event_type in all_event_types]
        
        # 由于可能的并发问题导致顺序不一致，我们验证集合相等
        assert set(recorded_types) == set(expected_types)
    
    def test_complex_payload_support(self):
        """测试 payload 支持复杂数据结构"""
        complex_payload = {
            "nested": {
                "data": [1, 2, 3],
                "values": {
                    "key1": "value1",
                    "key2": True,
                    "key3": None
                }
            },
            "list_of_objects": [
                {"id": 1, "name": "item1"},
                {"id": 2, "name": "item2"}
            ],
            "simple": "value"
        }
        
        asyncio.run(
            self.tracer.record_event(
                TraceEventType.POLICY_EVALUATION,
                complex_payload,
                self.test_trace_id
            )
        )
        
        events = asyncio.run(self.tracer.get_trace(self.test_trace_id))
        
        assert len(events) == 1
        assert events[0]["payload"] == complex_payload
        assert events[0]["event_type"] == TraceEventType.POLICY_EVALUATION.value
        assert events[0]["trace_id"] == self.test_trace_id
    
    def test_empty_trace_id_behavior(self):
        """测试空 trace_id 行为"""
        payload = {"test": "empty_trace_id"}
        
        asyncio.run(
            self.tracer.record_event(
                TraceEventType.ERROR_OCCURRED,
                payload,
                ""
            )
        )
        
        events = asyncio.run(self.tracer.get_trace(""))
        
        assert len(events) == 1
        assert events[0]["payload"] == payload
        assert events[0]["event_type"] == TraceEventType.ERROR_OCCURRED.value
        assert events[0]["trace_id"] == ""
    
    def test_nonexistent_trace_id(self):
        """测试不存在的 trace_id 返回空列表"""
        events = asyncio.run(self.tracer.get_trace("nonexistent-trace-id"))
        
        assert len(events) == 0