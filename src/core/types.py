"""
核心类型定义
来源：《关键接口抽象框架.md》v2.0
"""
from enum import Enum

# ==============================================================================
# 生命周期状态 (Engine 独占控制权)
# ==============================================================================

class LifecycleState(str, Enum):
    """生命周期状态 (Engine 独占控制权)"""
    INIT = "INIT"
    CONTEXT_BUILD = "CONTEXT_BUILD"
    PLAN_GENERATION = "PLAN_GENERATION"
    PLAN_CHECK = "PLAN_CHECK"
    EXECUTION_PREPARE = "EXECUTION_PREPARE"
    STEP_EXECUTION = "STEP_EXECUTION"
    STEP_REVIEW = "STEP_REVIEW"
    GLOBAL_REVIEW = "GLOBAL_REVIEW"
    REPLAN = "REPLAN"
    WAIT_HUMAN = "WAIT_HUMAN"
    ROLLBACK = "ROLLBACK"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ==============================================================================
# 步骤执行状态 (支持并行跟踪与自愈)
# ==============================================================================

class StepStatus(str, Enum):
    """步骤执行状态 (支持并行跟踪与自愈)"""
    PENDING = "PENDING"       # 等待执行
    RUNNING = "RUNNING"       # 并行执行中
    COMPLETED = "COMPLETED"   # 执行成功
    FAILED = "FAILED"         # 执行失败
    SKIPPED = "SKIPPED"       # 被跳过


# ==============================================================================
# 认知 Agent 角色 (匹配需求文档 5 类 Agent)
# ==============================================================================

class AgentRole(str, Enum):
    """认知 Agent 角色 (匹配需求文档 5 类 Agent)"""
    CONTEXT_BUILDER = "CONTEXT_BUILDER"
    PLANNER = "PLANNER"
    PLAN_CRITIC = "PLAN_CRITIC"
    STEP_EXECUTOR = "STEP_EXECUTOR"
    REVIEWER = "REVIEWER"


# ==============================================================================
# 风险等级 (用于策略治理)
# ==============================================================================

class RiskLevel(str, Enum):
    """风险等级 (用于策略治理)"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ==============================================================================
# 工具权限等级 (用于权限系统)
# ==============================================================================

class PermissionLevel(str, Enum):
    """工具权限等级 (用于权限系统)"""
    PUBLIC = "PUBLIC"         # 所有 Agent 可调用
    INTERNAL = "INTERNAL"     # 仅受信任 Agent 可调用
    ADMIN = "ADMIN"           # 需人工确认或最高权限


# ==============================================================================
# 可观测性事件类型 (支持完整 Trace 回放)
# ==============================================================================

class TraceEventType(str, Enum):
    """可观测性事件类型 (支持完整 Trace 回放)"""
    STATE_TRANSITION = "STATE_TRANSITION"
    AGENT_DECISION = "AGENT_DECISION"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_END = "TOOL_CALL_END"
    POLICY_EVALUATION = "POLICY_EVALUATION"
    SNAPSHOT_CREATED = "SNAPSHOT_CREATED"
    SNAPSHOT_RESTORED = "SNAPSHOT_RESTORED"
    HUMAN_INTERACTION = "HUMAN_INTERACTION"
    ERROR_OCCURRED = "ERROR_OCCURRED"


# ==============================================================================
# 记忆范围 (支持长期记忆与上下文隔离)
# ==============================================================================

class MemoryScope(str, Enum):
    """记忆范围 (支持长期记忆与上下文隔离)"""
    EPHEMERAL = "EPHEMERAL"   # 当前步骤临时变量 (Step Context)
    SESSION = "SESSION"       # 当前任务执行上下文 (Execution Context)
    GLOBAL = "GLOBAL"         # 跨任务长期记忆 (Long-term Memory)