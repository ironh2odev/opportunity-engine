import type { ReactNode } from "react";
import { cn } from "../lib/cn";

interface CardProps {
  className?: string;
  children: ReactNode;
}

export function Card({ className, children }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-xl shadow-black/15 backdrop-blur",
        className,
      )}
    >
      {children}
    </div>
  );
}
