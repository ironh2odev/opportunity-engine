"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { label: "Home / Daily Opportunities", href: "/" },
  { label: "Rule of 100 Engine", href: "/rule-of-100" },
  { label: "Personal Leads", href: "/personal-leads" },
];

export function GlobalNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-[1500px] flex-wrap items-center gap-2 px-4 py-3 sm:px-6 lg:px-8">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-accent text-slate-950"
                  : "border border-white/15 text-slate-200 hover:bg-white/5"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
        <span className="ml-auto text-xs text-slate-400">Manual execution only</span>
      </div>
    </header>
  );
}
