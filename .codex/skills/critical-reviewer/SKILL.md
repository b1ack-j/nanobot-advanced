---
name: critical-reviewer
description: Challenge the project plan from multiple expert perspectives. Produces a critical review with findings and recommendations. Use after blueprint is written.
---

# Critical Reviewer

## When to Use

- Requirements, architecture, and blueprint are established
- Need adversarial/constructive challenge before committing to implementation
- Want to surface blind spots, risks, and weak assumptions

## Core Principle

**Be the team of experts the user doesn't have access to. Challenge the plan honestly, constructively, and from multiple angles.**

This is not a rubber stamp. If the plan has problems, say so clearly. If it's solid, say that too. The goal is to make the plan better before any code is written.

## Inputs

- `docs/<project>/requirements.md`
- `docs/<project>/architecture.md`
- `docs/<project>/blueprint.md`
- Existing codebase context

## Workflow

1. **Read all prior docs**: Understand the full picture -- requirements, architecture, blueprint
2. **Interview on review scope**: Ask the user what they're most worried about / what to focus review on
3. **Multi-perspective review**: Analyze from several expert viewpoints
4. **Synthesize findings**: Rank by severity, provide actionable recommendations
5. **Output**: Write `docs/<project>/review.md`

## Interview Protocol

The reviewer should also interview, but more lightly -- 1-3 questions to calibrate:

- **Risk appetite**: How conservative should the review be?
- **Focus areas**: What are you most concerned about?
- **Decision authority**: If the review finds problems, what happens? (loop back / adjust / proceed with caution)

### Turn Template

```
Review setup | Focus: <what the user cares most about>

**Question**: <what to calibrate before reviewing>

1. <Option A> (Recommended)
2. <Option B>
3. <Option C>

You can also specify what you want me to focus on.
```

## Review Perspectives

Analyze the plan from at least 4 of these perspectives (choose based on project type):

### 1. Domain Expert
- Does this plan make sense for the domain?
- Are there domain-specific risks or patterns being ignored?
- Would someone experienced in this field do it differently?

### 2. System Architect
- Is the architecture appropriate for the requirements?
- Are there unnecessary complexities or missing components?
- Will this scale / evolve as needed?
- Are the component boundaries right?

### 3. Risk Analyst
- What are the biggest risks to success?
- What happens when things go wrong? (failure modes)
- Are there single points of failure?
- What assumptions are most likely to be wrong?

### 4. Economics / Feasibility Analyst
- Is this cost-effective? (build cost, run cost, opportunity cost)
- Does the ROI make sense?
- Are there cheaper / faster alternatives that achieve 80% of the value?
- Is the timeline realistic?

### 5. Operations / Reliability
- How will this be operated day-to-day?
- What needs monitoring? What breaks silently?
- How hard is it to debug when something goes wrong?
- What's the maintenance burden?

### 6. User / Stakeholder Advocate
- Does this actually solve the user's problem?
- Is the phasing aligned with what delivers value earliest?
- Are there usability or adoption risks?

## Output

Write: `docs/<project>/review.md`

### What the Review Should Cover

1. **Review Summary**: Overall assessment in 2-3 sentences. Is this plan ready? Conditionally ready? Needs rework?

2. **Findings by Severity**:
   - **Critical**: Must be addressed before proceeding (blocks success)
   - **Important**: Should be addressed, but won't block initial progress
   - **Minor**: Nice to fix, low impact if deferred

3. **Per Finding**:
   - What the issue is (clear, specific)
   - Which perspective surfaced it
   - Why it matters
   - Recommended action

4. **Strengths**: What's good about this plan (not just problems)

5. **Recommendation**: Proceed / Proceed with conditions / Loop back to <phase>

### Quality Bar

- Findings are specific and actionable (not vague "consider security")
- Severity rankings are honest (don't inflate or deflate)
- Each finding has a recommended action
- Strengths are noted too -- balanced review
- The user knows exactly what to do after reading this

## Boundaries

- Do NOT do external web research unless the user asks for it
- Do NOT produce risk_register.yaml, go_no_go.md, or similar mechanical artifacts
- Do NOT be a rubber stamp -- if there are problems, say so
- Do NOT invent problems for the sake of thoroughness -- be genuine
- Do NOT repeat the full requirements/architecture/blueprint -- reference them
- Keep findings to the most impactful items (aim for 5-15 findings, not 50)

## References

- `references/interview-guide.md` -- review calibration prompts
- `references/output-guide.md` -- what the review document should look like
