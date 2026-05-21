import {
  BriefcaseBusiness,
  FolderHeart,
  GaugeCircle,
  Kanban,
  Mail,
  PenSquare,
  Settings,
  Sparkles,
} from "lucide-react";

const navItems = [
  { label: "Daily Opportunities", icon: GaugeCircle },
  { label: "Opportunity Pipeline", icon: Kanban },
  { label: "Saved Opportunities", icon: FolderHeart },
  { label: "Draft Applications", icon: PenSquare },
  { label: "Outreach Queue", icon: Mail },
  { label: "Tailoring Assistant", icon: Sparkles },
  { label: "Knowledge Base", icon: BriefcaseBusiness },
  { label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="hidden w-[280px] flex-col border-r border-white/10 bg-slate-950/70 p-5 lg:flex">
      <div className="rounded-2xl border border-accent/30 bg-gradient-to-br from-accent/15 to-transparent p-4 shadow-aura">
        <p className="[font-family:var(--font-sora)] text-sm uppercase tracking-[0.2em] text-accent/80">
          Opportunity Engine
        </p>
        <h1 className="mt-3 text-2xl font-semibold">Operator Console</h1>
        <p className="mt-2 text-sm text-slate-300">
          Opportunity operations with grounded, human-reviewed drafts.
        </p>
      </div>

      <nav className="mt-8 space-y-2">
        {navItems.map(({ label, icon: Icon }, idx) => (
          <button
            key={label}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm transition ${
              idx === 0
                ? "bg-white/10 text-white"
                : "text-slate-300 hover:bg-white/5 hover:text-white"
            }`}
            type="button"
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="mt-auto rounded-xl border border-white/10 bg-panel/80 p-4 text-sm text-slate-300">
        Human approval is required before any application or outreach is sent.
      </div>
    </aside>
  );
}
