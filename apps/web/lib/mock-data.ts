import type {
  ActionChannel,
  DailyAction,
  DailyActionStatus,
  DailyRollup,
  Opportunity,
  PipelineSummary,
  RuleOf100Plan,
  TailoringDraft,
} from "@aoe/shared-types";

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

export const ruleOf100Plan: RuleOf100Plan = {
  id: "plan_2026-06-29",
  date: "2026-06-29",
  targetCount: 50,
  minTarget: 50,
  maxTarget: 100,
  defaultMode: "rule_of_50",
  allocation: {
    linkedin_comment: 20,
    client_lead_discovery: 10,
    connection_request: 5,
    follow_up: 5,
    content_creation: 5,
    outreach_dm: 3,
    job_application: 2,
  },
  notes:
    "Allocation is editable. Connection requests are optional and can be shifted to follow-ups or lead discovery as needed.",
};

const statusCycle: DailyActionStatus[] = [
  "suggested",
  "in_review",
  "approved",
  "completed",
  "suggested",
  "approved",
  "in_review",
  "completed",
];

const channelTemplates: Array<{
  channel: ActionChannel;
  actionType: string;
  opportunityType: DailyAction["opportunityType"];
  source: string;
  outboundCapable: boolean;
  titlePrefix: string;
}> = [
  {
    channel: "linkedin_comment",
    actionType: "Comment draft",
    opportunityType: "networking",
    source: "Mock LinkedIn Feed",
    outboundCapable: true,
    titlePrefix: "Comment on post about AI workflow operations",
  },
  {
    channel: "client_lead_discovery",
    actionType: "Lead profile save",
    opportunityType: "client-lead",
    source: "Mock Lead List",
    outboundCapable: false,
    titlePrefix: "Save and tag RevOps prospect profile",
  },
  {
    channel: "connection_request",
    actionType: "Connection request draft",
    opportunityType: "networking",
    source: "Mock Network Search",
    outboundCapable: true,
    titlePrefix: "Draft connection request with context",
  },
  {
    channel: "follow_up",
    actionType: "Follow-up draft",
    opportunityType: "freelance",
    source: "Mock Outreach Queue",
    outboundCapable: true,
    titlePrefix: "Draft follow-up for prior discovery note",
  },
  {
    channel: "content_creation",
    actionType: "Content research",
    opportunityType: "content",
    source: "Mock Content Backlog",
    outboundCapable: false,
    titlePrefix: "Outline a credibility-building content post",
  },
  {
    channel: "outreach_dm",
    actionType: "Outreach DM draft",
    opportunityType: "client-lead",
    source: "Mock Warm Intro Queue",
    outboundCapable: true,
    titlePrefix: "Draft personalized outbound intro",
  },
  {
    channel: "job_application",
    actionType: "Application draft",
    opportunityType: "job",
    source: "Mock Job Board",
    outboundCapable: true,
    titlePrefix: "Draft role-specific application summary",
  },
  {
    channel: "referral_request",
    actionType: "Referral request draft",
    opportunityType: "networking",
    source: "Mock Alumni Network",
    outboundCapable: true,
    titlePrefix: "Prepare referral request with proof points",
  },
];

function fakePerson(seed: number): { name: string; role: string; org: string } {
  const names = [
    "Taylor Rowan",
    "Avery Pike",
    "Jordan Vale",
    "Morgan Hale",
    "Casey Flint",
    "Riley North",
    "Parker Lane",
    "Quinn Harbor",
  ];
  const roles = [
    "Growth Lead",
    "RevOps Manager",
    "Product Marketing Lead",
    "Talent Partner",
    "Founder",
    "Head of Partnerships",
  ];
  const orgs = [
    "Northfield Systems",
    "Summit Relay",
    "Blue Harbor Labs",
    "Cobalt Ridge",
    "Pioneer Signal",
    "Asterline Works",
  ];
  return {
    name: names[seed % names.length],
    role: roles[seed % roles.length],
    org: orgs[seed % orgs.length],
  };
}

function channelSequenceFromAllocation(allocation: Partial<Record<ActionChannel, number>>): ActionChannel[] {
  return Object.entries(allocation).flatMap(([channel, count]) =>
    Array.from({ length: Number(count || 0) }, () => channel as ActionChannel),
  );
}

const sequence = channelSequenceFromAllocation(ruleOf100Plan.allocation);

export const dailyActions: DailyAction[] = sequence.map((channel, index) => {
  const template = channelTemplates.find((item) => item.channel === channel) ?? channelTemplates[0];
  const person = fakePerson(index + 3);
  const status = statusCycle[index % statusCycle.length];
  const createdAt = `2026-06-29T${String(7 + (index % 10)).padStart(2, "0")}:${String((index * 7) % 60).padStart(2, "0")}:00.000Z`;

  return {
    id: `action_${String(index + 1).padStart(3, "0")}`,
    date: "2026-06-29",
    channel,
    actionType: template.actionType,
    title: `${template.titlePrefix} #${index + 1}`,
    targetName: person.name,
    targetRole: person.role,
    targetOrganisation: person.org,
    opportunityType: template.opportunityType,
    source: template.source,
    fitScore: (index % 10) + 1,
    confidenceLabel: index % 3 === 0 ? "high" : index % 3 === 1 ? "medium" : "low",
    suggestedAction: `Prepare a concise draft for ${person.name} and keep claims grounded in verifiable outcomes.`,
    suggestedMessage:
      template.outboundCapable
        ? `Hi ${person.name}, I appreciated your perspective on workflow quality. I drafted a short note tailored to ${person.org} and would value your feedback.`
        : `Capture three notes from ${person.org} activity and tag one follow-up hypothesis for tomorrow.`,
    rationale:
      "This action supports consistent daily volume while prioritizing relevance and quality over spam behavior.",
    proofToReference:
      "Reference one measurable project outcome and one specific domain example from prior work.",
    status,
    followUpDate: index % 4 === 0 ? "2026-07-01" : null,
    createdAt,
    outboundCapable: template.outboundCapable,
    approvalRequired: template.outboundCapable,
  };
});

export const mockApprovalRecords = dailyActions
  .filter((item) => item.status === "approved" || item.status === "completed")
  .map((item, index) => ({
    id: `approval_${String(index + 1).padStart(3, "0")}`,
    actionId: item.id,
    approvedBy: "human.operator",
    approvedAt: `2026-06-29T15:${String((index * 5) % 60).padStart(2, "0")}:00.000Z`,
    note: "Approved for manual execution. Do not auto-send.",
  }));

export const dailyRollup: DailyRollup = {
  date: ruleOf100Plan.date,
  targetCount: ruleOf100Plan.targetCount,
  completedCount: dailyActions.filter((item) => item.status === "completed").length,
  progressPercent: Math.round(
    (dailyActions.filter((item) => item.status === "completed").length /
      ruleOf100Plan.targetCount) *
      100,
  ),
  pendingReviewCount: dailyActions.filter((item) => item.status === "in_review").length,
  approvedCount: dailyActions.filter((item) => item.status === "approved").length,
  completedApprovedCount: dailyActions.filter(
    (item) => item.status === "completed" && (!item.approvalRequired || item.outboundCapable),
  ).length,
  byChannel: dailyActions.reduce<Partial<Record<ActionChannel, number>>>((acc, item) => {
    acc[item.channel] = (acc[item.channel] ?? 0) + 1;
    return acc;
  }, {}),
};
