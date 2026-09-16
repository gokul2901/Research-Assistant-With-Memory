"use client";

import React from "react";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { MobileNav } from "./MobileNav";
import { AddSourceModal } from "@/components/sources/AddSourceModal";
import { Toaster } from "sonner";
import { usePathname } from "next/navigation";

export interface AppShellProps {
  children: React.ReactNode;
  hideSidebar?: boolean;
}

export function AppShell({ children, hideSidebar = false }: AppShellProps) {
  const pathname = usePathname();
  const isLanding = pathname === "/";

  if (isLanding) {
    return (
      <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 relative selection:bg-indigo-500/30">
        <Navbar />
        <main className="flex-1">{children}</main>
        <AddSourceModal />
        <Toaster
          position="bottom-right"
          theme="dark"
          richColors
          closeButton
          toastOptions={{
            style: {
              background: "#0e121b",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              color: "#f3f4f6",
            },
          }}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 relative selection:bg-indigo-500/30">
      {/* Top sticky Navbar */}
      <Navbar />

      {/* Main Workspace Frame */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Desktop Sidebar */}
        {!hideSidebar && (
          <div className="hidden md:block">
            <Sidebar />
          </div>
        )}

        {/* Center / Main Content */}
        <main className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <MobileNav />

      {/* Global Add Source Modal */}
      <AddSourceModal />

      {/* Toaster */}
      <Toaster
        position="bottom-right"
        theme="dark"
        richColors
        closeButton
        toastOptions={{
          style: {
            background: "#0e121b",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            color: "#f3f4f6",
          },
        }}
      />
    </div>
  );
}
