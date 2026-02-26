"""
Console Tracer 实现
将追踪事件打印到控制台，并提供基于内存的事件存储
"""
from typing import List, Dict, Any
from datetime import datetime
import json

from src.core.interfaces import BaseTracer
from src.core.types import TraceEventType
from src.core.models import GlobalState


class ConsoleTracer(BaseTracer):
    """
    控制台追踪器实现
    - 将事件记录到内存并打印到控制台
    - 支持按 trace_id 查询事件
    - 事件按时间顺序存储
    """
    
    def __init__(self):
        # 存储所有事件，按 trace_id 分组
        self._events: Dict[str, List[Dict[str, Any]]] = {}
    
    async def record_event(
        self,
        event_type: TraceEventType,
        payload: Dict[str, Any],
        trace_id: str
    ) -> None:
        """记录事件到内存并打印到控制台"""
        # 创建事件对象
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "payload": payload,
            "trace_id": trace_id
        }
        
        # 按 trace_id 分组存储事件
        if trace_id not in self._events:
            self._events[trace_id] = []
        
        self._events[trace_id].append(event)
        
        # 打印到控制台
        print(f"[TRACE] {event['timestamp']} | {event['event_type']} | "
              f"TraceID: {trace_id} | Payload: {json.dumps(payload, ensure_ascii=False)}")
    
    async def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """获取指定 trace_id 的所有事件，按时间顺序返回"""
        return self._events.get(trace_id, [])