import type { Opportunity } from "@aoe/shared-types";
import { Card } from "@aoe/ui";

const statusColor: Record<Opportunity["status"], string> = {
  new: "bg-cyan-500/25 text-cyan-200",
  reviewed: "bg-sky-500/25 text-sky-200",
  saved: "bg-emerald-500/25 text-emerald-200",
  contacted: "bg-amber-500/25 text-amber-200",
  rejected: "bg-rose-500/25 text-rose-200",
};

export function OpportunityCard({ item }: { item: Opportunity }) {
  return (
    <Card className="space-y-4 border-white/15 bg-slate-900/75">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="[font-family:var(--font-sora)] text-lg text-white">
            {item.title}
          </h3>
          <p className="text-sm text-slate-300">
            {item.organization} · {item.source}
          </p>
        </div>
        <span className="rounded-full bg-accent/20 px-3 py-1 text-xs font-medium text-accent">
          {item.relevanceScore}% fit
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-white/10 px-3 py-1 text-slate-200">
          {item.category}
        </span>
        <span className={`rounded-full px-3 py-1 font-medium ${statusColor[item.status]}`}>
          {item.status}
        </span>
      </div>

      <div className="space-y-2 text-sm text-slate-200">
        <p>{item.summary}</p>
        <p className="text-slate-300">
          <span className="text-slate-100">Why it matches:</span> {item.whyItMatches}
        </p>
        <p className="text-slate-300">
          <span className="text-slate-100">Suggested action:</span> {item.suggestedAction}
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <button className="rounded-lg bg-white px-3 py-2 text-sm font-medium text-slate-900 transition hover:bg-slate-200">
          Review
        </button>
        <button className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5">
          Save
        </button>
        <button className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5">
          Move to Outreach Queue
        </button>
      </div>
    </Card>
  );
}
