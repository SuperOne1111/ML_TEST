# 本次任务说明 (Task Specification)

## 会话编号

SESSION_005

## 本次目标

实现执行引擎层 - ExecutionEngine 核心骨架（第 1/3 部分）

> **任务拆分说明**：原 SESSION_005 拆分为三次实现
> - **SESSION_005**：ExecutionEngine 核心实现（本次）
> - **SESSION_006**：StateMachine 状态规则定义
> - **SESSION_007**：BatchManager 并行管理（可选）

## 任务范围

### 需要实现的文件

| 文件路径 | 优先级 | 说明 |
|----------|--------|------|
| src/engine/execution_engine.py | P0 | ExecutionEngine 核心实现 |
| src/engine/__init__.py | P0 | 模块导出 |
| tests/unit/test_execution_engine.py | P0 | Engine 单元测试 |

### 本次暂不实现的文件

| 文件路径 | 原因 | 后续会话 |
|----------|------|----------|
| src/engine/state_machine.py | 状态规则独立实现 | SESSION_006 |
| src/engine/batch_manager.py | 并行管理可选功能 | SESSION_007 |

### 不需要修改的文件

| 文件路径 | 原因 |
|----------|------|
| src/core/interfaces.py | 接口契约，禁止修改 |
| src/core/types.py | 枚举定义，禁止修改 |
| src/core/models.py | 数据模型，禁止修改 |
| src/core/protocols.py | 协议定义，禁止修改 |
| src/infrastructure/snapshot/ | SESSION_004 已完成，本次只读 |
| src/infrastructure/tracer/ | SESSION_002 已完成，本次只读 |
| src/infrastructure/memory/ | SESSION_003 已完成，本次只读 |

## 输入依赖

### 需要导入的模块

```python
from src.core.interfaces import BaseExecutionEngine
from src.core.types import LifecycleState, TraceEventType
from src.core.models import GlobalState, ExecutionContext, StepContext
from src.core.protocols import StructuredError
from src.infrastructure.snapshot.base_snapshot import BaseSnapshotManager
from src.infrastructure.tracer.base_tracer import BaseTracer
from src.infrastructure.memory.base_memory import BaseMemory
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any, List
from copy import deepcopy
```

### 需要调用的组件

| 组件 | 用途 |
|------|------|
| BaseSnapshotManager | 状态转移前创建快照 |
| BaseTracer | 记录状态转移事件 |
| BaseMemory | 存储执行上下文 |
| LifecycleState | 13 个生命周期状态枚举 |
| GlobalState | 不可变全局状态模型 |

## 输出要求

### 功能要求

#### ExecutionEngine（核心实现）

- [ ] 实现 `__init__()` 初始化方法，注入依赖组件（snapshot_manager, tracer, memory）
- [ ] 实现 `initialize()` 方法，创建初始 GlobalState（INIT 状态）
- [ ] 实现 `transition()` 方法，**唯一**能修改 lifecycle_state 的入口
- [ ] 实现 `get_state()` 方法，返回当前 GlobalState（只读）
- [ ] 实现 `get_context()` 方法，返回当前 ExecutionContext
- [ ] 实现 `create_snapshot()` 方法，在关键状态转移前创建快照
- [ ] 实现 `restore_snapshot()` 方法，支持回滚到指定快照
- [ ] 实现 `_record_transition()` 私有方法，记录状态转移事件到 Tracer

#### 状态转移保护（本次简化实现）

- [ ] transition() 方法需要验证目标状态是合法的 LifecycleState 枚举
- [ ] transition() 方法需要验证当前状态不是终端状态（COMPLETED/FAILED）
- [ ] **详细的状态转移规则验证移到 SESSION_006 实现**

#### 快照集成

- [ ] 状态转移前自动调用 snapshot_manager.create_snapshot()
- [ ] 支持通过 snapshot_id 恢复 ExecutionContext

### 代码要求

- [ ] ExecutionEngine 必须继承 BaseExecutionEngine
- [ ] 必须通过 mypy 类型检查
- [ ] 必须包含完整的类型注解
- [ ] 必须遵守 CONTEXT_CONSTRAINTS.md 设计约束
- [ ] **严禁** Agent 或 Tool 直接调用 transition()
- [ ] **严禁** 直接修改 GlobalState 字段（必须创建新实例）
- [ ] GlobalState 必须保持 `frozen=True`

### 测试要求

```python
# 必须覆盖的场景
- [ ] Engine 初始化后状态为 INIT
- [ ] transition() 能正确改变 lifecycle_state
- [ ] 终端状态（COMPLETED/FAILED）不能继续转移
- [ ] 状态转移前自动创建快照
- [ ] 状态转移事件被 Tracer 记录
- [ ] restore_snapshot() 能恢复 ExecutionContext
- [ ] GlobalState 保持不可变（frozen）
- [ ] 非法状态枚举被拒绝
```

## 验收标准

### 代码验收

```bash
# 类型检查
mypy src/engine/

# 单元测试
pytest tests/unit/test_execution_engine.py -v
```

**通过标准**：

- [ ] mypy 无错误
- [ ] 单元测试全部通过（预计 8-10 个用例）

### 功能验收

- [ ] Engine 能正确初始化 GlobalState
- [ ] transition() 能改变 lifecycle_state
- [ ] 只有 Engine.transition() 能修改 lifecycle_state
- [ ] 快照能在状态转移前正确创建
- [ ] Tracer 能记录所有 STATE_TRANSITION 事件
- [ ] 终端状态保护生效

### 设计约束验收

- [ ] GlobalState 设置 `frozen=True`
- [ ] 状态更新通过创建新实例实现
- [ ] 所有异常转换为 StructuredError
- [ ] 所有关键路径调用 Tracer.record_event
- [ ] 未修改 core/ 目录下任何文件
- [ ] Engine 不依赖 Agent/Tool 具体实现

## 预计耗时

4-5 小时

## 风险提示

| 风险 | 应对措施 |
|------|----------|
| 状态转移规则复杂 | 本次只做基础验证，详细规则移到 SESSION_006 |
| 快照与状态同步问题 | 确保 transition() 前先 create_snapshot() |
| 并发状态修改 | 本次单线程实现，后续添加异步锁 |
| 循环依赖 | 确保 Engine 不依赖 Agent/Tool 具体实现 |
| GlobalState 可变性 | 严格使用 model_copy() 创建新实例 |

## 下一步计划

### 本次任务完成后

1. 更新 SESSION_HANDOVER.md（记录 SESSION_005 完成情况）
2. 创建 SESSION_006 的 TASK_SPECIFICATION.md（StateMachine 状态规则）

### 下一个任务（SESSION_006）

| 任务 | 文件 | 优先级 |
|------|------|--------|
| StateMachine 核心类 | src/engine/state_machine.py | P0 |
| 13 状态转移规则 | src/engine/state_machine.py | P0 |
| can_transition() 验证 | src/engine/state_machine.py | P0 |
| StateMachine 单元测试 | tests/unit/test_state_machine.py | P0 |

### 后续任务路线

```

  
SESSION_004: Snapshot ✅ (已完成)
    ↓
SESSION_005: ExecutionEngine 核心 (本次)
    ↓
SESSION_006: StateMachine 状态规则
    ↓
SESSION_007: BatchManager 并行管理
    ↓
SESSION_008: Policy 治理层
    ↓
SESSION_009: Cognitive Agent 层
    ↓
SESSION_010: Tool Runtime 层
    ↓
...（参考 PROJECT_PLAN.md 完整执行计划）
```

## 会话结束指令

完成本次任务后，请执行：

1. 运行所有验收命令确保通过
2. 生成 SESSION_005 的 SESSION_HANDOVER.md 内容
3. 草拟 SESSION_006 的 TASK_SPECIFICATION.md 框架（StateMachine 状态规则）
4. 更新 PROJECT_PLAN.md 中的阶段 2 状态标记（2.1 标记为 ✅）
