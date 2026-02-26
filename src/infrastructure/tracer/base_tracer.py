"""
Tracer 抽象基类的实现模块
提供追踪系统的基础实现
"""

from abc import ABC
from src.core.interfaces import BaseTracer


class BaseTracerImpl(BaseTracer, ABC):
    """
    Tracer 抽象基类的具体实现基础
    提供一些通用的追踪功能实现
    """
    pass