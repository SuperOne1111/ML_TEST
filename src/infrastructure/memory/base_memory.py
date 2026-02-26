"""
Memory 抽象基类
来源：《关键接口抽象框架.md》v2.0
"""
from abc import ABC
from src.core.interfaces import BaseMemory


class BaseMemoryImpl(BaseMemory, ABC):
    """
    Memory 抽象基类的具体实现
    注意：由于 BaseMemory 已在 core.interfaces 中定义，这里提供实现基类
    """
    pass