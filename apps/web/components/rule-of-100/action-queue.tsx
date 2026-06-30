import type { DailyAction } from "@aoe/shared-types";
import { ActionCard } from "./action-card";

export type RuleQueueFilter =
  | "all"
  | "personal_mode"
  | "mock_demo"
  | "jobs"
  | "clients"
  | "comments"
  | "follow_ups"
  | "applications"
  | "outreach"
  | "needs_approval"
  | "approved"
  | "ready_to_complete"
  | "completed"
  | "skipped_blocked";

function isReadyToComplete(action: DailyAction): boolean {
  if (action.status === "completed" || action.status === "skipped" || action.status === "blocked") {
    return false;
  }
  if (action.approvalRequired) {
    return action.status === "approved";
  }
  return true;
}

function matchesFilter(action: DailyAction, filter: RuleQueueFilter): boolean {
  switch (filter) {
    case "all":
      return true;
    case "personal_mode":
      return action.sourceType === "personal_lead";
    case "mock_demo":
      return action.sourceType === "mock_demo";
    case "jobs":
      return action.opportunityType === "job" || action.channel === "job_application";
    case "clients":
      return action.opportunityType === "client-lead" || action.channel === "client_lead_discovery";
    case "comments":
      return action.channel === "linkedin_comment";
    case "follow_ups":
      return action.channel === "follow_up";
    case "applications":
      return action.channel === "job_application";
    case "outreach":
      return ["outreach_dm", "connection_request", "referral_request"].includes(action.channel);
    case "needs_approval":
      return action.approvalRequired && action.status !== "approved" && action.status !== "completed";
    case "approved":
      return action.status === "approved";
    case "ready_to_complete":
      return isReadyToComplete(action);
    case "completed":
      return action.status === "completed";
    case "skipped_blocked":
      return action.status === "skipped" || action.status === "blocked";
    default:
      return true;
  }
}

export function ActionQueue({
  actions,
  selectedActionId,
  onSelect,
  onFilterChange,
  currentFilter,
}: {
  actions: DailyAction[];
  selectedActionId: string | null;
  onSelect: (actionId: string) => void;
  onFilterChange: (status: RuleQueueFilter) => void;
  currentFilter: RuleQueueFilter;
}) {
  const filters: Array<{ key: RuleQueueFilter; label: string }> = [
    { key: "all", label: "All" },
    { key: "personal_mode", label: "Personal Mode" },
    { key: "mock_demo", label: "Mock Demo" },
    { key: "jobs", label: "Jobs" },
    { key: "clients", label: "Clients" },
    { key: "comments", label: "Comments" },
    { key: "follow_ups", label: "Follow-ups" },
    { key: "applications", label: "Applications" },
    { key: "outreach", label: "Outreach" },
    { key: "needs_approval", label: "Needs approval" },
    { key: "approved", label: "Approved" },
    { key: "ready_to_complete", label: "Ready to complete" },
    { key: "completed", label: "Completed" },
    { key: "skipped_blocked", label: "Skipped/blocked" },
  ];

  const filtered = actions.filter((item) => matchesFilter(item, currentFilter));

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {filters.map((filter) => (
          <button
            key={filter.key}
            type="button"
            onClick={() => onFilterChange(filter.key)}
            className={`rounded-full border px-3 py-1 text-xs uppercase tracking-wide transition ${
              currentFilter === filter.key
                ? "border-accent/60 bg-accent/15 text-accent"
                : "border-white/15 text-slate-300 hover:bg-white/5"
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="grid gap-3">
        {filtered.map((action) => (
          <ActionCard
            key={action.id}
            action={action}
            onSelect={onSelect}
            selected={selectedActionId === action.id}
          />
        ))}
      </div>
    </section>
  );
}
