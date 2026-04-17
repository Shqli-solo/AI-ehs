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
