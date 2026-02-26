# 本次任务说明 (Task Specification)

## 会话编号
SESSION_003

## 本次目标
实现基础设施层 - Memory 抽象基类与本地实现

## 任务范围

### 需要实现的文件
| 文件路径 | 优先级 | 说明 |
|----------|--------|------|
| src/infrastructure/memory/base_memory.py | P0 | BaseMemory 抽象实现 |
| src/infrastructure/memory/local_memory.py | P1 | LocalMemory 具体实现 |
| tests/infrastructure/test_memory.py | P0 | 单元测试 |

### 不需要修改的文件
| 文件路径 | 原因 |
|----------|------|
| src/core/interfaces.py | 接口契约，禁止修改 |
| src/core/types.py | 枚举定义，本次无关 |
| src/core/models.py | 数据模型，本次无关 |
| src/core/protocols.py | 协议定义，本次无关 |
| src/infrastructure/tracer/* | Tracer 已完成，本次无关 |

## 输入依赖

### 需要导入的模块
```python
from src.core.interfaces import BaseMemory
from src.core.types import MemoryScope
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
```

### 需要调用的组件
| 组件 | 用途 |
|------|------|
| MemoryScope | 标准化记忆范围 |
| BaseMemory | 抽象基类接口 |

## 输出要求

### 功能要求

#### BaseMemory（抽象类已在 interfaces.py 定义）
- [ ] 无需额外实现，interfaces.py 已定义

#### LocalMemory（具体实现）
- [ ] 实现 store() 方法，支持按 scope 存储数据
- [ ] 实现 retrieve() 方法，支持按 scope 检索数据  
- [ ] 实现 search() 方法，支持语义搜索
- [ ] 实现 record_failure_pattern() 方法，记录失败模式
- [ ] 支持三种 MemoryScope：EPHEMERAL、SESSION、GLOBAL
- [ ] 支持数据过期时间设置

### 代码要求
- [ ] LocalMemory 必须继承 BaseMemory
- [ ] 必须通过 mypy 类型检查
- [ ] 必须包含完整的类型注解
- [ ] 必须遵守 CONTEXT_CONSTRAINTS.md 设计约束

### 测试要求
```python
# 必须覆盖的场景
- [ ] 在不同 scope 下存储和检索数据
- [ ] search() 方法能返回匹配的结果
- [ ] record_failure_pattern() 正确记录失败模式
- [ ] 数据过期机制正常工作
- [ ] 不同 scope 的数据隔离
- [ ] 存储复杂数据结构
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
- [ ] pytest 全部通过（预计 6-8 个用例）

### 功能验收
- [ ] 能在 EPHEMERAL scope 存储临时数据
- [ ] 能在 SESSION scope 存储会话数据
- [ ] 能在 GLOBAL scope 存储全局数据
- [ ] search() 返回相关结果
- [ ] record_failure_pattern() 正确记录失败模式
- [ ] 数据按 scope 隔离

### 设计约束验收
- [ ] LocalMemory 继承 BaseMemory
- [ ] 使用标准 MemoryScope 枚举
- [ ] 未修改 core/ 目录下任何文件

## 预计耗时
4-5 小时

## 风险提示

| 风险 | 应对措施 |
|------|----------|
| 内存泄漏（数据无限累积） | 实现 TTL 机制，定期清理过期数据 |
| 并发访问冲突 | 添加锁机制保护共享资源 |
| 搜索性能问题 | 本次使用简单匹配，后续可扩展为向量搜索 |

## 下一步计划

### 本次任务完成后
1. 更新 SESSION_HANDOVER.md（记录 SESSION_003 完成情况）
2. 创建 SESSION_004 的 TASK_SPECIFICATION.md

### 下一个任务（SESSION_004）
| 任务 | 文件 | 优先级 |
|------|------|--------|
| Snapshot 抽象基类 | src/infrastructure/snapshot/base_snapshot.py | P0 |
| Snapshot JSON 实现 | src/infrastructure/snapshot/json_snapshot.py | P1 |
| Snapshot 单元测试 | tests/infrastructure/test_snapshot.py | P0 |

### 后续任务路线
```
SESSION_003: Memory ✅ (本次)
    ↓
SESSION_004: Snapshot
    ↓
SESSION_005: ExecutionEngine 骨架
    ↓
SESSION_006: 状态机规则
    ↓
...（参考PROJECT_PLAN.md 完整执行计划）
```

## 会话结束指令

完成本次任务后，请执行：
1. 运行所有验收命令确保通过
2. 生成 SESSION_003 的 SESSION_HANDOVER.md 内容
3. 草拟 SESSION_004 的 TASK_SPECIFICATION.md 框架
4. 更新 docs/CONTEXT.md 中的"当前进度"字段
