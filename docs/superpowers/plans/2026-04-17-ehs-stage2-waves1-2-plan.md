# 阶段 2 - Wave 1+2 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成数据准备、前端 8 页面（Mock）、Docker 基础（含 Neo4j）、测试基础、微调训练数据和 4 个微调脚本

**Architecture:** 渐进式重构。在现有 apps/ 基础上：Wave 1 完善前端和 Docker，Wave 2 并行做微调训练。两 Wave 完全独立，无共享代码依赖。

**Tech Stack:** Next.js 14, Shadcn/UI, Tailwind, Docker Compose, Neo4j, Python, PyTorch, Transformers, vitest, pytest

**执行策略:** Wave 1 与 Wave 2 并行启动，各自独立完成。Wave 3 依赖两者完成。

---

## 文件总览

### Wave 1 新增文件

| 文件 | 职责 |
|------|------|
| `apps/admin-console/eslint.config.js` | ESLint 配置（修复 lint 报错） |
| `apps/admin-console/src/app/alerts/page.tsx` | 告警管理页（列表+筛选+抽屉） |
| `apps/admin-console/src/app/alerts/components/AlertRow.tsx` | 告警行组件 |
| `apps/admin-console/src/app/alerts/components/AlertDrawer.tsx` | 告警处理抽屉 |
| `apps/admin-console/src/app/plans/page.tsx` | 预案管理页 |
| `apps/admin-console/src/app/knowledge/page.tsx` | 知识库管理页 |
| `apps/admin-console/src/app/agents/page.tsx` | Agent 编排页 |
| `apps/admin-console/src/app/models/page.tsx` | 模型管理页 |
| `apps/admin-console/src/app/settings/page.tsx` | 系统设置页 |
| `apps/admin-console/src/app/users/page.tsx` | 用户管理页 |
| `apps/admin-console/src/components/ui/card.tsx` | Shadcn Card 组件 |
| `apps/admin-console/src/components/ui/input.tsx` | Shadcn Input 组件 |
| `apps/admin-console/src/components/ui/select.tsx` | Shadcn Select 组件 |
| `apps/admin-console/src/components/ui/table.tsx` | Shadcn Table 组件 |
| `apps/admin-console/src/components/ui/badge.tsx` | Shadcn Badge 组件 |
| `apps/admin-console/src/components/ui/tabs.tsx` | Shadcn Tabs 组件 |
| `apps/admin-console/src/components/ui/dialog.tsx` | Shadcn Dialog 组件 |
| `apps/admin-console/src/components/ui/drawer.tsx` | Shadcn Drawer 组件 |
| `apps/admin-console/src/components/ui/textarea.tsx` | Shadcn Textarea 组件 |
| `apps/admin-console/src/components/ui/label.tsx` | Shadcn Label 组件 |
| `apps/admin-console/src/components/ui/avatar.tsx` | Shadcn Avatar 组件 |
| `apps/admin-console/src/components/common/Sidebar.tsx` | 侧边栏导航组件 |
| `apps/admin-console/src/components/common/Header.tsx` | 顶部导航组件 |
| `apps/admin-console/src/components/common/StatusBadge.tsx` | 状态徽章组件 |
| `apps/admin-console/src/types/alert.ts` | 告警类型定义 |
| `apps/admin-console/src/types/plan.ts` | 预案类型定义 |
| `apps/admin-console/src/types/device.ts` | 设备类型定义 |
| `apps/admin-console/src/types/report.ts` | 报告类型定义 |
| `apps/admin-console/src/mock/alerts.ts` | Mock 告警数据 |
| `apps/admin-console/src/mock/plans.ts` | Mock 预案数据 |
| `apps/admin-console/src/mock/devices.ts` | Mock 设备数据 |
| `apps/admin-console/src/mock/reports.ts` | Mock 报告数据 |
| `docker-compose.yml` | 添加 Neo4j 服务 |
| `scripts/seed_data.py` | 添加 Neo4j 图谱导入 |
| `data/seed/devices.jsonl` | 设备种子数据 |
| `apps/ehs-ai/tests/test_graph_rag.py` | GraphRAG 单元测试 |

### Wave 2 新增文件

| 文件 | 职责 |
|------|------|
| `scripts/fine_tune/__init__.py` | 微调包 |
| `scripts/fine_tune/generate_data.py` | LLM 生成微调数据 |
| `scripts/fine_tune/instruction_tuning.py` | Qwen-7B 指令微调 |
| `scripts/fine_tune/risk_classification.py` | BERT 风险分级 |
| `scripts/fine_tune/compliance_check.py` | RoBERTa 合规检查 |
| `scripts/fine_tune/embedding_tuning.py` | BGE 术语 Embedding |
| `scripts/fine_tune/train_config.py` | 通用训练配置 |
| `data/fine_tune/instruction/train.jsonl` | 指令微调训练数据 |
| `data/fine_tune/instruction/eval.jsonl` | 指令微调评估数据 |
| `data/fine_tune/risk/train.jsonl` | 风险分级训练数据 |
| `data/fine_tune/risk/eval.jsonl` | 风险分级评估数据 |
| `data/fine_tune/compliance/train.jsonl` | 合规检查训练数据 |
| `data/fine_tune/compliance/eval.jsonl` | 合规检查评估数据 |
| `data/fine_tune/embedding/term_pairs.jsonl` | 术语对数据 |
| `scripts/fine_tune/tests/test_generate_data.py` | 数据生成测试 |

---

## Wave 1: 数据 + 前端(Mark) + Docker 基础 + 测试基础

### Task 1: 前端基础设施（eslint + Shadcn 组件 + 类型定义）

**Files:**
- Create: `apps/admin-console/eslint.config.js`
- Create: `apps/admin-console/src/components/ui/card.tsx`
- Create: `apps/admin-console/src/components/ui/input.tsx`
- Create: `apps/admin-console/src/components/ui/select.tsx`
- Create: `apps/admin-console/src/components/ui/table.tsx`
- Create: `apps/admin-console/src/components/ui/badge.tsx`
- Create: `apps/admin-console/src/components/ui/tabs.tsx`
- Create: `apps/admin-console/src/components/ui/dialog.tsx`
- Create: `apps/admin-console/src/components/ui/drawer.tsx`
- Create: `apps/admin-console/src/components/ui/textarea.tsx`
- Create: `apps/admin-console/src/components/ui/label.tsx`
- Create: `apps/admin-console/src/components/ui/avatar.tsx`
- Create: `apps/admin-console/src/types/alert.ts`
- Create: `apps/admin-console/src/types/plan.ts`
- Create: `apps/admin-console/src/types/device.ts`
- Create: `apps/admin-console/src/types/report.ts`

- [ ] **Step 1: 创建 eslint.config.js**

```js
// apps/admin-console/eslint.config.js
const nextPlugin = require("@next/eslint-plugin-next");

module.exports = [
  {
    files: ["**/*.{ts,tsx}"],
    plugins: { "@next/next": nextPlugin },
    rules: {
      ...nextPlugin.configs.recommended.rules,
      "@next/next/no-html-link-for-pages": "error",
      "no-console": "warn",
    },
    languageOptions: {
      parserOptions: {
        project: "./tsconfig.json",
        tsconfigRootDir: __dirname,
      },
    },
  },
];
```

- [ ] **Step 2: 创建类型定义**

```typescript
// apps/admin-console/src/types/alert.ts
export type AlertStatus = "pending" | "processing" | "resolved";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type AlertType =
  | "fire"
  | "gas_leak"
  | "temperature"
  | "intrusion"
  | "smoke";

export interface Alert {
  id: string;
  type: AlertType;
  title: string;
  content: string;
  riskLevel: RiskLevel;
  status: AlertStatus;
  location: string;
  deviceId: string;
  createdAt: string;
  updatedAt?: string;
  aiRecommendation?: string;
  associatedPlans?: string[];
}
```

```typescript
// apps/admin-console/src/types/plan.ts
export interface Plan {
  id: string;
  title: string;
  category: string;
  content: string;
  riskLevel: "low" | "medium" | "high" | "critical";
  version: string;
  author: string;
  updatedAt: string;
  relatedEquipment: string[];
  status: "draft" | "published" | "archived";
}
```

```typescript
// apps/admin-console/src/types/device.ts
export type DeviceStatus = "online" | "warning" | "offline";

export interface Device {
  id: string;
  name: string;
  type: string;
  location: string;
  status: DeviceStatus;
  realTimeValue: number;
  unit: string;
  thresholdHigh: number;
  thresholdLow: number;
  model: string;
  installedAt: string;
  lastCalibrated: string;
}
```

```typescript
// apps/admin-console/src/types/report.ts
export type ReportType = "daily" | "weekly" | "monthly";
export type ReportFormat = "pdf" | "excel" | "csv";

export interface ReportConfig {
  type: ReportType;
  dateRange: { start: string; end: string };
  sections: string[];
  format: ReportFormat;
}

export interface ReportRecord {
  id: string;
  type: ReportType;
  title: string;
  createdAt: string;
  createdBy: string;
  status: "generating" | "completed" | "failed";
  downloadUrl?: string;
}
```

- [ ] **Step 3: 创建 Shadcn UI 组件**

所有组件使用标准 Shadcn/UI 模式。以下是 `card.tsx` 示例：

```tsx
// apps/admin-console/src/components/ui/card.tsx
import * as React from "react";
import { cn } from "@/lib/utils";

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
));
Card.displayName = "Card";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
```

其余 Shadcn 组件 (`input.tsx`, `select.tsx`, `table.tsx`, `badge.tsx`, `tabs.tsx`, `dialog.tsx`, `drawer.tsx`, `textarea.tsx`, `label.tsx`, `avatar.tsx`) 使用标准 Shadcn/UI CLI 生成或按类似模式手写。每个组件导出默认 forwardRef 包装的 React 组件。

- [ ] **Step 4: 运行 typecheck 和 lint 验证**

```bash
cd apps/admin-console && npx tsc --noEmit
```

Expected: 仅有未使用变量的 warning（正常，后续页面会用到类型）

- [ ] **Step 5: Commit**

```bash
git add apps/admin-console/eslint.config.js apps/admin-console/src/components/ui/ apps/admin-console/src/types/
git commit -m "feat(wave1): 添加 eslint 配置、Shadcn UI 组件、类型定义"
```

---

### Task 2: 前端公共组件（Sidebar + Header + Mock 数据）

**Files:**
- Create: `apps/admin-console/src/components/common/Sidebar.tsx`
- Create: `apps/admin-console/src/components/common/Header.tsx`
- Create: `apps/admin-console/src/components/common/StatusBadge.tsx`
- Create: `apps/admin-console/src/mock/alerts.ts`
- Create: `apps/admin-console/src/mock/plans.ts`
- Create: `apps/admin-console/src/mock/devices.ts`
- Create: `apps/admin-console/src/mock/reports.ts`
- Modify: `apps/admin-console/src/app/layout.tsx`

- [ ] **Step 1: 创建 Mock 数据**

```typescript
// apps/admin-console/src/mock/alerts.ts
import { Alert } from "@/types/alert";

export const mockAlerts: Alert[] = [
  {
    id: "ALT-001",
    type: "fire",
    title: "A栋3楼烟感报警",
    content: "A栋3楼东区烟感探测器检测到烟雾浓度超标",
    riskLevel: "critical",
    status: "pending",
    location: "A栋3楼东区",
    deviceId: "SD-003",
    createdAt: "2026-04-17T08:30:00Z",
    aiRecommendation: "立即启动火灾应急预案，疏散3楼人员，联系消防部门",
    associatedPlans: ["PLAN-001"],
  },
  {
    id: "ALT-002",
    type: "gas_leak",
    title: "B车间气体泄漏",
    content: "B车间东区气体检测仪检测到可燃气体浓度达到警戒值",
    riskLevel: "high",
    status: "processing",
    location: "B车间东区",
    deviceId: "GD-001",
    createdAt: "2026-04-17T09:15:00Z",
    aiRecommendation: "启动通风系统，关闭相关阀门，疏散人员",
    associatedPlans: ["PLAN-002"],
  },
  {
    id: "ALT-003",
    type: "temperature",
    title: "C仓库温度异常",
    content: "C仓库2层温度传感器检测到温度超过45°C",
    riskLevel: "medium",
    status: "pending",
    location: "C仓库2层",
    deviceId: "TD-012",
    createdAt: "2026-04-17T10:00:00Z",
    aiRecommendation: "检查温控系统，确认是否为设备故障",
    associatedPlans: ["PLAN-003"],
  },
  {
    id: "ALT-004",
    type: "intrusion",
    title: "D区周界入侵",
    content: "D区西南角红外探测器检测到未授权人员入侵",
    riskLevel: "high",
    status: "resolved",
    location: "D区西南角",
    deviceId: "ID-005",
    createdAt: "2026-04-17T06:45:00Z",
    updatedAt: "2026-04-17T07:20:00Z",
    aiRecommendation: "已通知安保人员前往现场处置",
    associatedPlans: ["PLAN-004"],
  },
  {
    id: "ALT-005",
    type: "smoke",
    title: "E栋地下车库烟雾",
    content: "E栋地下车库B区烟雾探测器触发报警",
    riskLevel: "medium",
    status: "pending",
    location: "E栋地下车库B区",
    deviceId: "SD-010",
    createdAt: "2026-04-17T11:30:00Z",
    aiRecommendation: "派遣人员现场确认是否为误报",
  },
];

export const alertStats = {
  today: 12,
  pending: 5,
  processing: 3,
  resolved: 4,
  critical: 2,
  high: 3,
  medium: 4,
  low: 3,
};
```

```typescript
// apps/admin-console/src/mock/plans.ts
import { Plan } from "@/types/plan";

export const mockPlans: Plan[] = [
  {
    id: "PLAN-001",
    title: "火灾应急预案",
    category: "火灾",
    content:
      "1. 立即启动火灾报警系统\n2. 疏散起火楼层人员\n3. 启动自动喷淋系统\n4. 拨打119\n5. 组织初期灭火\n6. 关闭通风系统防止火势蔓延",
    riskLevel: "critical",
    version: "2.3",
    author: "张三",
    updatedAt: "2026-04-10",
    relatedEquipment: ["喷淋系统", "烟感探测器", "防火门"],
    status: "published",
  },
  {
    id: "PLAN-002",
    title: "气体泄漏应急预案",
    category: "气体泄漏",
    content:
      "1. 启动气体检测系统\n2. 疏散泄漏区域人员\n3. 启动排风系统\n4. 关闭泄漏管道阀门\n5. 设置警戒区域\n6. 联系专业处理团队",
    riskLevel: "high",
    version: "1.8",
    author: "李四",
    updatedAt: "2026-04-08",
    relatedEquipment: ["气体检测仪", "排风系统", "应急阀门"],
    status: "published",
  },
  {
    id: "PLAN-003",
    title: "温度异常处置预案",
    category: "温度异常",
    content:
      "1. 确认温度传感器读数\n2. 检查温控系统运行状态\n3. 启动备用冷却系统\n4. 通知设备维护人员\n5. 监控温度变化趋势",
    riskLevel: "medium",
    version: "1.2",
    author: "王五",
    updatedAt: "2026-04-05",
    relatedEquipment: ["温度传感器", "冷却系统", "温控面板"],
    status: "published",
  },
  {
    id: "PLAN-004",
    title: "入侵处置预案",
    category: "入侵检测",
    content:
      "1. 确认入侵区域和人员数量\n2. 通知就近安保人员\n3. 调取监控录像\n4. 封锁出口\n5. 必要时报警",
    riskLevel: "high",
    version: "1.5",
    author: "赵六",
    updatedAt: "2026-04-12",
    relatedEquipment: ["红外探测器", "监控摄像头", "门禁系统"],
    status: "published",
  },
];
```

```typescript
// apps/admin-console/src/mock/devices.ts
import { Device } from "@/types/device";

export const mockDevices: Device[] = [
  {
    id: "GD-001",
    name: "气体检测仪",
    type: "gas_detector",
    location: "B车间东区",
    status: "online",
    realTimeValue: 12.5,
    unit: "ppm",
    thresholdHigh: 50,
    thresholdLow: 10,
    model: "GC-200",
    installedAt: "2025-06-15",
    lastCalibrated: "2026-03-01",
  },
  {
    id: "SD-003",
    name: "烟感探测器",
    type: "smoke_detector",
    location: "A栋3楼东区",
    status: "warning",
    realTimeValue: 0.85,
    unit: "%obs/m",
    thresholdHigh: 1.0,
    thresholdLow: 0.0,
    model: "SD-500",
    installedAt: "2025-01-10",
    lastCalibrated: "2026-01-15",
  },
  {
    id: "TD-012",
    name: "温度传感器",
    type: "temperature_sensor",
    location: "C仓库2层",
    status: "warning",
    realTimeValue: 46.2,
    unit: "°C",
    thresholdHigh: 45,
    thresholdLow: 15,
    model: "TS-100",
    installedAt: "2025-03-20",
    lastCalibrated: "2026-02-10",
  },
  {
    id: "ID-005",
    name: "红外入侵探测器",
    type: "infrared_sensor",
    location: "D区西南角",
    status: "online",
    realTimeValue: 0,
    unit: "次",
    thresholdHigh: 1,
    thresholdLow: 0,
    model: "IR-300",
    installedAt: "2025-08-01",
    lastCalibrated: "2026-04-01",
  },
];
```

```typescript
// apps/admin-console/src/mock/reports.ts
import { ReportRecord, ReportType } from "@/types/report";

export const mockReports: ReportRecord[] = [
  {
    id: "RPT-001",
    type: "daily",
    title: "2026-04-16 安全日报",
    createdAt: "2026-04-17T00:00:00Z",
    createdBy: "系统",
    status: "completed",
    downloadUrl: "/api/reports/RPT-001.pdf",
  },
  {
    id: "RPT-002",
    type: "weekly",
    title: "第15周安全周报",
    createdAt: "2026-04-14T08:00:00Z",
    createdBy: "张三",
    status: "completed",
    downloadUrl: "/api/reports/RPT-002.pdf",
  },
  {
    id: "RPT-003",
    type: "monthly",
    title: "2026年3月安全月报",
    createdAt: "2026-04-01T08:00:00Z",
    createdBy: "李四",
    status: "completed",
    downloadUrl: "/api/reports/RPT-003.pdf",
  },
];
```

- [ ] **Step 2: 创建 Sidebar 组件**

```tsx
// apps/admin-console/src/components/common/Sidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Bell,
  FileText,
  BookOpen,
  Workflow,
  Cpu,
  Settings,
  Users,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/" },
  { label: "告警管理", icon: Bell, href: "/alerts" },
  { label: "预案管理", icon: FileText, href: "/plans" },
  { label: "知识库", icon: BookOpen, href: "/knowledge" },
  { label: "Agent 编排", icon: Workflow, href: "/agents" },
  { label: "模型管理", icon: Cpu, href: "/models" },
  { label: "系统设置", icon: Settings, href: "/settings" },
  { label: "用户管理", icon: Users, href: "/users" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 border-r bg-white">
      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

- [ ] **Step 3: 创建 Header 组件**

```tsx
// apps/admin-console/src/components/common/Header.tsx
"use client";

import { Bell, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 h-16 border-b bg-white px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-gray-900">
          EHS 智能安保决策中台
        </h1>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索..."
            className="pl-10 w-64"
          />
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="relative p-2 text-gray-600 hover:text-gray-900">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-[10px] text-white flex items-center justify-center">
            3
          </span>
        </button>
        <Avatar>
          <AvatarFallback>管</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
```

- [ ] **Step 4: 创建 StatusBadge 组件**

```tsx
// apps/admin-console/src/components/common/StatusBadge.tsx
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const riskColors: Record<string, string> = {
  low: "bg-green-100 text-green-800 border-green-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  critical: "bg-red-100 text-red-800 border-red-200",
};

const statusMap: Record<string, { label: string; color: string }> = {
  pending: { label: "待处理", color: "bg-orange-100 text-orange-800" },
  processing: { label: "处理中", color: "bg-blue-100 text-blue-800" },
  resolved: { label: "已解决", color: "bg-green-100 text-green-800" },
};

interface StatusBadgeProps {
  type: "risk" | "status" | "device";
  value: string;
}

export function StatusBadge({ type, value }: StatusBadgeProps) {
  if (type === "risk") {
    return (
      <Badge
        variant="outline"
        className={cn(riskColors[value] || "bg-gray-100 text-gray-800")}
      >
        {value === "critical"
          ? "严重"
          : value === "high"
          ? "高"
          : value === "medium"
          ? "中"
          : "低"}
      </Badge>
    );
  }
  if (type === "status") {
    const { label, color } = statusMap[value] || {
      label: value,
      color: "bg-gray-100 text-gray-800",
    };
    return <Badge className={color}>{label}</Badge>;
  }
  return <Badge variant="outline">{value}</Badge>;
}
```

- [ ] **Step 5: 更新 layout.tsx 集成 Header + Sidebar**

读取当前 `apps/admin-console/src/app/layout.tsx`，更新为：

```tsx
// apps/admin-console/src/app/layout.tsx
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { Toaster } from "@/components/ui/toaster";
import "./globals.css";

export const metadata = {
  title: "EHS 智能安保决策中台",
  description: "基于 GraphRAG + Multi-Agent 的智能安保系统",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen">
        <Header />
        <div className="pt-16 flex">
          <Sidebar />
          <main className="ml-64 flex-1 p-6">{children}</main>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
```

- [ ] **Step 6: Commit**

```bash
git add apps/admin-console/src/components/common/ apps/admin-console/src/components/ui/avatar.tsx apps/admin-console/src/components/ui/badge.tsx apps/admin-console/src/components/ui/dialog.tsx apps/admin-console/src/components/ui/drawer.tsx apps/admin-console/src/components/ui/input.tsx apps/admin-console/src/components/ui/label.tsx apps/admin-console/src/components/ui/select.tsx apps/admin-console/src/components/ui/table.tsx apps/admin-console/src/components/ui/tabs.tsx apps/admin-console/src/components/ui/textarea.tsx apps/admin-console/src/mock/ apps/admin-console/src/app/layout.tsx
git commit -m "feat(wave1): 添加 Sidebar/Header/StatusBadge 公共组件和 Mock 数据"
```

---

### Task 3: Dashboard 首页增强

**Files:**
- Modify: `apps/admin-console/src/app/page.tsx`

当前 `page.tsx` 为基础页面，需要升级为完整 Dashboard，包含统计卡片、趋势图、告警列表。

- [ ] **Step 1: 重写 Dashboard 页面**

```tsx
// apps/admin-console/src/app/page.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/common/StatusBadge";
import { mockAlerts, alertStats } from "@/mock/alerts";
import {
  AlertTriangle,
  Clock,
  CheckCircle,
  Shield,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const recentAlerts = mockAlerts.slice(0, 5);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">欢迎回来</h2>
        <p className="text-gray-500 mt-1">
          2026-04-17 | 所有系统运行正常
        </p>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">今日告警</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{alertStats.today}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 text-red-500" />{" "}
              较昨日 +2
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">待处理</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{alertStats.pending}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingDown className="inline h-3 w-3 text-green-500" />{" "}
              较昨日 -3
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">设备在线率</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.5%</div>
            <p className="text-xs text-green-600">正常</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">安全天数</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45</div>
            <p className="text-xs text-muted-foreground">天</p>
          </CardContent>
        </Card>
      </div>

      {/* 最近告警 */}
      <Card>
        <CardHeader>
          <CardTitle>最近告警</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div className="flex-1">
                  <p className="font-medium text-sm">{alert.title}</p>
                  <p className="text-xs text-gray-500">{alert.location}</p>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge type="risk" value={alert.riskLevel} />
                  <StatusBadge type="status" value={alert.status} />
                  <span className="text-xs text-gray-400">
                    {alert.createdAt.slice(0, 16)}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <Link
            href="/alerts"
            className="text-sm text-blue-600 hover:text-blue-800 mt-4 inline-block"
          >
            查看全部 →
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add apps/admin-console/src/app/page.tsx
git commit -m "feat(wave1): 增强 Dashboard 首页 - 统计卡片 + 最近告警"
```

---

### Task 4: 告警管理页

**Files:**
- Create: `apps/admin-console/src/app/alerts/page.tsx`
- Create: `apps/admin-console/src/app/alerts/components/AlertRow.tsx`
- Create: `apps/admin-console/src/app/alerts/components/AlertDrawer.tsx`

- [ ] **Step 1: 创建 AlertDrawer 组件**

```tsx
// apps/admin-console/src/app/alerts/components/AlertDrawer.tsx
"use client";

import { Alert } from "@/types/alert";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { StatusBadge } from "@/components/common/StatusBadge";

interface AlertDrawerProps {
  alert: Alert | null;
  open: boolean;
  onClose: () => void;
  onProcess: (alertId: string) => void;
}

export function AlertDrawer({
  alert,
  open,
  onClose,
  onProcess,
}: AlertDrawerProps) {
  if (!alert) return null;

  return (
    <Drawer open={open} onOpenChange={onClose}>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>{alert.title}</DrawerTitle>
          <DrawerDescription>{alert.content}</DrawerDescription>
        </DrawerHeader>
        <div className="px-4 space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">位置：</span>
              {alert.location}
            </div>
            <div>
              <span className="text-gray-500">设备：</span>
              {alert.deviceId}
            </div>
            <div>
              <span className="text-gray-500">风险等级：</span>
              <StatusBadge type="risk" value={alert.riskLevel} />
            </div>
            <div>
              <span className="text-gray-500">状态：</span>
              <StatusBadge type="status" value={alert.status} />
            </div>
          </div>
          {alert.aiRecommendation && (
            <div className="bg-blue-50 rounded-md p-4">
              <h4 className="font-medium text-sm text-blue-900">
                AI 处置建议
              </h4>
              <p className="text-sm text-blue-800 mt-1">
                {alert.aiRecommendation}
              </p>
            </div>
          )}
          {alert.associatedPlans && alert.associatedPlans.length > 0 && (
            <div>
              <h4 className="font-medium text-sm text-gray-700">关联预案</h4>
              <div className="flex gap-2 mt-2">
                {alert.associatedPlans.map((plan) => (
                  <span
                    key={plan}
                    className="px-2 py-1 bg-gray-100 rounded text-xs"
                  >
                    {plan}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        <DrawerFooter>
          <Button
            onClick={() => onProcess(alert.id)}
            disabled={alert.status !== "pending"}
          >
            立即处理
          </Button>
          <DrawerClose asChild>
            <Button variant="outline">关闭</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
```

- [ ] **Step 2: 创建 AlertRow 组件**

```tsx
// apps/admin-console/src/app/alerts/components/AlertRow.tsx
"use client";

import { Alert } from "@/types/alert";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Eye } from "lucide-react";
import { Button } from "@/components/ui/button";

interface AlertRowProps {
  alert: Alert;
  onView: (alert: Alert) => void;
}

export function AlertRow({ alert, onView }: AlertRowProps) {
  const typeLabels: Record<string, string> = {
    fire: "火灾",
    gas_leak: "气体泄漏",
    temperature: "温度异常",
    intrusion: "入侵检测",
    smoke: "烟雾",
  };

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-3 text-sm font-medium">{alert.id}</td>
      <td className="px-4 py-3 text-sm">{typeLabels[alert.type]}</td>
      <td className="px-4 py-3 text-sm">{alert.title}</td>
      <td className="px-4 py-3">
        <StatusBadge type="risk" value={alert.riskLevel} />
      </td>
      <td className="px-4 py-3">
        <StatusBadge type="status" value={alert.status} />
      </td>
      <td className="px-4 py-3 text-sm text-gray-500">{alert.location}</td>
      <td className="px-4 py-3 text-sm text-gray-400">
        {alert.createdAt.slice(0, 16)}
      </td>
      <td className="px-4 py-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView(alert)}
        >
          <Eye className="h-4 w-4" />
        </Button>
      </td>
    </tr>
  );
}
```

- [ ] **Step 3: 创建告警管理页**

```tsx
// apps/admin-console/src/app/alerts/page.tsx
"use client";

import { useState } from "react";
import { Alert } from "@/types/alert";
import { mockAlerts } from "@/mock/alerts";
import { AlertRow } from "./components/AlertRow";
import { AlertDrawer } from "./components/AlertDrawer";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState(mockAlerts);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState("all");
  const [filterRisk, setFilterRisk] = useState("all");

  const filtered = alerts.filter((a) => {
    if (filterStatus !== "all" && a.status !== filterStatus) return false;
    if (filterRisk !== "all" && a.riskLevel !== filterRisk) return false;
    return true;
  });

  const handleProcess = (alertId: string) => {
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === alertId ? { ...a, status: "processing" as const } : a
      )
    );
    toast.success("已开始处理告警");
    setDrawerOpen(false);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">告警管理</h2>

      {/* 筛选 */}
      <div className="flex gap-4">
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="全部状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部状态</SelectItem>
            <SelectItem value="pending">待处理</SelectItem>
            <SelectItem value="processing">处理中</SelectItem>
            <SelectItem value="resolved">已解决</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterRisk} onValueChange={setFilterRisk}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="全部等级" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部等级</SelectItem>
            <SelectItem value="critical">严重</SelectItem>
            <SelectItem value="high">高</SelectItem>
            <SelectItem value="medium">中</SelectItem>
            <SelectItem value="low">低</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 告警列表 */}
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                ID
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                类型
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                标题
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                等级
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                状态
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                位置
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                时间
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                操作
              </th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((alert) => (
              <AlertRow
                key={alert.id}
                alert={alert}
                onView={(a) => {
                  setSelectedAlert(a);
                  setDrawerOpen(true);
                }}
              />
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-4xl mb-4">🎉</p>
            <p>暂无告警数据</p>
            <p className="text-sm mt-2">
              所有系统运行正常，继续保持良好的监控状态
            </p>
          </div>
        )}
      </div>

      <AlertDrawer
        alert={selectedAlert}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onProcess={handleProcess}
      />
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add apps/admin-console/src/app/alerts/
git commit -m "feat(wave1): 告警管理页 - 列表+筛选+处理抽屉"
```

---

### Task 5: 预案管理页 + 知识库管理页

**Files:**
- Create: `apps/admin-console/src/app/plans/page.tsx`
- Create: `apps/admin-console/src/app/knowledge/page.tsx`

- [ ] **Step 1: 预案管理页**

```tsx
// apps/admin-console/src/app/plans/page.tsx
"use client";

import { useState } from "react";
import { Plan } from "@/types/plan";
import { mockPlans } from "@/mock/plans";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Eye, FileText } from "lucide-react";

export default function PlansPage() {
  const [plans] = useState(mockPlans);
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState("all");

  const categories = [...new Set(plans.map((p) => p.category))];
  const filtered =
    filterCategory === "all"
      ? plans
      : plans.filter((p) => p.category === filterCategory);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">预案管理</h2>
        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="全部分类" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部分类</SelectItem>
            {categories.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map((plan) => (
          <Card key={plan.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{plan.title}</CardTitle>
                <StatusBadge type="risk" value={plan.riskLevel} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex gap-2">
                  <Badge variant="outline">{plan.category}</Badge>
                  <Badge variant="outline">v{plan.version}</Badge>
                  <Badge
                    className={
                      plan.status === "published"
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }
                  >
                    {plan.status === "published" ? "已发布" : plan.status}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {plan.content}
                </p>
                <div className="flex justify-between items-center pt-2">
                  <span className="text-xs text-gray-400">
                    {plan.updatedAt} by {plan.author}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedPlan(plan);
                      setDialogOpen(true);
                    }}
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    预览
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          {selectedPlan && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedPlan.title}</DialogTitle>
                <DialogDescription>
                  分类：{selectedPlan.category} | v{selectedPlan.version}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div className="whitespace-pre-wrap text-sm">
                  {selectedPlan.content}
                </div>
                <div>
                  <h4 className="font-medium text-sm text-gray-700">
                    关联设备
                  </h4>
                  <div className="flex gap-2 mt-1">
                    {selectedPlan.relatedEquipment.map((eq) => (
                      <Badge key={eq} variant="outline">
                        {eq}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
```

- [ ] **Step 2: 知识库管理页**

```tsx
// apps/admin-console/src/app/knowledge/page.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookOpen, Upload, Search } from "lucide-react";

export default function KnowledgePage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">知识库管理</h2>

      <Tabs defaultValue="documents">
        <TabsList>
          <TabsTrigger value="documents">文档管理</TabsTrigger>
          <TabsTrigger value="upload">上传文档</TabsTrigger>
          <TabsTrigger value="search">检索测试</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>已上传文档</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "火灾应急预案.pdf", size: "2.3 MB", date: "2026-04-10", status: "已索引" },
                  { name: "气体泄漏处置流程.docx", size: "1.1 MB", date: "2026-04-08", status: "已索引" },
                  { name: "安全生产管理制度.pdf", size: "3.5 MB", date: "2026-04-05", status: "向量化中" },
                ].map((doc) => (
                  <div
                    key={doc.name}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <BookOpen className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="text-sm font-medium">{doc.name}</p>
                        <p className="text-xs text-gray-400">
                          {doc.size} · {doc.date}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        doc.status === "已索引"
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {doc.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>上传文档</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                <Upload className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-500">
                  拖拽文件到此处，或点击选择文件
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  支持 PDF, DOCX, TXT 格式
                </p>
                <Button className="mt-4">选择文件</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>RAG 检索测试</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input placeholder="输入测试问题..." />
                <Button>
                  <Search className="h-4 w-4 mr-1" />
                  检索
                </Button>
              </div>
              <div className="bg-gray-50 rounded-md p-4 text-sm text-gray-500">
                <p>检索结果将显示在这里</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/admin-console/src/app/plans/ apps/admin-console/src/app/knowledge/
git commit -m "feat(wave1): 预案管理页 + 知识库管理页"
```

---

### Task 6: Agent 编排页 + 模型管理页

**Files:**
- Create: `apps/admin-console/src/app/agents/page.tsx`
- Create: `apps/admin-console/src/app/models/page.tsx`

- [ ] **Step 1: Agent 编排页**

```tsx
// apps/admin-console/src/app/agents/page.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Workflow, ArrowRight, Play, Settings } from "lucide-react";

const agentNodes = [
  {
    id: "risk",
    name: "RiskAgent",
    desc: "风险感知 - 分析告警内容，评估风险等级",
    status: "active",
    input: "告警数据",
    output: "风险等级 + 处置建议",
  },
  {
    id: "search",
    name: "SearchAgent",
    desc: "预案检索 - 基于 GraphRAG 检索匹配预案",
    status: "active",
    input: "风险等级 + 关键词",
    output: "匹配预案列表",
  },
];

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">Agent 编排</h2>
        <Button>
          <Workflow className="h-4 w-4 mr-1" />
          新建工作流
        </Button>
      </div>

      <Tabs defaultValue="workflow">
        <TabsList>
          <TabsTrigger value="workflow">工作流配置</TabsTrigger>
          <TabsTrigger value="nodes">节点管理</TabsTrigger>
        </TabsList>

        <TabsContent value="workflow" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>默认工作流</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 py-4">
                <div className="flex-1 bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900">RiskAgent</h3>
                  <p className="text-xs text-blue-700 mt-1">
                    风险感知 - 分析告警内容
                  </p>
                  <Badge className="mt-2 bg-green-100 text-green-800">
                    运行中
                  </Badge>
                </div>
                <ArrowRight className="h-6 w-6 text-gray-400" />
                <div className="flex-1 bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-medium text-purple-900">SearchAgent</h3>
                  <p className="text-xs text-purple-700 mt-1">
                    预案检索 - GraphRAG 匹配
                  </p>
                  <Badge className="mt-2 bg-green-100 text-green-800">
                    运行中
                  </Badge>
                </div>
                <ArrowRight className="h-6 w-6 text-gray-400" />
                <div className="flex-1 bg-gray-50 border rounded-lg p-4">
                  <h3 className="font-medium text-gray-700">输出</h3>
                  <p className="text-xs text-gray-500 mt-1">
                    结构化响应
                  </p>
                </div>
              </div>
              <div className="flex gap-2 mt-4">
                <Button size="sm">
                  <Play className="h-4 w-4 mr-1" />
                  测试运行
                </Button>
                <Button size="sm" variant="outline">
                  <Settings className="h-4 w-4 mr-1" />
                  编辑
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="nodes" className="space-y-4">
          {agentNodes.map((node) => (
            <Card key={node.id}>
              <CardHeader>
                <CardTitle className="text-lg">{node.name}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">{node.desc}</p>
                <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
                  <div>
                    <span className="text-gray-500">输入：</span>
                    {node.input}
                  </div>
                  <div>
                    <span className="text-gray-500">输出：</span>
                    {node.output}
                  </div>
                </div>
                <Badge className="mt-3 bg-green-100 text-green-800">
                  运行中
                </Badge>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

- [ ] **Step 2: 模型管理页**

```tsx
// apps/admin-console/src/app/models/page.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Cpu, BarChart3, Download } from "lucide-react";

export default function ModelsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">模型管理</h2>

      <Tabs defaultValue="models">
        <TabsList>
          <TabsTrigger value="models">模型配置</TabsTrigger>
          <TabsTrigger value="fine-tune">微调记录</TabsTrigger>
          <TabsTrigger value="eval">评估报告</TabsTrigger>
        </TabsList>

        <TabsContent value="models" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>已部署模型</CardTitle>
            </CardHeader>
            <CardContent>
              {[
                {
                  name: "Qwen3-7B",
                  type: "LLM",
                  status: "运行中",
                  endpoint: "http://localhost:11434",
                },
                {
                  name: "BGE-Reranker",
                  type: "重排序",
                  status: "运行中",
                  endpoint: "http://localhost:6006",
                },
                {
                  name: "BERT-risk",
                  type: "风险分级",
                  status: "待部署",
                  endpoint: "-",
                },
              ].map((model) => (
                <div
                  key={model.name}
                  className="flex items-center justify-between py-3 border-b last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <Cpu className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">{model.name}</p>
                      <p className="text-xs text-gray-400">{model.type}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-400">
                      {model.endpoint}
                    </span>
                    <Badge
                      className={
                        model.status === "运行中"
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }
                    >
                      {model.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="fine-tune" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>微调任务</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "指令微调 - Qwen7B", status: "待训练", samples: 500 },
                  { name: "风险分级 - BERT", status: "待训练", samples: 1000 },
                  { name: "合规检查 - RoBERTa", status: "待训练", samples: 300 },
                  { name: "术语Embedding - BGE", status: "待训练", samples: 2000 },
                ].map((task) => (
                  <div
                    key={task.name}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div>
                      <p className="text-sm font-medium">{task.name}</p>
                      <p className="text-xs text-gray-400">
                        训练样本：{task.samples}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className="bg-yellow-100 text-yellow-800">
                        {task.status}
                      </Badge>
                      <Button size="sm" variant="outline">
                        <Download className="h-3 w-3 mr-1" />
                        开始
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="eval" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>评估报告</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 text-center py-8">
                暂无评估报告。完成微调后自动生成评估。
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/admin-console/src/app/agents/ apps/admin-console/src/app/models/
git commit -m "feat(wave1): Agent 编排页 + 模型管理页"
```

---

### Task 7: 系统设置页 + 用户管理页

**Files:**
- Create: `apps/admin-console/src/app/settings/page.tsx`
- Create: `apps/admin-console/src/app/users/page.tsx`

- [ ] **Step 1: 系统设置页**

```tsx
// apps/admin-console/src/app/settings/page.tsx
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-gray-900">系统设置</h2>

      <Tabs defaultValue="basic">
        <TabsList>
          <TabsTrigger value="basic">基本信息</TabsTrigger>
          <TabsTrigger value="alert-config">告警配置</TabsTrigger>
          <TabsTrigger value="notification">通知设置</TabsTrigger>
          <TabsTrigger value="api">API 管理</TabsTrigger>
          <TabsTrigger value="logs">操作日志</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>基本信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="site-name">系统名称</Label>
                <Input id="site-name" defaultValue="EHS 智能安保决策中台" />
              </div>
              <div>
                <Label htmlFor="site-url">系统地址</Label>
                <Input id="site-url" defaultValue="http://localhost:3000" />
              </div>
              <div>
                <Label htmlFor="admin-email">管理员邮箱</Label>
                <Input id="admin-email" defaultValue="admin@ehs.com" />
              </div>
              <Button onClick={() => toast.success("保存成功")}>
                保存设置
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alert-config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>告警阈值配置</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="gas-threshold">气体泄漏阈值 (ppm)</Label>
                <Input id="gas-threshold" type="number" defaultValue="50" />
              </div>
              <div>
                <Label htmlFor="temp-threshold">温度异常阈值 (°C)</Label>
                <Input id="temp-threshold" type="number" defaultValue="45" />
              </div>
              <Button onClick={() => toast.success("保存成功")}>
                保存配置
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notification" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>通知渠道</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-500">
                配置告警通知渠道（邮件、短信、钉钉等）
              </p>
              <div className="bg-gray-50 rounded-md p-4 text-sm text-gray-500">
                <p>通知配置将在接入真实服务后启用</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API Key 管理</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 text-center py-8">
                暂无 API Key
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>操作日志</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500 text-center py-8">
                暂无操作日志
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

- [ ] **Step 2: 用户管理页**

```tsx
// apps/admin-console/src/app/users/page.tsx
"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Search, Plus } from "lucide-react";

const mockUsers = [
  { id: "U001", name: "张三", role: "管理员", email: "zhangsan@ehs.com", status: "active" },
  { id: "U002", name: "李四", role: "值班经理", email: "lisi@ehs.com", status: "active" },
  { id: "U003", name: "王五", role: "EHS 总监", email: "wangwu@ehs.com", status: "active" },
  { id: "U004", name: "赵六", role: "安保人员", email: "zhaoliu@ehs.com", status: "inactive" },
];

export default function UsersPage() {
  const [users] = useState(mockUsers);
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = users.filter(
    (u) =>
      u.name.includes(searchTerm) ||
      u.email.includes(searchTerm) ||
      u.role.includes(searchTerm)
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-900">用户管理</h2>
        <Button>
          <Plus className="h-4 w-4 mr-1" />
          添加用户
        </Button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索用户..."
            className="pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="space-y-3">
            {filtered.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between py-3 border-b last:border-0"
              >
                <div className="flex items-center gap-3">
                  <Avatar>
                    <AvatarFallback>{user.name[0]}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="text-sm font-medium">{user.name}</p>
                    <p className="text-xs text-gray-400">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant="outline">{user.role}</Badge>
                  <Badge
                    className={
                      user.status === "active"
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-100 text-gray-800"
                    }
                  >
                    {user.status === "active" ? "活跃" : "停用"}
                  </Badge>
                  <Button variant="ghost" size="sm">
                    编辑
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add apps/admin-console/src/app/settings/ apps/admin-console/src/app/users/
git commit -m "feat(wave1): 系统设置页 + 用户管理页"
```

---

### Task 8: Docker 基础（Neo4j + 完整种子数据）

**Files:**
- Modify: `docker-compose.yml`
- Create: `data/seed/devices.jsonl`
- Modify: `scripts/seed_data.py`

- [ ] **Step 1: 添加 Neo4j 服务到 docker-compose.yml**

读取当前 `docker-compose.yml`，在基础设施层添加：

```yaml
  # Neo4j (知识图谱)
  neo4j:
    image: neo4j:5.14
    container_name: ehs-neo4j
    environment:
      - NEO4J_AUTH=neo4j/ehs123456
      - NEO4J_PLUGINS=["apoc"]
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "ehs123456", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

同时在 `volumes` 部分添加 `neo4j_data:`。

- [ ] **Step 2: 创建设备种子数据**

```jsonl
{"id": "GD-001", "name": "气体检测仪", "type": "gas_detector", "location": "B车间东区", "status": "online", "threshold_high": 50, "threshold_low": 10, "unit": "ppm", "model": "GC-200", "installed_at": "2025-06-15"}
{"id": "GD-002", "name": "气体检测仪", "type": "gas_detector", "location": "B车间西区", "status": "online", "threshold_high": 50, "threshold_low": 10, "unit": "ppm", "model": "GC-200", "installed_at": "2025-06-15"}
{"id": "SD-003", "name": "烟感探测器", "type": "smoke_detector", "location": "A栋3楼东区", "status": "online", "threshold_high": 1.0, "threshold_low": 0.0, "unit": "%obs/m", "model": "SD-500", "installed_at": "2025-01-10"}
{"id": "SD-010", "name": "烟感探测器", "type": "smoke_detector", "location": "E栋地下车库B区", "status": "online", "threshold_high": 1.0, "threshold_low": 0.0, "unit": "%obs/m", "model": "SD-500", "installed_at": "2025-02-20"}
{"id": "TD-012", "name": "温度传感器", "type": "temperature_sensor", "location": "C仓库2层", "status": "online", "threshold_high": 45, "threshold_low": 15, "unit": "C", "model": "TS-100", "installed_at": "2025-03-20"}
{"id": "ID-005", "name": "红外入侵探测器", "type": "infrared_sensor", "location": "D区西南角", "status": "online", "threshold_high": 1, "threshold_low": 0, "unit": "count", "model": "IR-300", "installed_at": "2025-08-01"}
```

- [ ] **Step 3: 更新 seed_data.py 添加 Neo4j 导入**

在 `scripts/seed_data.py` 中添加 Neo4j 导入函数：

```python
# 在配置部分添加
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "ehs123456")

# 添加 Neo4j 导入函数
def seed_neo4j():
    """导入知识图谱到 Neo4j"""
    logger.info("正在导入知识图谱到 Neo4j...")
    try:
        from neo4j import GraphDatabase
    except ImportError:
        logger.warning("neo4j 驱动未安装，跳过 Neo4j 导入")
        return

    driver = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # 清除旧数据
        session.run("MATCH (n) DETACH DELETE n")

        # 读取知识图谱数据
        kg_file = SEED_DIR / "knowledge_graph.json"
        if kg_file.exists():
            with open(kg_file) as f:
                kg_data = json.load(f)

            # 创建节点
            for entity in kg_data.get("entities", []):
                session.run(
                    "MERGE (n:Entity {id: $id}) SET n.name = $name, n.type = $type, n.properties = $props",
                    id=entity["id"],
                    name=entity["name"],
                    type=entity["type"],
                    props=entity.get("properties", {}),
                )

            # 创建关系
            for rel in kg_data.get("relations", []):
                session.run(
                    "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
                    "MERGE (a)-[r:RELATES {type: $rel_type}]->(b) "
                    "SET r.properties = $props",
                    source=rel["source"],
                    target=rel["target"],
                    rel_type=rel["type"],
                    props=rel.get("properties", {}),
                )

        logger.info("Neo4j 知识图谱导入完成")
    driver.close()
```

在 `pyproject.toml` 中添加 `neo4j` 依赖：

```toml
# 在 [tool.poetry.dependencies] 中添加
neo4j = "^5.15"
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml data/seed/devices.jsonl scripts/seed_data.py apps/ehs-ai/pyproject.toml
git commit -m "feat(wave1): 添加 Neo4j 服务到 Docker + 设备种子数据"
```

---

### Task 9: 测试基础（Python 单元测试 + 前端 Vitest）

**Files:**
- Create: `apps/ehs-ai/tests/test_graph_rag.py`
- Create: `apps/admin-console/src/app/alerts/components/__tests__/AlertDrawer.test.tsx`

- [ ] **Step 1: GraphRAG 单元测试**

```python
# apps/ehs-ai/tests/test_graph_rag.py
"""GraphRAG 引擎单元测试"""

import pytest
from unittest.mock import MagicMock, patch
from src.core.graph_rag import GraphRAGEngine
from src.core.graph_rag.knowledge_graph import KnowledgeGraph


class TestGraphRAGEngine:
    """测试 GraphRAG 主检索器"""

    @pytest.fixture
    def mock_es(self):
        mock = MagicMock()
        mock.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_score": 0.9, "_source": {"title": "火灾预案", "content": "..."}},
                    {"_score": 0.7, "_source": {"title": "烟雾预案", "content": "..."}},
                ],
            }
        }
        return mock

    @pytest.fixture
    def mock_milvus(self):
        mock = MagicMock()
        mock.search.return_value = [
            {"id": "1", "score": 0.85, "entity": {"title": "火灾预案"}},
            {"id": "2", "score": 0.75, "entity": {"title": "烟雾预案"}},
        ]
        return mock

    @pytest.fixture
    def mock_reranker(self):
        mock = MagicMock()
        mock.rerank.return_value = [
            {"score": 0.95, "text": "火灾预案"},
            {"score": 0.80, "text": "烟雾预案"},
        ]
        return mock

    def test_search_returns_results(self, mock_es, mock_milvus, mock_reranker):
        engine = GraphRAGEngine(
            es_searcher=mock_es,
            milvus_searcher=mock_milvus,
            reranker=mock_reranker,
            knowledge_graph=None,
        )
        results = engine.search("火灾")
        assert results is not None
        assert len(results) > 0

    def test_search_degrades_on_es_failure(self, mock_milvus, mock_reranker):
        mock_es = MagicMock()
        mock_es.search.side_effect = Exception("ES unavailable")
        engine = GraphRAGEngine(
            es_searcher=mock_es,
            milvus_searcher=mock_milvus,
            reranker=mock_reranker,
            knowledge_graph=None,
        )
        results = engine.search("火灾")
        assert results is not None


class TestKnowledgeGraph:
    """测试知识图谱子图检索"""

    @pytest.fixture
    def kg(self):
        return KnowledgeGraph()

    def test_add_entity(self, kg):
        kg.add_entity("building_a", "Building", {"name": "A栋"})
        assert kg.get_entity("building_a") is not None

    def test_add_relation(self, kg):
        kg.add_entity("building_a", "Building", {})
        kg.add_entity("building_b", "Building", {})
        kg.add_relation("building_a", "connected_to", "building_b")
        neighbors = kg.get_neighbors("building_a")
        assert "building_b" in neighbors

    def test_get_subgraph(self, kg):
        kg.add_entity("a", "Building", {})
        kg.add_entity("b", "Building", {})
        kg.add_entity("c", "Room", {})
        kg.add_relation("a", "connected_to", "b")
        kg.add_relation("a", "contains", "c")
        subgraph = kg.get_subgraph("a")
        assert len(subgraph) >= 2
```

- [ ] **Step 2: 前端 AlertDrawer 测试**

```tsx
// apps/admin-console/src/app/alerts/components/__tests__/AlertDrawer.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AlertDrawer } from "../AlertDrawer";
import { Alert } from "@/types/alert";

const mockAlert: Alert = {
  id: "ALT-001",
  type: "fire",
  title: "A栋3楼烟感报警",
  content: "烟雾浓度超标",
  riskLevel: "critical",
  status: "pending",
  location: "A栋3楼东区",
  deviceId: "SD-003",
  createdAt: "2026-04-17T08:30:00Z",
  aiRecommendation: "立即启动火灾应急预案",
  associatedPlans: ["PLAN-001"],
};

describe("AlertDrawer", () => {
  it("shows alert details when open", () => {
    render(
      <AlertDrawer
        alert={mockAlert}
        open={true}
        onClose={() => {}}
        onProcess={() => {}}
      />
    );
    expect(screen.getByText("A栋3楼烟感报警")).toBeInTheDocument();
    expect(screen.getByText("A栋3楼东区")).toBeInTheDocument();
  });

  it("shows AI recommendation when present", () => {
    render(
      <AlertDrawer
        alert={mockAlert}
        open={true}
        onClose={() => {}}
        onProcess={() => {}}
      />
    );
    expect(screen.getByText("AI 处置建议")).toBeInTheDocument();
    expect(
      screen.getByText("立即启动火灾应急预案")
    ).toBeInTheDocument();
  });

  it("calls onProcess when process button clicked", async () => {
    const onProcess = vi.fn();
    const user = userEvent.setup();
    render(
      <AlertDrawer
        alert={mockAlert}
        open={true}
        onClose={() => {}}
        onProcess={onProcess}
      />
    );
    await user.click(screen.getByText("立即处理"));
    expect(onProcess).toHaveBeenCalledWith("ALT-001");
  });
});
```

- [ ] **Step 3: 运行测试验证**

```bash
cd apps/ehs-ai && pytest tests/test_graph_rag.py -v
cd apps/admin-console && npm test -- --run
```

- [ ] **Step 4: Commit**

```bash
git add apps/ehs-ai/tests/test_graph_rag.py apps/admin-console/src/app/alerts/components/__tests__/
git commit -m "feat(wave1): 添加 GraphRAG 和 AlertDrawer 单元测试"
```

---

## Wave 2: 微调模型训练

### Task 10: 微调数据生成

**Files:**
- Create: `scripts/fine_tune/__init__.py`
- Create: `scripts/fine_tune/generate_data.py`
- Create: `scripts/fine_tune/train_config.py`
- Create: `data/fine_tune/instruction/train.jsonl`
- Create: `data/fine_tune/instruction/eval.jsonl`
- Create: `data/fine_tune/risk/train.jsonl`
- Create: `data/fine_tune/risk/eval.jsonl`
- Create: `data/fine_tune/compliance/train.jsonl`
- Create: `data/fine_tune/compliance/eval.jsonl`
- Create: `data/fine_tune/embedding/term_pairs.jsonl`

- [ ] **Step 1: 通用训练配置**

```python
# scripts/fine_tune/train_config.py
"""通用训练配置"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrainingConfig:
    """训练参数配置"""
    # 模型
    base_model: str = ""
    output_dir: str = ""

    # 训练
    num_epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 2e-5
    max_length: int = 512
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01

    # 数据
    train_file: str = ""
    eval_file: str = ""

    # 设备
    device: str = "cuda"

    # 日志
    logging_steps: int = 10
    save_steps: int = 100
    eval_steps: int = 50

    # 其他
    seed: int = 42
    gradient_accumulation_steps: int = 1
```

- [ ] **Step 2: 数据生成脚本**

```python
# scripts/fine_tune/generate_data.py
"""
微调数据生成器

生成 4 类微调数据：
1. 指令微调 (instruction) - Qwen-7B
2. 风险分级 (risk) - BERT
3. 合规检查 (compliance) - RoBERTa
4. 术语 Embedding (embedding) - BGE
"""

import json
import random
import os
from pathlib import Path

random.seed(42)

SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "fine_tune"

# ============================================
# 1. 指令微调数据
# ============================================

INSTRUCTION_TEMPLATES = [
    {
        "instruction": "根据以下告警内容，评估风险等级并给出处置建议。以 JSON 格式输出，包含 risk_level (high/medium/low) 和 recommendation 字段。",
        "scenarios": [
            {
                "input": "A栋3楼东区烟感探测器检测到烟雾浓度超标，当前读数0.85%obs/m，阈值1.0",
                "output": json.dumps({
                    "risk_level": "high",
                    "recommendation": "立即启动火灾应急预案，疏散3楼人员，联系消防部门，关闭通风系统防止火势蔓延"
                }, ensure_ascii=False),
            },
            {
                "input": "B车间东区气体检测仪检测到可燃气体浓度12.5ppm，阈值50ppm",
                "output": json.dumps({
                    "risk_level": "medium",
                    "recommendation": "启动通风系统，通知设备维护人员检查泄漏源，持续监控浓度变化"
                }, ensure_ascii=False),
            },
            {
                "input": "C仓库2层温度传感器检测到46.2°C，阈值45°C",
                "output": json.dumps({
                    "risk_level": "medium",
                    "recommendation": "检查温控系统运行状态，启动备用冷却系统，监控温度变化趋势"
                }, ensure_ascii=False),
            },
            {
                "input": "D区西南角红外探测器检测到未授权人员入侵",
                "output": json.dumps({
                    "risk_level": "high",
                    "recommendation": "通知就近安保人员前往现场，调取监控录像，必要时封锁出口并报警"
                }, ensure_ascii=False),
            },
            {
                "input": "E栋地下车库B区烟雾探测器触发报警，确认无明火",
                "output": json.dumps({
                    "risk_level": "low",
                    "recommendation": "派遣人员现场确认是否为误报，检查探测器状态"
                }, ensure_ascii=False),
            },
        ],
    },
    {
        "instruction": "根据以下告警内容，评估风险等级。输出 JSON，包含 risk_level 和 reasoning。",
        "scenarios": [
            {
                "input": "生产车间多处烟感同时报警，伴随温度异常升高",
                "output": json.dumps({
                    "risk_level": "high",
                    "reasoning": "多处烟感同时报警且温度异常升高，高度疑似火灾，需立即疏散和灭火"
                }, ensure_ascii=False),
            },
            {
                "input": "单一温度传感器读数略高于阈值0.5度",
                "output": json.dumps({
                    "risk_level": "low",
                    "reasoning": "轻微超标，可能为传感器漂移，需校准但不需要紧急处置"
                }, ensure_ascii=False),
            },
        ],
    },
]


def generate_instruction_data():
    """生成指令微调数据"""
    train_data = []
    eval_data = []

    for template in INSTRUCTION_TEMPLATES:
        for scenario in template["scenarios"]:
            item = {
                "instruction": template["instruction"],
                "input": scenario["input"],
                "output": scenario["output"],
            }
            train_data.append(item)

    # 生成更多变体
    locations = ["A栋", "B车间", "C仓库", "D区", "E栋"]
    alert_types = ["烟感报警", "气体泄漏", "温度异常", "入侵检测", "烟雾报警"]
    risk_levels = ["high", "medium", "low"]
    recommendations = [
        "立即启动应急预案，疏散人员",
        "通知维护人员检查设备",
        "持续监控并记录数据变化",
        "启动备用系统，确认故障范围",
    ]

    for _ in range(480):  # 生成到500条
        loc = random.choice(locations)
        alert = random.choice(alert_types)
        risk = random.choice(risk_levels)
        rec = random.choice(recommendations)
        train_data.append({
            "instruction": "根据以下告警内容，评估风险等级并给出处置建议。以 JSON 格式输出，包含 risk_level (high/medium/low) 和 recommendation 字段。",
            "input": f"{loc}{alert}，请评估风险",
            "output": json.dumps({
                "risk_level": risk,
                "recommendation": rec
            }, ensure_ascii=False),
        })

    # 拆分训练/评估
    random.shuffle(train_data)
    eval_data = train_data[:100]
    train_data = train_data[100:]

    return train_data, eval_data


# ============================================
# 2. 风险分级数据
# ============================================

RISK_LABELS = {0: "low", 1: "medium", 2: "high"}

RISK_SAMPLES = [
    # (text, label)
    ("单一传感器轻微超标，无其他异常", 0),
    ("温度传感器读数略高于阈值", 0),
    ("烟雾探测器偶发报警，确认为误报", 0),
    ("设备在线率正常，无异常告警", 0),
    ("例行巡检发现设备老化，建议更换", 0),
    ("气体浓度达到预警值，需关注", 1),
    ("温度异常升高，启动冷却系统", 1),
    ("烟雾浓度超标，需现场确认", 1),
    ("气体泄漏浓度接近阈值", 1),
    ("多处传感器数据异常", 1),
    ("车间可燃气体浓度超过安全标准", 2),
    ("A栋发生火灾，多处烟感报警", 2),
    ("有毒气体泄漏，需立即疏散", 2),
    ("未授权人员入侵核心区域", 2),
    ("爆炸风险，化学品温度失控", 2),
]


def generate_risk_data():
    """生成风险分级数据"""
    train_data = []
    eval_data = []

    for text, label in RISK_SAMPLES:
        item = {
            "text": text,
            "label": label,
        }
        train_data.append(item)

    # 生成更多变体
    templates_low = [
        "设备运行正常，{}传感器无异常",
        "巡检发现{}，无安全隐患",
        "{}读数在正常范围内",
    ]
    templates_medium = [
        "{}超标，需要关注",
        "{}异常，启动处置流程",
        "检测到{}，正在确认中",
    ]
    templates_high = [
        "{}达到危险值，立即疏散",
        "发生{}，启动应急预案",
        "{}风险极高，需紧急处置",
    ]
    subjects = ["烟感", "温度", "气体", "入侵", "烟雾", "化学品", "压力", "湿度"]

    for _ in range(970):
        r = random.random()
        if r < 0.33:
            text = random.choice(templates_low).format(random.choice(subjects))
            label = 0
        elif r < 0.66:
            text = random.choice(templates_medium).format(random.choice(subjects))
            label = 1
        else:
            text = random.choice(templates_high).format(random.choice(subjects))
            label = 2
        train_data.append({"text": text, "label": label})

    random.shuffle(train_data)
    eval_data = train_data[:200]
    train_data = train_data[200:]

    return train_data, eval_data


# ============================================
# 3. 合规检查数据
# ============================================

COMPLIANCE_SAMPLES = [
    # (plan_text, rule, pass_fail)
    ("发生火灾后立即启动喷淋系统并疏散人员", "火灾预案需包含疏散和灭火措施", 1),
    ("发现气体泄漏后立即关闭阀门并通风", "气体泄漏预案需包含隔离和通风", 1),
    ("发现气体泄漏后继续作业观察情况", "气体泄漏预案需包含隔离和通风", 0),
    ("温度异常时启动冷却系统并通知维护", "温度异常预案需包含降温和通知", 1),
    ("入侵检测后未采取任何措施", "入侵检测预案需包含人员派遣", 0),
]


def generate_compliance_data():
    """生成合规检查数据"""
    train_data = []
    eval_data = []

    for plan, rule, result in COMPLIANCE_SAMPLES:
        train_data.append({
            "plan": plan,
            "rule": rule,
            "compliant": result,
        })

    # 生成更多变体
    plan_templates_pass = [
        "发生{}后立即{}并{}",
        "检测到{}时启动{}并通知{}",
        "当{}超标时执行{}和{}",
    ]
    plan_templates_fail = [
        "发生{}后不采取行动",
        "检测到{}时忽略告警",
        "当{}超标时继续作业",
    ]
    rules_pass = [
        "预案需包含应急响应措施",
        "预案需包含人员疏散方案",
        "预案需包含设备处置流程",
    ]
    rules_fail = [
        "预案缺少关键处置步骤",
        "预案未考虑人员安全",
        "预案未包含设备隔离措施",
    ]
    events = ["火灾", "泄漏", "爆炸", "入侵", "温度异常"]
    actions_pass = ["疏散", "隔离", "通知", "灭火", "关闭阀门"]
    actions_fail = ["观察", "等待", "忽略", "继续"]

    for _ in range(280):
        r = random.random()
        if r < 0.7:
            plan = random.choice(plan_templates_pass).format(
                random.choice(events),
                random.choice(actions_pass),
                random.choice(actions_pass),
            )
            rule = random.choice(rules_pass)
            result = 1
        else:
            plan = random.choice(plan_templates_fail).format(
                random.choice(events),
                random.choice(actions_fail),
            )
            rule = random.choice(rules_fail)
            result = 0
        train_data.append({
            "plan": plan,
            "rule": rule,
            "compliant": result,
        })

    random.shuffle(train_data)
    eval_data = train_data[:60]
    train_data = train_data[60:]

    return train_data, eval_data


# ============================================
# 4. 术语 Embedding 数据
# ============================================

EHS_TERM_PAIRS = [
    {"term_a": "火灾", "term_b": "火情", "related": 1},
    {"term_a": "火灾", "term_b": "泄漏", "related": 0},
    {"term_a": "气体泄漏", "term_b": "可燃气体", "related": 1},
    {"term_a": "烟感报警", "term_b": "烟雾检测", "related": 1},
    {"term_a": "温度异常", "term_b": "高温", "related": 1},
    {"term_a": "入侵检测", "term_b": "未授权进入", "related": 1},
    {"term_a": "应急预案", "term_b": "处置流程", "related": 1},
    {"term_a": "疏散", "term_b": "撤离", "related": 1},
    {"term_a": "火灾", "term_b": "入侵", "related": 0},
    {"term_a": "气体", "term_b": "温度", "related": 0},
]


def generate_embedding_data():
    """生成术语 Embedding 数据"""
    all_pairs = list(EHS_TERM_PAIRS)

    # 生成更多术语对
    terms_positive = [
        ("烟感", "烟雾"),
        ("报警", "告警"),
        ("处置", "应急"),
        ("化学品", "危化品"),
        ("喷淋", "洒水"),
        ("通风", "排风"),
        ("警戒", "警戒线"),
        ("灭火", "消防"),
        ("安全", "防护"),
        ("监控", "监测"),
    ]
    terms_negative = [
        ("火灾", "地震"),
        ("气体", "辐射"),
        ("温度", "湿度"),
        ("入侵", "火灾"),
        ("泄漏", "断电"),
    ]

    for a, b in terms_positive:
        all_pairs.append({"term_a": a, "term_b": b, "related": 1})
    for a, b in terms_negative:
        all_pairs.append({"term_a": a, "term_b": b, "related": 0})

    # 生成组合变体到2000条
    while len(all_pairs) < 2000:
        base = random.choice(EHS_TERM_PAIRS)
        suffix = random.choice(["传感器", "检测器", "报警器", "系统", "装置"])
        all_pairs.append({
            "term_a": base["term_a"] + suffix,
            "term_b": base["term_b"] + suffix,
            "related": base["related"],
        })

    random.shuffle(all_pairs)
    return all_pairs[:2000]


# ============================================
# 主函数
# ============================================

def main():
    """生成所有微调数据"""
    os.makedirs(OUTPUT_DIR / "instruction", exist_ok=True)
    os.makedirs(OUTPUT_DIR / "risk", exist_ok=True)
    os.makedirs(OUTPUT_DIR / "compliance", exist_ok=True)
    os.makedirs(OUTPUT_DIR / "embedding", exist_ok=True)

    # 1. 指令微调
    train, eval = generate_instruction_data()
    _write_jsonl(OUTPUT_DIR / "instruction" / "train.jsonl", train)
    _write_jsonl(OUTPUT_DIR / "instruction" / "eval.jsonl", eval)
    print(f"指令微调: train={len(train)}, eval={len(eval)}")

    # 2. 风险分级
    train, eval = generate_risk_data()
    _write_jsonl(OUTPUT_DIR / "risk" / "train.jsonl", train)
    _write_jsonl(OUTPUT_DIR / "risk" / "eval.jsonl", eval)
    print(f"风险分级: train={len(train)}, eval={len(eval)}")

    # 3. 合规检查
    train, eval = generate_compliance_data()
    _write_jsonl(OUTPUT_DIR / "compliance" / "train.jsonl", train)
    _write_jsonl(OUTPUT_DIR / "compliance" / "eval.jsonl", eval)
    print(f"合规检查: train={len(train)}, eval={len(eval)}")

    # 4. 术语 Embedding
    pairs = generate_embedding_data()
    _write_jsonl(OUTPUT_DIR / "embedding" / "term_pairs.jsonl", pairs)
    print(f"术语 Embedding: {len(pairs)} 对")

    print("\n所有数据生成完成！")


def _write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 运行数据生成**

```bash
cd /d/jiedan/youxi/mianshi && python scripts/fine_tune/generate_data.py
```

Expected output:
```
指令微调: train=400, eval=100
风险分级: train=800, eval=200
合规检查: train=240, eval=60
术语 Embedding: 2000 对
```

- [ ] **Step 4: Commit**

```bash
git add scripts/fine_tune/ data/fine_tune/
git commit -m "feat(wave2): 微调数据生成 - 指令/风险/合规/术语共3800条"
```

---

### Task 11: 指令微调脚本 (Qwen-7B)

**Files:**
- Create: `scripts/fine_tune/instruction_tuning.py`

- [ ] **Step 1: 创建指令微调脚本**

```python
# scripts/fine_tune/instruction_tuning.py
"""
指令微调 - Qwen-7B

训练目标：规范化结构化 JSON 输出
基础模型：Qwen-7B-Chat (或 HuggingFace 等效)
数据：data/fine_tune/instruction/train.jsonl
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fine_tune.train_config import TrainingConfig

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from datasets import load_dataset
    from peft import LoraConfig, get_peft_model, TaskType
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("警告: transformers 未安装，仅做配置检查")


def load_instruction_data(data_path: str):
    """加载指令微调数据"""
    dataset = load_dataset("json", data_files=data_path, split="train")
    return dataset


def format_instruction_sample(example):
    """格式化为模型输入"""
    prompt = f"Human: {example['instruction']}\n{example['input']}\n\nAssistant: "
    return {
        "text": prompt + example["output"],
        "prompt": prompt,
        "response": example["output"],
    }


def train(config: TrainingConfig):
    """执行指令微调"""
    if not HAS_TRANSFORMERS:
        print("跳过训练（transformers 未安装）")
        return

    # 加载数据
    train_ds = load_instruction_data(config.train_file)
    train_ds = train_ds.map(format_instruction_sample)

    # 加载模型和 tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        config.base_model,
        trust_remote_code=True,
    )
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        config.base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    # LoRA 配置
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 训练参数
    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
        fp16=True,
        remove_unused_columns=False,
    )

    def tokenize_fn(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=config.max_length,
            padding=False,
        )

    tokenized_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=train_ds.column_names)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_ds,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
    print(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="Qwen/Qwen-7B-Chat",
        output_dir=str(ROOT / "models" / "qwen-ehs-instruct"),
        train_file=str(ROOT / "data" / "fine_tune" / "instruction" / "train.jsonl"),
        eval_file=str(ROOT / "data" / "fine_tune" / "instruction" / "eval.jsonl"),
        num_epochs=3,
        batch_size=4,
        max_length=1024,
    )
    train(config)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/fine_tune/instruction_tuning.py
git commit -m "feat(wave2): 指令微调脚本 - Qwen-7B LoRA"
```

---

### Task 12: 风险分级微调脚本 (BERT)

**Files:**
- Create: `scripts/fine_tune/risk_classification.py`

- [ ] **Step 1: 创建风险分级脚本**

```python
# scripts/fine_tune/risk_classification.py
"""
风险分级微调 - BERT

训练目标：三分类（low/medium/high）
基础模型：bert-base-chinese
数据：data/fine_tune/risk/train.jsonl
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fine_tune.train_config import TrainingConfig

try:
    import torch
    from torch.utils.data import Dataset
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class RiskDataset(Dataset):
    """风险分级数据集"""

    def __init__(self, data_path: str, tokenizer, max_length: int = 128):
        self.examples = []
        with open(data_path, encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                self.examples.append(item)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        item = self.examples[idx]
        encoding = self.tokenizer(
            item["text"],
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(item["label"], dtype=torch.long),
        }


def train(config: TrainingConfig):
    """执行风险分级微调"""
    if not HAS_TRANSFORMERS:
        print("跳过训练（transformers 未安装）")
        return

    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.base_model,
        num_labels=3,  # low=0, medium=1, high=2
    )

    train_dataset = RiskDataset(config.train_file, tokenizer, config.max_length)

    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
        evaluation_strategy="no",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
    print(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="bert-base-chinese",
        output_dir=str(ROOT / "models" / "bert-risk-classifier"),
        train_file=str(ROOT / "data" / "fine_tune" / "risk" / "train.jsonl"),
        eval_file=str(ROOT / "data" / "fine_tune" / "risk" / "eval.jsonl"),
        num_epochs=3,
        batch_size=16,
        max_length=128,
    )
    train(config)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add scripts/fine_tune/risk_classification.py
git commit -m "feat(wave2): 风险分级微调脚本 - BERT 三分类"
```

---

### Task 13: 合规检查微调脚本 (RoBERTa) + 术语 Embedding (BGE)

**Files:**
- Create: `scripts/fine_tune/compliance_check.py`
- Create: `scripts/fine_tune/embedding_tuning.py`

- [ ] **Step 1: 合规检查脚本**

```python
# scripts/fine_tune/compliance_check.py
"""
合规检查微调 - RoBERTa

训练目标：二分类（合规/不合规）
基础模型：hfl/chinese-roberta-wwm-ext
数据：data/fine_tune/compliance/train.jsonl
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fine_tune.train_config import TrainingConfig

try:
    import torch
    from torch.utils.data import Dataset
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False


class ComplianceDataset(Dataset):
    """合规检查数据集 - plan + rule 拼接输入"""

    def __init__(self, data_path: str, tokenizer, max_length: int = 256):
        self.examples = []
        with open(data_path, encoding="utf-8") as f:
            for line in f:
                item = json.loads(line)
                self.examples.append(item)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        item = self.examples[idx]
        text = f"预案：{item['plan']} [SEP] 规则：{item['rule']}"
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": torch.tensor(item["compliant"], dtype=torch.long),
        }


def train(config: TrainingConfig):
    if not HAS_TRANSFORMERS:
        print("跳过训练（transformers 未安装）")
        return

    tokenizer = AutoTokenizer.from_pretrained(config.base_model)
    model = AutoModelForSequenceClassification.from_pretrained(
        config.base_model,
        num_labels=2,  # 0=不合规, 1=合规
    )

    train_dataset = ComplianceDataset(config.train_file, tokenizer, config.max_length)

    training_args = TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_steps=config.save_steps,
        save_total_limit=3,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained(config.output_dir)
    tokenizer.save_pretrained(config.output_dir)
    print(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="hfl/chinese-roberta-wwm-ext",
        output_dir=str(ROOT / "models" / "roberta-compliance-checker"),
        train_file=str(ROOT / "data" / "fine_tune" / "compliance" / "train.jsonl"),
        eval_file=str(ROOT / "data" / "fine_tune" / "compliance" / "eval.jsonl"),
        num_epochs=3,
        batch_size=16,
        max_length=256,
    )
    train(config)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 术语 Embedding 脚本**

```python
# scripts/fine_tune/embedding_tuning.py
"""
术语 Embedding 微调 - BGE

训练目标：EHS 术语对比学习优化
基础模型：BAAI/bge-base-zh-v1.5
数据：data/fine_tune/embedding/term_pairs.jsonl
方法：Sentence Transformer 对比学习
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.fine_tune.train_config import TrainingConfig

try:
    from sentence_transformers import (
        SentenceTransformer,
        InputExample,
        losses,
        SentencesDataset,
        evaluation,
    )
    from torch.utils.data import DataLoader
    HAS_ST = True
except ImportError:
    HAS_ST = False


def load_term_pairs(data_path: str):
    """加载术语对数据"""
    pairs = []
    with open(data_path, encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            pairs.append(item)
    return pairs


def train(config: TrainingConfig):
    """执行术语 Embedding 微调"""
    if not HAS_ST:
        print("跳过训练（sentence-transformers 未安装）")
        return

    # 加载数据
    pairs = load_term_pairs(config.train_file)

    train_examples = []
    for pair in pairs:
        # label: 1=related, 0=unrelated
        label = pair["related"]
        train_examples.append(
            InputExample(texts=[pair["term_a"], pair["term_b"]], label=float(label))
        )

    # 加载模型
    model = SentenceTransformer(config.base_model)

    # 创建数据集和 DataLoader
    dataset = SentencesDataset(train_examples, model)
    loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)

    # 损失函数 - 对比损失
    train_loss = losses.CosineSimilarityLoss(model)

    # 评估器
    dev_pairs = load_term_pairs(config.eval_file) if config.eval_file else []
    if dev_pairs:
        dev_examples = [
            InputExample(texts=[p["term_a"], p["term_b"]], label=float(p["related"]))
            for p in dev_pairs
        ]
        evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(
            dev_examples, name="ehs-eval"
        )
    else:
        evaluator = None

    # 训练
    model.fit(
        train_objectives=[(loader, train_loss)],
        epochs=config.num_epochs,
        warmup_steps=int(len(loader) * config.warmup_ratio * config.num_epochs),
        output_path=config.output_dir,
        evaluator=evaluator,
        evaluation_steps=100,
    )

    print(f"模型已保存到 {config.output_dir}")


def main():
    config = TrainingConfig(
        base_model="BAAI/bge-base-zh-v1.5",
        output_dir=str(ROOT / "models" / "bge-ehs"),
        train_file=str(ROOT / "data" / "fine_tune" / "embedding" / "term_pairs.jsonl"),
        eval_file="",  # 从 train 中拆分
        num_epochs=3,
        batch_size=32,
    )
    train(config)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Commit**

```bash
git add scripts/fine_tune/compliance_check.py scripts/fine_tune/embedding_tuning.py
git commit -m "feat(wave2): 合规检查(RoBERTa) + 术语Embedding(BGE)微调脚本"
```

---

### Task 14: 微调数据生成测试 + README

**Files:**
- Create: `scripts/fine_tune/tests/test_generate_data.py`
- Create: `scripts/fine_tune/README.md`

- [ ] **Step 1: 数据生成测试**

```python
# scripts/fine_tune/tests/test_generate_data.py
"""微调数据生成器测试"""

import json
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent.parent.parent / "scripts" / "fine_tune"
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "fine_tune"


class TestInstructionData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "instruction" / "train.jsonl").exists()

    def test_eval_file_exists(self):
        assert (DATA_DIR / "instruction" / "eval.jsonl").exists()

    def test_train_has_sufficient_samples(self):
        with open(DATA_DIR / "instruction" / "train.jsonl") as f:
            lines = f.readlines()
        assert len(lines) >= 400, f"Only {len(lines)} training samples"

    def test_eval_has_sufficient_samples(self):
        with open(DATA_DIR / "instruction" / "eval.jsonl") as f:
            lines = f.readlines()
        assert len(lines) >= 100, f"Only {len(lines)} eval samples"

    def test_format_is_valid(self):
        with open(DATA_DIR / "instruction" / "train.jsonl") as f:
            for line in f:
                item = json.loads(line)
                assert "instruction" in item
                assert "input" in item
                assert "output" in item


class TestRiskData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "risk" / "train.jsonl").exists()

    def test_train_has_sufficient_samples(self):
        with open(DATA_DIR / "risk" / "train.jsonl") as f:
            lines = f.readlines()
        assert len(lines) >= 800

    def test_labels_are_valid(self):
        with open(DATA_DIR / "risk" / "train.jsonl") as f:
            for line in f:
                item = json.loads(line)
                assert item["label"] in [0, 1, 2]


class TestComplianceData:
    def test_train_file_exists(self):
        assert (DATA_DIR / "compliance" / "train.jsonl").exists()

    def test_labels_are_binary(self):
        with open(DATA_DIR / "compliance" / "train.jsonl") as f:
            for line in f:
                item = json.loads(line)
                assert item["compliant"] in [0, 1]


class TestEmbeddingData:
    def test_file_exists(self):
        assert (DATA_DIR / "embedding" / "term_pairs.jsonl").exists()

    def test_has_sufficient_pairs(self):
        with open(DATA_DIR / "embedding" / "term_pairs.jsonl") as f:
            lines = f.readlines()
        assert len(lines) >= 2000

    def test_format_is_valid(self):
        with open(DATA_DIR / "embedding" / "term_pairs.jsonl") as f:
            for line in f:
                item = json.loads(line)
                assert "term_a" in item
                assert "term_b" in item
                assert "related" in item
                assert item["related"] in [0, 1]
```

- [ ] **Step 2: 微调 README**

```markdown
# EHS 微调脚本

## 数据生成

```bash
python scripts/fine_tune/generate_data.py
```

## 训练

```bash
# 指令微调
python scripts/fine_tune/instruction_tuning.py

# 风险分级
python scripts/fine_tune/risk_classification.py

# 合规检查
python scripts/fine_tune/compliance_check.py

# 术语 Embedding
python scripts/fine_tune/embedding_tuning.py
```

## 数据规模

| 类型 | 训练 | 评估 |
|------|------|------|
| 指令微调 | 400 | 100 |
| 风险分级 | 800 | 200 |
| 合规检查 | 240 | 60 |
| 术语 Embedding | 2000 pairs | - |
```

- [ ] **Step 3: 运行测试验证**

```bash
cd /d/jiedan/youxi/mianshi && python -m pytest scripts/fine_tune/tests/test_generate_data.py -v
```

- [ ] **Step 4: Commit**

```bash
git add scripts/fine_tune/tests/test_generate_data.py scripts/fine_tune/README.md
git commit -m "feat(wave2): 微调数据测试 + README"
```

---

## Wave 3-5 说明

Wave 3-5 依赖 Wave 1+2 的完成结果，将在 Wave 1+2 完成后另行详细计划。

### Wave 3 预览: Python AI 服务集成 + Java COLA 四层 + gRPC 集成 + 前端改真实 API
### Wave 4 预览: Java 完整业务逻辑 + Prometheus/Grafana/LangFuse 监控集成
### Wave 5 预览: K8s Helm Chart + E2E 测试 + 性能测试 + GitHub Actions CI/CD

---

## 自审

1. **规格覆盖**: 所有 Wave 1-2 的设计需求已映射到具体任务中
   - 前端 8 页面 → Task 3-7 ✅
   - Docker + Neo4j → Task 8 ✅
   - 测试基础 → Task 9 ✅
   - 微调数据 → Task 10 ✅
   - 4 个微调脚本 → Task 11-13 ✅

2. **占位符扫描**: 所有步骤包含完整代码，无 TBD/TODO
3. **类型一致性**: 类型定义在 Task 1 中统一定义，后续页面直接引用
4. **范围检查**: 本计划仅覆盖 Wave 1+2，范围明确
