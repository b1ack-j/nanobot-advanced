# Output Guide: blueprint.md

## Purpose

The blueprint translates requirements + architecture into an actionable build plan. It answers: "What do we build first? What comes next? What are the key milestones?"

## File Location

`docs/<project>/blueprint.md`

## Quality Bar

- **Actionable**: A developer knows where to start after reading this
- **Phased**: Work is broken into clear, sequential phases with milestones
- **Realistic**: Acknowledges complexity, dependencies, and unknowns
- **Prioritized**: The most important / riskiest things are addressed first
- **Concise**: Each phase is described in enough detail to start, not a full spec

## Revision Header

Every blueprint document must start with a revision header. On first creation, use revision 1. On updates (loop-back from review or new pass), increment the revision.

```markdown
> Revision: N | Pass: N | Updated: YYYY-MM-DD
> Previous revisions: see CHANGELOG.md and git history
```

When updating an existing document, the skill must:
1. Increment the revision number in the header
2. Update the date
3. Return a **change summary** to the orchestrator (1-3 sentences describing what changed and why) for logging in CHANGELOG.md

## Suggested Structure

```markdown
# Blueprint: <Project Name>

> Revision: 1 | Pass: 1 | Updated: YYYY-MM-DD
> Previous revisions: see CHANGELOG.md and git history

> One-line summary of the build approach.

## Phase Overview

| Phase | Goal | Key Deliverable | Estimated Effort |
|-------|------|-----------------|-----------------|
| 1     | ...  | ...             | S/M/L/XL        |
| 2     | ...  | ...             | S/M/L/XL        |
| 3     | ...  | ...             | S/M/L/XL        |

(Optional: mermaid diagram showing phase dependencies)

## Phase 1: <Name>

### Goal
What this phase achieves and why it's first.

### What to Build
- Component or capability 1
- Component or capability 2

### Done Criteria
How we know this phase is complete.

### Unlocks
What this phase enables for subsequent phases.

## Phase 2: <Name>
(same structure)

## Phase N: <Name>
(same structure)

## Key Interfaces

Critical integration points that need early definition or agreement.
- Interface 1: between X and Y -- what contract is needed
- Interface 2: between Y and Z -- what data flows

## Build vs Buy / Reuse

| Need | Approach | Why |
|------|----------|-----|
| ...  | Build / Use X | ... |

## Open Decisions

Things we can decide later without blocking early phases.

## Risks to the Plan

What could go wrong with this build sequence and how to mitigate.
```

## Anti-Patterns

- Do NOT produce YAML task files or executable plans
- Do NOT assign specific owners or estimate hours
- Do NOT repeat the full architecture -- reference it
- Do NOT over-detail later phases (they will change)
- Do NOT list every possible task -- focus on milestones and phases
- Do NOT use version suffixes in filenames (no `blueprint-v2.md`) -- use revision headers
