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
