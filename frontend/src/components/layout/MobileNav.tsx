"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Database, Layers, Plus, Settings } from "lucide-react";
import { cn } from "@/lib/utils";
import { useResearch } from "@/context/ResearchContext";

export function MobileNav() {
  const pathname = usePathname();
  const { setIsAddSourceOpen } = useResearch();

  const items = [
    { href: "/research", label: "Research", icon: Compass },
    { href: "/sources", label: "Sources", icon: Database },
    {
      action: () => setIsAddSourceOpen(true),
      label: "Add",
      icon: Plus,
      isSpecial: true,
    },
    { href: "/sessions", label: "Sessions", icon: Layers },
    { href: "/settings", label: "Settings", icon: Settings },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-slate-800 bg-slate-950/90 backdrop-blur-xl px-2 py-1.5 flex items-center justify-around">
      {items.map((item, idx) => {
        if (item.isSpecial) {
          return (
            <button
              key={idx}
              onClick={item.action}
              className="flex flex-col items-center justify-center -mt-4 p-2.5 rounded-full bg-gradient-to-r from-indigo-500 to-violet-600 text-white shadow-lg shadow-indigo-950/50 border border-indigo-400/40"
              aria-label="Add Source"
            >
              <Plus className="w-5 h-5" />
            </button>
          );
        }

        const Icon = item.icon;
        const isActive =
          pathname === item.href ||
          (item.href !== "/" && pathname.startsWith(item.href || ""));

        return (
          <Link
            key={item.href}
            href={item.href || "/"}
            className={cn(
              "flex flex-col items-center gap-1 py-1 px-3 rounded-lg text-[10px] font-medium transition-colors",
              isActive
                ? "text-indigo-400"
                : "text-slate-400 hover:text-slate-200"
            )}
          >
            <Icon className="w-4 h-4" />
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
