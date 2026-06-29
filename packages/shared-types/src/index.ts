export type OpportunityCategory =
  | "job"
  | "freelance"
  | "client-lead"
  | "partnership";

export type OpportunityType =
  | "job"
  | "freelance"
  | "client-lead"
  | "partnership"
  | "networking"
  | "content";

export type OpportunityStatus =
  | "new"
  | "reviewed"
  | "saved"
  | "contacted"
  | "rejected";

export type DailyActionStatus =
  | "suggested"
  | "in_review"
  | "approved"
  | "completed"
  | "skipped"
  | "blocked";

export type ActionChannel =
  | "linkedin_comment"
  | "connection_request"
  | "outreach_dm"
  | "follow_up"
  | "job_application"
  | "client_lead_discovery"
  | "referral_request"
  | "content_creation";

export type ConfidenceLabel = "low" | "medium" | "high";

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

export interface RuleOf100Plan {
  id: string;
  date: string;
  targetCount: number;
  minTarget: number;
  maxTarget: number;
  defaultMode: "rule_of_50" | "rule_of_100";
  allocation: Partial<Record<ActionChannel, number>>;
  notes: string;
}

export interface DailyAction {
  id: string;
  date: string;
  channel: ActionChannel;
  actionType: string;
  title: string;
  targetName: string;
  targetRole: string;
  targetOrganisation: string;
  opportunityType: OpportunityType;
  source: string;
  fitScore: number;
  confidenceLabel: ConfidenceLabel;
  suggestedAction: string;
  suggestedMessage: string;
  rationale: string;
  proofToReference: string;
  status: DailyActionStatus;
  followUpDate: string | null;
  createdAt: string;
  outboundCapable: boolean;
  approvalRequired: boolean;
}

export interface ApprovalRecord {
  id: string;
  actionId: string;
  approvedBy: string;
  approvedAt: string;
  note?: string;
}

export interface DailyRollup {
  date: string;
  targetCount: number;
  completedCount: number;
  progressPercent: number;
  pendingReviewCount: number;
  approvedCount: number;
  completedApprovedCount: number;
  byChannel: Partial<Record<ActionChannel, number>>;
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
