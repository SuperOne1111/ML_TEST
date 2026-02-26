"""
LocalMemory 实现
来源：《关键接口抽象框架.md》v2.0
基于内存的本地记忆实现，支持三种作用域
"""
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.core.interfaces import BaseMemory
from src.core.types import MemoryScope


class LocalMemory(BaseMemory):
    """
    本地内存实现的记忆系统
    - 支持三种 MemoryScope：EPHEMERAL、SESSION、GLOBAL
    - 支持数据过期时间设置
    - 包含简单的语义搜索功能
    """
    
    def __init__(self):
        # 存储数据的字典，key为scope，value为{key: (value, expire_time)}
        self._memory_store: Dict[MemoryScope, Dict[str, tuple]] = {
            MemoryScope.EPHEMERAL: {},
            MemoryScope.SESSION: {},
            MemoryScope.GLOBAL: {}
        }
        
        # 存储失败模式
        self._failure_patterns: List[Dict[str, Any]] = []
        
        # 清理任务的锁
        self._cleanup_lock = asyncio.Lock()
    
    async def store(self, key: str, value: Any, scope: MemoryScope) -> None:
        """存储记忆"""
        expire_time = datetime.now() + timedelta(hours=24)  # 默认24小时过期
        self._memory_store[scope][key] = (value, expire_time)
        
        # 定期清理过期数据
        await self._cleanup_expired(scope)
    
    async def retrieve(self, key: str, scope: MemoryScope) -> Any:
        """检索记忆"""
        await self._cleanup_expired(scope)  # 检索前先清理过期数据
        
        if key in self._memory_store[scope]:
            value, expire_time = self._memory_store[scope][key]
            if datetime.now() < expire_time:
                return value
            else:
                # 如果已过期，则删除并返回None
                del self._memory_store[scope][key]
        
        return None
    
    async def search(self, query: str, scope: MemoryScope) -> List[Any]:
        """语义搜索"""
        await self._cleanup_expired(scope)  # 搜索前先清理过期数据
        
        results = []
        for stored_key, (stored_value, expire_time) in self._memory_store[scope].items():
            if datetime.now() >= expire_time:
                # 如果已过期，则删除该条目
                del self._memory_store[scope][stored_key]
                continue
            
            # 简单的文本匹配，可以扩展为向量搜索
            if query.lower() in str(stored_key).lower() or query.lower() in str(stored_value).lower():
                results.append(stored_value)
        
        return results
    
    async def record_failure_pattern(self, pattern: Dict[str, Any]) -> None:
        """记录失败模式"""
        pattern_with_timestamp = {
            **pattern,
            "timestamp": datetime.now().isoformat(),
        }
        self._failure_patterns.append(pattern_with_timestamp)
        
        # 限制失败模式列表大小，避免无限增长
        if len(self._failure_patterns) > 1000:
            self._failure_patterns = self._failure_patterns[-500:]  # 保留最近500个
    
    async def _cleanup_expired(self, scope: MemoryScope) -> None:
        """清理指定scope下的过期数据"""
        async with self._cleanup_lock:
            expired_keys = []
            for key, (_, expire_time) in self._memory_store[scope].items():
                if datetime.now() >= expire_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_store[scope][key]