# Interview Guide: Blueprint Decisions

Prompt bank for phasing and prioritization interviews. Ask one per turn.

## MVP and Phase 1 Scope

- What's the smallest version of this that would be useful?
- If you could only build one component first, which would it be?
- What's the riskiest assumption we should validate first?
- Is there a "walking skeleton" (thin end-to-end slice) that would prove the concept?

## Build Order and Dependencies

- Component A needs data from Component B -- should we build B first, or mock it?
- Should we build depth-first (one component fully) or breadth-first (all components partially)?
- Are there external dependencies that have long lead times we should start early?
- What can be built in parallel vs what must be sequential?

## Risk vs Speed

- Would you rather de-risk the hardest part first, or build momentum with quick wins?
- What's the biggest technical unknown? Should we spike on it before planning the rest?
- If this phase takes twice as long as expected, what would you cut?
- What's the cost of getting this wrong vs the cost of moving slowly?

## Integration Strategy

- Should components be built in isolation then integrated, or should we build end-to-end from day one?
- What's the testing strategy between components? (contract tests, integration tests, manual)
- How will we validate that components work together before everything is done?

## Automation vs Manual

- What processes should be automated from the start?
- What can start as manual and be automated later?
- Where is the automation effort worth it vs where is manual acceptable?

## Effort and Realism

- Does this phase feel like days, weeks, or months of work?
- What's the most likely thing to take longer than expected?
- Are there skills or knowledge gaps that could slow this down?
- What can we reuse from existing code vs what must be built from scratch?

## Best Practices

1. Start with "what's the first useful milestone?" -- everything else follows
2. Phases should be small enough to complete and validate (1-4 weeks each)
3. Each phase should deliver something testable, not just "infrastructure"
4. Don't over-plan later phases -- they'll change based on what you learn
5. Make dependencies explicit -- "Phase 2 cannot start until Phase 1 delivers X"
