# Output Guide: requirements.md

## Purpose

The requirements document is the single source of truth for what we're building and why. It should be readable by anyone -- engineers, stakeholders, future-you.

## File Location

`docs/<project>/requirements.md`

Where `<project>` is a descriptive project slug (e.g., `trading-agent`, `auth-system`).

## Quality Bar

- **Readable**: A newcomer can understand the project in 5 minutes
- **Complete**: All key decisions are captured, not hidden in chat history
- **Grounded**: Current-state claims reference actual code/config
- **Actionable**: An architect or planning agent could start designing from this alone
- **Honest**: Assumptions and risks are explicit, not buried

## Suggested Structure

```markdown
# <Project Name>

> One-line summary of what this project is.

## Background and Motivation

Why are we doing this? What triggered it? What context matters?

## Goals

What concrete outcomes do we want? Be specific.

## Non-Goals

What are we explicitly NOT doing in this phase?

## Target Users

Who will use this? What do they care about?

## Scope

### In Scope
- Item 1
- Item 2

### Out of Scope
- Deferred item 1
- Deferred item 2

## Constraints

Technical, budget, time, compliance, or operational constraints.

## Current State

What exists today in the codebase that's relevant? Reference specific files/modules.
What's missing? What are the gaps?

## Desired End State

What does the system look like when this phase is done?

## Success Criteria

Concrete, testable criteria. Examples:
- "Strategy backtests can run end-to-end on historical data"
- "User receives signal notifications via Telegram within 30 seconds"

## Assumptions

Things we're treating as true but haven't fully verified:
- Assumption 1
- Assumption 2

## Open Risks

Known unknowns that could affect the plan:
- Risk 1
- Risk 2
```

## Anti-Patterns

- Do NOT produce a mechanical checklist with field labels like "Goal: locked"
- Do NOT include status metadata, envelope keys, or machine-readable wrappers
- Do NOT copy-paste interview Q&A verbatim -- synthesize into coherent prose
- Do NOT include implementation details (that's for architecture/blueprint phases)

## Language

Match the language established during the interview. If bilingual conversation, pick the dominant language for the document and note the other in key terms where helpful.

---

# Output Guide: research-brief.md (Optional)

## Purpose

The research brief is a focused prompt designed to be fed to a specialized deep-research agent (e.g., GPT deep research, Perplexity, dedicated research tools). It captures the key unknowns that need external validation before architecture design can begin.

## File Location

`docs/<project>/research-brief.md`

## When to Produce

Only when the requirements interview reveals significant unknowns:
- Market viability is unvalidated
- Major technical unknowns exist
- Competitive landscape is unclear
- Regulatory/legal questions need answering

## Quality Bar

- **Focused**: 5-15 specific research questions, not a vague "research everything"
- **Actionable**: Each question can be independently researched
- **Prioritized**: Most critical unknowns first
- **Context-rich**: Enough background for a research agent to understand what matters

## Suggested Structure

```markdown
# Research Brief: <Project Name>

> Context for research agent: <1-2 sentence project summary and what we need to validate>

## Research Priority

Rank: which unknowns would most change our architecture or kill the idea entirely?

## Market & Feasibility Questions

- Question 1 (e.g., "What is the market size for X in region Y?")
- Question 2 (e.g., "Who are the top 5 competitors and what are their revenue models?")
- Question 3 (e.g., "What is the typical customer acquisition cost in this space?")

## Technical Feasibility Questions

- Question 4 (e.g., "Does a public API for X exist? What are its limitations?")
- Question 5 (e.g., "What are the typical latency/throughput constraints for Y?")

## Regulatory / Legal Questions

- Question 6 (e.g., "What regulations apply to X in jurisdiction Y?")
- Question 7 (e.g., "Are there content/compliance restrictions for Z?")

## Existing Solutions & Prior Art

- Question 8 (e.g., "What open-source tools exist for X?")
- Question 9 (e.g., "What approaches have failed and why?")

## Output Expectations

What format should the research results be in?
(e.g., "Put findings in docs/<project>/research-results.md, organized by question, with sources linked")
```

## Anti-Patterns

- Do NOT ask vague questions ("research the industry")
- Do NOT ask implementation questions ("what framework should we use") -- that's architecture
- Do NOT produce a research brief for well-understood projects
- Do NOT include more than 15 questions -- focus on what matters most
