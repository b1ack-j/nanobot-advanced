---
name: blueprint-writer
description: Synthesize requirements and architecture into an actionable implementation blueprint. Produces a phased build plan through interactive prioritization. Use after architecture is designed.
---

# Blueprint Writer

## When to Use

- Requirements and architecture are established
- Need to figure out what to build first, how to phase work, and what the key interfaces are
- Team (or solo developer) needs an actionable plan, not just a design

## Core Principle

**Turn understanding into action. The blueprint answers: "What do we build, in what order, and what are the key milestones?"**

This is not a task tracker or project management artifact. It's a thinking document that helps humans and agents understand the build sequence and make smart trade-offs about phasing.

## Inputs

- `docs/<project>/requirements.md`
- `docs/<project>/architecture.md`
- Existing codebase context

## Workflow

1. **Review prior docs**: Read requirements and architecture; identify what needs to be built
2. **Interview on priorities**: Ask the user about phasing preferences, MVP scope, and build order
3. **Design phases**: Break the work into logical phases with clear milestones
4. **Identify key interfaces**: What are the critical integration points between phases?
5. **Output**: Write `docs/<project>/blueprint.md`

## Interview Protocol

Same rules as other skills:
- **One question per turn**, 2-4 options, first marked `Recommended`
- Allow free-text
- Echo understanding before moving on

### Key Questions to Interview On

- **MVP scope**: What's the smallest useful thing we can build first?
- **Build order**: Which component should we start with? What depends on what?
- **Risk vs speed**: Build the riskiest thing first (de-risk) or the easiest thing first (momentum)?
- **Integration strategy**: Build components in isolation then integrate, or build end-to-end incrementally?
- **Automation vs manual**: What should be automated from the start vs manually handled initially?

### Turn Template

```
Blueprint Progress: <N> phases sketched | Current focus: <topic>

<reflection on emerging build plan>

**Question**: <what needs to be decided about build order / phasing>

1. <Approach A> (Recommended)
2. <Approach B>
3. <Approach C>

You can also suggest a different approach.
```

## Output

When phasing decisions are made, write: `docs/<project>/blueprint.md`

### What the Blueprint Should Cover

1. **Phase Overview**: A table or list showing each phase, its goal, and key deliverable
   - Include a mermaid diagram showing phase dependencies if helpful

2. **Per-Phase Detail**: For each phase:
   - What to build
   - Why this order (dependencies, risk reduction, value delivery)
   - Key milestone / "done" criteria
   - What it unlocks for the next phase

3. **Key Interfaces**: Critical integration points between components or phases
   - What contracts need to be defined early
   - What can be deferred

4. **Build vs Buy / Reuse Decisions**: What existing tools, libraries, or services to use
   - For each: why this choice, alternatives considered

5. **Open Decisions**: Things that can be decided later without blocking early phases

6. **Estimated Effort**: Rough t-shirt sizing per phase (S/M/L/XL), not detailed hour estimates

### Quality Bar

- A developer should be able to read this and know where to start
- Phases should have clear boundaries and "done" definitions
- Dependencies between phases should be explicit
- The plan should be realistic -- acknowledge complexity honestly
- It should be clear what the first week of work looks like

## Boundaries

- Do not produce YAML/JSON task files or project management artifacts
- Do not assign owners or estimate hours -- keep it at the thinking level
- Do not repeat architecture details -- reference the architecture doc
- Do not make phasing decisions without interviewing the user
- Stay focused on "what and when" not "how to code it"

## References

- `references/interview-guide.md` -- phasing and prioritization prompts
- `references/output-guide.md` -- what the blueprint document should look like
