export type OpportunityCategory =
  | "job"
  | "freelance"
  | "client-lead"
  | "partnership";

export type OpportunityStatus =
  | "new"
  | "reviewed"
  | "saved"
  | "contacted"
  | "rejected";

export interface Opportunity {
  id: string;
  title: string;
  organization: string;
  source: string;
  category: OpportunityCategory;
  relevanceScore: number;
  summary: string;
  whyItMatches: string;
  suggestedAction: string;
  status: OpportunityStatus;
  createdAt: string;
}

export interface TailoringInput {
  targetRole: string;
  jobDescription: string;
  resumeHighlights: string[];
}

export interface ConfidenceSignal {
  label: "needs-refinement" | "more-specific" | "ground-with-example";
  message: string;
}

export interface TailoringDraft {
  id: string;
  opportunityId: string;
  cvBullets: string[];
  motivationLetter: string;
  outreachDraft: string;
  projectEmphasis: string[];
  confidenceSignals: ConfidenceSignal[];
  humanApproved: boolean;
}

export interface PipelineSummary {
  total: number;
  byStatus: Record<OpportunityStatus, number>;
  byCategory: Record<OpportunityCategory, number>;
}
