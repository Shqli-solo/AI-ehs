"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Bell,
  FileText,
  BookOpen,
  Workflow,
  Cpu,
  Settings,
  Users,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/" },
  { label: "告警管理", icon: Bell, href: "/alerts" },
  { label: "预案管理", icon: FileText, href: "/plans" },
  { label: "知识库", icon: BookOpen, href: "/knowledge" },
  { label: "Agent 编排", icon: Workflow, href: "/agents" },
  { label: "模型管理", icon: Cpu, href: "/models" },
  { label: "系统设置", icon: Settings, href: "/settings" },
  { label: "用户管理", icon: Users, href: "/users" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 border-r bg-white">
      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              )}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
