"use client";

import * as React from 'react';
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

  const categories = Array.from(new Set(plans.map((p) => p.category)));
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
                  <h4 className="font-medium text-sm text-gray-700">关联设备</h4>
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
