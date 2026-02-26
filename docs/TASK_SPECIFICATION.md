# 本次任务说明 (Task Specification)

## 会话编号
SESSION_002

## 本次目标
实现基础设施层 - Tracer 追踪系统

## 任务范围

### 需要实现的文件
| 文件路径 | 优先级 | 说明 |
|----------|--------|------|
| src/infrastructure/tracer/base_tracer.py | P0 | BaseTracer 抽象实现 |
| src/infrastructure/tracer/console_tracer.py | P0 | ConsoleTracer 具体实现 |
| src/infrastructure/tracer/__init__.py | P0 | 模块导出 |
| tests/infrastructure/test_tracer.py | P0 | 单元测试 |

### 不需要修改的文件
| 文件路径 | 原因 |
|----------|------|
| src/core/interfaces.py | 接口契约，禁止修改 |
| src/core/types.py | 枚举定义，本次无关 |
| src/core/models.py | 数据模型，本次无关 |
| src/core/protocols.py | 协议定义，本次无关 |

## 输入依赖

### 需要导入的模块
```python
from src.core.interfaces import BaseTracer
from src.core.types import TraceEventType
from src.core.models import GlobalState
from datetime import datetime
from typing import List, Dict, Any
import json
import os
```

### 需要调用的组件
| 组件 | 用途 |
|------|------|
| TraceEventType | 标准化事件类型 |
| GlobalState.trace_id | 追踪 ID 来源 |

## 输出要求

### 功能要求

#### BaseTracer（抽象类已在 interfaces.py 定义）
- [ ] 无需额外实现，interfaces.py 已定义

#### ConsoleTracer（具体实现）
- [ ] 实现 record_event() 方法，打印到控制台
- [ ] 实现 get_trace() 方法，返回事件列表
- [ ] 事件必须包含：timestamp, event_type, payload, trace_id
- [ ] 支持按 trace_id 过滤事件
- [ ] 事件按时间顺序存储

### 代码要求
- [ ] ConsoleTracer 必须继承 BaseTracer
- [ ] 必须通过 mypy 类型检查
- [ ] 必须包含完整的类型注解
- [ ] 必须遵守 CONTEXT_CONSTRAINTS.md 设计约束

### 测试要求
```python
# 必须覆盖的场景
- [ ] 记录事件后能在 get_trace 中查询到
- [ ] 不同 trace_id 的事件相互隔离
- [ ] 事件按时间顺序返回
- [ ] 所有 TraceEventType 都能正常记录
- [ ] payload 支持任意 Dict 数据
```

## 验收标准

### 代码验收
```bash
# 类型检查
mypy src/infrastructure/tracer/

# 单元测试
pytest tests/infrastructure/test_tracer.py -v
```

**通过标准**：
- [ ] mypy 无错误
- [ ] pytest 全部通过（预计 5-8 个用例）

### 功能验收
- [ ] 能记录 STATE_TRANSITION 事件
- [ ] 能记录 AGENT_DECISION 事件
- [ ] 能记录 TOOL_CALL_START/END 事件
- [ ] get_trace(trace_id) 返回正确的事件列表
- [ ] 事件包含完整的时间戳

### 设计约束验收
- [ ] ConsoleTracer 继承 BaseTracer
- [ ] 使用标准 TraceEventType 枚举
- [ ] 未修改 core/ 目录下任何文件

## 预计耗时
3-4 小时

## 风险提示

| 风险 | 应对措施 |
|------|----------|
| 时间戳格式不统一 | 使用 datetime.isoformat() 标准化 |
| 内存泄漏（事件无限累积） | 后续添加事件清理机制，本次暂不实现 |
| 并发写入冲突 | 本次单线程实现，后续添加锁 |

## 下一步计划

### 本次任务完成后
1. 更新 SESSION_HANDOVER.md（记录 SESSION_002 完成情况）
2. 创建 SESSION_003 的 TASK_SPECIFICATION.md

### 下一个任务（SESSION_003）
| 任务 | 文件 | 优先级 |
|------|------|--------|
| Memory 抽象基类 | src/infrastructure/memory/base_memory.py | P0 |
| Memory 本地实现 | src/infrastructure/memory/local_memory.py | P1 |
| Memory 单元测试 | tests/infrastructure/test_memory.py | P0 |

### 后续任务路线
```
SESSION_002: Tracer ✅ (本次)
    ↓
SESSION_003: Memory
    ↓
SESSION_004: Snapshot
    ↓
SESSION_005: ExecutionEngine 骨架
    ↓
SESSION_006: 状态机规则
    ↓
...（参考完整执行计划）
```

## 会话结束指令

完成本次任务后，请执行：
1. 运行所有验收命令确保通过
2. 生成 SESSION_002 的 SESSION_HANDOVER.md 内容
3. 草拟 SESSION_003 的 TASK_SPECIFICATION.md 框架
4. 更新 docs/CONTEXT.md 中的"当前进度"字段