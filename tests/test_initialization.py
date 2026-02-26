"""
初始化验证测试
确保所有核心模块可正确导入
"""

def test_core_types():
    from src.core.types import LifecycleState, AgentRole
    assert LifecycleState.INIT.value == "INIT"
    assert AgentRole.PLANNER.value == "PLANNER"

def test_core_models():
    from src.core.models import GlobalState, ExecutionContext, StepContext
    from src.core.types import LifecycleState
    state = GlobalState(original_goal="test", lifecycle_state=LifecycleState.INIT, trace_id="t1")
    assert state.execution_id is not None

def test_core_protocols():
    from src.core.protocols import StructuredError, PolicyDecision, AgentOutput
    from src.core.types import AgentRole
    error = StructuredError(code="E001", message="test", severity="WARNING")
    assert error.code == "E001"

def test_core_interfaces():
    from src.core.interfaces import BaseAgent, BaseTool, BaseExecutionEngine, BasePolicy
    assert BaseAgent is not None

def test_registry():
    from src.registry.agent_registry import AgentRegistry
    from src.registry.tool_registry import ToolRegistry
    assert AgentRegistry is not None
    assert ToolRegistry is not None

if __name__ == "__main__":
    test_core_types()
    test_core_models()
    test_core_protocols()
    test_core_interfaces()
    test_registry()
    print("✅ 所有初始化验证通过！")