# EHS E2E 测试指南

本目录包含 EHS 智能安保决策中台的端到端 (E2E) 测试。

## 测试文件结构

```
tests/e2e/
├── playwright.config.ts      # Playwright 配置
├── test_dashboard.spec.ts    # Dashboard 页面测试 (8 个场景)
├── test_alerts.spec.ts       # 告警管理测试 (8 个场景)
├── test_plans.spec.ts        # 预案管理测试 (10 个场景)
└── README.md                 # 本文件
```

## 核心测试场景（10+）

### Dashboard 测试 (test_dashboard.spec.ts) - 8 个场景

| 场景 | 描述 | 状态 |
|------|------|------|
| 1 | Dashboard 页面加载 | ✅ |
| 2 | 统计卡片显示 | ✅ |
| 3 | 告警列表渲染 | ✅ |
| 4 | 健康检查指示器 | ✅ |
| 5 | Toast 通知功能 | ✅ |
| 6 | 桌面端响应式布局 | ✅ |
| 7 | 移动端响应式布局 | ✅ |
| 8 | 骨架屏加载状态 | ✅ |

### 告警管理测试 (test_alerts.spec.ts) - 8 个场景

| 场景 | 描述 | 状态 |
|------|------|------|
| 1 | 告警列表页面加载 | ✅ |
| 2 | 告警状态标签显示 | ✅ |
| 3 | 风险等级标签显示 | ✅ |
| 4 | 空状态显示 | ✅ |
| 5 | 告警时间显示 | ✅ |
| 6 | 告警类型显示 | ✅ |
| 7 | 告警位置显示 | ✅ |
| 8 | 列表滚动加载 | ✅ |

### 预案管理测试 (test_plans.spec.ts) - 10 个场景

| 场景 | 描述 | 状态 |
|------|------|------|
| 1 | 预案检索入口 | ✅ |
| 2 | 预案检索功能 | ✅ |
| 3 | 空查询处理 | ✅ |
| 4 | 预案详情展示 | ✅ |
| 5 | API 错误处理 | ✅ |
| 6 | 加载状态 | ✅ |
| 7 | 风险等级过滤 | ✅ |
| 8 | 详情展开交互 | ✅ |
| 9 | 搜索历史/建议 | ✅ |
| 10 | 搜索清除功能 | ✅ |

**总计：26 个 E2E 测试场景**

## 运行测试

### 前置条件

1. 确保前端开发服务器运行：
```bash
npm run dev
```

2. 确保后端服务运行（可选，用于真实 API 测试）：
```bash
npm run dev:backend
```

### 运行所有测试

```bash
# 使用默认配置（headless 模式）
npm run test:e2e
```

### 有头模式（可视化调试）

```bash
# 在浏览器中运行测试
npm run test:e2e:headed
```

### UI 模式（交互调试）

```bash
# 打开 Playwright UI
npm run test:e2e:ui
```

### 运行特定测试文件

```bash
# 运行 Dashboard 测试
npx playwright test tests/e2e/test_dashboard.spec.ts

# 运行告警测试
npx playwright test tests/e2e/test_alerts.spec.ts

# 运行预案测试
npx playwright test tests/e2e/test_plans.spec.ts
```

### 运行特定测试用例

```bash
# 按名称过滤
npx playwright test --grep "should load dashboard"

# 按标签过滤
npx playwright test --grep @smoke
```

## 环境配置

### 环境变量

| 变量 | 描述 | 默认值 |
|------|------|--------|
| `E2E_BASE_URL` | E2E 测试基础 URL | `http://localhost:5173` |
| `CI` | CI 环境标志 | `false` |

### 示例

```bash
# 使用自定义 URL
E2E_BASE_URL=http://localhost:3000 npm run test:e2e

# CI 模式
CI=true npm run test:e2e
```

## 测试报告

测试完成后，HTML 报告会生成在 `playwright-report` 目录：

```bash
# 查看 HTML 报告
npx playwright show-report
```

## 追踪调试

测试失败时会自动保存追踪文件，可在 UI 模式中查看：

```bash
npx playwright test --ui
```

## 多浏览器测试

配置支持以下浏览器：

- Chromium (默认)
- Firefox
- WebKit (Safari)
- Mobile (Pixel 5)

运行特定浏览器测试：

```bash
# 仅运行 Chromium
npx playwright test --project=chromium

# 仅运行 Firefox
npx playwright test --project=firefox

# 运行所有浏览器
npx playwright test
```

## 故障排除

### 常见问题

**测试超时**
- 增加 `timeout` 配置
- 检查前端服务器是否运行
- 检查网络连接

**元素未找到**
- 使用 `page.waitForTimeout()` 等待加载
- 使用 `expect().toBeVisible({ timeout })` 设置合理超时

**Mock 数据不生效**
- 检查 route 匹配模式
- 确保 `page.route()` 在 `page.goto()` 之前调用

## 最佳实践

1. **使用有意义的测试名称**: 描述测试场景和预期结果
2. **保持测试独立**: 每个测试应该是独立的，不依赖其他测试
3. **使用 Page Object 模式**: 复杂场景考虑封装 Page Object
4. **合理设置超时**: 根据网络条件和加载时间设置
5. **善用 Mock**: 对于不稳定的外部依赖使用 Mock

## 参考资料

- [Playwright 官方文档](https://playwright.dev)
- [Playwright Test](https://playwright.dev/docs/test-intro)
- [Test Assertions](https://playwright.dev/docs/test-assertions)
