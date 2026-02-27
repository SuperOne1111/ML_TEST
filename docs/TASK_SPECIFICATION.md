# 本次任务说明 (Task Specification)

## 会话编号
SESSION_004

## 本次目标
实现基础设施层 - Snapshot 抽象基类与JSON实现

## 任务范围

### 需要实现的文件
| 文件路径 | 优先级 | 说明 |
|----------|--------|------|
| src/infrastructure/snapshot/base_snapshot.py | P0 | BaseSnapshot 抽象实现 |
| src/infrastructure/snapshot/json_snapshot.py | P1 | JsonSnapshot 具体实现 |
| tests/infrastructure/test_snapshot.py | P0 | 单元测试 |

### 不需要修改的文件
| 文件路径 | 原因 |
|----------|------|
| src/core/interfaces.py | 接口契约，禁止修改 |
| src/core/types.py | 枚举定义，本次无关 |
| src/core/models.py | 数据模型，本次无关 |
| src/core/protocols.py | 协议定义，本次无关 |
| src/infrastructure/tracer/* | Tracer 已完成，本次无关 |
| src/infrastructure/memory/* | Memory 已完成，本次无关 |

## 输入依赖

### 需要导入的模块
```python
from src.core.interfaces import BaseSnapshot
from src.core.models import AgentState, Task
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
```

### 需要调用的组件
| 组件 | 用途 |
|------|------|
| AgentState | 标准化智能体状态模型 |
| Task | 标准化任务模型 |
| BaseSnapshot | 抽象基类接口 |

## 输出要求

### 功能要求

#### BaseSnapshot（抽象类已在 interfaces.py 定义）
- [ ] 无需额外实现，interfaces.py 已定义

#### JsonSnapshot（具体实现）
- [ ] 实现 save() 方法，支持序列化保存状态
- [ ] 实现 load() 方法，支持反序列化解析状态  
- [ ] 实现 list_snapshots() 方法，支持查询快照列表
- [ ] 实现 delete() 方法，支持删除指定快照
- [ ] 支持多种数据格式：AgentState、Task、自定义对象
- [ ] 支持快照过期时间设置

### 代码要求
- [ ] JsonSnapshot 必须继承 BaseSnapshot
- [ ] 必须通过 mypy 类型检查
- [ ] 必须包含完整的类型注解
- [ ] 必须遵守 CONTEXT_CONSTRAINTS.md 设计约束

### 测试要求
```python
# 必须覆盖的场景
- [ ] save() 和 load() 方法能正确序列化和反序列化数据
- [ ] list_snapshots() 方法能返回正确的快照列表
- [ ] delete() 方法能正确删除指定快照
- [ ] 快照过期机制正常工作
- [ ] 支持多种数据格式（AgentState, Task等）
- [ ] 数据持久化功能
```

## 验收标准

### 代码验收
```bash
# 类型检查
mypy src/infrastructure/snapshot/

# 单元测试
pytest tests/infrastructure/test_snapshot.py -v
```

**通过标准**：
- [ ] mypy 无错误
- [ ] pytest 全部通过（预计 6-8 个用例）

### 功能验收
- [ ] save() 能正确序列化并保存 AgentState
- [ ] load() 能正确反序列化并加载快照
- [ ] list_snapshots() 返回所有可用快照
- [ ] delete() 正确删除指定快照
- [ ] 数据按格式正确持久化
- [ ] 快照过期机制正常工作

### 设计约束验收
- [ ] JsonSnapshot 继承 BaseSnapshot
- [ ] 使用标准 AgentState 和 Task 模型
- [ ] 未修改 core/ 目录下任何文件

## 预计耗时
4-5 小时

## 风险提示

| 风险 | 应对措施 |
|------|----------|
| 存储空间无限增长 | 实现 TTL 机制，定期清理过期快照 |
| 并发写入冲突 | 添加锁机制保护共享资源 |
| 序列化性能问题 | 优化序列化算法，支持增量快照 |

## 下一步计划

### 本次任务完成后
1. 更新 SESSION_HANDOVER.md（记录 SESSION_003 完成情况）
2. 创建 下一次任务SESSION_004 的 TASK_SPECIFICATION.md

### 下一个任务（SESSION_005）
| 任务 | 文件 | 优先级 |
|------|------|--------|
| ExecutionEngine 骨架 | src/engine/base_engine.py | P0 |
| ExecutionEngine 实现 | src/engine/default_engine.py | P1 |
| ExecutionEngine 单元测试 | tests/engine/test_engine.py | P0 |

### 后续任务路线
```
SESSION_004: Snapshot ✅ (本次)
    ↓
SESSION_005: ExecutionEngine 骨架(下一次任务）
    ↓
SESSION_006: 状态机规则
    ↓
SESSION_007: Policy 引擎
    ↓
...（参考PROJECT_PLAN.md 完整执行计划）
```


