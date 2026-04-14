# EHS Admin Console - 告警管理前端

EHS 智能安保决策中台的管理后台前端项目，基于 React 18 + TypeScript + Ant Design 5.x + TailwindCSS。

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| React | 18.2.0 | UI 框架 |
| TypeScript | 5.3.3 | 类型系统 |
| Ant Design | 5.15.0 | UI 组件库 |
| TailwindCSS | 3.4.1 | 原子化 CSS |
| Vite | 5.1.0 | 构建工具 |
| Axios | 1.6.7 | HTTP 客户端 |

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
npm run format
```

## 项目结构

```
admin-console/
├── src/
│   ├── pages/
│   │   └── alert/
│   │       ├── SimulateAlert.tsx    # 模拟告警上报组件
│   │       ├── AlertList.tsx        # 告警列表组件
│   │       └── index.ts             # 模块导出
│   ├── types/
│   │   └── alert.ts                 # 类型定义
│   ├── components/                   # 公共组件
│   ├── hooks/                        # 自定义 Hooks
│   ├── App.tsx                       # 应用入口
│   ├── main.tsx                      # React 入口
│   └── index.css                     # 全局样式
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## 核心组件

### SimulateAlert - 模拟告警上报

**功能特性：**
- 预设场景按钮（火灾、气体泄漏、温度异常、入侵检测）
- 告警类型下拉选择
- 告警内容文本域
- 提交按钮（带 loading 状态）
- 成功后 Toast 提示

**UI 状态：**
- Loading 状态 - 提交按钮显示 loading spinner
- Error 状态 - Toast 错误消息 + 重试能力

### AlertList - 告警列表

**功能特性：**
- 告警列表表格（ID、类型、内容、级别、位置、时间、状态、关联预案）
- 使用 Mock 数据（阶段 1 不连接真实 API）
- 支持新增告警后刷新列表

**UI 状态：**
- Loading 状态 - 表格显示 loading spinner
- Empty 状态 - 空列表时显示"暂无告警"引导
- Error 状态 - 显示错误提示 + 重试按钮

## 类型定义

```typescript
// 告警类型
enum AlertType {
  FIRE = 'fire',
  GAS_LEAK = 'gas_leak',
  TEMPERATURE_ABNORMAL = 'temperature_abnormal',
  INTRUSION = 'intrusion',
}

// 告警级别
enum AlertLevel {
  LOW = 1,
  MEDIUM = 2,
  HIGH = 3,
  CRITICAL = 4,
}

// 告警状态
enum AlertStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
}
```

## 下一阶段

- [ ] 连接真实 REST API
- [ ] 添加告警详情页面
- [ ] 添加告警筛选功能
- [ ] 添加告警统计图表
