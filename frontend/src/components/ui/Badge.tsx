import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "indigo" | "outline" | "secondary";
  size?: "sm" | "md";
}

export function Badge({
  className,
  variant = "default",
  size = "sm",
  children,
  ...props
}: BadgeProps) {
  const sizeClasses = {
    sm: "px-2 py-0.5 text-[11px] font-medium tracking-tight",
    md: "px-2.5 py-1 text-xs font-medium",
  };

  const variantClasses = {
    default: "bg-slate-800 text-slate-300 border border-slate-700/80",
    secondary: "bg-slate-800/50 text-slate-400 border border-slate-700/40",
    success: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/25",
    warning: "bg-amber-500/10 text-amber-400 border border-amber-500/25",
    error: "bg-red-500/10 text-red-400 border border-red-500/25",
    indigo: "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30",
    outline: "bg-transparent text-slate-300 border border-slate-700",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full",
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
