"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type {
  CareerContextInput,
  CareerContextExtractionMode,
  CareerContextExtractionResult,
  CaptureSourceType,
  ExtractFromTextResult,
  LeadPriority,
  PersonalLead,
  PersonalRuleAction,
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

const captureSourceTypes: CaptureSourceType[] = [
  "job_listing",
  "linkedin_profile",
  "linkedin_post",
  "company_website",
  "recruiter_message",
  "client_website",
  "personal_notes",
  "other",
];

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

const emptyCareerContext: CareerContextInput = {
  currentHeadline: "",
  targetRoles: [],
  coreSkills: [],
  technicalStack: [],
  projectHighlights: [],
  industries: [],
  locationPreferences: [],
  visaNotes: "",
  preferredOpportunityTypes: [],
  positioningStatement: "",
  proofPoints: [],
  rawCvText: "",
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
  const [createdAction, setCreatedAction] = useState<PersonalRuleAction | null>(null);
  const [linkedActions, setLinkedActions] = useState<PersonalRuleAction[]>([]);
  const [careerContext, setCareerContext] = useState<CareerContextInput>(emptyCareerContext);
  const [careerExtractionMode, setCareerExtractionMode] = useState<CareerContextExtractionMode>("local");
  const [careerImportText, setCareerImportText] = useState("");
  const [careerImportFile, setCareerImportFile] = useState<File | null>(null);
  const [careerExtractionResult, setCareerExtractionResult] = useState<CareerContextExtractionResult | null>(null);
  const [careerExtractBusy, setCareerExtractBusy] = useState(false);
  const [captureSourceType, setCaptureSourceType] = useState<CaptureSourceType>("job_listing");
  const [captureSourceUrl, setCaptureSourceUrl] = useState("");
  const [captureGoal, setCaptureGoal] = useState<PersonalOpportunityType>("job");
  const [captureUseCareerContext, setCaptureUseCareerContext] = useState(true);
  const [captureRawText, setCaptureRawText] = useState("");
  const [captureResult, setCaptureResult] = useState<ExtractFromTextResult | null>(null);
  const [captureBusy, setCaptureBusy] = useState(false);
  const [careerBusy, setCareerBusy] = useState(false);
  const [saveExtractAndCreateAction, setSaveExtractAndCreateAction] = useState(false);

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

  useEffect(() => {
    async function loadCareerContext() {
      try {
        const data = await personalLeadsApi.getCareerContext();
        setCareerContext({
          currentHeadline: data.currentHeadline,
          targetRoles: data.targetRoles,
          coreSkills: data.coreSkills,
          technicalStack: data.technicalStack,
          projectHighlights: data.projectHighlights,
          industries: data.industries,
          locationPreferences: data.locationPreferences,
          visaNotes: data.visaNotes,
          preferredOpportunityTypes: data.preferredOpportunityTypes,
          positioningStatement: data.positioningStatement,
          proofPoints: data.proofPoints,
          rawCvText: data.rawCvText,
        });
      } catch {
        setCareerContext(emptyCareerContext);
      }
    }
    void loadCareerContext();
  }, []);

  useEffect(() => {
    async function loadLinkedActions() {
      if (!selectedLeadId) {
        setLinkedActions([]);
        return;
      }
      try {
        const data = await personalLeadsApi.listRuleActions(selectedLeadId);
        setLinkedActions(data);
      } catch {
        setLinkedActions([]);
      }
    }
    void loadLinkedActions();
  }, [selectedLeadId]);

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
      setLinkedActions((prev) => [action, ...prev]);
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setSaving(false);
    }
  }

  function applySuggestionToForm(result: ExtractFromTextResult) {
    const suggested = result.suggestedLead;
    setFormData((prev) => ({
      ...prev,
      name: suggested.name,
      role: suggested.role,
      organisation: suggested.organisation,
      organisationWebsite: suggested.organisationWebsite,
      linkedinUrl: suggested.linkedinUrl,
      email: suggested.email,
      location: suggested.location,
      source: suggested.source || `capture:${captureSourceType}`,
      opportunityType: suggested.opportunityType,
      relationshipStrength: suggested.relationshipStrength,
      fitScore: suggested.fitScore,
      priority: suggested.priority,
      problemObserved: suggested.problemObserved,
      whyRelevant: suggested.whyRelevant,
      suggestedAngle: suggested.suggestedAngle,
      notes: suggested.notes,
      tags: suggested.tags,
      nextAction: suggested.nextAction,
      followUpDate: suggested.followUpDate,
    }));
  }

  async function handleSaveCareerContext() {
    setCareerBusy(true);
    setError(null);
    setMessage(null);
    try {
      const updated = await personalLeadsApi.updateCareerContext(careerContext);
      setCareerContext({
        currentHeadline: updated.currentHeadline,
        targetRoles: updated.targetRoles,
        coreSkills: updated.coreSkills,
        technicalStack: updated.technicalStack,
        projectHighlights: updated.projectHighlights,
        industries: updated.industries,
        locationPreferences: updated.locationPreferences,
        visaNotes: updated.visaNotes,
        preferredOpportunityTypes: updated.preferredOpportunityTypes,
        positioningStatement: updated.positioningStatement,
        proofPoints: updated.proofPoints,
        rawCvText: updated.rawCvText,
      });
      setMessage("Career context saved locally.");
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setCareerBusy(false);
    }
  }

  function applyExtractedCareerContext(result: CareerContextExtractionResult) {
    const suggested = result.suggestedCareerContext;
    setCareerContext({
      currentHeadline: suggested.currentHeadline,
      targetRoles: suggested.targetRoles,
      coreSkills: suggested.coreSkills,
      technicalStack: suggested.technicalStack,
      projectHighlights: suggested.projectHighlights,
      industries: suggested.industries,
      locationPreferences: suggested.locationPreferences,
      visaNotes: suggested.visaNotes,
      preferredOpportunityTypes: suggested.preferredOpportunityTypes,
      positioningStatement: suggested.positioningStatement,
      proofPoints: suggested.proofPoints,
      rawCvText: suggested.rawCvText,
    });
  }

  async function handleExtractCareerContext() {
    setCareerExtractBusy(true);
    setError(null);
    setMessage(null);
    setCareerExtractionResult(null);
    try {
      const result = await personalLeadsApi.extractCareerContext({
        rawCvText: careerImportText,
        extractionMode: careerExtractionMode,
        file: careerImportFile,
      });
      setCareerExtractionResult(result);
      applyExtractedCareerContext(result);
      setMessage("Career context extracted as draft. Review fields, then save manually.");
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setCareerExtractBusy(false);
    }
  }

  async function handleExtract() {
    setCaptureBusy(true);
    setError(null);
    setMessage(null);
    setCaptureResult(null);
    try {
      const result = await personalLeadsApi.extractFromText({
        rawText: captureRawText,
        sourceType: captureSourceType,
        optionalSourceUrl: captureSourceUrl,
        userGoal: captureGoal,
        useCareerContext: captureUseCareerContext,
      });
      setCaptureResult(result);
      applySuggestionToForm(result);
      setMessage("Draft extraction generated. Review and save manually.");
    } catch (err) {
      setError((err as PersonalApiError).message);
    } finally {
      setCaptureBusy(false);
    }
  }

  async function handleSaveExtractedLead() {
    if (!captureResult) return;
    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      const created = await personalLeadsApi.create({
        ...emptyLeadInput,
        ...captureResult.suggestedLead,
      });
      if (saveExtractAndCreateAction) {
        await personalLeadsApi.createRuleAction(created.id);
      }
      setMessage(
        saveExtractAndCreateAction
          ? "Extracted lead saved and Rule of 100 draft action created."
          : "Extracted lead saved in private local mode.",
      );
      await loadLeads();
      setSelectedLeadId(created.id);
      setCaptureResult(null);
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

        <section className="grid gap-4 xl:grid-cols-2">
          <Card className="space-y-3">
            <details open>
              <summary className="cursor-pointer [font-family:var(--font-sora)] text-lg font-semibold">Career Context</summary>
              <p className="mt-2 text-xs text-slate-300">
                Private local context. Used only to improve extraction, fit scoring, and draft suggestions.
              </p>
              <p className="mt-1 text-xs text-slate-300">
                Private local context. Review before saving. Do not include sensitive data you do not want stored locally.
              </p>
              <div className="mt-3 space-y-2 rounded-lg border border-white/10 bg-white/5 p-3">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-300">Import from CV</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  <select
                    value={careerExtractionMode}
                    onChange={(e) => setCareerExtractionMode(e.target.value as CareerContextExtractionMode)}
                    className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                  >
                    <option value="local">local</option>
                    <option value="ai_assisted">ai_assisted</option>
                  </select>
                  <input
                    type="file"
                    accept=".txt,.pdf,.docx"
                    onChange={(e) => setCareerImportFile(e.target.files?.[0] ?? null)}
                    className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-xs"
                  />
                </div>
                <textarea
                  placeholder="Paste CV text"
                  value={careerImportText}
                  onChange={(e) => setCareerImportText(e.target.value)}
                  className="h-28 rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-xs"
                />
                <p className="text-xs text-slate-400">
                  This version supports pasted text and .txt upload. PDF/DOCX parsing is planned next.
                </p>
                <p className="text-xs text-slate-400">
                  AI-assisted mode is optional and review-first. If unavailable, extraction falls back to local mode.
                </p>
                <button
                  disabled={careerExtractBusy || (!careerImportText.trim() && !careerImportFile)}
                  onClick={() => void handleExtractCareerContext()}
                  className="rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-slate-900 disabled:opacity-50"
                >
                  Extract Career Context
                </button>
              </div>

              {careerExtractionResult ? (
                <div className="mt-3 space-y-2 rounded-lg border border-white/10 bg-white/5 p-3 text-xs text-slate-200">
                  <p>Confidence: {careerExtractionResult.extractionConfidence}</p>
                  <p>Mode used: {careerExtractionResult.extractionModeUsed}</p>
                  <p>AI used: {careerExtractionResult.aiUsed ? "yes" : "no"}</p>
                  <p>Missing fields: {careerExtractionResult.missingFields.join(", ") || "none"}</p>
                  <p>Warnings: {careerExtractionResult.reviewWarnings.join(" | ") || "none"}</p>
                  <p>Reasoning: {careerExtractionResult.reasoningSummary}</p>
                </div>
              ) : null}

              <div className="mt-3 grid gap-2">
                <input
                  placeholder="Current headline"
                  value={careerContext.currentHeadline}
                  onChange={(e) => setCareerContext((p) => ({ ...p, currentHeadline: e.target.value }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Target roles (comma separated)"
                  value={careerContext.targetRoles.join(", ")}
                  onChange={(e) => setCareerContext((p) => ({ ...p, targetRoles: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Core skills (comma separated)"
                  value={careerContext.coreSkills.join(", ")}
                  onChange={(e) => setCareerContext((p) => ({ ...p, coreSkills: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Technical stack (comma separated)"
                  value={careerContext.technicalStack.join(", ")}
                  onChange={(e) => setCareerContext((p) => ({ ...p, technicalStack: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Preferred opportunity types (comma separated)"
                  value={careerContext.preferredOpportunityTypes.join(", ")}
                  onChange={(e) =>
                    setCareerContext((p) => ({
                      ...p,
                      preferredOpportunityTypes: e.target.value
                        .split(",")
                        .map((item) => item.trim())
                        .filter(Boolean) as PersonalOpportunityType[],
                    }))
                  }
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <textarea
                  placeholder="Visa notes"
                  value={careerContext.visaNotes}
                  onChange={(e) => setCareerContext((p) => ({ ...p, visaNotes: e.target.value }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Industries (comma separated)"
                  value={careerContext.industries.join(", ")}
                  onChange={(e) => setCareerContext((p) => ({ ...p, industries: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Location preferences (comma separated)"
                  value={careerContext.locationPreferences.join(", ")}
                  onChange={(e) => setCareerContext((p) => ({ ...p, locationPreferences: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <input
                  placeholder="Proof points (comma separated)"
                  value={careerContext.proofPoints.join(", ")}
                  onChange={(e) => setCareerContext((p) => ({ ...p, proofPoints: e.target.value.split(",").map((item) => item.trim()).filter(Boolean) }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <textarea
                  placeholder="Positioning statement"
                  value={careerContext.positioningStatement}
                  onChange={(e) => setCareerContext((p) => ({ ...p, positioningStatement: e.target.value }))}
                  className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
                />
                <textarea
                  placeholder="Raw CV text"
                  value={careerContext.rawCvText}
                  onChange={(e) => setCareerContext((p) => ({ ...p, rawCvText: e.target.value }))}
                  className="h-28 rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-xs"
                />
              </div>
              <button
                disabled={careerBusy}
                onClick={() => void handleSaveCareerContext()}
                className="mt-3 rounded-lg border border-white/15 px-3 py-2 text-sm disabled:opacity-50"
              >
                Save career context
              </button>
            </details>
          </Card>

          <Card className="space-y-3">
            <h2 className="[font-family:var(--font-sora)] text-lg font-semibold">Capture Opportunity Assistant</h2>
            <p className="text-xs text-slate-300">
              AI suggests. You review before saving. Private local mode. No scraping. No auto-send. No auto-apply.
              Manual execution only.
            </p>
            <p className="text-xs text-slate-300">
              CV/career context is used only to support fit scoring and drafting.
            </p>
            <div className="grid gap-2 sm:grid-cols-2">
              <select
                value={captureSourceType}
                onChange={(e) => setCaptureSourceType(e.target.value as CaptureSourceType)}
                className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
              >
                {captureSourceTypes.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
              <select
                value={captureGoal}
                onChange={(e) => setCaptureGoal(e.target.value as PersonalOpportunityType)}
                className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
              >
                {opportunityTypes.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </div>
            <input
              placeholder="Optional source URL"
              value={captureSourceUrl}
              onChange={(e) => setCaptureSourceUrl(e.target.value)}
              className="rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
            />
            <textarea
              placeholder="Paste job listing, recruiter message, profile text, or notes"
              value={captureRawText}
              onChange={(e) => setCaptureRawText(e.target.value)}
              className="h-36 rounded-md border border-white/20 bg-slate-950 px-3 py-2 text-sm"
            />
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={captureUseCareerContext}
                onChange={(e) => setCaptureUseCareerContext(e.target.checked)}
              />
              Use career context for fit scoring
            </label>
            <button
              disabled={captureBusy || !captureRawText.trim()}
              onClick={() => void handleExtract()}
              className="rounded-lg bg-accent px-3 py-2 text-sm font-semibold text-slate-900 disabled:opacity-50"
            >
              Extract draft lead
            </button>

            {captureResult ? (
              <div className="space-y-2 rounded-lg border border-white/10 bg-white/5 p-3 text-xs text-slate-200">
                <p>Confidence: {captureResult.extractionConfidence}</p>
                <p>Fit score: {captureResult.careerFitScore}/10</p>
                <p>Recommended action: {captureResult.recommendedAction}</p>
                <p>Matched skills: {captureResult.matchedSkills.join(", ") || "-"}</p>
                <p>Gaps: {captureResult.missingSkillsOrGaps.join(", ") || "-"}</p>
                <p>Missing fields: {captureResult.missingFields.join(", ") || "none"}</p>
                {captureResult.reviewWarnings.length > 0 ? (
                  <p>Warnings: {captureResult.reviewWarnings.join(" | ")}</p>
                ) : null}
                <div className="flex flex-wrap gap-2 pt-2">
                  <button
                    onClick={() => applySuggestionToForm(captureResult)}
                    className="rounded-lg border border-white/15 px-3 py-2 text-xs"
                  >
                    Prefill lead form
                  </button>
                  <label className="flex items-center gap-2 rounded-lg border border-white/10 px-2 py-1 text-xs">
                    <input
                      type="checkbox"
                      checked={saveExtractAndCreateAction}
                      onChange={(e) => setSaveExtractAndCreateAction(e.target.checked)}
                    />
                    Create Rule action now
                  </label>
                  <button
                    disabled={saving}
                    onClick={() => void handleSaveExtractedLead()}
                    className="rounded-lg bg-white px-3 py-2 text-xs font-semibold text-slate-900 disabled:opacity-50"
                  >
                    Save extracted lead
                  </button>
                </div>
              </div>
            ) : null}
          </Card>
        </section>

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

                <div className="mt-3 space-y-2">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Generated Rule Actions</p>
                  {linkedActions.length === 0 ? (
                    <p className="text-xs text-slate-400">No linked actions yet.</p>
                  ) : (
                    linkedActions.map((item) => (
                      <div key={item.id} className="rounded-lg border border-white/10 bg-white/5 p-2">
                        <p className="text-xs text-slate-200">Status: {item.status}</p>
                        <p className="text-xs text-slate-300">Created: {new Date(item.createdAt).toLocaleString()}</p>
                        <p className="text-xs text-slate-300">Follow-up: {item.followUpDate ?? "-"}</p>
                        <p className="text-xs text-slate-300">Message: {item.suggestedMessage.slice(0, 120)}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-300">Select a lead to view details.</p>
            )}

            {createdAction ? (
              <div className="rounded-lg border border-cyan-400/30 bg-cyan-500/10 p-3 text-xs text-cyan-100">
                Created draft action: {createdAction.actionType} ({createdAction.status})
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
