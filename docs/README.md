# AntiDeepFake - Documentation Index

This directory contains the engineering specifications, API contracts, sprint planning, validation matrix, and contributor guides for AntiDeepFake (MoMo TechDay '26).

---

## Directory Structure

```text
docs/
├── README.md & README.vi.md             # Documentation index & quick navigation
├── specs/                               # Core Specifications & Contracts
│   ├── spec-product.md & .vi.md         # Scope boundaries, testable rules (R01-R08), mechanisms
│   ├── spec-architecture.md & .vi.md    # 100% Serverless architecture, privacy, ephemeral lifecycle
│   ├── spec-api-contract.md & .vi.md    # Endpoints, Pydantic schemas, HTTP errors, Supabase SQL
│   └── spec-demo.md & .vi.md            # 1-Page judge guide with 3 demo test cases
├── sprints/                             # Agile Sprint Planning
│   └── sprint-plan.md & .vi.md          # 3-Sprint roadmap & Exit Gates towards Dec 03 deadline
├── tasks/                               # Role-Based Tasklists
│   └── tasklist.md & .vi.md             # Concrete tasks for 1 AI Engineer & 2 Backend Engineers
├── validation/                          # Acceptance Gates & Test Matrix
│   └── validation-plan.md & .vi.md      # Offline Gate 1, Live Probe Gate 2, 10-Case Test Matrix
└── guidelines/                          # Workflow & Development Runbooks
    ├── team-workflow.md & .vi.md        # Git branching, Conventional Commits, security & DoD
    └── development.md & .vi.md          # Local setup, ffmpeg, offline tests vs bounded --live check
```

---

## Quick Navigation

- **Product Scope & Rules (R01–R08)**: `docs/specs/spec-product.md` / `.vi.md`
- **Cloud Architecture & Privacy**: `docs/specs/spec-architecture.md` / `.vi.md`
- **API & SQL Data Contracts**: `docs/specs/spec-api-contract.md` / `.vi.md`
- **Online Demo & Judge Guide**: `docs/specs/spec-demo.md` / `.vi.md`
- **Validation Matrix & Gates**: `docs/validation/validation-plan.md` / `.vi.md`
- **Sprint Roadmap & Exit Gates**: `docs/sprints/sprint-plan.md` / `.vi.md`
- **Role Tasklist (1 AI, 2 BE)**: `docs/tasks/tasklist.md` / `.vi.md`
- **Local Setup & Testing Guide**: `docs/guidelines/development.md` / `.vi.md`
- **Team Workflow & Conventions**: `docs/guidelines/team-workflow.md` / `.vi.md`
