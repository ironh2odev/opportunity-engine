import type { DailyActionStatus } from "@aoe/shared-types";

const statusStyles: Record<DailyActionStatus, string> = {
  suggested: "bg-slate-500/20 text-slate-200 border-slate-400/30",
  in_review: "bg-amber-500/20 text-amber-200 border-amber-400/30",
  approved: "bg-emerald-500/20 text-emerald-200 border-emerald-400/30",
  completed: "bg-cyan-500/20 text-cyan-200 border-cyan-400/30",
  skipped: "bg-zinc-500/20 text-zinc-200 border-zinc-400/30",
  blocked: "bg-rose-500/20 text-rose-200 border-rose-400/30",
};

export function StatusBadge({ status }: { status: DailyActionStatus }) {
  return (
    <span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${statusStyles[status]}`}>
      {status.replace("_", " ")}
    </span>
  );
}
