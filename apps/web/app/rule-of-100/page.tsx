"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type {
  ActionChannel,
  ApprovalRecord,
  DailyAction,
  DailyActionStatus,
  DailyRollup,
  RuleOf100Plan,
} from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { ActionDetailPanel } from "../../components/rule-of-100/action-detail-panel";
import { ActionQueue } from "../../components/rule-of-100/action-queue";
import { PlannerSummary } from "../../components/rule-of-100/planner-summary";
import { type ApiError, ruleOf100Api } from "../../lib/rule-of-100-api";

export default function RuleOf100Page() {
  const [plan, setPlan] = useState<RuleOf100Plan | null>(null);
  const [actions, setActions] = useState<DailyAction[]>([]);
  const [rollup, setRollup] = useState<DailyRollup | null>(null);
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([]);
  const [selectedActionId, setSelectedActionId] = useState<string | null>(null);
  const [filter, setFilter] = useState<DailyActionStatus | "all">("all");
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [mutatingActionId, setMutatingActionId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [planSaving, setPlanSaving] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);

  const selectedAction = useMemo(
    () => actions.find((item) => item.id === selectedActionId) ?? null,
    [actions, selectedActionId],
  );

  const selectedApproval = useMemo(
    () => approvals.find((item) => item.actionId === selectedActionId) ?? null,
    [approvals, selectedActionId],
  );

  const loadData = useCallback(async () => {
    setLoadingInitial(true);
    setLoadError(null);
    try {
      const [planData, actionsData, rollupData, approvalsData] = await Promise.all([
        ruleOf100Api.getPlan(),
        ruleOf100Api.getActions(),
        ruleOf100Api.getRollup(),
        ruleOf100Api.getApprovals(),
      ]);
      setPlan(planData as RuleOf100Plan);
      setActions(actionsData as DailyAction[]);
      setRollup(rollupData);
      setApprovals(approvalsData);
      setSelectedActionId((current) => current ?? actionsData[0]?.id ?? null);
    } catch (err) {
      const apiErr = err as ApiError;
      setLoadError(
        apiErr.message ?? "Failed to load data. Is the FastAPI server running?",
      );
    } finally {
      setLoadingInitial(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const refreshRollup = useCallback(async () => {
    setRollup(await ruleOf100Api.getRollup());
  }, []);

  const refreshApprovals = useCallback(async () => {
    setApprovals(await ruleOf100Api.getApprovals());
  }, []);

  const refreshPlanAndRollup = useCallback(async () => {
    const [planData, rollupData] = await Promise.all([ruleOf100Api.getPlan(), ruleOf100Api.getRollup()]);
    setPlan(planData);
    setRollup(rollupData);
  }, []);

  async function updateTargetCount(value: number) {
    if (!plan) return;
    setPlanSaving(true);
    setPlanError(null);
    try {
      await ruleOf100Api.updatePlan({ target_count: value });
      await refreshPlanAndRollup();
    } catch (err) {
      setPlanError((err as ApiError).message);
      await refreshPlanAndRollup();
    } finally {
      setPlanSaving(false);
    }
  }

  async function updateAllocation(channel: ActionChannel, value: number) {
    if (!plan) return;
    setPlanSaving(true);
    setPlanError(null);
    try {
      await ruleOf100Api.updatePlan({ allocation: { [channel]: value } });
      await refreshPlanAndRollup();
    } catch (err) {
      setPlanError((err as ApiError).message);
      await refreshPlanAndRollup();
    } finally {
      setPlanSaving(false);
    }
  }

  async function handleStatusChange(status: DailyActionStatus) {
    if (!selectedActionId) return;
    setMutatingActionId(selectedActionId);
    setActionError(null);
    try {
      const updated = await ruleOf100Api.updateStatus(selectedActionId, status);
      setActions((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      await refreshRollup();
    } catch (err) {
      setActionError((err as ApiError).message);
    } finally {
      setMutatingActionId(null);
    }
  }

  async function handleApprove() {
    if (!selectedActionId) return;
    setMutatingActionId(selectedActionId);
    setActionError(null);
    try {
      const record = await ruleOf100Api.approveAction(selectedActionId);
      setActions((prev) =>
        prev.map((item) =>
          item.id === selectedActionId ? { ...item, status: "approved" as DailyActionStatus } : item,
        ),
      );
      setApprovals((prev) => {
        const existingIndex = prev.findIndex((item) => item.actionId === record.actionId);
        if (existingIndex === -1) {
          return [...prev, record];
        }
        const next = [...prev];
        next[existingIndex] = record;
        return next;
      });
      await refreshRollup();
      await refreshApprovals();
    } catch (err) {
      setActionError((err as ApiError).message);
    } finally {
      setMutatingActionId(null);
    }
  }

  async function handleComplete() {
    if (!selectedActionId) return;
    setMutatingActionId(selectedActionId);
    setActionError(null);
    try {
      const updated = await ruleOf100Api.completeAction(selectedActionId);
      setActions((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      await refreshRollup();
    } catch (err) {
      setActionError((err as ApiError).message);
    } finally {
      setMutatingActionId(null);
    }
  }

  if (loadingInitial) {
    return (
      <div className="soft-grid flex min-h-screen items-center justify-center bg-mesh-gradient text-slate-100">
        <p className="text-sm text-slate-300">Loading daily actions from API...</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="soft-grid flex min-h-screen items-center justify-center bg-mesh-gradient px-6 text-slate-100">
        <div className="max-w-lg space-y-4 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-8">
          <h2 className="[font-family:var(--font-sora)] text-xl font-semibold text-white">API unavailable</h2>
          <p className="text-sm text-rose-200">{loadError}</p>
          <p className="text-xs text-slate-300">
            Start the API server:{" "}
            <code className="rounded bg-white/10 px-1">
              cd apps/api &amp;&amp; uvicorn app.main:app --reload
            </code>
          </p>
          <button
            type="button"
            onClick={() => void loadData()}
            className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="soft-grid min-h-screen bg-mesh-gradient px-4 py-6 text-slate-100 sm:px-6 lg:px-8">
      <main className="mx-auto max-w-[1400px] space-y-6">
        <header className="rounded-2xl border border-white/10 bg-slate-900/60 p-6 shadow-aura backdrop-blur">
          <p className="text-xs uppercase tracking-[0.2em] text-accent/90">Rule of 100 Engine</p>
          <h1 className="mt-2 [font-family:var(--font-sora)] text-3xl font-semibold text-white sm:text-4xl">
            Daily action planning with human-controlled execution
          </h1>
          <div className="mt-3 grid gap-2 text-sm text-slate-200 sm:grid-cols-2">
            <p>Draft-only workflow</p>
            <p>Human approval required</p>
            <p>No auto-send</p>
            <p>No auto-apply</p>
            <p>Manual execution only</p>
          </div>
        </header>

        {plan && rollup && (
          <PlannerSummary
            plan={plan}
            rollup={rollup}
            onTargetCountChange={updateTargetCount}
            onAllocationChange={updateAllocation}
            isSaving={planSaving}
          />
        )}

        {planError ? (
          <Card className="border-amber-400/30 bg-amber-500/10 text-sm text-amber-100">
            {planError}
          </Card>
        ) : null}

        <section className="grid gap-4 xl:grid-cols-[1.35fr_1fr]">
          <ActionQueue
            actions={actions}
            selectedActionId={selectedActionId}
            onSelect={(id) => {
              setSelectedActionId(id);
              setActionError(null);
            }}
            currentFilter={filter}
            onFilterChange={setFilter}
          />
          <ActionDetailPanel
            action={selectedAction}
            approval={selectedApproval}
            onStatusChange={(status) => void handleStatusChange(status)}
            onApprove={() => void handleApprove()}
            onComplete={() => void handleComplete()}
            isLoading={mutatingActionId === selectedActionId}
            actionError={actionError}
            onDismissError={() => setActionError(null)}
          />
        </section>

        <Card className="border-amber-400/30 bg-amber-500/10 text-sm text-amber-100">
          Outbound-capable actions can only be completed after explicit approval. This MVP is mock-data-first
          and does not send messages, submit applications, or call external platforms.
        </Card>
      </main>
    </div>
  );
}
