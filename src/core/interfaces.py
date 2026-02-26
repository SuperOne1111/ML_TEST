"""
核心抽象接口定义
来源：《关键接口抽象框架.md》v2.0
所有核心组件必须继承以下抽象类，实现多态与插件化。
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Literal

from .types import AgentRole, PermissionLevel, TraceEventType, MemoryScope
from .models import GlobalState, ExecutionContext, StepContext, ExecutionPlan
from .protocols import AgentOutput, ToolExecutionResult, PolicyDecision, StructuredError, EngineResult


# ==============================================================================
# 1️⃣ BaseAgent 抽象接口 (认知层)
# ==============================================================================

class BaseAgent(ABC):
    """
    认知 Agent 只负责思考与评估，不做控制。
    对应需求：Context Builder, Planner, Critic, Executor, Reviewer
    
    核心约束：
    - 只读 global_state，不可修改 state
    - 返回 AgentOutput，不直接触发状态转移
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 唯一名称"""
        pass

    @property
    @abstractmethod
    def role(self) -> AgentRole:
        """明确 Agent 角色，以便 Engine 路由逻辑"""
        pass

    @abstractmethod
    async def run(
        self,
        global_state: GlobalState,
        execution_context: ExecutionContext,
        step_context: Optional[StepContext] = None,
    ) -> AgentOutput:
        """
        执行认知任务。
        约束：只读 global_state，不可修改 state。
        """
        pass

    @abstractmethod
    def validate_output(self, output: AgentOutput) -> bool:
        """本地输出格式校验"""
        pass


# ==============================================================================
# 2️⃣ BaseTool 抽象接口 (工具运行层)
# ==============================================================================

class BaseTool(ABC):
    """
    工具层完全独立于 Agent。
    对应需求：工具注册中心声明 (name, version, schema, timeout, permission, side_effect)
    
    核心约束：
    - 不可访问 Engine, Agent, Policy
    - 必须包含 Schema 验证与异常捕获
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """工具唯一名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """工具版本号，用于兼容性管理"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """输入数据 Schema"""
        pass

    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """输出数据 Schema"""
        pass

    @property
    @abstractmethod
    def timeout_ms(self) -> int:
        """超时控制，防止挂起"""
        pass

    @property
    @abstractmethod
    def permission_level(self) -> PermissionLevel:
        """权限等级，用于 Policy 校验"""
        pass

    @property
    @abstractmethod
    def has_side_effect(self) -> bool:
        """是否产生副作用，用于回滚策略判断"""
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> ToolExecutionResult:
        """
        执行工具。
        约束：不可访问 Engine, Agent, Policy。
        必须包含 Schema 验证与异常捕获。
        """
        pass


# ==============================================================================
# 3️⃣ BaseExecutionEngine 抽象接口 (控制核心)
# ==============================================================================

class BaseExecutionEngine(ABC):
    """
    系统真正的"大脑"。
    对应需求：维护状态机、管理生命周期、控制 Agent 调用、处理异常与回滚。
    
    核心约束：
    - 唯一允许修改 GlobalState.lifecycle_state 的地方
    - 所有状态转移必须通过 transition() 方法
    """

    @abstractmethod
    async def start(self, user_input: str) -> EngineResult:
        """启动任务，初始化 GlobalState"""
        pass

    @abstractmethod
    async def transition(self) -> None:
        """
        驱动状态机流转。
        规则：Current State + Trigger Event + Guard Condition → Next State
        这是唯一允许修改 GlobalState.lifecycle_state 的地方。
        """
        pass

    @abstractmethod
    async def submit_human_feedback(self, feedback: str) -> None:
        """处理 WAIT_HUMAN 状态后的用户输入"""
        pass

    @abstractmethod
    async def rollback(self, scope: Literal["LOCAL", "GLOBAL"]) -> None:
        """
        触发回滚。
        调用 SnapshotManager 恢复 ExecutionContext。
        """
        pass

    @abstractmethod
    def register_agent(self, agent: BaseAgent) -> None:
        """注册 Agent 到引擎"""
        pass

    @abstractmethod
    def register_tool(self, tool: BaseTool) -> None:
        """注册工具到引擎"""
        pass

    @abstractmethod
    def set_policy(self, policy: 'BasePolicy') -> None:
        """注入策略引擎"""
        pass


# ==============================================================================
# 4️⃣ BasePolicy 抽象接口 (治理层)
# ==============================================================================

class BasePolicy(ABC):
    """
    策略与治理层。
    对应需求：规则引擎、风险控制模块、权限系统。
    """

    @abstractmethod
    def evaluate_transition(
        self,
        global_state: GlobalState,
        execution_context: ExecutionContext,
        agent_output: Optional[AgentOutput] = None,
        tool_result: Optional[ToolExecutionResult] = None,
    ) -> PolicyDecision:
        """
        评估状态转移是否允许。
        检查：连续失败次数、数据来源风险、工具权限、置信度阈值。
        """
        pass

    @abstractmethod
    def check_tool_permission(
        self,
        agent_role: AgentRole,
        tool: BaseTool,
    ) -> bool:
        """
        权限系统核心：控制哪些 Agent 可调用哪些工具。
        """
        pass


# ==============================================================================
# 5️⃣ BaseMemory 抽象接口 (记忆基础设施)
# ==============================================================================

class BaseMemory(ABC):
    """
    支持持续优化与长期记忆。
    对应需求：成功案例缓存、失败模式库、工具统计系统。
    """

    @abstractmethod
    async def store(self, key: str, value: Any, scope: MemoryScope) -> None:
        """
        存储记忆。
        scope 决定存储位置 (Redis/VectorDB/Local)。
        """
        pass

    @abstractmethod
    async def retrieve(self, key: str, scope: MemoryScope) -> Any:
        """检索记忆"""
        pass

    @abstractmethod
    async def search(self, query: str, scope: MemoryScope) -> List[Any]:
        """
        语义搜索，用于 Planner 参考历史成功案例。
        """
        pass

    @abstractmethod
    async def record_failure_pattern(self, pattern: Dict[str, Any]) -> None:
        """专门记录失败模式，用于风险预警"""
        pass


# ==============================================================================
# 6️⃣ BaseSnapshotManager 抽象接口 (自愈基础)
# ==============================================================================

class BaseSnapshotManager(ABC):
    """
    回滚机制核心。
    对应需求：每个关键阶段创建快照，支持多级回滚。
    """

    @abstractmethod
    async def create_snapshot(
        self,
        execution_context: ExecutionContext,
        label: str,
    ) -> str:
        """
        创建快照。
        返回 snapshot_id
        """
        pass

    @abstractmethod
    async def restore_snapshot(
        self,
        snapshot_id: str,
    ) -> ExecutionContext:
        """恢复快照"""
        pass


# ==============================================================================
# 7️⃣ BaseTracer 抽象接口 (可观测性)
# ==============================================================================

class BaseTracer(ABC):
    """
    可观测性系统。
    对应需求：状态转移日志、Agent 决策日志、工具调用日志、支持完整 Trace 回放。
    """

    @abstractmethod
    async def record_event(
        self,
        event_type: TraceEventType,
        payload: Dict[str, Any],
        trace_id: str
    ):
        """
        记录标准化事件。
        必须包含时间戳、上下文 ID、事件类型。
        """
        pass

    @abstractmethod
    async def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """支持 Trace 回放"""
        pass