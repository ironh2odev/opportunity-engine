import { useEffect, useState } from "react";
import type {
  AIDraftActionResult,
  ActionDraftRevision,
  ApprovalRecord,
  DailyAction,
  DailyActionStatus,
} from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { StatusBadge } from "./status-badge";

export function ActionDetailPanel({
  action,
  approval,
  onStatusChange,
  onApprove,
  onComplete,
  onGenerateAiDraft,
  onUseDraft,
  draftRevisions,
  draftSavedAt,
  isLoading = false,
  actionError = null,
  onDismissError,
}: {
  action: DailyAction | null;
  approval?: ApprovalRecord | null;
  onStatusChange: (status: DailyActionStatus) => void;
  onApprove: () => void;
  onComplete: () => void;
  onGenerateAiDraft: (action: DailyAction) => Promise<AIDraftActionResult>;
  onUseDraft: (draft: AIDraftActionResult) => Promise<string | null>;
  draftRevisions: ActionDraftRevision[];
  draftSavedAt: string | null;
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
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiDraft, setAiDraft] = useState<AIDraftActionResult | null>(null);
  const [aiSaveLoading, setAiSaveLoading] = useState(false);
  const [aiSaveNotice, setAiSaveNotice] = useState<string | null>(null);

  const isJobRelated = action.opportunityType === "job" || action.channel === "job_application";

  async function handleGenerateDraft() {
    if (!action) {
      return;
    }
    setAiLoading(true);
    setAiError(null);
    try {
      const result = await onGenerateAiDraft(action);
      setAiDraft(result);
    } catch (error) {
      const maybe = error as { message?: string };
      setAiError(maybe.message ?? "Failed to generate AI draft.");
    } finally {
      setAiLoading(false);
    }
  }

  async function handleUseDraft() {
    if (!aiDraft) {
      return;
    }
    setAiSaveLoading(true);
    setAiError(null);
    try {
      const savedAt = await onUseDraft(aiDraft);
      const suffix = savedAt ? ` ${new Date(savedAt).toLocaleString()}` : "";
      setAiSaveNotice(`Saved as draft.${suffix} Manual review still required.`);
    } catch (error) {
      const maybe = error as { message?: string };
      setAiError(maybe.message ?? "Failed to save draft.");
    } finally {
      setAiSaveLoading(false);
    }
  }

  useEffect(() => {
    setAiError(null);
    setAiDraft(null);
    setAiSaveNotice(null);
  }, [action.id]);

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
        {action.sourceType === "personal_lead" ? (
          <div className="space-y-1 rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-3 text-xs text-cyan-100">
            <p className="font-semibold uppercase tracking-wide">Private lead action</p>
            <p>From Personal Mode</p>
            <p>Source lead: {action.sourceLeadName || action.sourceLeadOrganisation || "Personal lead"}</p>
            <p>Private mode: {action.privateMode ? "true" : "false"}</p>
          </div>
        ) : (
          <div className="space-y-1 rounded-lg border border-violet-400/30 bg-violet-500/10 p-3 text-xs text-violet-100">
            <p className="font-semibold uppercase tracking-wide">Mock demo action</p>
            <p>Public-safe demo dataset</p>
            <p>Private mode: false</p>
          </div>
        )}
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
        <p className="font-semibold uppercase tracking-wide text-slate-300">AI Assist</p>
        <div className="space-y-3 rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-3">
          <p className="text-xs text-cyan-100">
            AI output is draft-only and requires human review before any use. No auto-send, no auto-apply.
          </p>
          <button
            type="button"
            disabled={aiLoading}
            onClick={() => void handleGenerateDraft()}
            className="rounded-lg bg-cyan-400/90 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 disabled:opacity-45"
          >
            {aiLoading ? "Generating draft..." : "Generate draft"}
          </button>

          {aiError ? <p className="text-xs text-rose-200">{aiError}</p> : null}

          {aiDraft ? (
            <div className="space-y-2 text-xs text-slate-100">
              <p className="font-semibold uppercase tracking-wide text-cyan-100">Draft message</p>
              <p className="rounded-md border border-white/10 bg-white/5 p-2">{aiDraft.draftMessage}</p>

              {aiDraft.shortVersion ? (
                <>
                  <p className="font-semibold uppercase tracking-wide text-cyan-100">Short version</p>
                  <p className="rounded-md border border-white/10 bg-white/5 p-2">{aiDraft.shortVersion}</p>
                </>
              ) : null}

              <p className="font-semibold uppercase tracking-wide text-cyan-100">Reasoning summary</p>
              <p className="rounded-md border border-white/10 bg-white/5 p-2">{aiDraft.reasoningSummary}</p>

              <p className="font-semibold uppercase tracking-wide text-cyan-100">Risks or gaps</p>
              <ul className="list-disc pl-5 text-slate-200">
                {aiDraft.risksOrGaps.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>

              <p className="font-semibold uppercase tracking-wide text-cyan-100">Confidence</p>
              <p>{aiDraft.confidenceLabel}</p>

              <p className="font-semibold uppercase tracking-wide text-cyan-100">Review notes</p>
              <ul className="list-disc pl-5 text-slate-200">
                {aiDraft.reviewNotes.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>

              <button
                type="button"
                onClick={() => void handleUseDraft()}
                disabled={aiSaveLoading}
                className="rounded-lg border border-cyan-300/50 px-3 py-2 text-xs text-cyan-100 transition hover:bg-cyan-500/10"
              >
                {aiSaveLoading ? "Saving draft..." : "Use this draft"}
              </button>
            </div>
          ) : null}

          {aiSaveNotice ? <p className="text-xs text-emerald-200">{aiSaveNotice}</p> : null}
          {draftSavedAt ? (
            <p className="text-xs text-cyan-100">Latest saved draft at {new Date(draftSavedAt).toLocaleString()}</p>
          ) : null}
        </div>
      </section>

      <section className="space-y-2 text-sm text-slate-200">
        <p className="font-semibold uppercase tracking-wide text-slate-300">Draft history</p>
        {draftRevisions.length === 0 ? (
          <p className="rounded-lg border border-white/10 bg-white/5 p-3 text-xs text-slate-300">No saved drafts yet.</p>
        ) : (
          <div className="space-y-2">
            {draftRevisions.map((revision) => (
              <div key={revision.id} className="rounded-lg border border-white/10 bg-white/5 p-3 text-xs text-slate-200">
                <p className="font-semibold text-white">{revision.source.replaceAll("_", " ")}</p>
                <p>Created: {new Date(revision.createdAt).toLocaleString()}</p>
                <p>By: {revision.createdBy}</p>
                {revision.confidenceLabel ? <p>Confidence: {revision.confidenceLabel}</p> : null}
                <p className="mt-1 text-slate-100">{revision.draftMessage}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      {isJobRelated ? (
        <section className="space-y-2 rounded-lg border border-amber-400/40 bg-amber-500/10 p-3 text-xs text-amber-100">
          <p className="font-semibold uppercase tracking-wide">Job/CV safety</p>
          <p>Reframe real experience only.</p>
          <p>Do not invent experience.</p>
          <p>Human review required before use.</p>
          <p>CV/cover letter drafts are starting points, not final documents.</p>
        </section>
      ) : null}

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
