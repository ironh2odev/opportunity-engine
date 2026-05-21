import type { TailoringDraft } from "@aoe/shared-types";
import { Card } from "@aoe/ui";

export function TailoringPanel({ draft }: { draft: TailoringDraft }) {
  return (
    <Card className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="[font-family:var(--font-sora)] text-lg font-semibold">
          Tailoring Assistant (Mock)
        </h2>
        <span className="rounded-full bg-signal/20 px-3 py-1 text-xs font-medium text-signal">
          Human review required
        </span>
      </div>

      <section>
        <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-300">
          Suggested CV Bullets
        </h3>
        <ul className="space-y-2 text-sm text-slate-200">
          {draft.cvBullets.map((bullet) => (
            <li key={bullet} className="rounded-lg border border-white/10 bg-white/5 p-3">
              {bullet}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-300">
          Confidence Prompts
        </h3>
        <ul className="space-y-2 text-sm text-slate-200">
          {draft.confidenceSignals.map((signal) => (
            <li key={signal.message} className="rounded-lg border border-white/10 bg-white/5 p-3">
              {signal.message}
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-2 text-sm text-slate-200">
        <h3 className="font-semibold uppercase tracking-wide text-slate-300">
          Outreach Draft
        </h3>
        <p className="rounded-lg border border-white/10 bg-white/5 p-3">
          {draft.outreachDraft}
        </p>
      </section>

      <div className="flex flex-wrap gap-2">
        <button className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-accent/90">
          Mark as Approved
        </button>
        <button className="rounded-lg border border-white/15 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/5">
          Request More Specificity
        </button>
      </div>
    </Card>
  );
}
