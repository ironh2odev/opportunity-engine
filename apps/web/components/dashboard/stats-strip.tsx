import type { PipelineSummary } from "@aoe/shared-types";
import { Card } from "@aoe/ui";

export function StatsStrip({ summary }: { summary: PipelineSummary }) {
  const metrics = [
    { label: "Total opportunities", value: summary.total },
    { label: "New", value: summary.byStatus.new },
    { label: "Saved", value: summary.byStatus.saved },
    { label: "Reviewed", value: summary.byStatus.reviewed },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((item) => (
        <Card key={item.label} className="border-white/10 bg-slate-900/65 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{item.label}</p>
          <p className="mt-2 [font-family:var(--font-sora)] text-3xl font-semibold text-white">
            {item.value}
          </p>
        </Card>
      ))}
    </div>
  );
}
