# 编码约定指南 (Coding Conventions)

本指南规范 EHS 智能安保决策中台项目的代码风格，确保代码一致性和可维护性。

---

## 目录

1. [Python 代码风格](#python-代码风格)
2. [类型注解](#类型注解)
3. [错误处理](#错误处理)
4. [测试约定](#测试约定)
5. [提交信息](#提交信息)
6. [前端代码风格 (React)](#前端代码风格 react)

---

## Python 代码风格

### 基本原则

- 遵循 [PEP 8](https://pep8.org/) Python 代码风格指南
- 使用 4 空格缩进（禁止使用 Tab）
- 行宽限制为 100 字符

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量 | snake_case | `user_name`, `max_retries` |
| 函数 | snake_case | `get_user_data()`, `calculate_score()` |
| 类 | PascalCase | `UserProfile`, `DataProcessor` |
| 常量 | UPPER_CASE | `MAX_CONNECTIONS`, `API_VERSION` |
| 私有属性 | 前缀下划线 | `_internal_cache`, `_helper_method()` |
| 模块级私有 | 双前缀下划线 | `__internal_only()` |

### 代码示例

```python
# ✅ 正确示例
class DataProcessor:
    """处理数据的核心类"""
    
    MAX_BATCH_SIZE = 1000
    
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._cache = {}
    
    def process_batch(self, items: list) -> list:
        """处理批量数据"""
        return [self._process_item(item) for item in items]


# ❌ 错误示例
class data_processor:  # 类名应使用 PascalCase
    max_batch_size = 1000  # 常量应使用 UPPER_CASE
    
    def ProcessBatch(self, Items):  # 函数和参数应使用 snake_case
        pass
```

---

## 类型注解

### 基本要求

- 所有公共函数必须有类型注解
- 所有模块级变量应有类型注解
- 复杂类型使用 `typing` 模块

### Docstring 格式

使用 Google 风格的 docstring：

```python
def function_name(arg1: type1, arg2: type2) -> ReturnType:
    """简短描述函数功能。

    详细描述（可选），可以多行说明函数的行为和用途。

    Args:
        arg1: 参数 1 的描述
        arg2: 参数 2 的描述

    Returns:
        返回值的描述

    Raises:
        ValueError: 当参数无效时
        ConnectionError: 当连接失败时

    Example:
        >>> result = function_name("value1", 42)
        >>> print(result)
        expected_output
    """
    pass
```

### 代码示例

```python
from typing import Optional, List, Dict, Any, Union


def get_user_by_id(
    user_id: int,
    include_profile: bool = True
) -> Optional[Dict[str, Any]]:
    """根据用户 ID 获取用户信息。

    Args:
        user_id: 用户的唯一标识符
        include_profile: 是否包含用户档案信息，默认为 True

    Returns:
        包含用户信息的字典，如果用户不存在则返回 None

    Example:
        >>> user = get_user_by_id(123)
        >>> if user:
        ...     print(user["name"])
    """
    pass


def calculate_statistics(
    values: List[float]
) -> Dict[str, float]:
    """计算统计指标。

    Args:
        values: 数值列表

    Returns:
        包含 mean、median、std 的字典
    """
    pass


def parse_value(value: Union[str, int, float]) -> Any:
    """解析不同类型的值。

    Args:
        value: 待解析的值，可以是字符串、整数或浮点数

    Returns:
        解析后的值
    """
    pass
```

---

## 错误处理

### 基本原则

- 使用具体的异常类型，避免裸 `except:`
- 在边界层（API、文件 I/O、网络）捕获异常
- 在核心逻辑层抛出异常
- 所有异常必须记录日志

### try-except 模式

```python
import logging

logger = logging.getLogger(__name__)


def load_user_data(user_id: int) -> Dict[str, Any]:
    """加载用户数据。

    Args:
        user_id: 用户 ID

    Returns:
        用户数据字典

    Raises:
        UserNotFoundError: 当用户不存在时
        DataCorruptionError: 当数据损坏时
    """
    try:
        return _read_from_database(user_id)
    except UserNotFoundError:
        # 预期异常，重新抛出
        raise
    except DatabaseConnectionError as e:
        # 记录异常并转换为业务异常
        logger.error(f"数据库连接失败，user_id={user_id}", exc_info=True)
        raise ServiceUnavailableError("暂时无法访问用户数据") from e
    except Exception as e:
        # 未知异常，记录完整堆栈
        logger.exception(f"加载用户数据时发生未知错误，user_id={user_id}")
        raise DataCorruptionError("用户数据格式异常") from e
```

### 自定义异常

```python
class EHSError(Exception):
    """EHS 系统基础异常类"""
    pass


class UserNotFoundError(EHSError):
    """用户不存在"""
    pass


class DataValidationError(EHSError):
    """数据验证失败"""
    pass


class ServiceUnavailableError(EHSError):
    """服务暂时不可用"""
    pass


# 使用示例
def validate_input(data: Dict[str, Any]) -> None:
    """验证输入数据。

    Args:
        data: 待验证的数据字典

    Raises:
        DataValidationError: 当数据验证失败时
    """
    if not data:
        raise DataValidationError("输入数据不能为空")
    
    if "user_id" not in data:
        raise DataValidationError("缺少必需字段：user_id")
```

### 日志记录

```python
import logging

logger = logging.getLogger(__name__)


def process_request(request_id: str, payload: Dict[str, Any]) -> bool:
    """处理请求。

    Args:
        request_id: 请求 ID
        payload: 请求负载

    Returns:
        处理是否成功
    """
    logger.info(f"开始处理请求，request_id={request_id}")
    
    try:
        result = _execute(payload)
        logger.info(f"请求处理成功，request_id={request_id}")
        return True
    except Exception as e:
        logger.error(
            f"请求处理失败，request_id={request_id}, error={str(e)}",
            exc_info=True
        )
        return False
```

---

## 测试约定

### 测试框架

- 使用 [pytest](https://docs.pytest.org/) 作为测试框架
- 使用 `pytest-cov` 进行覆盖率统计
- 使用 `pytest-asyncio` 测试异步代码

### 测试文件路径

```
project/
├── src/
│   └── module/
│       ├── __init__.py
│       └── processor.py
└── tests/
    ├── __init__.py
    └── module/
        ├── __init__.py
        └── test_processor.py
```

### 测试命名规范

```python
# 测试类命名：Test<模块名>
class TestProcessor:
    """Processor 模块的测试"""

    # 测试方法命名：test_<被测函数>_<场景>_<预期结果>
    def test_process_batch_empty_list_returns_empty(self):
        """测试空列表输入返回空列表"""
        processor = Processor()
        result = processor.process_batch([])
        assert result == []

    def test_process_batch_invalid_type_raises_error(self):
        """测试无效类型输入抛出异常"""
        processor = Processor()
        with pytest.raises(TypeError):
            processor.process_batch(None)

    def test_process_batch_logs_on_failure(self, caplog):
        """测试处理失败时记录日志"""
        processor = Processor()
        with caplog.at_level(logging.ERROR):
            processor.process_batch([INVALID_ITEM])
        assert "处理失败" in caplog.text
```

### 测试覆盖率要求

```bash
# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# 覆盖率要求：
# - 核心模块：>= 90%
# - 业务模块：>= 80%
# - 集成测试：覆盖所有外部接口
```

### Fixture 使用示例

```python
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_database():
    """模拟数据库连接"""
    db = Mock()
    db.query.return_value = [{"id": 1, "name": "test"}]
    return db


@pytest.fixture
def sample_user_data():
    """示例用户数据"""
    return {
        "id": 1,
        "name": "测试用户",
        "email": "test@example.com"
    }


@pytest.mark.asyncio
async def test_async_operation(mock_database, sample_user_data):
    """测试异步操作"""
    with patch("module.database", mock_database):
        result = await async_fetch_user(1)
        assert result["id"] == sample_user_data["id"]
```

---

## 提交信息

### 提交格式

```
<type>: <subject>

[可选的正文]

[可选的脚注]

Co-Authored-By: Name <email>
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加用户认证模块` |
| `fix` | Bug 修复 | `fix: 修复数据解析空指针异常` |
| `refactor` | 代码重构（不影响功能） | `refactor: 提取共享验证逻辑` |
| `docs` | 文档更新 | `docs: 添加 API 使用说明` |
| `test` | 测试相关 | `test: 添加边界条件测试用例` |
| `chore` | 构建/工具/配置 | `chore: 更新 pytest 配置` |
| `perf` | 性能优化 | `perf: 优化数据库查询索引` |
| `style` | 代码格式（不影响功能） | `style: 格式化代码符合 PEP 8` |

### 提交示例

```bash
# 单次提交
git commit -m "feat: 添加 GraphRAG 知识图谱模块

- 实现实体抽取和关系构建
- 支持 Neo4j 存储和查询
- 添加单元测试覆盖"

# 包含 Co-Authored-By
git commit -m "$(cat <<'EOF'
feat: 实现 Multi-Agent 编排引擎

- 基于 LangGraph 构建状态机
- 支持 Agent 动态切换
- 添加对话历史管理

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## 前端代码风格 (React)

### TypeScript

- 所有组件必须使用 TypeScript
- 禁止使用 `any` 类型，使用 `unknown` 或具体类型
- 使用接口定义 props 和状态

```typescript
// ✅ 正确示例
interface UserProfile {
  id: number;
  name: string;
  email: string;
}

interface UserCardProps {
  user: UserProfile;
  onEdit?: (user: UserProfile) => void;
  className?: string;
}

// ❌ 错误示例
function UserCard({ user }: any) {  // 禁止使用 any
  return <div>{user.name}</div>;
}
```

### 函数组件 + Hooks

```typescript
import React, { useState, useEffect, useCallback, useMemo } from "react";


interface CounterProps {
  initialValue: number;
  step?: number;
}

/**
 * 计数器组件
 */
export const Counter: React.FC<CounterProps> = ({
  initialValue,
  step = 1
}) => {
  // State hooks
  const [count, setCount] = useState<number>(initialValue);
  const [isRunning, setIsRunning] = useState<boolean>(false);

  // 使用 useCallback 缓存回调函数
  const handleIncrement = useCallback(() => {
    setCount(prev => prev + step);
  }, [step]);

  // 使用 useMemo 缓存计算结果
  const doubled = useMemo(() => count * 2, [count]);

  // Effect hooks
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;
    
    if (isRunning) {
      timer = setInterval(() => {
        setCount(prev => prev + step);
      }, 1000);
    }

    return () => {
      if (timer) {
        clearInterval(timer);
      }
    };
  }, [isRunning, step]);

  return (
    <div className="counter">
      <p>Count: {count}</p>
      <p>Doubled: {doubled}</p>
      <button onClick={handleIncrement}>+{step}</button>
      <button onClick={() => setIsRunning(!isRunning)}>
        {isRunning ? "Stop" : "Start"}
      </button>
    </div>
  );
};
```

### 组件命名规范

```typescript
// 组件文件命名：PascalCase + .tsx
// ✅ 正确
UserProfile.tsx
DataChart.tsx
SidebarMenu.tsx

// ❌ 错误
userProfile.tsx
data_chart.tsx

// 组件导出：使用具名导出
export const UserProfile: React.FC<UserProfileProps> = (props) => {
  // ...
};

// 或者默认导出单个组件
const UserProfile: React.FC<UserProfileProps> = (props) => {
  // ...
};
export default UserProfile;
```

### Props 类型定义

```typescript
// 使用 interface 定义 props
interface ButtonProps {
  // 必需属性
  label: string;
  onClick: () => void;
  
  // 可选属性
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  className?: string;
  
  // 子元素
  children?: React.ReactNode;
}

// 使用类型联合
type InputType = "text" | "number" | "email" | "password";

interface InputProps {
  type: InputType;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}
```

### TailwindCSS 样式

```typescript
// 使用 className 组合样式
interface CardProps {
  title: string;
  children: React.ReactNode;
  variant?: "default" | "elevated";
}

export const Card: React.FC<CardProps> = ({
  title,
  children,
  variant = "default"
}) => {
  return (
    <div
      className={`
        rounded-lg border p-6
        ${variant === "elevated" ? "shadow-lg" : "shadow"}
        bg-white border-gray-200
      `}
    >
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {title}
      </h3>
      <div className="text-gray-600">
        {children}
      </div>
    </div>
  );
};

// 复杂样式可以使用 classnames 库
import classNames from "classnames";

const buttonClasses = classNames(
  "px-4 py-2 rounded font-medium transition-colors",
  {
    "bg-blue-500 text-white hover:bg-blue-600": variant === "primary",
    "bg-gray-200 text-gray-800 hover:bg-gray-300": variant === "secondary",
    "bg-red-500 text-white hover:bg-red-600": variant === "danger",
    "opacity-50 cursor-not-allowed": disabled,
  }
);
```

### 自定义 Hooks

```typescript
import { useState, useEffect, useCallback } from "react";

/**
 * 使用示例:
 * const { data, loading, error } = useFetch<UserData>("/api/user");
 */
export function useFetch<T>(
  url: string,
  options?: RequestInit
): {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error"));
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
```

---

## 参考资源

- [PEP 8 - Python 代码风格指南](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest 官方文档](https://docs.pytest.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [React 官方文档](https://react.dev/)
- [TailwindCSS 官方文档](https://tailwindcss.com/)
