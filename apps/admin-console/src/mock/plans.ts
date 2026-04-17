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
