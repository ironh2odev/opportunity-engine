# Opportunity Engine

Portfolio-grade, SaaS-style platform for AI-assisted opportunity discovery, application tailoring, and human-reviewed outreach.

## Product Guardrails

- Human approval is required before sending any application or outreach.
- The engine optimizes repetitive work; it does not auto-apply or spam.
- Grounded positioning is prioritized through confidence checks and review workflow.

## Monorepo Structure

- `apps/web`: Next.js App Router dashboard (TypeScript, TailwindCSS, shadcn/ui-ready, Framer Motion)
- `apps/api`: FastAPI backend (mock-data-first)
- `packages/shared-types`: shared TypeScript contracts
- `packages/ui`: reusable UI primitives and domain components
- `docs`: architecture, schema, and product docs
- `private`: local-only personal data (gitignored)

## Privacy Model

This repository uses a privacy-conscious architecture with a local private data boundary.

- Commit only mock/demo data and reusable architecture.
- Keep personal CVs, guides, testimonials, lead databases, and secrets under `private/`.
- `private/`, `.env`, `.env.local`, `*.pdf`, `*.docx`, `*.doc`, and `*.csv` are excluded by `.gitignore`.
- The private RAG corpus is optional and local-only; do not commit personal source documents.

## Mock-Only Runtime Guarantee (Phase 1)

- The web app renders from `apps/web/lib/mock-data.ts`.
- The API serves mock records from `apps/api/app/mock_data.py`.
- No private documents are required to run the MVP.

## Quick Start

### 1) Install dependencies

```bash
pnpm install
```

### 2) Run web app

```bash
pnpm dev:web
```

### 3) Run API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Phase 1 Scope

- Monorepo scaffolding
- Shared types and modular architecture
- Premium mock dashboard UX
- Opportunity cards + workflow queues
- Tailoring assistant with mock drafts
- FastAPI mock endpoints + schema guidance

## Non-Goals (for now)

- Live scraping
- Browser automation
- Auto-applying or auto-sending
- Fully autonomous agents

See `docs/roadmap.md` and `docs/architecture.md` for implementation phases.
