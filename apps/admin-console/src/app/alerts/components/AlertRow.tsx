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
        <Button variant="ghost" size="sm" onClick={() => onView(alert)}>
          <Eye className="h-4 w-4" />
        </Button>
      </td>
    </tr>
  );
}
