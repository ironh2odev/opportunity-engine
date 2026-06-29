import type { ActionChannel, DailyRollup, RuleOf100Plan } from "@aoe/shared-types";
import { Card } from "@aoe/ui";

const channelLabels: Record<ActionChannel, string> = {
  linkedin_comment: "LinkedIn comments",
  connection_request: "Connection requests",
  outreach_dm: "Outreach DMs",
  follow_up: "Follow-ups",
  job_application: "Job applications",
  client_lead_discovery: "Lead discovery",
  referral_request: "Referral requests",
  content_creation: "Content/research",
};

export function PlannerSummary({
  plan,
  rollup,
  onTargetCountChange,
  onAllocationChange,
}: {
  plan: RuleOf100Plan;
  rollup: DailyRollup;
  onTargetCountChange: (value: number) => void;
  onAllocationChange: (channel: ActionChannel, value: number) => void;
}) {
  return (
    <div className="space-y-4">
      <Card className="border-white/15 bg-slate-900/75">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-accent/90">Rule of 100 Daily Actions</p>
            <h2 className="mt-2 [font-family:var(--font-sora)] text-2xl font-semibold text-white">
              Rule of 50 default, scalable to 100
            </h2>
            <p className="mt-2 max-w-3xl text-sm text-slate-300">{plan.notes}</p>
          </div>
          <div className="rounded-xl border border-accent/30 bg-accent/10 p-3 text-right">
            <p className="text-xs uppercase tracking-wide text-accent/90">Today target</p>
            <input
              type="number"
              min={plan.minTarget}
              max={plan.maxTarget}
              value={plan.targetCount}
              onChange={(event) => onTargetCountChange(Number(event.target.value))}
              className="mt-1 w-24 rounded-md border border-white/20 bg-slate-950 px-2 py-1 text-right [font-family:var(--font-sora)] text-2xl font-bold text-white"
            />
            <p className="text-xs text-slate-300">Supported range {plan.minTarget}-{plan.maxTarget}</p>
          </div>
        </div>
      </Card>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <Metric label="Completed" value={rollup.completedCount} />
        <Metric label="Progress" value={`${rollup.progressPercent}%`} />
        <Metric label="Pending review" value={rollup.pendingReviewCount} />
        <Metric label="Approved" value={rollup.approvedCount} />
        <Metric label="Completed (approved)" value={rollup.completedApprovedCount} />
      </div>

      <Card>
        <h3 className="[font-family:var(--font-sora)] text-lg font-semibold text-white">
          Editable allocation (mock configuration)
        </h3>
        <div className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {Object.entries(plan.allocation).map(([channel, count]) => (
            <div key={channel} className="rounded-lg border border-white/10 bg-white/5 p-3">
              <p className="text-xs uppercase tracking-wide text-slate-400">
                {channelLabels[channel as ActionChannel]}
              </p>
              <input
                type="number"
                min={0}
                max={100}
                value={count}
                onChange={(event) =>
                  onAllocationChange(channel as ActionChannel, Number(event.target.value))
                }
                className="mt-1 w-20 rounded-md border border-white/20 bg-slate-950 px-2 py-1 text-xl font-semibold text-white"
              />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number | string }) {
  return (
    <Card className="border-white/10 bg-slate-900/65 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 [font-family:var(--font-sora)] text-3xl font-semibold text-white">{value}</p>
    </Card>
  );
}
