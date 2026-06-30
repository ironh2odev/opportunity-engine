"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type {
  DailyAction,
  LeadPriority,
  PersonalLead,
  PersonalLeadStatus,
  PersonalOpportunityType,
  RelationshipStrength,
} from "@aoe/shared-types";
import { Card } from "@aoe/ui";
import { personalLeadsApi, type PersonalApiError, type PersonalLeadInput } from "../../lib/personal-leads-api";

const opportunityTypes: PersonalOpportunityType[] = [
  "job",
  "client",
  "collaborator",
  "referrer",
  "content",
  "recruiter",
  "founder",
  "professional_service",
];

const relationshipStrengths: RelationshipStrength[] = [
  "cold",
  "warm",
  "engaged",
  "connected",
  "previous_client",
  "referral",
];

const statuses: PersonalLeadStatus[] = [
  "new",
  "saved",
  "reviewed",
  "action_planned",
  "contacted",
  "follow_up_due",
  "archived",
];

const priorities: LeadPriority[] = ["low", "medium", "high"];

const emptyLeadInput: PersonalLeadInput = {
  name: "",
  role: "",
  organisation: "",
  organisationWebsite: "",
  linkedinUrl: "",
  email: "",
  location: "",
  source: "manual",
  opportunityType: "client",
  relationshipStrength: "cold",
  status: "new",
  fitScore: 5,
  priority: "medium",
  problemObserved: "",
  whyRelevant: "",
  suggestedAngle: "",
  notes: "",
  tags: [],
  nextAction: "",
  followUpDate: null,
};

export default function PersonalLeadsPage() {
  const [leads, setLeads] = useState<PersonalLead[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [filters, setFilters] = useState<{
    opportunityType?: PersonalOpportunityType;
    status?: PersonalLeadStatus;
    priority?: LeadPriority;
  }>({});
  const [formData, setFormData] = useState<PersonalLeadInput>(emptyLeadInput);
  const [csvText, setCsvText] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [createdAction, setCreatedAction] = useState<DailyAction | null>(null);

  const selectedLead = useMemo(
    () => leads.find((item) => item.id === selectedLeadId) ?? null,
    [leads, selectedLeadId],
  );

  const loadLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await personalLeadsApi.list(filters);
      setLeads(data);
      setSelectedLeadId((current) => current ?? data[0]?.id ?? null);
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadLeads();
  }, [loadLeads]);

  function hydrateForm(lead: PersonalLead) {
    setFormData({
      name: lead.name,
      role: lead.role,
      organisation: lead.organisation,
      organisationWebsite: lead.organisationWebsite,
      linkedinUrl: lead.linkedinUrl,
      email: lead.email,
      location: lead.location,
      source: lead.source,
      opportunityType: lead.opportunityType,
      relationshipStrength: lead.relationshipStrength,
      status: lead.status,
      fitScore: lead.fitScore,
      priority: lead.priority,
      problemObserved: lead.problemObserved,
      whyRelevant: lead.whyRelevant,
      suggestedAngle: lead.suggestedAngle,
      notes: lead.notes,
      tags: lead.tags,
      nextAction: lead.nextAction,
      followUpDate: lead.followUpDate,
    });
  }

  async function handleCreateLead() {
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await personalLeadsApi.create(formData);
      setFormData(emptyLeadInput);
      setMessage("Lead created in private local mode.");
      await loadLeads();
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setSaving(false);
    }
  }

  async function handleUpdateLead() {
    if (!selectedLeadId) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await personalLeadsApi.update(selectedLeadId, formData);
      setMessage("Lead updated.");
      await loadLeads();
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteLead() {
    if (!selectedLeadId) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await personalLeadsApi.remove(selectedLeadId);
      setSelectedLeadId(null);
      setFormData(emptyLeadInput);
      setMessage("Lead deleted.");
      await loadLeads();
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setSaving(false);
    }
  }

  async function handleImportCsv() {
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const imported = await personalLeadsApi.importCsv(csvText);
      setMessage(`Imported ${imported.length} leads into private local mode.`);
      setCsvText("");
      await loadLeads();
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateRuleAction() {
    if (!selectedLeadId) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const action = await personalLeadsApi.createRuleAction(selectedLeadId);
      setCreatedAction(action);
      setMessage("Draft Rule of 100 action created. Manual execution only.");
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="soft-grid min-h-screen bg-mesh-gradient px-4 py-6 text-slate-100 sm:px-6 lg:px-8">
      <main className="mx-auto max-w-[1500px] space-y-6">
        <header className="rounded-2xl border border-white/10 bg-slate-900/60 p-6 shadow-aura backdrop-blur">
          <p className="text-xs uppercase tracking-[0.2em] text-accent/90">Personal Mode</p>
          <h1 className="mt-2 [font-family:var(--font-sora)] text-3xl font-semibold text-white sm:text-4xl">
            Private local leads workspace
          </h1>
          <div className="mt-3 grid gap-2 text-sm text-slate-200 sm:grid-cols-2">
            <p>Private local mode</p>
            <p>Manual execution only</p>
            <p>Human approval required</p>
            <p>No auto-send</p>
            <p>No auto-apply</p>
            <p>No scraping</p>
          </div>
        </header>

        {error ? <Card className="border-rose-400/30 bg-rose-500/10 text-sm text-rose-100">{error}</Card> : null}
        {message ? <Card className="border-cyan-400/30 bg-cyan-500/10 text-sm text-cyan-100">{message}</Card> : null}

        <section className="grid gap-4 xl:grid-cols-[1.1fr_1fr_1fr]">
          <Card className="space-y-3">
            <h2 className="[font-family:var(--font-sora)] text-lg font-semibold">Lead filters and list</h2>
            <div className="grid gap-2 sm:grid-cols-3">
              <select
                value={filters.opportunityType ?? ""}
                onChange={(event) =>
                  setFilters((prev) => ({ ...prev, opportunityType: (event.target.value as PersonalOpportunityType) || undefined }))
                }
                className="rounded-md border border-white/20 bg-slate-950 px-2 py-2 text-sm"
              >
                <option value="">All types</option>
                {opportunityTypes.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
              <select
                value={filters.status ?? ""}
                onChange={(event) =>
                  setFilters((prev) => ({ ...prev, status: (event.target.value as PersonalLeadStatus) || undefined }))
                }
                className="rounded-md border border-white/20 bg-slate-950 px-2 py-2 text-sm"
              >
                <option value="">All status</option>
                {statuses.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
              <select
                value={filters.priority ?? ""}
                onChange={(event) =>
                  setFilters((prev) => ({ ...prev, priority: (event.target.value as LeadPriority) || undefined }))
                }
                className="rounded-md border border-white/20 bg-slate-950 px-2 py-2 text-sm"
              >
                <option value="">All priority</option>
                {priorities.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>

            <div className="max-h-[520px] space-y-2 overflow-auto pr-1">
              {loading ? (
                <p className="text-sm text-slate-300">Loading leads...</p>
              ) : (
                leads.map((lead) => (
                  <button
                    key={lead.id}
                    type="button"
                    onClick={() => {
                      setSelectedLeadId(lead.id);
                      hydrateForm(lead);
                    }}
                    className={`w-full rounded-lg border px-3 py-2 text-left text-sm ${
                      selectedLeadId === lead.id
                        ? "border-accent/50 bg-accent/15"
                        : "border-white/10 bg-white/5 hover:bg-white/10"
                    }`}
                  >
                    <p className="font-semibold text-white">{lead.name || lead.organisation || "Unnamed lead"}</p>
                    <p className="text-xs text-slate-300">{lead.role} · {lead.organisation}</p>
                    <p className="text-xs text-slate-400">{lead.opportunityType} · {lead.status} · {lead.priority}</p>
                  </button>
                ))
              )}
            </div>
          </Card>

          <Card className="space-y-3">
            <h2 className="[font-family:var(--font-sora)] text-lg font-semibold">Add or edit lead</h2>
            <div className="grid gap-2">
              <input placeholder="Name" value={formData.name} onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Role" value={formData.role} onChange={(e) => setFormData((p) => ({ ...p, role: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Organisation" value={formData.organisation} onChange={(e) => setFormData((p) => ({ ...p, organisation: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Organisation website" value={formData.organisationWebsite} onChange={(e) => setFormData((p) => ({ ...p, organisationWebsite: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="LinkedIn URL" value={formData.linkedinUrl} onChange={(e) => setFormData((p) => ({ ...p, linkedinUrl: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Email" value={formData.email} onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Location" value={formData.location} onChange={(e) => setFormData((p) => ({ ...p, location: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Source" value={formData.source} onChange={(e) => setFormData((p) => ({ ...p, source: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <select value={formData.opportunityType} onChange={(e) => setFormData((p) => ({ ...p, opportunityType: e.target.value as PersonalOpportunityType }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm">
                {opportunityTypes.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
              <select value={formData.relationshipStrength} onChange={(e) => setFormData((p) => ({ ...p, relationshipStrength: e.target.value as RelationshipStrength }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm">
                {relationshipStrengths.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
              <select value={formData.status} onChange={(e) => setFormData((p) => ({ ...p, status: e.target.value as PersonalLeadStatus }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm">
                {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
              <select value={formData.priority} onChange={(e) => setFormData((p) => ({ ...p, priority: e.target.value as LeadPriority }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm">
                {priorities.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
              <input type="number" min={1} max={10} placeholder="Fit score 1-10" value={formData.fitScore} onChange={(e) => setFormData((p) => ({ ...p, fitScore: Number(e.target.value) || 1 }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <textarea placeholder="Problem observed" value={formData.problemObserved} onChange={(e) => setFormData((p) => ({ ...p, problemObserved: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <textarea placeholder="Why relevant" value={formData.whyRelevant} onChange={(e) => setFormData((p) => ({ ...p, whyRelevant: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <textarea placeholder="Suggested angle" value={formData.suggestedAngle} onChange={(e) => setFormData((p) => ({ ...p, suggestedAngle: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <textarea placeholder="Notes" value={formData.notes} onChange={(e) => setFormData((p) => ({ ...p, notes: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input placeholder="Tags (comma separated)" value={formData.tags.join(", ")} onChange={(e) => setFormData((p) => ({ ...p, tags: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <textarea placeholder="Next action" value={formData.nextAction} onChange={(e) => setFormData((p) => ({ ...p, nextAction: e.target.value }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
              <input type="date" value={formData.followUpDate ?? ""} onChange={(e) => setFormData((p) => ({ ...p, followUpDate: e.target.value || null }))} className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm" />
            </div>
            <div className="flex flex-wrap gap-2">
              <button disabled={saving} onClick={() => void handleCreateLead()} className="rounded-lg bg-white px-3 py-2 text-sm font-semibold text-slate-900 disabled:opacity-50">Add lead</button>
              <button disabled={saving || !selectedLeadId} onClick={() => void handleUpdateLead()} className="rounded-lg border border-white/15 px-3 py-2 text-sm">Save edits</button>
              <button disabled={saving || !selectedLeadId} onClick={() => void handleDeleteLead()} className="rounded-lg border border-rose-400/50 px-3 py-2 text-sm text-rose-200">Delete</button>
            </div>
          </Card>

          <Card className="space-y-3">
            <h2 className="[font-family:var(--font-sora)] text-lg font-semibold">Lead detail + CSV import</h2>
            {selectedLead ? (
              <div className="space-y-2 text-sm text-slate-300">
                <p className="text-white font-semibold">{selectedLead.name || selectedLead.organisation}</p>
                <p>{selectedLead.role} · {selectedLead.organisation}</p>
                <p>{selectedLead.location}</p>
                <p>{selectedLead.email}</p>
                <p>{selectedLead.linkedinUrl}</p>
                <p>Status: {selectedLead.status}</p>
                <p>Priority: {selectedLead.priority}</p>
                <p>Next action: {selectedLead.nextAction || "-"}</p>
                <button disabled={saving} onClick={() => void handleCreateRuleAction()} className="rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-slate-900 disabled:opacity-50">
                  Create Rule of 100 action
                </button>
              </div>
            ) : (
              <p className="text-sm text-slate-300">Select a lead to view details.</p>
            )}

            {createdAction ? (
              <div className="rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-3 text-xs text-cyan-100">
                Created draft action: {createdAction.title} ({createdAction.status})
              </div>
            ) : null}

            <div className="space-y-2">
              <p className="text-sm font-semibold">CSV import (private local data)</p>
              <textarea
                value={csvText}
                onChange={(e) => setCsvText(e.target.value)}
                placeholder="Paste CSV with required columns"
                className="h-40 w-full rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-xs"
              />
              <button disabled={saving || !csvText.trim()} onClick={() => void handleImportCsv()} className="rounded-lg border border-white/15 px-3 py-2 text-sm disabled:opacity-50">
                Import CSV
              </button>
            </div>
          </Card>
        </section>
      </main>
    </div>
  );
}
