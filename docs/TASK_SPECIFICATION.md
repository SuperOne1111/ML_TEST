
## 本次任务说明 (Task Specification)

### 会话编号

- SESSION_005
 
## 🎯 任务目标
- 实现执行引擎层（Execution Engine Layer）的核心骨架，包括基本的状态管理、生命周期控制和核心调度逻辑。

## 📋 具体要求

### 5.1 创建 ExecutionEngine 骨架类
- **文件路径**: `src/engine/execution_engine.py`
- **实现**: `BaseExecutionEngine` 的具体实现
- **功能**:
  - 初始化时接收 `GlobalState` 和基础设施组件引用
  - 维护内部状态（如当前步骤、当前批次ID）
  - 实现 `start()` 方法启动工作流
  - 实现 `transition()` 方法驱动状态机流转
  - 实现 `rollback()` 方法触发回滚机制
  - 实现 `submit_human_feedback()` 方法处理人工反馈
  - 实现 `register_tool()` 和 `set_policy()` 注入工具和策略

### 5.2 实现基础状态机逻辑
- **文件路径**: `src/engine/state_machine.py`
- **内容**:
  - 定义 `StateMachine` 类
  - 包含硬编码的13个 `LifecycleState` 的流转规则（INIT → PLAN_CHECK → EXECUTION_PREPARE → STEP_EXECUTION → ... → COMPLETED/FAILED）
  - 每个状态转换应有明确的触发条件和守卫条件（例如，从 `STEP_EXECUTION` 到 `STEP_REVIEW` 需要当前步骤完成）
  - `transition()` 方法应能根据当前状态和事件调用正确的状态处理逻辑

### 5.3 创建批处理器
- **文件路径**: `src/engine/batch_manager.py`
- **实现**: `BatchManager` 类
- **功能**:
  - 管理并行执行的步骤批次
  - 提供添加步骤到批次的方法
  - 提供执行整个批次的方法
  - 提供获取批次执行结果的方法

### 5.4 编写单元测试
- **文件路径**: `tests/unit/test_engine.py`
- **内容**:
  - 测试 `ExecutionEngine` 的初始化
  - 测试 `start()` 方法能正确初始化流程
  - 测试 `transition()` 方法能在不同状态间正确流转（至少覆盖3-5个主要流转）
  - 测试 `rollback()` 方法能正确调用快照管理器
  - 测试 `register_tool()` 和 `set_policy()` 的注入逻辑
  - 测试 `BatchManager` 的批处理逻辑

### 5.5 更新模块导入
- **文件路径**: `src/engine/__init__.py`
- **内容**: 导出新创建的类 `ExecutionEngine`, `StateMachine`, `BatchManager`

## ⚠️ 重要限制
- **严禁** 修改 `src/core/` 目录下的任何文件。
- **必须** 继承 `src/core/interfaces.py` 中定义的 `BaseExecutionEngine` 抽象类。
- **必须** 使用在 `src/core/types.py` 中定义的 `LifecycleState` 枚举。
- **必须** 在代码中使用 `src/core/models.py` 中定义的 `GlobalState`, `ExecutionContext`, `ExecutionPlan` 等模型。
- **必须** 依赖已实现的 `src/infrastructure/snapshot/json_snapshot.py` 来实现 `rollback()` 功能。
- **必须** 通过 `mypy` 类型检查和 `pytest` 单元测试。

## 📝 补充说明
- 此次实现是引擎的最小可行版本，专注于核心状态流转和回滚机制。高级调度、动态规划等功能将在后续迭代中添加。
- `ExecutionContext` 是可快照化的状态，而 `GlobalState` 是引擎唯一可以修改其 `lifecycle_state` 的地方，这一点需要在 `transition()` 方法中严格遵守。
- 批处理机制应考虑步骤间的依赖关系，确保前置步骤完成后，依赖它的步骤才能开始。
