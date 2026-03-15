---
name: architecture-designer
description: Design system architecture through interactive exploration. Produces a multi-dimensional architecture document with diagrams. Use after requirements are aligned.
---

# Architecture Designer

## When to Use

- Requirements are aligned (requirements.md exists or equivalent understanding is established)
- The system needs component design, interaction patterns, and structural decisions
- Multiple architectural approaches exist and trade-offs need exploration

## Core Principle

**Show the system from multiple angles so humans and agents can build a shared mental model.**

Architecture is not a single diagram -- it's a collection of perspectives that together explain how the system works, why it's structured this way, and what trade-offs were made.

## Inputs

- `docs/<project>/requirements.md` (or equivalent aligned requirements from conversation)
- `docs/<project>/research-results.md` (optional -- if the research checkpoint produced validated findings)
- Existing codebase as evidence of current state

If `research-results.md` exists, read it before making architectural decisions. Research findings should inform technology choices, feasibility assessments, competitive positioning, and risk evaluation.

## Workflow

1. **Review requirements**: Read the aligned requirements; identify architectural decisions that need to be made
2. **Interview on key decisions**: Ask the user about major architectural choices (don't decide alone)
3. **Design multi-dimensional views**: Component view, data flow, interaction patterns, deployment view
4. **Document trade-offs**: For every major decision, note what was considered and why this was chosen
5. **Output**: Write `docs/<project>/architecture.md`

## Interview Protocol

Same rules as requirements-clarifier:
- **One question per turn**, 2-4 options, first marked `Recommended`
- Allow free-text
- Echo understanding before moving on
- Resolve conflicts immediately

### Architectural Decisions to Interview On

Not all projects need all of these. Use judgment on what matters:

- **Component boundaries**: What are the major building blocks? How do they separate?
- **Communication patterns**: How do components talk? (REST API, events, shared DB, message queue)
- **Data ownership**: Who owns what data? Where does it live?
- **Deployment model**: How is this deployed? (monolith, services, serverless, hybrid)
- **Technology choices**: Any strong preferences or constraints on stack?
- **Scalability vs simplicity**: Optimize for scale or keep it simple?
- **Build vs buy**: What should be custom-built vs using existing tools/services?

### Turn Template

```
Architecture Progress: <N> key decisions made | Current focus: <topic>

<reflection on what you've learned and how it shapes the design>

**Decision**: <what needs to be decided>

1. <Approach A> -- <brief trade-off> (Recommended)
2. <Approach B> -- <brief trade-off>
3. <Approach C> -- <brief trade-off>

You can also propose a different approach.
```

## Output

When key decisions are made, write: `docs/<project>/architecture.md`

### Required Perspectives (adapt to project)

The document should include multiple views of the system:

1. **Component View**: What are the major components? What does each do? How do they relate?
   - Include a mermaid component/block diagram
   - Explain the responsibility of each component in 2-3 sentences

2. **Interaction / Data Flow View**: How does data move through the system?
   - Include a mermaid sequence or flowchart diagram
   - Show the main user-facing flows end-to-end

3. **Deployment View**: How is this deployed and operated?
   - Where does each component run?
   - How do components connect in production?

4. **Domain Model** (essential for multi-component or multi-agent builds):
   - **Glossary**: Define key domain terms used across the system (e.g., what IS an "order_intent"?)
   - **Core entity schemas**: For the 3-5 most important domain objects, show fields as a markdown table (name, type, required?, description). Not full OpenAPI -- just enough for agents to build compatible interfaces.
   - **State machines**: If any entity has a lifecycle (e.g., order states), include a mermaid stateDiagram showing valid transitions.
   - **Interface contracts**: For each cross-component integration point, define the minimal agreed-upon shape (endpoint, key fields, event types). This is what two agents need to build independently without producing incompatible interfaces.

5. **Key Decisions and Trade-offs**: For each major architectural choice:
   - What was decided
   - What alternatives were considered
   - Why this choice was made
   - What risks or limitations it introduces

6. **Integration Points**: How does this system connect to external services, APIs, or existing components?

7. **Open Questions**: Architectural questions that remain open for later phases

### Quality Bar

- A developer should be able to read this and understand the system structure in 10 minutes
- Diagrams should be readable and meaningful (not decoration)
- Trade-offs should be honest -- acknowledge what was sacrificed
- Every component should trace back to a goal in the requirements

## Boundaries

- Do not produce full OpenAPI specs or AsyncAPI specs -- that's implementation detail
- Do produce **minimal interface contracts** (markdown tables with key fields) for cross-component boundaries -- agents need these to build independently
- Do not design internal implementation details (private methods, internal DTOs) -- only the shared domain model
- Do not generate JSON/YAML artifacts -- produce readable markdown with diagrams and tables
- Stay at the "boxes, arrows, and shared vocabulary" level, not the "class diagram" level
- Interview on decisions that matter; don't ask about trivial choices

## References

- `references/interview-guide.md` -- architectural decision prompts
- `references/output-guide.md` -- what the architecture document should look like
