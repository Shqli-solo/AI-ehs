export type AlertStatus = "pending" | "processing" | "resolved";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type AlertType = "fire" | "gas_leak" | "temperature" | "intrusion" | "smoke";

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
