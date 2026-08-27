---
name: refine-prompt-from-codebase
description: "Refine a rough implementation prompt using verified codebase evidence and interactive grilling. Investigates repository code, exposes hidden assumptions, and interviews the user to resolve ambiguities before producing an implementation-ready prompt."
argument-hint: "Provide the rough prompt or feature request to refine."
disable-model-invocation: true
---

# Refine Prompt From Codebase

Transform a rough implementation prompt into an accurate, implementation-ready prompt grounded in the codebase and stress-tested through structured grilling.

Treat the user's prompt as **intent and initial assumptions**, not as technical truth.

## Workflow

### 1. Understand Intent

Extract from the user's input:

* requested outcome and core user goal
* expected behavior and capabilities
* doctypes, modules, files, APIs, hooks, jobs, UI elements, or integrations mentioned
* stated constraints and assumptions

Do not rewrite the prompt yet.

### 2. Verify Against Codebase

Search the repository for every technical claim and entity referenced in the prompt.

Verify and trace:

* existing files, classes, modules, and functions
* data models, fields, and relationships
* API endpoints and request/response handling
* lifecycle hooks, events, background jobs, and queue triggers
* cross-module dependencies and end-to-end data/control flows
* existing error handling, validation, and unit tests

Trace flows end-to-end rather than verifying names in isolation.

### 3. Classify Findings

Classify each technical claim into one of four buckets:

* **Verified** — directly supported by codebase evidence
* **Inferred** — strongly supported by code patterns but not explicitly documented
* **Unknown** — cannot be determined from the codebase alone
* **Contradicted** — code shows behavior different from the user's prompt assumptions

Never present unknown or contradicted information as fact.

### 4. Interactive Grilling (Grill-Me Phase)

Before drafting the final prompt, conduct a rigorous, structured interview with the user to resolve all **Unknowns**, **Contradictions**, open decision branches, and edge cases uncovered in Steps 2 and 3.

#### Grilling Rules:
* **Explore code first:** Only ask the user questions that the codebase *cannot* answer on its own.
* **Ask one question at a time:** Do not overwhelm the user with multiple questions in a single message. (Exception: Interdependent questions may be presented as a numbered sequence).
* **Process each response:** After the user answers, summarize what was learned, flag new contradictions/assumptions, and state your recommended position.
* **Cover critical dimensions:**
  1. **Goal & Scope** — Clarify edge cases or boundary conditions not specified in code.
  2. **Contradictions** — Present contradicted assumptions found in code and ask how to proceed.
  3. **Unknowns & Trade-offs** — Present options for unestablished details and resolve decision tree branches.
  4. **Constraints & Failure Handling** — Define behavior during edge cases, failures, or rollback scenarios.
* **Probe, don't implement:** Keep focus entirely on clarifying the specification.

Continue grilling until all decision branches, unknown technical requirements, and contradictions are fully resolved.

### 5. Synthesize & Build the Refined Prompt

Combine verified codebase facts with user decisions from the grilling phase to draft a concise, actionable, implementation-ready prompt.

Use this structure when applicable:

```markdown
## Context
Verified current codebase behavior and architecture.

## Current Flow
Relevant end-to-end data and control flow verified in code.

## Requested Change
Exact, unambiguous behavior to implement (including decisions resolved during grilling).

## Constraints & Edge Cases
Existing behavior that must remain unchanged, plus error handling/edge case rules.

## Implementation References
Exact files, functions, models, hooks, APIs, and test files to touch or reference.

## Acceptance Criteria
Specific, testable conditions defining successful implementation.
```

Adapt the structure when a section is unnecessary.

### 6. Validate the Prompt

Before returning the final output, verify that:

* Every technical claim is supported by codebase evidence or explicit user confirmation.
* All contradictions and unknowns identified during research were resolved via grilling.
* Current behavior is clearly separated from requested change.
* Implementation references point to real files and symbols.
* Edge cases, error handling, and failure modes are explicitly specified.
* Acceptance criteria are concrete and testable.
* No invented APIs, fields, functions, or business rules exist.

## Output

Return:

### Refined Prompt

The final, implementation-ready prompt formatted in standard markdown.

### Corrections & Resolved Contradictions

Key differences between original assumptions and actual codebase behavior, with notes on how they were resolved.

### Grill Summary & Decisions Made

Brief summary of open questions, trade-offs, and edge cases resolved during the grilling phase.

### Unknowns

Any remaining unresolved details (if any). If all were resolved, state:

`No material unknowns found.`

## Decision Rules

| Situation | Action |
|---|---|
| Code answers the question | Do not ask user; verify in codebase directly |
| Code contradicts user assumption | Flag contradiction to user during grilling phase with codebase evidence |
| Ambiguous requirement or decision point | Grill user with focused, 1-at-a-time questions to resolve decision tree |
| User requests immediate prompt drafting | Complete codebase verification, ask essential grilling questions concisely |

## Rules

* **Codebase evidence overrides memory-based assumptions.**
* **Grill relentlessly until ambiguities and edge cases are eliminated.**
* Do not invent missing technical details without verifying or asking.
* Do not redesign the system unless explicitly requested.
* Prefer exact file paths, class names, and function signatures from the codebase.
* Prefer concise, actionable instructions over explanations.
* Investigate first, grill second, rewrite third.

