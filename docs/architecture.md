# Architecture Overview

## Principles

- Public-by-default architecture, private-by-design data boundaries.
- Human-in-the-loop is a hard requirement for all outbound actions.
- Mock-data-first implementation to validate UX and workflows before integrations.
- Modular engines with typed contracts and clear ownership.

## Layers

1. `apps/web` (presentation + workflow orchestration)
2. `apps/api` (domain services + validation + persistence adapters)
3. `packages/shared-types` (cross-layer contract surface)
4. `packages/ui` (reusable visual primitives)
5. `private/` (local-only user corpus, never committed)

## Product Engines

- Opportunity Discovery Engine
- Application Tailoring Engine
- Application Confidence System
- RAG Knowledge Layer (optional in Phase 1, private/local-only corpus)

## Trust and Defensibility

Generated text is reviewed against user-provided experience.

Preferred UI language:
- Needs refinement
- Could be more specific
- Consider grounding this with an example

## Public vs Private Boundaries

Public:
- Mock records, fake company names, architecture docs, reusable prompts, schemas

Private (local only):
- Real CVs
- Personal lead databases
- Paid guides
- Testimonials
- API keys and secrets
