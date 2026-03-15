# Output Guide: architecture.md

## Purpose

The architecture document explains the system's structure from multiple perspectives. It answers: "How is this built? Why is it structured this way? What trade-offs were made?"

## File Location

`docs/<project>/architecture.md`

## Quality Bar

- **Multi-dimensional**: At least 3 different views of the system (component, data flow, deployment)
- **Visual**: Mermaid diagrams for key views (not optional decoration)
- **Decision-grounded**: Every major structural choice is explained with trade-offs
- **Traceable**: Components link back to goals in requirements
- **Honest**: Trade-offs and limitations are explicit

## Suggested Structure

```markdown
# Architecture: <Project Name>

> One-line summary of the architectural approach.

## Overview

Brief narrative: what kind of system is this, what's the high-level approach?

## Component View

### Diagram

(mermaid block diagram or flowchart showing components and their relationships)

### Component Descriptions

For each component:
- **Name**: What it does (2-3 sentences)
- **Responsibilities**: Bullet list
- **Depends on**: Other components it interacts with
- **Goal linkage**: Which requirements goal(s) this serves

## Data Flow

### Diagram

(mermaid sequence diagram or flowchart showing how data moves through key user flows)

### Flow Descriptions

Walk through 1-3 primary flows end-to-end. Explain what happens at each step.

## Deployment View

How and where components are deployed. Include a diagram if helpful.
- What runs where
- How components connect
- Key operational considerations

## Domain Model

### Glossary

Define the key domain terms used across the system. Any term that appears
in more than one document or crosses a component boundary should be here.

| Term | Definition |
|------|-----------|
| order_intent | A structured expression of a trading action the system recommends... |
| risk_snapshot | A point-in-time capture of risk metrics at the moment of... |

### Core Entity Schemas

For the 3-5 most important shared domain objects, define the minimal agreed shape.
This is NOT a full database schema -- it's the shared contract between components.

Example:

#### order_intent

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string (UUID) | yes | Unique identifier |
| symbol | string | yes | Stock ticker |
| direction | enum (buy/sell) | yes | Trade direction |
| ... | ... | ... | ... |

### State Machines

If any entity has a lifecycle with multiple states (e.g., order processing,
user onboarding), include a mermaid stateDiagram showing valid transitions.

Example:

    ```mermaid
    stateDiagram-v2
        [*] --> pending_confirm
        pending_confirm --> confirmed : user confirms
        pending_confirm --> expired : timeout
        pending_confirm --> user_skipped : user declines
        confirmed --> user_submitted : user executes manually
        user_submitted --> filled : full fill reported
        user_submitted --> partially_filled : partial fill reported
        confirmed --> rejected_cancelled : user cancels
    ```

### Interface Contracts

For each cross-component API or event, define the minimal agreed shape.
Two agents building different components should be able to build compatible
interfaces from this alone.

#### API: <endpoint name>
- **Method**: GET/POST/...
- **Path**: /api/v1/...
- **Key request fields**: (markdown table)
- **Key response fields**: (markdown table)
- **Error format**: (standard shape)

#### Event: <event name>
- **Direction**: producer -> consumer
- **Trigger**: when does this fire?
- **Key payload fields**: (markdown table)

## Key Decisions and Trade-offs

For each major architectural decision:

### Decision: <title>
- **Chosen**: <what we decided>
- **Alternatives considered**: <what else we looked at>
- **Rationale**: <why this choice>
- **Trade-off**: <what we're giving up>

## Integration Points

External services, APIs, data sources the system connects to.
For each: what it provides, how we connect, what happens when it's unavailable.

## Open Questions

Architectural questions deferred to later phases.
```

## Diagram Guidelines

- Use mermaid syntax (flowchart, sequence, or block-beta)
- Keep diagrams focused -- one concept per diagram
- Label edges with the interaction type (calls, emits, reads, writes)
- Don't try to show everything in one diagram -- multiple simple diagrams beat one complex one

## Domain Model Guidelines

The domain model section is **essential for multi-component or multi-agent builds**. Without it, agents building different components will produce incompatible interfaces.

- **Glossary**: Include every term that crosses a component boundary. If you use a term in one component's description that another component also references, define it.
- **Entity schemas**: Only the shared/cross-boundary entities. Internal-only objects are implementation detail and should not be here.
- **State machines**: Include for any entity with a lifecycle. Use mermaid `stateDiagram-v2`. Show all valid transitions and what triggers them.
- **Interface contracts**: Define the minimum agreed shape for each cross-component interaction. Not full OpenAPI -- just the key fields, types, and semantics.

For simple projects with a single component, the domain model can be light (just a glossary). For multi-component systems, it should be thorough enough that two agents can build compatible code without talking to each other.

## Anti-Patterns

- Do NOT produce full OpenAPI/AsyncAPI spec files -- keep contracts as readable markdown tables
- Do NOT produce JSON/YAML artifacts (component_map.json, etc.)
- Do NOT design internal/private data models or class hierarchies -- only shared domain objects
- Do NOT make the document a mechanical template fill -- write coherent prose
- Do NOT skip diagrams -- they're essential, not optional
- Do NOT skip the domain model for multi-component systems -- agents need shared vocabulary to build independently
