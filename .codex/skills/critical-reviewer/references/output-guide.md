# Output Guide: review.md

## Purpose

The review document provides an honest, multi-perspective assessment of the project plan. It surfaces blind spots, validates strengths, and provides actionable recommendations.

## File Location

`docs/<project>/review.md`

## Quality Bar

- **Honest**: Problems are stated clearly, not softened into uselessness
- **Actionable**: Every finding has a recommended action
- **Balanced**: Strengths noted alongside weaknesses
- **Prioritized**: Findings ranked by severity -- reader knows what matters most
- **Specific**: "The risk engine lacks a max-drawdown hard stop" not "consider risk management"

## Suggested Structure

```markdown
# Review: <Project Name>

> Overall assessment in 2-3 sentences.

## Recommendation

**Proceed** / **Proceed with conditions** / **Loop back to <phase>**

<brief rationale>

## Strengths

What's working well in this plan:
- Strength 1
- Strength 2
- Strength 3

## Critical Findings

Issues that must be addressed before proceeding.

### F1: <Title>
- **Perspective**: <which expert viewpoint>
- **Issue**: <specific description>
- **Impact**: <why this matters>
- **Recommendation**: <what to do>

### F2: <Title>
...

## Important Findings

Issues that should be addressed but don't block initial progress.

### F3: <Title>
...

## Minor Findings

Nice to address, low impact if deferred.

### FN: <Title>
...

## Open Questions for User

Questions the review surfaced that need user input.
```

## Anti-Patterns

- Do NOT produce YAML risk registers or formal go/no-go decision artifacts
- Do NOT list 30+ minor findings -- focus on what matters (5-15 total)
- Do NOT be vague ("consider security" -- instead: "the API has no auth mechanism")
- Do NOT repeat the full plan -- reference specific sections
- Do NOT do external research unless asked -- review based on the docs and codebase
- Do NOT rubber-stamp -- if the plan is weak, say so constructively
