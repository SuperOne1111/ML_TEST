"""
核心数据模型
来源：《关键接口抽象框架.md》v2.0
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from .types import LifecycleState, StepStatus, AgentRole, RiskLevel, PermissionLevel, TraceEventType, MemoryScope


# ==============================================================================
# 计划结构 (支持并行依赖)
# ==============================================================================

class PlanStep(BaseModel):
    """执行计划中的单个步骤"""
    id: str
    description: str
    tool_name: str
    input_schema: Dict[str, Any]
    expected_output: Optional[str] = None
    dependencies: List[str] = []  # 依赖步骤 ID 列表 (为空则可并行)
    timeout_ms: Optional[int] = None  # 步骤级超时覆盖


class ExecutionPlan(BaseModel):
    """完整执行计划"""
    goal: str
    steps: List[PlanStep]
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)


# ==============================================================================
# 状态分层模型 (严格隔离)
# ==============================================================================

class GlobalState(BaseModel):
    """
    Immutable Global State (不可变全局状态)
    仅 Engine 可更新引用，Agent 只读
    """
    model_config = ConfigDict(frozen=True)  # 强制不可变

    execution_id: UUID = Field(default_factory=uuid4)
    original_goal: str
    lifecycle_state: LifecycleState
    iteration_count: int = 0
    trace_id: str
    created_at: datetime = Field(default_factory=datetime.now)


class ExecutionContext(BaseModel):
    """
    Execution Context (可快照回滚)
    包含当前计划、中间结果、错误记录
    """
    current_plan: Optional[ExecutionPlan] = None
    active_steps: Dict[str, StepStatus] = {}  # 支持并行状态跟踪
    current_batch_id: Optional[str] = None    # 支持并行批次追踪
    replan_scope: Optional[str] = None        # 自愈范围标记 ("LOCAL" 或 "GLOBAL")
    intermediate_results: Dict[str, Any] = {}
    errors: List[str] = []
    snapshot_id: Optional[str] = None  # 当前关联的快照 ID


class StepContext(BaseModel):
    """
    Ephemeral Step Context (临时上下文)
    执行完成后清理，仅包含当前步骤必要信息
    """
    step_id: str
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    validation_flags: Dict[str, bool] = {}
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None