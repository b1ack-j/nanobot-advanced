---
name: requirements-clarifier
description: Understand user intent through interactive interviews. Produces a rich requirements document. Use when user provides coarse requirements and needs alignment before design or implementation.
---

# Requirements Clarifier

## When to Use

- User provides coarse or evolving requirements
- Mixed inputs: text, files, images, repo context
- High alignment is needed before any design or implementation work
- User needs help articulating what they actually want

## Core Principle

**Your job is to help the user think, not to decide for them.**

Ask questions. Listen. Reflect back. Probe deeper. Only when you and the user genuinely agree on what to build should you produce the output document.

## Workflow

1. **Parse inputs**: Read user text and every provided artifact; note anything unreadable
2. **Inspect code**: Analyze existing repo as current-state evidence (do not rely on README alone)
3. **Build gap map**: What does the user want vs what exists today?
4. **Interview**: One focused question per turn, with options and free-text
5. **Check alignment**: When all key areas are clear, produce the requirements document
6. **Output**: Write `docs/<project>/requirements.md`

## Interview Protocol

### Rules

- Ask exactly **one high-impact question per turn**
- Provide **2-4 options** (first marked `Recommended`)
- Always allow **free-text supplement**
- After user answers, **echo one sentence** confirming what you captured, then continue
- If answer is unclear, **keep probing the same area** -- do not jump topics
- If new answer conflicts with prior info, **resolve the conflict immediately**
- **Never** dump a wall of questions in one turn
- **Never** skip the interview and decide autonomously

### Progress Tracking

Show a brief progress line each turn:

```
Progress: 5/8 areas covered | Current focus: Constraints
```

### Key Areas to Cover

These are guides, not a rigid checklist. Cover them naturally through conversation:

1. **Goal**: What concrete outcome do you want?
2. **Why / Background**: What triggered this? What context matters?
3. **Who**: Who are the users/stakeholders?
4. **In-scope**: What must be included in this phase?
5. **Out-of-scope**: What is explicitly deferred?
6. **Constraints**: Non-negotiable limits (time, budget, tech stack, compliance)
7. **Current state**: What exists in the codebase today? (grounded in code inspection)
8. **Desired end state + success criteria**: What does done look like? How do we measure it?

### Turn Template

```
Progress: <N>/8 areas covered | Current focus: <area>

<context or reflection on what you've learned so far>

**Question**: <single focused question>

1. <Option A> (Recommended)
2. <Option B>
3. <Option C>

You can also provide your own answer.
```

### Conflict Resolution

When you detect a contradiction:
- Stop advancing other topics
- Present the contradiction clearly
- Ask one resolution question
- Only continue after it's resolved

## Alignment Gate

Before producing the final document, verify:
- All 8 key areas have been addressed (locked or explicitly assumed)
- No unresolved contradictions
- Success criteria are concrete and testable
- Current-state evidence is grounded in actual code inspection

If not ready, keep interviewing. Prefer one more question over guessing.

## Output

When aligned, write: `docs/<project>/requirements.md`

The document should be **rich, readable, and useful** -- not a mechanical checklist dump. It should read like a well-written brief that anyone on the team could pick up and understand what we're building and why.

Suggested structure (adapt as needed):
- Project name and one-line summary
- Background and motivation
- Goals and non-goals
- Target users
- Scope (in/out)
- Constraints
- Current state (with code evidence)
- Desired end state
- Success criteria
- Accepted assumptions
- Open risks

### Optional: Research Brief

If the idea has **significant unknowns** that need external validation before architecture can begin, also produce: `docs/<project>/research-brief.md`

This is a focused prompt/brief designed to be fed to a specialized deep-research agent (or done manually). Produce it when:
- The market viability is unvalidated (e.g., "will anyone pay for this?")
- There are major technical unknowns (e.g., "does an API for X even exist?")
- Competitive landscape is unclear (e.g., "who else does this?")
- Regulatory/legal questions exist (e.g., "is this allowed in jurisdiction Y?")

Do NOT produce a research brief when:
- The domain is well-understood by the user
- The project is internal tooling with no market question
- The user explicitly says they don't need research

When in doubt, ask the user:
> "There are some unknowns that could benefit from external research before we design the architecture. Would you like me to produce a research brief, or are you ready to move to design?"

## Language

- Mirror the user's language by default
- If user specifies `zh` or `en`, use that consistently
- Keep terminology consistent across the entire conversation

## Boundaries

- Do not output implementation steps or code
- Do not rely on README as sole evidence -- inspect actual code
- Do not bypass interviews by making assumptions on high-impact decisions
- Keep the conversation focused but not rigid

## References

- `references/interview-guide.md` -- question bank organized by area
- `references/output-guide.md` -- what the requirements and research-brief documents should look like
