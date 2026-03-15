# Phase Transition Guide

## General Rules

1. A phase is complete when its output document is written and the user is satisfied
2. Each phase must include user interviews before producing output
3. Never skip a phase (exception: user explicitly says to)
4. The orchestrator decides when to transition, but announces it to the user
5. Every phase transition must include a changelog entry and decision record updates

## Transition Checklist (Every Phase)

Before moving to the next phase, complete all of these:

1. **Document written** — the phase's output document exists with a revision header
2. **Decisions recorded** — any significant decisions from this phase have been added to `decisions/` as ADR files
3. **Changelog updated** — append a sub-entry under the current pass in `CHANGELOG.md` noting what this phase produced or changed
4. **Overview updated** — update the status table and exploration map in `overview.md`
5. **User informed** — tell the user what was completed and what comes next

## Phase 1 -> Research Checkpoint -> Phase 2 (Understand -> [Research] -> Design)

### Phase 1 complete when:
- requirements.md has been written (with revision header)
- Key areas are covered: goals, scope, constraints, success criteria
- No unresolved contradictions
- User confirms the requirements capture their intent
- Decisions from Phase 1 recorded in `decisions/`

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
- architecture.md has been written (with revision header)
- Major components are identified with clear boundaries
- Key architectural decisions are made and documented in `decisions/`
- Trade-offs are explicit
- Relevant `specs/` files created (data-models, api-contracts, protocols as applicable)

### Transition message:
"Architecture is established. Let's figure out the build plan -- what to build first and how to phase the work."

## Phase 3 -> Phase 4 (Synthesize -> Challenge)

### Ready when:
- blueprint.md has been written (with revision header)
- Phases are defined with milestones
- Build order is justified
- Key interfaces identified

### Transition message:
"Blueprint is ready. Let me review it critically from multiple expert perspectives before we commit to building."

## Phase 4 -> Done (or Loop Back / New Pass)

### If review approves:
- Update overview.md with "Planning Complete" status
- Summarize the key outputs to the user
- **Recommend a git commit**: `planning(<project>): pass N — <summary>`
- The user can start implementing from the docs

### If review finds critical issues (loop back within same pass):
- Identify which earlier phase needs revision
- Explain to user what needs to change and why
- Re-enter the appropriate phase
- The phase skill updates the existing document (increments revision)
- The phase skill returns a change summary
- Log the change summary in CHANGELOG.md under the current pass
- Record any new/revised decisions in `decisions/`
- Continue forward from there

### Starting a new pass (deeper exploration):
- Increment the pass number
- Add a new pass header to CHANGELOG.md
- Re-enter the appropriate phase(s)
- Each updated document gets its revision incremented
- New decisions are recorded; superseded decisions are linked forward
- **Recommend a git commit at pass boundary**: `planning(<project>): pass N — <summary>`

## Handling User Requests to Skip or Jump

- If user says "skip to architecture" -- ask if they're comfortable with the current requirements understanding. If yes, note the assumption and proceed.
- If user says "I just need a quick review" -- still read all existing docs before reviewing, but keep the review focused.
- If user wants to go back to an earlier phase -- that's fine, update overview.md and re-enter that phase with the specific issue. This counts as a loop-back, not necessarily a new pass.

## Resuming an Interrupted Session

When resuming:
1. Read overview.md to understand current state (phase, pass number)
2. Read CHANGELOG.md to understand the evolution so far
3. Read the most recent phase document
4. Scan `decisions/` to understand key decisions
5. Tell the user where you left off
6. Continue from there
