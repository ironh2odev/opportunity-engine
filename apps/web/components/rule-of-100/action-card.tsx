import type { DailyAction } from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { StatusBadge } from "./status-badge";

export function ActionCard({
  action,
  onSelect,
  selected,
}: {
  action: DailyAction;
  onSelect: (actionId: string) => void;
  selected: boolean;
}) {
  return (
    <Card
      className={`cursor-pointer space-y-3 border ${
        selected ? "border-accent/60 bg-accent/10" : "border-white/10 bg-slate-900/70"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">{action.channel.replaceAll("_", " ")}</p>
          <h4 className="mt-1 text-base font-semibold text-white">{action.title}</h4>
          {action.sourceType === "personal_lead" ? (
            <div className="mt-2 flex flex-wrap gap-2 text-[11px] uppercase tracking-wide">
              <span className="rounded-full bg-cyan-500/15 px-2 py-1 text-cyan-200">Private lead action</span>
              <span className="rounded-full bg-white/10 px-2 py-1 text-slate-200">From Personal Mode</span>
            </div>
          ) : (
            <div className="mt-2 flex flex-wrap gap-2 text-[11px] uppercase tracking-wide">
              <span className="rounded-full bg-violet-500/15 px-2 py-1 text-violet-200">Mock demo action</span>
              <span className="rounded-full bg-white/10 px-2 py-1 text-slate-200">Public-safe dataset</span>
            </div>
          )}
        </div>
        <StatusBadge status={action.status} />
      </div>

      <p className="text-sm text-slate-300">
        {action.targetName} · {action.targetRole} · {action.targetOrganisation}
      </p>

      {action.sourceType === "personal_lead" ? (
        <p className="text-xs text-cyan-100">
          Source lead: {action.sourceLeadName || action.sourceLeadOrganisation || "Personal lead"}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-white/10 px-2 py-1 text-slate-200">Fit {action.fitScore}/10</span>
        <span className="rounded-full bg-white/10 px-2 py-1 text-slate-200">
          Confidence {action.confidenceLabel}
        </span>
        {action.approvalRequired ? (
          <span className="rounded-full bg-amber-500/20 px-2 py-1 text-amber-200">Approval required</span>
        ) : (
          <span className="rounded-full bg-cyan-500/20 px-2 py-1 text-cyan-200">Non-outbound</span>
        )}
      </div>

      <button
        type="button"
        onClick={() => onSelect(action.id)}
        className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5"
      >
        Review draft
      </button>
    </Card>
  );
}
