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
