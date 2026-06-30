import type {
  CareerContext,
  CareerContextExtractionMode,
  CareerContextExtractionResult,
  CareerContextInput,
  CaptureSourceType,
  ExtractFromTextResult,
  LeadPriority,
  PersonalLead,
  PersonalRuleAction,
  PersonalLeadStatus,
  PersonalOpportunityType,
  RelationshipStrength,
} from "@aoe/shared-types";

export interface PersonalApiError {
  message: string;
  status: number;
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function toCamel(s: string): string {
  return s.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());
}

function transformKeys<T>(value: unknown): T {
  if (Array.isArray(value)) {
    return value.map((item) => transformKeys(item)) as unknown as T;
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [toCamel(k), transformKeys(v)]),
    ) as T;
  }
  return value as T;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const hasCustomHeaders = Boolean(options?.headers);
  const headers = hasCustomHeaders
    ? (options?.headers as HeadersInit)
    : { "Content-Type": "application/json" };
  const res = await fetch(`${BASE}${path}`, {
    headers,
    ...options,
  });
  const data: unknown = await res.json();
  if (!res.ok) {
    const detail = (data as { detail?: string }).detail;
    throw {
      message: detail ?? `Request failed (${res.status})`,
      status: res.status,
    } as PersonalApiError;
  }
  return transformKeys<T>(data);
}

export interface PersonalLeadInput {
  name: string;
  role: string;
  organisation: string;
  organisationWebsite: string;
  linkedinUrl: string;
  email: string;
  location: string;
  source: string;
  opportunityType: PersonalOpportunityType;
  relationshipStrength: RelationshipStrength;
  status: PersonalLeadStatus;
  fitScore: number;
  priority: LeadPriority;
  problemObserved: string;
  whyRelevant: string;
  suggestedAngle: string;
  notes: string;
  tags: string[];
  nextAction: string;
  followUpDate: string | null;
}

export interface ExtractFromTextInput {
  rawText: string;
  sourceType: CaptureSourceType;
  optionalSourceUrl: string;
  userGoal: PersonalOpportunityType;
  useCareerContext: boolean;
}

export interface ExtractCareerContextInput {
  rawCvText: string;
  extractionMode: CareerContextExtractionMode;
  file?: File | null;
}

function toSnakePayload(payload: Partial<PersonalLeadInput>): Record<string, unknown> {
  return {
    name: payload.name,
    role: payload.role,
    organisation: payload.organisation,
    organisation_website: payload.organisationWebsite,
    linkedin_url: payload.linkedinUrl,
    email: payload.email,
    location: payload.location,
    source: payload.source,
    opportunity_type: payload.opportunityType,
    relationship_strength: payload.relationshipStrength,
    status: payload.status,
    fit_score: payload.fitScore,
    priority: payload.priority,
    problem_observed: payload.problemObserved,
    why_relevant: payload.whyRelevant,
    suggested_angle: payload.suggestedAngle,
    notes: payload.notes,
    tags: payload.tags,
    next_action: payload.nextAction,
    follow_up_date: payload.followUpDate,
  };
}

export const personalLeadsApi = {
  list(filters?: {
    opportunityType?: PersonalOpportunityType;
    status?: PersonalLeadStatus;
    priority?: LeadPriority;
  }): Promise<PersonalLead[]> {
    const query = new URLSearchParams();
    if (filters?.opportunityType) query.set("opportunity_type", filters.opportunityType);
    if (filters?.status) query.set("status", filters.status);
    if (filters?.priority) query.set("priority", filters.priority);
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return apiFetch<PersonalLead[]>(`/personal/leads${suffix}`);
  },

  create(payload: PersonalLeadInput): Promise<PersonalLead> {
    return apiFetch<PersonalLead>("/personal/leads", {
      method: "POST",
      body: JSON.stringify(toSnakePayload(payload)),
    });
  },

  get(id: string): Promise<PersonalLead> {
    return apiFetch<PersonalLead>(`/personal/leads/${encodeURIComponent(id)}`);
  },

  update(id: string, payload: Partial<PersonalLeadInput>): Promise<PersonalLead> {
    return apiFetch<PersonalLead>(`/personal/leads/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(toSnakePayload(payload)),
    });
  },

  remove(id: string): Promise<{ deleted: boolean }> {
    return apiFetch<{ deleted: boolean }>(`/personal/leads/${encodeURIComponent(id)}`, {
      method: "DELETE",
    });
  },

  importCsv(csvText: string): Promise<PersonalLead[]> {
    return apiFetch<PersonalLead[]>("/personal/leads/import-csv", {
      method: "POST",
      body: JSON.stringify({ csv_text: csvText }),
    });
  },

  createRuleAction(id: string): Promise<PersonalRuleAction> {
    return apiFetch<PersonalRuleAction>(`/personal/leads/${encodeURIComponent(id)}/create-rule-action`, {
      method: "POST",
    });
  },

  listRuleActions(leadId: string): Promise<PersonalRuleAction[]> {
    return apiFetch<PersonalRuleAction[]>(
      `/personal/leads/${encodeURIComponent(leadId)}/rule-actions`,
    );
  },

  getCareerContext(): Promise<CareerContext> {
    return apiFetch<CareerContext>("/personal/career-context");
  },

  updateCareerContext(payload: CareerContextInput): Promise<CareerContext> {
    return apiFetch<CareerContext>("/personal/career-context", {
      method: "PUT",
      body: JSON.stringify({
        current_headline: payload.currentHeadline,
        target_roles: payload.targetRoles,
        core_skills: payload.coreSkills,
        technical_stack: payload.technicalStack,
        project_highlights: payload.projectHighlights,
        industries: payload.industries,
        location_preferences: payload.locationPreferences,
        visa_notes: payload.visaNotes,
        preferred_opportunity_types: payload.preferredOpportunityTypes,
        positioning_statement: payload.positioningStatement,
        proof_points: payload.proofPoints,
        raw_cv_text: payload.rawCvText,
      }),
    });
  },

  extractFromText(payload: ExtractFromTextInput): Promise<ExtractFromTextResult> {
    return apiFetch<ExtractFromTextResult>("/personal/leads/extract-from-text", {
      method: "POST",
      body: JSON.stringify({
        raw_text: payload.rawText,
        source_type: payload.sourceType,
        optional_source_url: payload.optionalSourceUrl || null,
        user_goal: payload.userGoal,
        use_career_context: payload.useCareerContext,
      }),
    });
  },

  async extractCareerContext(payload: ExtractCareerContextInput): Promise<CareerContextExtractionResult> {
    const body = new FormData();
    body.append("raw_cv_text", payload.rawCvText || "");
    body.append("extraction_mode", payload.extractionMode);
    if (payload.file) {
      body.append("cv_file", payload.file);
    }
    return apiFetch<CareerContextExtractionResult>("/personal/career-context/extract", {
      method: "POST",
      body,
      headers: {},
    });
  },
};
