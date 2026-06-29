import type { DailyAction, DailyActionStatus } from "@aoe/shared-types";
import { ActionCard } from "./action-card";

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
  onFilterChange: (status: DailyActionStatus | "all") => void;
  currentFilter: DailyActionStatus | "all";
}) {
  const filters: Array<DailyActionStatus | "all"> = [
    "all",
    "suggested",
    "in_review",
    "approved",
    "completed",
    "skipped",
    "blocked",
  ];

  const filtered =
    currentFilter === "all"
      ? actions
      : actions.filter((item) => item.status === currentFilter);

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        {filters.map((filter) => (
          <button
            key={filter}
            type="button"
            onClick={() => onFilterChange(filter)}
            className={`rounded-full border px-3 py-1 text-xs uppercase tracking-wide transition ${
              currentFilter === filter
                ? "border-accent/60 bg-accent/15 text-accent"
                : "border-white/15 text-slate-300 hover:bg-white/5"
            }`}
          >
            {filter.replace("_", " ")}
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
