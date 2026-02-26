"""
错误与决策协议
来源：《关键接口抽象框架.md》v2.0
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

from .types import AgentRole, RiskLevel


# ==============================================================================
# 结构化错误 (禁止抛裸异常跨层传播)
# ==============================================================================

class StructuredError(BaseModel):
    """
    结构化错误 (禁止抛裸异常跨层传播)
    支持自愈逻辑判断
    """
    code: str
    message: str
    severity: Literal["INFO", "WARNING", "CRITICAL"]
    retryable: bool = False           # 指示引擎是否应自动重试
    suggested_action: Optional[Literal["RETRY", "REPLAN", "ROLLBACK", "HALT"]] = None
    metadata: Dict[str, Any] = {}


# ==============================================================================
# 策略决策 (包含风险控制与权限判断)
# ==============================================================================

class PolicyDecision(BaseModel):
    """
    策略决策 (包含风险控制与权限判断)
    """
    allow: bool
    next_state: Optional[str] = None  # 使用字符串避免循环导入
    reason: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    require_human_approval: bool = False  # 强制人工介入标记
    blocked_tools: List[str] = []         # 因权限被拦截的工具


# ==============================================================================
# Agent 输出协议 (认知层统一返回格式)
# ==============================================================================

class AgentOutput(BaseModel):
    """Agent 认知任务输出"""
    success: bool
    data: Optional[Any] = None
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    errors: List[StructuredError] = []
    role: AgentRole  # 明确输出所属 Agent 角色


# ==============================================================================
# 工具执行结果 (工具层统一返回格式)
# ==============================================================================

class ToolExecutionResult(BaseModel):
    """工具执行结果"""
    success: bool
    output: Optional[Any] = None
    error: Optional[StructuredError] = None
    latency_ms: Optional[int] = None
    side_effect_occurred: bool = False  # 记录是否产生副作用


# ==============================================================================
# 引擎最终结果 (系统对外返回格式)
# ==============================================================================

class EngineResult(BaseModel):
    """引擎执行最终结果"""
    success: bool
    final_output: Optional[Any]
    trace_id: str
    errors: List[StructuredError] = []
    total_latency_ms: Optional[int] = None