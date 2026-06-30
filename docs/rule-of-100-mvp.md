# Rule of 100 Daily Actions (Mock-First MVP)

## What this workflow is

Rule of 100 Daily Actions helps operators complete a consistent number of opportunity-creation actions every day across comments, discovery, outreach drafts, follow-ups, applications, referrals, and content work.

This MVP is planning and review software only.

- Draft-only workflow
- Human approval required
- No auto-send
- No auto-apply
- Manual execution only

## Why MVP starts with Rule of 50

The implementation defaults to Rule of 50 to balance consistency and quality in early workflow validation.

- Supported target range is 50 to 100 actions
- Initial default is 50 actions
- Allocation is editable/configurable for platform constraints (for example, connection request limits)

## Human approval model

Some actions are outbound-capable (for example: comment drafts, connection requests, outreach, follow-ups, application drafts, referral requests).

Guard rule:
Outbound-capable actions cannot move to completed unless they have explicit approval first.

This is enforced in API logic and mirrored in UI controls.

## Mock-safe data policy

Safe in this MVP:

- Synthetic/fake people and organizations
- Mock opportunities and action drafts
- Public-safe workflow metadata and status tracking

Never include:

- Real CV details
- Real testimonials
- Real lead exports
- Real contacts
- API keys
- Paid/private materials

## Future roadmap

1. AI scoring refinement
- Better ranking and prioritization signals
- Quality safeguards to avoid low-relevance actions

2. Private-local RAG support
- Optional private corpus grounding
- Keep private data local-only

3. Integrations (future, guarded)
- Read-only ingestion adapters first
- No autonomous outbound actions

4. Analytics
- Channel conversion rates
- Follow-up effectiveness
- Quality metrics and streak reporting

## Personal Mode linkage

- Lead-generated draft actions are persisted in local SQLite storage under `private/local-data/`.
- Each action retains source lead linkage for traceability across restarts.
- Human approval remains mandatory for outbound-capable completion.
- Manual execution only: no auto-send, no auto-apply, no scraping.
