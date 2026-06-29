"use client";

import { motion } from "framer-motion";
import { OpportunityCard } from "../components/dashboard/opportunity-card";
import { Sidebar } from "../components/dashboard/sidebar";
import { StatsStrip } from "../components/dashboard/stats-strip";
import { TailoringPanel } from "../components/dashboard/tailoring-panel";
import { opportunities, pipelineSummary, tailoringDrafts } from "../lib/mock-data";
import { Card } from "@aoe/ui";
import Link from "next/link";

const queueSections = [
  "Opportunity Pipeline",
  "Saved Opportunities",
  "Draft Applications",
  "Outreach Queue",
  "Knowledge Base",
  "Settings",
];

export default function HomePage() {
  return (
    <div className="soft-grid min-h-screen bg-mesh-gradient text-slate-100">
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="w-full p-4 sm:p-6 lg:p-8">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            className="mx-auto max-w-[1400px] space-y-6"
          >
            <header className="rounded-2xl border border-white/10 bg-slate-900/60 p-6 shadow-aura backdrop-blur">
              <p className="text-xs uppercase tracking-[0.2em] text-accent/90">
                Daily Brief
              </p>
              <h1 className="mt-2 [font-family:var(--font-sora)] text-3xl font-semibold text-white sm:text-4xl">
                Build leverage without losing authenticity.
              </h1>
              <p className="mt-3 max-w-3xl text-sm text-slate-300 sm:text-base">
                Focus on discovery, tailoring, and thoughtful outreach. Every draft stays
                review-first, and every claim remains defensible.
              </p>
            </header>

            <StatsStrip summary={pipelineSummary} />

            <Card className="border-accent/25 bg-accent/10">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-accent/90">New workflow</p>
                  <h2 className="mt-1 [font-family:var(--font-sora)] text-xl font-semibold text-white">
                    Rule of 100 Daily Actions
                  </h2>
                  <p className="mt-2 text-sm text-slate-300">
                    Draft-only planning for daily opportunity actions with explicit human approval gates.
                  </p>
                </div>
                <Link
                  href="/rule-of-100"
                  className="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-slate-200"
                >
                  Open Rule of 100 dashboard
                </Link>
              </div>
            </Card>

            <section>
              <div className="mb-4 flex items-center justify-between">
                <h2 className="[font-family:var(--font-sora)] text-xl font-semibold">
                  Daily Opportunities
                </h2>
                <button className="rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 transition hover:bg-white/5">
                  Refresh Mock Feed
                </button>
              </div>
              <div className="grid gap-4 xl:grid-cols-2">
                {opportunities.map((item, idx) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <OpportunityCard item={item} />
                  </motion.div>
                ))}
              </div>
            </section>

            <section className="grid gap-4 xl:grid-cols-[1.35fr_1fr]">
              <TailoringPanel draft={tailoringDrafts[0]} />
              <Card className="space-y-4">
                <h2 className="[font-family:var(--font-sora)] text-lg font-semibold">
                  Workflow Queues
                </h2>
                <div className="space-y-2">
                  {queueSections.map((label, index) => (
                    <div
                      key={label}
                      className="flex items-center justify-between rounded-lg border border-white/10 bg-white/5 p-3"
                    >
                      <span className="text-sm text-slate-100">{label}</span>
                      <span className="rounded-full bg-white/10 px-2 py-1 text-xs text-slate-300">
                        {index + 1} ready
                      </span>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-slate-400">
                  Outbound messages and applications remain in draft state until explicitly approved.
                </p>
              </Card>
            </section>
          </motion.div>
        </main>
      </div>
    </div>
  );
}
