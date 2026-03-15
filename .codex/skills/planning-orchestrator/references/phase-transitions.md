# Phase Transition Guide

## General Rules

1. A phase is complete when its output document is written and the user is satisfied
2. Each phase must include user interviews before producing output
3. Never skip a phase (exception: user explicitly says to)
4. The orchestrator decides when to transition, but announces it to the user

## Phase 1 -> Research Checkpoint -> Phase 2 (Understand -> [Research] -> Design)

### Phase 1 complete when:
- requirements.md has been written
- Key areas are covered: goals, scope, constraints, success criteria
- No unresolved contradictions
- User confirms the requirements capture their intent

### Research checkpoint decision:

**If research-brief.md was produced:**
- Pause and tell the user research is needed
- Transition message:
  "Requirements are aligned. I've identified some unknowns that should be validated before we design. The research brief is at `docs/<project>/research-brief.md` -- please feed it to your deep research agent (or research manually), and put the results in `docs/<project>/research-results.md`. Let me know when it's ready."
- Wait for user to signal research is complete
- When ready, read research-results.md and proceed to Phase 2

**If no research-brief.md was produced:**
- Ask the user: "There are no major unknowns flagged. Are you ready to move to architecture design, or would you like to do some research first?"
- If ready, proceed directly to Phase 2
- Transition message:
  "Requirements are aligned. Let's move to architecture -- I'll start by looking at the key structural decisions we need to make."

**If user explicitly skips research:**
- Note in overview.md: "Research: skipped (user decision)"
- Proceed to Phase 2

## Phase 2 -> Phase 3 (Design -> Synthesize)

### Ready when:
- architecture.md has been written
- Major components are identified with clear boundaries
- Key architectural decisions are made and documented
- Trade-offs are explicit

### Transition message:
"Architecture is established. Let's figure out the build plan -- what to build first and how to phase the work."

## Phase 3 -> Phase 4 (Synthesize -> Challenge)

### Ready when:
- blueprint.md has been written
- Phases are defined with milestones
- Build order is justified
- Key interfaces identified

### Transition message:
"Blueprint is ready. Let me review it critically from multiple expert perspectives before we commit to building."

## Phase 4 -> Done (or Loop Back)

### If review approves:
- Update overview.md with "Planning Complete" status
- Summarize the key outputs to the user
- The user can start implementing from the docs

### If review finds critical issues:
- Identify which earlier phase needs revision
- Explain to user what needs to change and why
- Re-enter the appropriate phase
- Update the existing document (don't start from scratch)
- Continue forward from there

## Handling User Requests to Skip or Jump

- If user says "skip to architecture" -- ask if they're comfortable with the current requirements understanding. If yes, note the assumption and proceed.
- If user says "I just need a quick review" -- still read all existing docs before reviewing, but keep the review focused.
- If user wants to go back to an earlier phase -- that's fine, update overview.md and re-enter that phase with the specific issue.

## Resuming an Interrupted Session

When resuming:
1. Read overview.md to understand current state
2. Read the most recent phase document
3. Tell the user where you left off
4. Continue from there
