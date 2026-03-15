# Interview Guide: Architecture Decisions

Prompt bank for architectural interviews. Ask one per turn. Adapt to context.

## Component Boundaries

- Should X and Y be one component or two? (trade-off: simplicity vs separation of concerns)
- Where should this responsibility live? Component A or Component B?
- Is this component worth building custom, or should we use an existing tool/service?
- What's the minimum number of components that solves this problem?

## Communication Patterns

- How should these components communicate? (REST API / event bus / shared state / direct call)
- Does this interaction need to be synchronous or can it be async?
- How real-time does this need to be? (seconds / minutes / batch is fine)
- Should we use push (component sends) or pull (component polls)?

## Data Ownership and Flow

- Who is the source of truth for this data?
- Should data be replicated across components or accessed from a single source?
- What happens if the data source is unavailable?
- How fresh does this data need to be?

## Deployment and Operations

- Should this be a single deployable unit or separate services?
- Where should this run? (local machine / cloud / edge / hybrid)
- What's the expected load? Does it need to scale?
- How should we handle failures and restarts?

## Technology and Stack

- Are there strong preferences for language/framework?
- Should we match the existing codebase's stack or is a different stack justified?
- Any infrastructure we already have that we should leverage?

## Trade-off Questions

- Would you prefer simpler architecture with more manual steps, or more complex architecture with more automation?
- Is it more important to ship quickly or to build for long-term evolution?
- Should we optimize for developer experience or operational simplicity?
- How much coupling between components is acceptable for the sake of simplicity?

## Integration Points

- What external services does this need to connect to?
- Are there existing APIs we must conform to?
- What happens if an external dependency is down?
- Are there rate limits or costs we need to be aware of?

## Best Practices

1. Start with the highest-impact decision first
2. If the user is unsure, present the trade-offs clearly and make a recommendation
3. Don't interview on obvious choices -- just note them in the doc
4. After 3-5 key decisions, you likely have enough to draft the architecture
5. Use the interview to test your emerging design -- "based on what you've said, I'm thinking X -- does that sound right?"
