---
name: system-surveyor
description: Produce a current-state snapshot of the codebase — what exists, how components work together, what's healthy, what's broken. Use before planning, when onboarding to a project, or when you need grounded understanding of what you're working with. Outputs a structured survey document consumable by humans and downstream skills (planning-orchestrator, requirements-clarifier, etc.).
---

# System Surveyor

## When to Use

- Before starting a planning effort (feeds into planning-orchestrator Phase 1)
- Onboarding to an unfamiliar codebase
- User asks "what do we have right now?" or "how does this work?"
- Need grounded evidence before proposing changes
- Periodic health check — has the system drifted from its documented design?

## Core Principle

**Report what IS, not what should be. Observe like a doctor doing a physical exam — measure, record, diagnose. Do not prescribe yet.**

The survey is evidence-based. Every claim must be traceable to a specific file, function, or configuration. Do not rely on README or docs alone — inspect the actual code.

## Position in the Pipeline

```
system-surveyor  →  planning-orchestrator  →  requirements  →  architecture  →  blueprint  →  review
     (WHAT IS)         (WHAT TO DO)
```

The survey document is designed to be consumed by:
- **Humans**: engineers, PMs, stakeholders who need to understand the system
- **planning-orchestrator**: as input context for Phase 1 (Understand)
- **requirements-clarifier**: as current-state evidence
- **architecture-designer**: as the baseline for proposed changes
- **New agent sessions**: as a cold-start context document

## Workflow

1. **Scan structure**: Map the directory tree, identify modules, locate entry points
2. **Trace data flows**: Follow the main user-facing paths end-to-end through the code
3. **Inventory components**: List every module with its responsibility, status, and connections
4. **Assess health**: For each component, note what works, what's broken, what's missing
5. **Map external dependencies**: APIs, databases, services, SDKs
6. **Interview** (optional): If ambiguities exist, ask the user 1-2 targeted questions
7. **Output**: Write `docs/<project>/survey.md` (or `docs/survey.md` for the whole system)

## What to Examine

### Layer 1: Structure

- Directory tree (top 2-3 levels)
- Entry points (main.py, app factory, CLI, scripts)
- Module boundaries — which directories are self-contained vs tightly coupled
- Dependency management (requirements.txt, package.json, etc.)

### Layer 2: Data Flows

Trace the **3-5 most important user-facing paths** end-to-end. For each:
- Trigger (HTTP route, WebSocket event, CLI command, scheduled job)
- Components touched in order
- Data transformations at each step
- Terminal output (response, side effect, stored artifact)

### Layer 3: Component Inventory

For each distinct module/package, record:

| Field | What to capture |
|-------|----------------|
| **Name** | Module/package name and path |
| **Responsibility** | What it does (1-2 sentences, grounded in code) |
| **Status** | `active` / `deprecated` / `stub` / `dead code` |
| **Key interfaces** | Public functions/classes other modules call |
| **Dependencies** | What it imports from (internal modules + external packages) |
| **Dependents** | What imports from it |
| **Database/storage** | Tables, files, or external services it reads/writes |
| **Health notes** | Known issues, TODOs in code, missing error handling, test coverage |

### Layer 4: External Dependencies

- APIs called (LLM providers, STT, TTS, search, etc.)
- Databases (type, location, schema summary)
- Infrastructure (deployment target, scheduler, background workers)
- SDK/library versions that matter

### Layer 5: Configuration & Environment

- Environment variables and what they control
- Config loading mechanism
- Secrets management approach
- Dev vs prod differences

### Layer 6: Health Assessment

For each major component, assign a health status:

| Status | Meaning |
|--------|---------|
| Healthy | Working correctly, well-structured, tested |
| Functional | Works but has known issues, tech debt, or missing tests |
| Fragile | Works sometimes, unclear failure modes, needs attention |
| Broken | Known to not work correctly |
| Dead | Not called, not needed, should be removed |
| Stub | Interface exists, implementation is placeholder |

## Output

Write: `docs/<project>/survey.md` (or `docs/survey.md` for the whole system)

### Document Structure

```markdown
# System Survey: <Project Name>

> One-line description of what this system does.
> Survey date: YYYY-MM-DD

## Quick Facts

| Metric | Value |
|--------|-------|
| Language / Framework | ... |
| Entry point | ... |
| Total modules | ... |
| Database(s) | ... |
| External APIs | ... |
| Overall health | Healthy / Functional / Fragile |

## Architecture Overview

Brief narrative (3-5 paragraphs) explaining how the system works at a high level.
Include a mermaid diagram if the system has 3+ interacting components.

## Data Flows

### Flow 1: <name> (e.g., "User sends chat message")
Step-by-step trace through the code. File paths and function names.

### Flow 2: <name>
...

## Component Inventory

### <module_name>

| Field | Value |
|-------|-------|
| Path | `src/...` |
| Responsibility | ... |
| Status | active / deprecated / stub / dead |
| Key interfaces | `function_a()`, `ClassB` |
| Health | Healthy / Functional / Fragile / Broken |
| Notes | ... |

(Repeat for each module)

## External Dependencies

| Dependency | Type | Used by | Config |
|------------|------|---------|--------|
| OpenAI API | LLM | agent, tts | `LLM_API_KEY` |
| Deepgram | STT | voice | `DEEPGRAM_API_KEY` |
| ... | ... | ... | ... |

## Database Schema Summary

For each database, list tables with column count and purpose.
Do NOT dump full DDL — summarize.

## Health Summary

| Component | Status | Key Issues |
|-----------|--------|------------|
| ... | Healthy / Functional / Fragile / Broken | ... |

## Gaps and Dead Code

- List modules/files that are dead or deprecated
- List documented features that aren't implemented
- List TODO/FIXME/HACK comments with file locations

## Observations

Objective observations (not recommendations) that downstream skills should know:
- Architectural patterns in use (and violations of those patterns)
- Coupling hotspots (modules with too many dependents or dependencies)
- Missing infrastructure (no tests, no CI, no monitoring, etc.)
- Inconsistencies between docs and code
```

### Quality Bar

- Every claim is backed by a file path or code reference
- No speculation — if uncertain, say "unclear, needs investigation"
- Health assessments are honest, not optimistic
- A new developer could read this and understand the system in 15 minutes
- The planning-orchestrator could read this and skip half of Phase 1 discovery

## Boundaries

- Do NOT recommend changes — that's the job of downstream skills
- Do NOT produce code, scripts, or migration plans
- Do NOT rely on docs/README alone — verify against actual code
- Do NOT list every single file — focus on modules and boundaries
- Do NOT include credentials or secret values
- Keep the survey under 1000 lines — use progressive disclosure for deep dives
- If a deep dive is needed for one component, reference a separate file: `survey-<component>.md`

## Integration with Other Skills

| Downstream skill | What it uses from the survey |
|------------------|------------------------------|
| **planning-orchestrator** | Quick Facts + Health Summary → calibrate scope of planning effort |
| **requirements-clarifier** | Current state evidence → ground requirements in reality |
| **architecture-designer** | Component Inventory + Data Flows → identify what to keep, change, or replace |
| **blueprint-writer** | Health Summary + Gaps → prioritize what to fix first |
| **critical-reviewer** | Dead Code + Gaps → surface risks the plan missed |

## Tips for Speed

- Use `find` / `glob` to map the directory tree first
- Use `grep` to count imports and find coupling hotspots
- Read `__init__.py` files to understand public APIs
- Read entry points (main.py, app factory) to understand the startup graph
- Check database schema by reading DDL in code or migrations
- Skim test directories to gauge coverage
