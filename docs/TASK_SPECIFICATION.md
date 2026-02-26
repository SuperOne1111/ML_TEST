# 本次任务说明 (Task Specification)

## 会话编号
SESSION_003

## 本次目标
实现基础设施层 - Memory 记忆系统

## 任务范围

### 需要实现的文件
| 文件路径 | 优先级 | 说明 |
|----------|--------|------|
| src/infrastructure/memory/base_memory.py | P0 | BaseMemory 抽象实现 |
| src/infrastructure/memory/local_memory.py | P1 | LocalMemory 具体实现 |
| src/infrastructure/memory/__init__.py | P0 | 模块导出 |
| tests/infrastructure/test_memory.py | P0 | 单元测试 |

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
from src.core.interfaces import BaseMemory
from src.core.types import MemoryScope
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
```

### 需要调用的组件
| 组件 | 用途 |
|------|------|
| MemoryScope | 标准化记忆范围 |
| BaseMemory | 抽象基类 |

## 输出要求

### 功能要求

#### BaseMemory（抽象类已在 interfaces.py 定义）
- [ ] 无需额外实现，interfaces.py 已定义

#### LocalMemory（具体实现）
- [ ] 实现 store() 方法，支持三种 MemoryScope 存储
- [ ] 实现 retrieve() 方法，从指定范围检索数据
- [ ] 实现 search() 方法，支持语义搜索
- [ ] 实现 record_failure_pattern() 方法，记录失败模式
- [ ] EPHEMERAL: 临时存储，随进程销毁
- [ ] SESSION: 会话存储，任务期间持久
- [ ] GLOBAL: 全局存储，跨任务共享

### 代码要求
- [ ] LocalMemory 必须继承 BaseMemory
- [ ] 必须通过 mypy 类型检查
- [ ] 必须包含完整的类型注解
- [ ] 必须遵守 CONTEXT_CONSTRAINTS.md 设计约束

### 测试要求
```python
# 必须覆盖的场景
- [ ] 不同 MemoryScope 的数据隔离
- [ ] store/retrieve 功能验证
- [ ] search 功能验证（简单匹配）
- [ ] record_failure_pattern 功能验证
- [ ] 数据序列化/反序列化正确性
```

## 验收标准

### 代码验收
```bash
# 类型检查
mypy src/infrastructure/memory/

# 单元测试
pytest tests/infrastructure/test_memory.py -v
```

**通过标准**：
- [ ] mypy 无错误
- [ ] pytest 全部通过（预计 5-8 个用例）

### 功能验收
- [ ] 能正确区分三种 MemoryScope
- [ ] EPHEMERAL 数据随进程重启丢失
- [ ] SESSION 数据在任务期间保持
- [ ] GLOBAL 数据跨任务持久化
- [ ] search 能找到相关内容

### 设计约束验收
- [ ] LocalMemory 继承 BaseMemory
- [ ] 使用标准 MemoryScope 枚举
- [ ] 未修改 core/ 目录下任何文件

## 预计耗时
4-5 小时

## 风险提示

| 风险 | 应对措施 |
|------|----------|
| 内存泄漏（数据无限累积） | 实现简单的 TTL 机制或限制数量 |
| 并发访问冲突 | 添加基本的锁机制 |
| 序列化复杂对象失败 | 提供错误处理和降级方案 |

## 下一步计划

### 本次任务完成后
1. 更新 SESSION_HANDOVER.md（记录 SESSION_003 完成情况）
2. 创建 SESSION_004 的 TASK_SPECIFICATION.md

### 下一个任务（SESSION_004）
| 任务 | 文件 | 优先级 |
|------|------|--------|
| Snapshot 抽象基类 | src/infrastructure/snapshot/base_snapshot.py | P0 |
| Snapshot JSON 实现 | src/infrastructure/snapshot/json_snapshot.py | P0 |
| Snapshot 单元测试 | tests/infrastructure/test_snapshot.py | P0 |

### 后续任务路线
```
SESSION_002: Tracer ✅ (已完成)
    ↓
SESSION_003: Memory ✅ (本次)
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
2. 生成 SESSION_003 的 SESSION_HANDOVER.md 内容
3. 草拟 SESSION_004 的 TASK_SPECIFICATION.md 框架
4. 更新 docs/CONTEXT.md 中的"当前进度"字段