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

export function AlertDrawer({ alert, open, onClose, onProcess }: AlertDrawerProps) {
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
              <h4 className="font-medium text-sm text-blue-900">AI 处置建议</h4>
              <p className="text-sm text-blue-800 mt-1">{alert.aiRecommendation}</p>
            </div>
          )}
          {alert.associatedPlans && alert.associatedPlans.length > 0 && (
            <div>
              <h4 className="font-medium text-sm text-gray-700">关联预案</h4>
              <div className="flex gap-2 mt-2">
                {alert.associatedPlans.map((plan) => (
                  <span key={plan} className="px-2 py-1 bg-gray-100 rounded text-xs">
                    {plan}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        <DrawerFooter>
          <Button onClick={() => onProcess(alert.id)} disabled={alert.status !== "pending"}>
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
