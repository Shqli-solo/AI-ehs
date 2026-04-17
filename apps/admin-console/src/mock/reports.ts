import { ReportRecord } from "@/types/report";

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
