"use client";

import { useMemo, useState } from "react";
import type { ActionChannel, DailyAction, DailyActionStatus, DailyRollup } from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { ActionDetailPanel } from "../../components/rule-of-100/action-detail-panel";
import { ActionQueue } from "../../components/rule-of-100/action-queue";
import { PlannerSummary } from "../../components/rule-of-100/planner-summary";
import { dailyActions, mockApprovalRecords, ruleOf100Plan } from "../../lib/mock-data";

export default function RuleOf100Page() {
  const [plan, setPlan] = useState(ruleOf100Plan);
  const [actions, setActions] = useState<DailyAction[]>(dailyActions);
  const [selectedActionId, setSelectedActionId] = useState<string | null>(dailyActions[0]?.id ?? null);
  const [approvedActionIds, setApprovedActionIds] = useState<Set<string>>(
    new Set(mockApprovalRecords.map((record) => record.actionId)),
  );
  const [filter, setFilter] = useState<DailyActionStatus | "all">("all");

  const selectedAction = useMemo(
    () => actions.find((item) => item.id === selectedActionId) ?? null,
    [actions, selectedActionId],
  );

  const rollup: DailyRollup = useMemo(() => {
    const completedCount = actions.filter((item) => item.status === "completed").length;
    const pendingReviewCount = actions.filter((item) => item.status === "in_review").length;
    const approvedCount = actions.filter((item) => item.status === "approved").length;
    const byChannel = actions.reduce<Partial<Record<ActionChannel, number>>>((acc, item) => {
      acc[item.channel] = (acc[item.channel] ?? 0) + 1;
      return acc;
    }, {});

    return {
      date: plan.date,
      targetCount: plan.targetCount,
      completedCount,
      progressPercent: Math.round((completedCount / Math.max(plan.targetCount, 1)) * 100),
      pendingReviewCount,
      approvedCount,
      completedApprovedCount: actions.filter(
        (item) => item.status === "completed" && (!item.approvalRequired || approvedActionIds.has(item.id)),
      ).length,
      byChannel,
    };
  }, [actions, approvedActionIds, plan.targetCount]);

  function updateTargetCount(value: number) {
    const safeValue = Math.min(Math.max(value || plan.minTarget, plan.minTarget), plan.maxTarget);
    setPlan((prev) => ({ ...prev, targetCount: safeValue }));
  }

  function updateAllocation(channel: ActionChannel, value: number) {
    const safeValue = Math.max(0, Number.isFinite(value) ? value : 0);
    setPlan((prev) => ({
      ...prev,
      allocation: {
        ...prev.allocation,
        [channel]: safeValue,
      },
    }));
  }

  function updateStatus(status: DailyActionStatus) {
    if (!selectedActionId) {
      return;
    }
    setActions((prev) =>
      prev.map((item) => {
        if (item.id !== selectedActionId) {
          return item;
        }
        if (status === "completed" && item.approvalRequired && !approvedActionIds.has(item.id)) {
          return item;
        }
        return { ...item, status };
      }),
    );
  }

  function approveSelectedAction() {
    if (!selectedActionId) {
      return;
    }
    setApprovedActionIds((prev) => {
      const next = new Set(prev);
      next.add(selectedActionId);
      return next;
    });
    setActions((prev) =>
      prev.map((item) => (item.id === selectedActionId ? { ...item, status: "approved" } : item)),
    );
  }

  function completeSelectedAction() {
    if (!selectedActionId) {
      return;
    }
    setActions((prev) =>
      prev.map((item) => {
        if (item.id !== selectedActionId) {
          return item;
        }
        if (item.approvalRequired && !approvedActionIds.has(item.id)) {
          return item;
        }
        return { ...item, status: "completed" };
      }),
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

        <PlannerSummary
          plan={plan}
          rollup={rollup}
          onTargetCountChange={updateTargetCount}
          onAllocationChange={updateAllocation}
        />

        <section className="grid gap-4 xl:grid-cols-[1.35fr_1fr]">
          <ActionQueue
            actions={actions}
            selectedActionId={selectedActionId}
            onSelect={setSelectedActionId}
            currentFilter={filter}
            onFilterChange={setFilter}
          />
          <ActionDetailPanel
            action={selectedAction}
            onStatusChange={updateStatus}
            onApprove={approveSelectedAction}
            onComplete={completeSelectedAction}
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
