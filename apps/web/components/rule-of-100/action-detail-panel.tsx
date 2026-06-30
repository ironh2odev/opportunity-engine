import type { ApprovalRecord, DailyAction, DailyActionStatus } from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { StatusBadge } from "./status-badge";

export function ActionDetailPanel({
  action,
  approval,
  onStatusChange,
  onApprove,
  onComplete,
  isLoading = false,
  actionError = null,
  onDismissError,
}: {
  action: DailyAction | null;
  approval?: ApprovalRecord | null;
  onStatusChange: (status: DailyActionStatus) => void;
  onApprove: () => void;
  onComplete: () => void;
  isLoading?: boolean;
  actionError?: string | null;
  onDismissError?: () => void;
}) {
  if (!action) {
    return (
      <Card className="text-sm text-slate-300">
        Select an action to review draft details and approval controls.
      </Card>
    );
  }

  const completeDisabled = (action.approvalRequired && action.status !== "approved") || isLoading;
  const isApproved = action.status === "approved" || action.status === "completed" || Boolean(approval);

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

      <section className="space-y-2 text-sm text-slate-200">
        <p className="font-semibold uppercase tracking-wide text-slate-300">Approval</p>
        <div className="rounded-lg border border-white/10 bg-white/5 p-3 space-y-1">
          <p>
            <span className="text-slate-400">Status:</span>{" "}
            {isApproved ? "Approved" : "Not approved"}
          </p>
          <p>
            <span className="text-slate-400">Approved by:</span>{" "}
            {approval?.approvedBy ?? "-"}
          </p>
          <p>
            <span className="text-slate-400">Approved at:</span>{" "}
            {approval?.approvedAt ? new Date(approval.approvedAt).toLocaleString() : "-"}
          </p>
          <p>
            <span className="text-slate-400">Approval note:</span>{" "}
            {approval?.note ?? "-"}
          </p>
        </div>
      </section>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={isLoading}
          onClick={() => onStatusChange("in_review")}
          className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-45"
        >
          Move to in review
        </button>
        <button
          type="button"
          disabled={isLoading}
          onClick={onApprove}
          className="rounded-lg bg-emerald-500/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-45"
        >
          {isLoading ? "Saving…" : "Approve draft"}
        </button>
        <button
          type="button"
          onClick={onComplete}
          disabled={completeDisabled}
          className="rounded-lg bg-cyan-500/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-45"
        >
          {isLoading ? "Saving…" : "Complete action"}
        </button>
        <button
          type="button"
          disabled={isLoading}
          onClick={() => onStatusChange("blocked")}
          className="rounded-lg border border-rose-400/40 px-3 py-2 text-sm text-rose-200 transition hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-45"
        >
          Block
        </button>
        <button
          type="button"
          disabled={isLoading}
          onClick={() => onStatusChange("skipped")}
          className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-45"
        >
          Skip
        </button>
      </div>

      {actionError ? (
        <div className="flex items-start justify-between gap-2 rounded-lg border border-rose-400/40 bg-rose-500/10 p-3 text-xs text-rose-200">
          <p>{actionError}</p>
          {onDismissError && (
            <button type="button" onClick={onDismissError} className="shrink-0 text-rose-300 hover:text-white">
              ✕
            </button>
          )}
        </div>
      ) : null}

      {!actionError && action.approvalRequired && !isApproved ? (
        <p className="rounded-lg border border-amber-400/40 bg-amber-500/10 p-3 text-xs text-amber-200">
          Approval required before completion for outbound-capable actions.
        </p>
      ) : null}
    </Card>
  );
}
