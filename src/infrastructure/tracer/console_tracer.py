"""
Console Tracer 实现
提供控制台追踪功能，记录系统关键事件
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any

from src.core.interfaces import BaseTracer
from src.core.types import TraceEventType


class ConsoleTracer(BaseTracer):
    """
    控制台追踪器实现
    记录所有关键事件到内存，并提供查询接口
    """
    
    def __init__(self):
        """初始化追踪器"""
        self._events: List[Dict[str, Any]] = []
        
    async def record_event(
        self,
        event_type: TraceEventType,
        payload: Dict[str, Any],
        trace_id: str
    ) -> None:
        """
        记录标准化事件
        
        Args:
            event_type: 事件类型
            payload: 事件负载数据
            trace_id: 追踪ID
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value if isinstance(event_type, TraceEventType) else event_type,
            "payload": payload,
            "trace_id": trace_id
        }
        
        self._events.append(event)
        
        # 同时打印到控制台
        print(f"[TRACE] {event['timestamp']} | {event['event_type']} | "
              f"TraceID: {event['trace_id']} | Payload: {event['payload']}")
    
    async def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        获取特定追踪ID的所有事件
        
        Args:
            trace_id: 追踪ID
            
        Returns:
            该追踪ID相关的所有事件列表，按时间排序
        """
        filtered_events = [
            event for event in self._events
            if event["trace_id"] == trace_id
        ]
        
        # 按时间戳排序
        filtered_events.sort(key=lambda x: x["timestamp"])
        return filtered_events
    
    def clear_events(self) -> None:
        """清空所有事件（用于测试）"""
        self._events.clear()
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """获取所有事件（用于测试）"""
        return self._events.copy()