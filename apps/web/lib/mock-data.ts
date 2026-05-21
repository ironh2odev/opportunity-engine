import type { Opportunity, PipelineSummary, TailoringDraft } from "@aoe/shared-types";

export const opportunities: Opportunity[] = [
  {
    id: "opp_1",
    title: "Senior Product Engineer (AI Tooling)",
    organization: "North Harbor Labs",
    source: "LinkedIn",
    category: "job",
    relevanceScore: 91,
    summary:
      "High-growth SaaS team shipping workflow automation for revenue operations.",
    whyItMatches:
      "Strong overlap with React platform work, AI-assisted feature delivery, and B2B dashboard systems.",
    suggestedAction:
      "Draft tailored CV bullets around internal tools, feature ownership, and measurable outcomes.",
    status: "new",
    createdAt: "2026-05-20T08:00:00.000Z",
  },
  {
    id: "opp_2",
    title: "Fractional Growth Engineer",
    organization: "Arclight Commerce",
    source: "Warm intro",
    category: "freelance",
    relevanceScore: 87,
    summary:
      "Hands-on 8-week engagement focused on conversion funnel diagnostics and experiment velocity.",
    whyItMatches:
      "You have shipped onboarding and pricing experiments with clear impact metrics.",
    suggestedAction:
      "Use outreach draft with a concise 30-60-90 implementation plan.",
    status: "saved",
    createdAt: "2026-05-20T10:00:00.000Z",
  },
  {
    id: "opp_3",
    title: "AI Workflow Partnership",
    organization: "NimbleStack Studio",
    source: "Community",
    category: "partnership",
    relevanceScore: 78,
    summary:
      "Boutique studio seeks partner for reusable workflow + dashboard productization.",
    whyItMatches:
      "Direct fit with your strategy-first positioning and technical architecture focus.",
    suggestedAction:
      "Schedule discovery call and validate ICP alignment before proposal.",
    status: "reviewed",
    createdAt: "2026-05-20T11:30:00.000Z",
  },
  {
    id: "opp_4",
    title: "Outbound RevOps Lead Identification",
    organization: "Monarch Metrics",
    source: "Apollo export",
    category: "client-lead",
    relevanceScore: 83,
    summary:
      "Potential lead list for teams hiring GTM engineers with AI process bottlenecks.",
    whyItMatches:
      "Your positioning and case studies align with ops automation and measurable throughput gains.",
    suggestedAction:
      "Queue personalized outreach and include one relevant mini-case example.",
    status: "new",
    createdAt: "2026-05-20T13:10:00.000Z",
  },
];

export const pipelineSummary: PipelineSummary = {
  total: opportunities.length,
  byStatus: {
    new: 2,
    reviewed: 1,
    saved: 1,
    contacted: 0,
    rejected: 0,
  },
  byCategory: {
    job: 1,
    freelance: 1,
    "client-lead": 1,
    partnership: 1,
  },
};

export const tailoringDrafts: TailoringDraft[] = [
  {
    id: "draft_1",
    opportunityId: "opp_1",
    cvBullets: [
      "Led development of a workflow orchestration dashboard used by 12 internal teams, reducing response time by 41%.",
      "Shipped AI-assisted writing tooling with human approval gates, improving draft quality and reducing revision loops.",
      "Collaborated across product and data to build a typed analytics layer for experimentation reporting.",
    ],
    motivationLetter:
      "Your focus on practical AI tooling resonates with how I build: structured systems, clear user controls, and measurable outcomes.",
    outreachDraft:
      "I was drawn to your AI tooling mission. I can contribute across workflow UX, typed contracts, and production reliability from week one.",
    projectEmphasis: [
      "Workflow dashboard architecture",
      "Human-in-the-loop AI UX",
      "Typed data contracts",
    ],
    confidenceSignals: [
      {
        label: "needs-refinement",
        message: "Needs refinement: add one concrete metric for cross-functional delivery impact.",
      },
      {
        label: "ground-with-example",
        message: "Consider grounding this with an example from your most recent AI-enabled project.",
      },
    ],
    humanApproved: false,
  },
];
