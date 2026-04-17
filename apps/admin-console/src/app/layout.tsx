import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { Toaster } from "@/components/ui/toaster";
import "./globals.css";

export const metadata = {
  title: "EHS 智能安保决策中台",
  description: "基于 GraphRAG + Multi-Agent 的智能安保系统",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="bg-gray-50 min-h-screen">
        <Header />
        <div className="pt-16 flex">
          <Sidebar />
          <main className="ml-64 flex-1 p-6">{children}</main>
        </div>
        <Toaster />
      </body>
    </html>
  );
}
