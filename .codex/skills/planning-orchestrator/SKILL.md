---
name: planning-orchestrator
description: Coordinate the 4-phase planning pipeline (Understand, Design, Synthesize, Challenge). Maintains project overview. Use when starting a new project planning effort.
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
- **Output**: `docs/<project>/architecture.md`
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
2. Create `docs/<project>/overview.md` with initial status
3. Begin Phase 1 by invoking the requirements-clarifier skill's interview protocol
4. Follow each phase through to completion before advancing

### During Each Phase

- **Invoke the phase skill's interview protocol** -- the skill defines what questions to ask
- **Do not skip interviews** -- every phase must interact with the user before producing output
- **Do not rush** -- one question per turn, let the user think
- **Track progress** -- update overview.md as phases complete

### Phase Transitions

Before advancing to the next phase:
- The current phase's document has been written
- The user has been informed of the transition
- Overview.md has been updated

### Looping Back

If the critical reviewer (Phase 4) recommends changes:
- Identify which phase needs revision
- Re-enter that phase with the specific issue to address
- The existing document gets updated, not replaced
- Continue forward from there

## Output: overview.md

Maintain `docs/<project>/overview.md` as a living document. It serves three purposes:
1. **Navigation**: Where are we? What documents exist?
2. **Comprehension**: What did we explore? What did we decide?
3. **Resume point**: A new agent or session can read this and understand the full context.

```markdown
# <Project Name>

> One-line project description.

## Status

| Phase | Status | Document |
|-------|--------|----------|
| 1. Understand | complete / in-progress / pending | requirements.md |
| Research | complete / skipped / pending | research-brief.md, research-results.md |
| 2. Design | complete / in-progress / pending | architecture.md |
| 3. Synthesize | complete / in-progress / pending | blueprint.md |
| 4. Challenge | complete / in-progress / pending | review.md |

## Current Phase

<which phase we're in and what's happening>

## Exploration Map

A mermaid graph showing the key decisions and exploration path.
This is like a DFS tree -- it shows where we started, what branches we explored,
what we decided at each fork, and what remains unexplored.

Update this graph as planning progresses. It should grow with each phase.

(mermaid flowchart TD showing:
- Root: the initial idea
- Branches: key questions/decision points explored
- Leaves: decisions made with brief rationale
- Flagged nodes: areas identified but not yet explored)

Example:
    ```mermaid
    flowchart TD
        root["Project Idea"]
        root --> goal["Goal?"]
        goal --> goalDecision["Decided: ..."]
        root --> arch["Architecture?"]
        arch --> archDecision["Decided: ..."]
        arch --> openQ["Open: ..."]
    ```

## Key Decisions

Grouped by topic. Each decision: what was decided, why, and which phase it came from.

### Scope & Goals
- ...

### Architecture
- ...

### Risk & Constraints
- ...

### Execution & Phasing
- ...

## Document Map

How the docs connect and what each covers:
- **requirements.md**: WHY and WHAT -- goals, scope, constraints, success criteria
- **research-brief.md** (if exists): Key unknowns to validate externally
- **research-results.md** (if exists): External research findings
- **architecture.md**: HOW -- components, data flow, deployment, domain model, trade-offs
- **blueprint.md**: WHEN -- phased build plan, milestones, interfaces, effort estimates
- **review.md**: CHALLENGE -- multi-expert findings, risks, recommendation
```

Update this document as phases progress. The exploration map should grow with each phase -- add new decision nodes as they're made.

## Boundaries

- Do NOT generate artifacts beyond the core markdown documents (overview + 4 phase docs + optional research-brief + user-provided research-results)
- Do NOT create Python scripts, JSON schemas, or validation tools
- Do NOT skip phases or rush through interviews
- Do NOT make major decisions without asking the user
- Do NOT create planning/runs/ directories or stage-status tracking systems
- Keep the overhead minimal -- the value is in the documents, not the process

## References

- `references/phase-transitions.md` -- when and how to move between phases
