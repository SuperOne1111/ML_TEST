"""
Tracer 基础抽象实现
"""
from abc import ABC
from typing import List, Dict, Any
from datetime import datetime

from src.core.interfaces import BaseTracer
from src.core.types import TraceEventType


class BaseTracerImpl(BaseTracer, ABC):
    """
    Tracer 基础抽象实现
    提供通用的事件记录和追踪功能基础
    """
    pass