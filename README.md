# Opportunity Engine

AI-assisted, human-reviewed workflow platform for opportunity discovery, application tailoring, and confidence feedback.

## Overview

Opportunity Engine helps engineers and job seekers structure and accelerate application work without automating outbound actions. It combines a modern full-stack dashboard with backend extraction and recommendation logic, while enforcing review-first guardrails and privacy-conscious data boundaries. The project is designed as a portfolio-grade case study of full-stack architecture, Python backend engineering, and applied AI workflow integration.

## Key Features

- Human-in-the-loop workflow: outbound actions require explicit user approval.
- Personal Leads management: create, update, list, and safely delete leads.
- Capture Opportunity Assistant: parses pasted listing text into normalized lead fields.
- Career Context import pipeline for local CV/career materials (safe PDF/DOCX extraction support).
- Fit/gap style matching signals and tailored suggestion scaffolding.
- Duplicate lead prevention at persistence level.
- Job-oriented Rule action generation (instead of generic outreach-only actions for job leads).
- Responsive Next.js dashboard UX with sidebar, cards, stats, and tailoring panel.
- Monorepo structure with shared TypeScript contracts and reusable UI package.
- Mock-data-first runtime mode for safe demos and predictable local development.

## Tech Stack

- Frontend:
  - Next.js 14 (App Router), React 18, TypeScript
  - Tailwind CSS
  - Framer Motion
- Backend:
  - FastAPI
  - Pydantic v2
  - Uvicorn
  - python-multipart
- Document Extraction:
  - pypdf
  - python-docx
- Data & Storage:
  - SQLite-backed local store for personal leads/context/actions (implemented in backend service layer)
  - Mock data modules for deterministic demo flows
- Monorepo / Tooling:
  - pnpm workspaces
  - Turbo
  - Shared packages (`packages/shared-types`, `packages/ui`)
- AI / Applied Intelligence:
  - Heuristic extraction + normalization workflow for listing ingestion
  - Optional private/local RAG direction documented (Phase-oriented; see status notes)

## Architecture / How It Works

1. The Next.js frontend provides workflow views for opportunities, personal leads, and tailoring interactions.
2. The frontend calls FastAPI endpoints for lead ingestion, extraction, normalization, and action generation.
3. The backend validates payloads with Pydantic schemas and persists lead/context/action data in a local store.
4. Capture Assistant processes pasted job/opportunity text, removes common boilerplate noise, and synthesizes structured fields (title, company, location, skills, etc.).
5. Tailoring and fit/gap signals are generated as review inputs, not auto-submission outputs.
6. Private user data is expected to stay local (under private boundaries), while public repo content remains mock/sanitized.

Design guardrail: no auto-apply/auto-send behavior is part of the intended flow.

## Screenshots

![Dashboard Screenshot](./screenshots/dashboard.png)  
![Personal Leads Screenshot](./screenshots/personal-leads.png)  
![Capture Assistant Screenshot](./screenshots/capture-assistant.png)

## Getting Started

### Prerequisites

- Node.js 18+ (Needs confirmation: exact minimum version used in your environment)
- pnpm 9+
- Python 3.11+ (Needs confirmation: exact tested minimum)
- macOS/Linux terminal (Windows should also work with equivalent commands; Needs confirmation)

### Installation

```bash
# From repository root
pnpm install
