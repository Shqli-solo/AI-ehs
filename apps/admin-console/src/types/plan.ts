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
