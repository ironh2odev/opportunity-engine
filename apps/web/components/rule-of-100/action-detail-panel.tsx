import type { DailyAction, DailyActionStatus } from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { StatusBadge } from "./status-badge";

export function ActionDetailPanel({
  action,
  onStatusChange,
  onApprove,
  onComplete,
}: {
  action: DailyAction | null;
  onStatusChange: (status: DailyActionStatus) => void;
  onApprove: () => void;
  onComplete: () => void;
}) {
  if (!action) {
    return (
      <Card className="text-sm text-slate-300">
        Select an action to review draft details and approval controls.
      </Card>
    );
  }

  const completeDisabled = action.approvalRequired && action.status !== "approved";

  return (
    <Card className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="[font-family:var(--font-sora)] text-lg font-semibold text-white">Draft review</h3>
        <StatusBadge status={action.status} />
      </div>

      <div className="space-y-1 text-sm text-slate-300">
        <p className="text-white">{action.title}</p>
        <p>
          {action.targetName} · {action.targetRole} · {action.targetOrganisation}
        </p>
        <p>Source: {action.source}</p>
      </div>

      <section className="space-y-2 text-sm text-slate-200">
        <p className="font-semibold uppercase tracking-wide text-slate-300">Suggested action</p>
        <p className="rounded-lg border border-white/10 bg-white/5 p-3">{action.suggestedAction}</p>
      </section>

      <section className="space-y-2 text-sm text-slate-200">
        <p className="font-semibold uppercase tracking-wide text-slate-300">Suggested draft message</p>
        <p className="rounded-lg border border-white/10 bg-white/5 p-3">{action.suggestedMessage}</p>
      </section>

      <section className="space-y-2 text-sm text-slate-200">
        <p className="font-semibold uppercase tracking-wide text-slate-300">Rationale</p>
        <p className="rounded-lg border border-white/10 bg-white/5 p-3">{action.rationale}</p>
      </section>

      <section className="space-y-2 text-sm text-slate-200">
        <p className="font-semibold uppercase tracking-wide text-slate-300">Proof to reference</p>
        <p className="rounded-lg border border-white/10 bg-white/5 p-3">{action.proofToReference}</p>
      </section>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => onStatusChange("in_review")}
          className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5"
        >
          Move to in review
        </button>
        <button
          type="button"
          onClick={onApprove}
          className="rounded-lg bg-emerald-500/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400"
        >
          Approve draft
        </button>
        <button
          type="button"
          onClick={onComplete}
          disabled={completeDisabled}
          className="rounded-lg bg-cyan-500/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-45"
        >
          Complete action
        </button>
        <button
          type="button"
          onClick={() => onStatusChange("blocked")}
          className="rounded-lg border border-rose-400/40 px-3 py-2 text-sm text-rose-200 transition hover:bg-rose-500/10"
        >
          Block
        </button>
        <button
          type="button"
          onClick={() => onStatusChange("skipped")}
          className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5"
        >
          Skip
        </button>
      </div>

      {completeDisabled ? (
        <p className="rounded-lg border border-amber-400/40 bg-amber-500/10 p-3 text-xs text-amber-200">
          This action is outbound-capable. Approval is required before completion.
        </p>
      ) : null}
    </Card>
  );
}
