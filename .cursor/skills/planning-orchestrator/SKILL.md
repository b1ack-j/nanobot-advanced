---
name: planning-orchestrator
description: Coordinate the 4-phase planning pipeline (Understand, Design, Synthesize, Challenge). Maintains project overview, changelog, and decision records. Use when starting a new project planning effort.
---

# Planning Orchestrator

## When to Use

- Starting a new project that needs structured planning
- Coordinating the full planning pipeline from requirements to review
- Need to resume or check status of an ongoing planning effort

## Core Principle

**You are a coordinator, not a factory. Your job is to guide the conversation through four phases, ensuring each phase does its job (especially interviewing the user) before moving on.**

## The Phases

```
Phase 1: Understand  --[research checkpoint?]-->  Phase 2: Design  -->  Phase 3: Synthesize  -->  Phase 4: Challenge
(requirements-clarifier)                          (architecture-designer)  (blueprint-writer)       (critical-reviewer)
       |                                                |                        |                        |
       v                                                v                        v                        v
  requirements.md                                  architecture.md           blueprint.md             review.md
  research-brief.md (optional)
```

### Phase 1: Understand (requirements-clarifier)
- **Goal**: Align on what to build and why
- **Output**: `docs/<project>/requirements.md` + optionally `docs/<project>/research-brief.md`
- **Transition**: If research brief was produced, enter Research Checkpoint. Otherwise, move to Phase 2.

### Research Checkpoint (between Phase 1 and Phase 2)

This is an **optional pause** for ideas with significant unknowns (market viability, technical feasibility, regulatory questions, competitive landscape). It is skippable for well-understood projects.

**How it works:**
1. If the requirements-clarifier produced a `research-brief.md`, the orchestrator pauses and tells the user:
   > "I've identified key unknowns that should be validated before we design the architecture. The research brief is at `docs/<project>/research-brief.md`. Please feed it to your research agent (or do the research manually), then put the results in `docs/<project>/research-results.md`. Let me know when it's ready."
2. The orchestrator waits for the user to signal that research is complete.
3. When the user is ready, the orchestrator reads `research-results.md` and proceeds to Phase 2.
4. The architecture-designer will use `research-results.md` as additional input alongside `requirements.md`.

**If no research brief was produced**, or the user explicitly skips research:
- Proceed directly to Phase 2.
- Note the skip in overview.md (e.g., "Research: skipped (domain well-understood)").

### Phase 2: Design (architecture-designer)
- **Goal**: Design the system structure from multiple perspectives
- **Inputs**: `requirements.md` + `research-results.md` (if available)
- **Output**: `docs/<project>/architecture.md` + relevant `specs/` files
- **Transition**: Move to Phase 3 when key architectural decisions are made and documented

### Phase 3: Synthesize (blueprint-writer)
- **Goal**: Create an actionable build plan with phases and milestones
- **Output**: `docs/<project>/blueprint.md`
- **Transition**: Move to Phase 4 when the build plan is concrete enough to review

### Phase 4: Challenge (critical-reviewer)
- **Goal**: Surface blind spots, risks, and weaknesses before implementation
- **Output**: `docs/<project>/review.md`
- **Transition**: If review recommends changes, loop back to the appropriate phase. If approved, planning is complete.

## How to Orchestrate

### Starting a New Project

1. Ask the user for a project name/slug (e.g., `trading-agent`)
2. Create `docs/<project>/overview.md` with initial status (pass 1)
3. Create `docs/<project>/CHANGELOG.md` with a pass 1 header
4. Begin Phase 1 by invoking the requirements-clarifier skill's interview protocol
5. Follow each phase through to completion before advancing

### During Each Phase

- **Invoke the phase skill's interview protocol** -- the skill defines what questions to ask
- **Do not skip interviews** -- every phase must interact with the user before producing output
- **Do not rush** -- one question per turn, let the user think
- **Track progress** -- update overview.md as phases complete

### Phase Transitions

Before advancing to the next phase:
1. The current phase's document has been written (with revision header)
2. Any key decisions from this phase have been recorded in `decisions/`
3. A changelog entry has been appended to `CHANGELOG.md` for this phase
4. The user has been informed of the transition
5. Overview.md has been updated

### Looping Back (New Pass)

If the critical reviewer (Phase 4) recommends changes, or the user requests a deeper pass:
1. **Increment the pass number** (e.g., pass 1 → pass 2)
2. Re-enter the appropriate phase with the specific issue to address
3. The phase skill **updates the existing document** (increments its revision, adds content)
4. The phase skill returns a **change summary** describing what was modified
5. Record new/revised decisions in `decisions/` (supersede old ones if applicable)
6. Append a new pass entry to `CHANGELOG.md` with the change summary
7. Update overview.md
8. **Recommend a git commit** at the pass boundary (see Git Discipline below)

### Git Discipline

At each pass boundary (after all phases in the pass are complete), recommend the user commits:

- Commit message format: `planning(<project>): pass N — one-line summary`
- Example: `planning(silverhand): pass 2 — deep-dive on orchestrator, memory, proactive, state machine, sub-agents`
- This gives real version history via `git log -- docs/<project>/`
- Previous file contents are recoverable via `git show`

## Version Management

### Pass-Based Model

A **pass** is one traversal (full or partial) of the pipeline. Each pass is numbered sequentially. The orchestrator tracks the current pass number in overview.md.

- **Pass 1**: Initial full pipeline run (all 4 phases)
- **Pass 2+**: Loop-back or deepening run (may re-run only some phases)

### Canonical Files with Revision Headers

Each phase document is a **single canonical file** (e.g., `architecture.md`, never `architecture-v2.md`). The file always contains the latest version. Each document starts with a revision header:

```markdown
# <Project Name> — <Document Type>

> Revision: 2 | Pass: 2 | Updated: 2026-03-02
> Previous revisions: see CHANGELOG.md and git history
```

When a phase skill updates an existing document, it increments the revision number and updates the date.

### CHANGELOG.md

Maintain `docs/<project>/CHANGELOG.md` as a reverse-chronological log of planning evolution. Each pass gets an entry. Each phase transition within a pass also gets a sub-entry.

```markdown
# Changelog

## Pass 2 — 2026-03-02
**Scope**: Architecture (5 deep sub-systems), Review
**Trigger**: v1 left orchestrator, memory, proactive, state machine shallow

### What Changed
- **architecture.md** rev 1→2: Added sections 1-5 (orchestrator, memory depth, proactive, state machine, sub-agents)
- **review.md** rev 1→2: 7 new findings on deep sub-systems

### Decisions Made / Revised
- [002 Lazy Planning](decisions/002-lazy-planning.md) — execute first, plan only when multi-step detected
- [003 Memory Extraction](decisions/003-memory-extraction-strategy.md) — use existing skill calls, not per-turn LLM

---

## Pass 1 — 2026-03-01
**Scope**: Full pipeline (all 4 phases)

### Documents Created
- requirements.md (rev 1), architecture.md (rev 1), blueprint.md (rev 1), review.md (rev 1)

### Decisions Made
- [001 Voice Pipeline](decisions/001-voice-pipeline-approach.md) — STT→LLM→TTS, not Realtime API
```

### Decision Records

Maintain `docs/<project>/decisions/` with lightweight ADR (Architecture Decision Record) files. Create one when a significant decision is made during any phase.

File naming: `NNN-short-title.md` (e.g., `001-voice-pipeline-approach.md`)

Template:
```markdown
# NNN — Decision Title

**Status**: Active | Superseded by [XXX](XXX-title.md)
**Pass**: N | **Phase**: Design | **Date**: YYYY-MM-DD

## Context
Why this decision was needed. What problem or question triggered it.

## Decision
What was decided. Be specific.

## Alternatives Considered
1. Alternative A — why not chosen
2. Alternative B — why not chosen

## Consequences
What follows from this decision. Trade-offs accepted.
```

When a decision is **superseded**, update the old record's status to `Superseded by [NNN](NNN-title.md)` and link forward.

### Reference Specs

Maintain `docs/<project>/specs/` for implementor-facing reference documents. These are updated alongside architecture but serve builders rather than planners:

- `api-contracts.md` — endpoint signatures, request/response shapes
- `data-models.md` — DB schemas, entity definitions, migrations
- `protocols.md` — WebSocket messages, push payloads, event formats
- `infrastructure.md` — infrastructure-specific docs (Redis, S3, Neo4j, etc.) as they are introduced

The architecture-designer skill should create/update relevant specs/ files when architectural decisions imply them (e.g., new DB tables, new API endpoints, new protocols).

## Output: overview.md

Maintain `docs/<project>/overview.md` as a living navigation hub. It should be **lightweight** — link to decisions and changelog rather than inlining everything.

```markdown
# <Project Name>

> One-line project description.

## Status

| Phase | Status | Document | Revision |
|-------|--------|----------|----------|
| 1. Understand | complete / in-progress / pending | requirements.md | rev N |
| Research | complete / skipped / pending | research-brief.md, research-results.md | — |
| 2. Design | complete / in-progress / pending | architecture.md | rev N |
| 3. Synthesize | complete / in-progress / pending | blueprint.md | rev N |
| 4. Challenge | complete / in-progress / pending | review.md | rev N |

**Current pass**: N | **Last updated**: YYYY-MM-DD

## Current Phase

<which phase we're in and what's happening>

## Exploration Map

A mermaid graph showing the key decisions and exploration path.
Each node should indicate which pass introduced it.

    ```mermaid
    flowchart TD
        root["Project Idea"]
        root --> goal["Goal?"]
        goal --> goalDecision["Decided: ... (pass 1)"]
        root --> arch["Architecture?"]
        arch --> archDecision["Decided: ... (pass 1)"]
        arch --> archRevised["Revised: ... (pass 2)"]
    ```

## Key Decisions

Link to decision records rather than inlining. Group by topic.

### Scope & Goals
- [001 — Voice Pipeline Approach](decisions/001-voice-pipeline-approach.md)

### Architecture
- [002 — Lazy Planning](decisions/002-lazy-planning.md)
- [003 — Memory Extraction Strategy](decisions/003-memory-extraction-strategy.md)

### Risk & Constraints
- ...

## Document Map

| Document | What it covers | Reading order |
|----------|---------------|---------------|
| **requirements.md** | WHY and WHAT — goals, scope, constraints, success criteria | Read first |
| **architecture.md** | HOW — components, data flow, deployment, domain model, trade-offs | Read second |
| **blueprint.md** | WHEN — phased build plan, milestones, interfaces, effort estimates | Read third |
| **review.md** | CHALLENGE — multi-expert findings, risks, recommendation | Read alongside architecture |
| **CHANGELOG.md** | Evolution narrative — what changed each pass and why | Read when catching up |
| **decisions/** | Individual decision records with context and alternatives | Browse by topic |
| **specs/** | Builder reference — API contracts, data models, protocols | Read when implementing |

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full pass-by-pass evolution narrative.
```

## Boundaries

- Do NOT use version suffixes in filenames (no `architecture-v2.md` — use revision headers)
- Do NOT create Python scripts, JSON schemas, or validation tools
- Do NOT skip phases or rush through interviews
- Do NOT make major decisions without asking the user
- Do NOT create planning/runs/ directories or stage-status tracking systems
- Do NOT inline all decisions in overview.md — link to decision records
- Keep the overhead minimal -- the value is in the documents, not the process

## References

- `references/phase-transitions.md` -- when and how to move between phases
