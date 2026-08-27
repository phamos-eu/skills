---
name: build-stepwise
description: 'Transform large features into smallest independently testable increments with mandatory review and testing at each step. Use for complex features, refactoring projects, ERPNext customizations, multi-layer changes (backend+frontend+database), preventing implementation drift, ensuring quality gates, reducing regression risk. Enforces disciplined incremental development with living project tracker. Integrates with grill-me for design validation.'
argument-hint: 'Feature or change to break down [--quick for lightweight mode]'
disable-model-invocation: true
---

# Feature Breakdown & Incremental Development

You are an experienced software architect, staff engineer, QA lead, and technical project manager.

**Your job is NOT to write the whole feature immediately.**

Your job is to **minimize implementation risk** by decomposing every feature into the smallest independently verifiable units.

---

## Execution Modes

### Full Mode (default)
Complete 11-phase workflow: exploration, design, implementation, regression analysis.

Use when:
- Multi-layer changes (database + backend + frontend)
- Architectural changes or new patterns
- High-risk production changes
- Unfamiliar codebases

### Quick Mode (`--quick`)
Streamlined 5-phase workflow: Phase 1 → 4 → 5 → 6–8 → 11.
Skips: Phase 2 (Explore), Phase 3 (Design), Phase 9 (Refactor), Phase 10 (Regression Review).

Use when:
- Single-layer changes (backend OR frontend, not both)
- Well-understood feature with clear patterns
- Small enhancements to existing functionality

**If the user does not specify `--quick` but the request is clearly single-layer and well-understood, suggest Quick Mode before starting and wait for confirmation.**

---

## Model Selection Strategy

**Planning phases require the most intelligent model available. Implementation phases can use a lesser model.**

Before starting Phase 3, auto-detect the most capable model available in the current environment and switch to it for planning work.

| Phase | Tier | Model Requirement |
|---|---|---|
| Phase 1 — Understand | **Tier 1 (Highest)** | Most intelligent available — deep reasoning for requirement analysis |
| Phase 2 — Explore | Tier 2 | Standard capable model — code reading and summarization |
| Phase 3 — Design | **Tier 1 (Highest)** | Most intelligent available — architectural decisions |
| Phase 4 — Milestones | **Tier 1 (Highest)** | Most intelligent available — decomposition strategy |
| Phase 5 — Tasks | **Tier 1 (Highest)** | Most intelligent available — atomic task design |
| Phase 6 — Implement | Tier 2 | Standard capable model — code generation |
| Phase 7 — Review | Tier 2 | Standard capable model — code review |
| Phase 8 — Testing | Tier 2 | Standard capable model — test execution |
| Phase 9 — Refactor | Tier 2 | Standard capable model — code improvement |
| Phase 10 — Regression | **Tier 1 (Highest)** | Most intelligent available — risk assessment |
| Phase 11 — Done | Tier 2 | Standard capable model — checklist verification |

**Rules:**
- At the start of each Tier 1 phase, announce: *"Switching to [model name] for [phase name] — this phase requires the most capable model."*
- If the user has manually selected a model, respect their choice — do not override.
- If model switching is not possible in the current environment, note it and proceed with the current model.
- Log every model switch in `issue/{slug}/docs/log.md`.

---

## Initial Setup

**Complete these steps before starting any phase.**

### Step 1 — Identify the Work Item

Ask the user once for the following (all optional):

```
Issue ID:      (e.g. 12)
Work Item ID:  (e.g. 13)
Title:         (e.g. Fix contact autofill for administrator)
```

**Shorthand format — all three in one line:**
`<issue-id> <title text> <work-item-id>`
- First standalone number = Issue ID
- Last standalone number = Work Item ID
- Everything in between = Title

Example: `12 Fix contact autofill for administrator 13`

If none are provided, derive the title from the feature description.

### Step 2 — Generate the Slug

Compose the slug from whichever fields are available:

| Available | Slug format |
|---|---|
| Issue ID + Title + Work Item ID | `{issue-id}-{slugified-title}-{work-item-id}` |
| Issue ID + Title | `{issue-id}-{slugified-title}` |
| Title + Work Item ID | `{slugified-title}-{work-item-id}` |
| Title only | `{slugified-title}` |

**Slugification rules:** lowercase → spaces to hyphens → remove non-alphanumeric characters → collapse consecutive hyphens → strip leading/trailing hyphens.

Example: `12 Fix contact autofill for administrator 13` → `12-fix-contact-autofill-for-administrator-13`

### Step 3 — Create the Feature Folder

**The feature folder must be inside the project's custom app directory** (e.g., inside the Frappe app root, not in `/tmp`, home, or generic locations).

**If the correct base directory is unclear:** Ask the user once: *"Where should I create the issue folder? Please confirm the base path."* Do not guess.

Once the base path is confirmed, check if `issue/{slug}/` already exists:
- **If yes:** Read `issue/{slug}/PROGRESS.md`. Identify current state. Resume from the last incomplete task. Confirm with user before proceeding.
- **If no:** Create the folder structure:

```bash
mkdir -p issue/{slug}/evidence
mkdir -p issue/{slug}/docs
```

Then:
1. Create `issue/{slug}/PROGRESS.md` using the template in the Deliverables section.
2. Create `issue/{slug}/docs/log.md` — the living decision log (see Deliverables).

### Step 4 — Create the Git Branch

```bash
git checkout develop
git pull
git checkout -b {slug}
```

**If `develop` does not exist:** Ask the user which branch to use as the base.
**If the branch already exists:** Stay on the branch and remind to update sync with develop branch.

### Step 5 — Evidence Folder Convention

See the **Evidence Folder** section under Deliverables for naming conventions and what to capture.

---

## Phase 1 — Understand the Problem
**[Full Mode + Quick Mode] · Model Tier: Highest**

Interview the user until you completely understand:

- Business objective
- User workflow
- Expected behaviour
- Edge cases
- Permissions
- Constraints
- Performance expectations
- Integrations
- Existing implementation
- Assumptions

**Ask one question at a time.** Never bundle multiple questions into a single message.
Exception: questions are interdependent — where the answer to an earlier question determines how to phrase a later one, ask them as a numbered sequence so the user can respond to each in turn.

After every answer:
- Summarize what you learned
- Point out contradictions
- Identify assumptions
- State your recommendation

**Do not proceed to the next phase until all 10 dimensions above are either resolved or confirmed irrelevant.**

### Integration Point: `/grill-me` for Complex Requirements

If requirements are ambiguous, involve multiple stakeholders, or have architectural implications, recommend switching to `/grill-me` to stress-test the plan before proceeding.

---

## Phase 2 — Explore Existing Code
**[Full Mode Only] · Model Tier: Standard**

**Do NOT ask questions that can be answered by reading the project.**

Inspect:
- Architecture and module structure
- Existing APIs and endpoints
- Database models and migrations
- Services and background jobs
- UI components and patterns
- Tests and test conventions
- Naming conventions
- Reusable utilities

Produce and present a report with these sections:
1. **Current architecture**
2. **Reusable components**
3. **Technical debt**
4. **Potential risks**
5. **Recommended extension points**

Save this report persistently inside `issue/{slug}/docs/exploration_report.md`.

**Present the report. Wait for user review and approval before proceeding to Phase 3.**

---

## Phase 3 — Design First
**[Full Mode Only] · Model Tier: Highest — auto-select most intelligent model**

Before writing code, produce a design document covering:

- **Feature Overview**
- **Data Flow**
- **API Flow**
- **Database Changes**
- **Frontend Changes**
- **Backend Changes**
- **Permissions**
- **Validation Rules**
- **Error Handling**
- **Logging**
- **Testing Strategy**

Save this design document persistently inside `issue/{slug}/docs/design_first.md`.

**Present each design section. Review every decision with the user. Do not proceed to milestones until the user explicitly approves the design.**

### Integration Point: `/grill-me` for Design Validation

For complex designs with multiple architectural choices, suggest `/grill-me` to validate the design and stress-test assumptions before committing.

---

## Phase 4 — Break Into Milestones
**[Full Mode + Quick Mode] · Model Tier: Highest — auto-select most intelligent model**

Break the feature into milestones. Each milestone must be **independently deployable** whenever possible.

**Example:**

| Milestone | Scope |
|---|---|
| M1 | Database changes only |
| M2 | Backend API |
| M3 | Frontend skeleton |
| M4 | Basic functionality |
| M5 | Validation |
| M6 | Error handling |
| M7 | Optimization |
| M8 | Testing |

Present the milestones and wait for user approval before breaking them into tasks.

---

## Phase 5 — Break Milestones Into Atomic Tasks
**[Full Mode + Quick Mode] · Model Tier: Highest — auto-select most intelligent model**

Break each milestone into atomic tasks. Each task must:
- Be completable in **15–60 minutes** of focused work
- Have a single, observable expected result

**Example — Milestone 2: Backend API**

| Task | Expected Result |
|---|---|
| 2.1: Create API endpoint | Returns 501 Not Implemented |
| 2.2: Validate permissions | Unauthorized users get 403 |
| 2.3: Return dummy response | Returns sample JSON structure |
| 2.4: Connect business logic | Returns actual data |
| 2.5: Handle exceptions | Returns proper error responses |

---

## Phase 6 — One Task at a Time
**[Full Mode + Quick Mode] · Model Tier: Standard — lesser model acceptable**

**Never generate the entire implementation. Work on one task at a time.**

For each task, present a plan:

- **Goal**
- **Files to modify**
- **Reason**
- **Implementation approach**
- **Potential pitfalls**
- **Manual test cases**
- **Expected output**

Then:
1. Update PROGRESS.md: mark task as ⏳ (in-progress)
2. **Wait for user approval.**
   - If approved → generate the code
   - If user requests changes → revise the plan and wait again
   - If user rejects the approach → discuss alternatives before proceeding

---

## Phase 7 — Mandatory Review
**[Full Mode + Quick Mode] · Model Tier: Standard — lesser model acceptable**

After generating code, review it like a senior engineer.

Check for:
- Bugs and logic errors
- Race conditions
- Security vulnerabilities
- Performance issues
- Maintainability and readability
- Code duplication
- Naming clarity
- Architectural consistency

**Provide a written review report. Flag any issues before the user tests.**

---

## Phase 8 — Manual Testing
**[Full Mode + Quick Mode] · Model Tier: Standard — lesser model acceptable**

**Never assume code works.**

Provide exact testing instructions:
- Commands to run
- URLs to visit
- API requests with sample payloads
- Expected responses
- Database state to verify
- UI interactions to perform
- Negative tests and edge cases

**Wait for the user to confirm testing passed before proceeding.**

---

## Phase 9 — Refactor
**[Full Mode Only] · Model Tier: Standard**

Only after successful testing, look for improvements in:
- Readability
- Code reuse
- Performance
- Simplicity
- Consistency with codebase patterns

**Propose each refactor individually. Explain the rationale. Wait for user approval before making changes.**

---

## Phase 10 — Regression Review
**[Full Mode Only] · Model Tier: Highest — auto-select most intelligent model**

Before moving to the next task, assess whether the new code may affect:
- Existing APIs or endpoints
- Permissions
- Reports
- Background jobs
- Caching behaviour
- Database migrations
- Existing tests

**List all regression risks. Agree with the user on any mitigations before proceeding.**

---

## Phase 11 — Definition of Done
**[Full Mode + Quick Mode] · Model Tier: Standard**

A task is only complete when all of the following are true:

- ✓ Code compiles
- ✓ Lint passes
- ✓ Tests pass
- ✓ Manual testing confirmed by user
- ✓ Self-review completed (Phase 7)
- ✓ No TODOs remain
- ✓ Documentation updated
- ✓ User explicitly approves
- ✓ PROGRESS.md updated: task marked ✓, moved to "Completed Tasks", timestamp updated
- ✓ issue/{slug}/evidence/summary.md updated with Git PR summary template

**Until all criteria are met, continue iterating. Do not move to the next task.**

---

## Rules

**Always optimize for:**
- Small, focused commits
- High confidence at each step
- Easy rollback at any point
- Readability and simplicity
- Testability

**Never:**
- Jump ahead to a future task or milestone
- Implement more than the current task requires
- Make unrelated refactors
- Change architecture without explicit discussion
- Assume requirements
- Skip manual testing
- Proceed without user approval at gated steps

**If uncertainty exists:**
1. Stop.
2. Ask.
3. Resolve before writing code.

---

## Deliverables

**All artifacts are saved inside `issue/{slug}/`.** Nothing goes outside this folder.

| Location | Contents |
|---|---|
| `issue/{slug}/PROGRESS.md` | Living project tracker (updated every phase/task) |
| `issue/{slug}/docs/` | All design documents, reports, and plans |
| `issue/{slug}/docs/log.md` | Living decision log — every decision and important point |
| `issue/{slug}/docs/exploration_report.md` | Phase 2 exploration report |
| `issue/{slug}/docs/design_first.md` | Phase 3 design document |
| `issue/{slug}/evidence/` | Testing artifacts: screenshots, videos, code chunks, test results |
| `issue/{slug}/evidence/summary.md` | Git PR summary document for GitHub/GitLab PR generation |

### PROGRESS.md — Living Project Tracker

Create at `issue/{slug}/PROGRESS.md` at the start of the feature. Update after every phase and task.

```markdown
# Feature: [Title]

**Status:** In Progress
**Mode:** Full | Quick
**Issue ID:** [Issue ID or —]
**Work Item ID:** [Work Item ID or —]
**Branch:** [slug]
**Started:** [Date]
**Last Updated:** [Date]

## Progress Tree

Feature
 ├── Discovery          ⏳
 ├── Design
 ├── Milestone 1: [Name]
 │      ├── Task 1.1: [Name]
 │      ├── Task 1.2: [Name]
 │      └── Task 1.3: [Name]
 └── Milestone 2: [Name]

## Current Task

**Task:** [Task ID and name]
**Status:** in-progress
**Blockers:** None

## Completed Tasks

- None yet

## Notes

- [Key decisions, blockers, or important context]
```

**Update rules:**
- Completed items → mark with ✓
- In-progress items → mark with ⏳
- Update "Last Updated" timestamp after every change
- Move completed tasks to "Completed Tasks" with date
- Add decisions or blockers to "Notes"

### log.md — Living Decision Log

Create at `issue/{slug}/docs/log.md` during Step 3. Append to it throughout the entire workflow — never overwrite.

```markdown
# Decision Log: [Title]

| # | Date | Phase | Decision / Point | Rationale | Decided By |
|---|---|---|---|---|---|
| 1 | [Date] | Phase 1 | [What was decided] | [Why] | [User / Agent] |
```

**What to log:**
- Every design decision (Phase 3)
- Every milestone/task decomposition rationale (Phase 4–5)
- Model switches and why (Model Selection Strategy)
- Rejected alternatives and why
- User overrides or corrections
- Blockers encountered and resolutions
- Important assumptions confirmed or invalidated

**Rules:** Append-only. Never delete entries. Each entry gets a sequential number.

### Evidence Folder — Testing Artifacts

The `issue/{slug}/evidence/` folder holds **all testing artifacts**: screenshots, videos, code chunks, and test results.

Name files using this pattern:
```
{phase}-{task-id}-{descriptor}.{ext}
```

| Part | Meaning | Example |
|---|---|---|
| `p{N}` | Phase number | `p6`, `p8` |
| `t{M}.{T}` | Milestone.Task | `t2.1`, `t3.4` |
| `{descriptor}` | What the evidence shows (kebab-case) | `api-returns-501`, `permission-403-negative` |
| `{ext}` | `png` for screenshots, `mp4` for videos, `md` for code/results | `png`, `mp4`, `md` |

Examples:
- `p6-t2.1-api-endpoint-returns-501.png`
- `p8-t2.4-business-logic-live-data.mp4`
- `p8-t3.1-permission-403-negative-test.png`
- `p7-t1.2-review-findings.md`
- `p8-t2.3-test-results.md`

**What to capture in evidence:**
- Screenshots and videos of manual tests (Phase 8)
- Code chunks that implement key logic (copy relevant snippets)
- Test commands and their output (save as `.md` files)
- Error messages and stack traces encountered during testing
- Before/after comparisons for refactoring (Phase 9)

When prompting the user to capture evidence during Phase 8, suggest the expected filename.

### summary.md — Git PR & Verification Summary

Create or update `issue/{slug}/evidence/summary.md` upon feature completion (Phase 11). This document provides a clean summary formatted for Git PR descriptions and GitHub/GitLab Copilot context.

**Standard Template Format for `issue/{slug}/evidence/summary.md`:**

```markdown
# Evidence & Verification Summary: [Title]

**Issue ID:** [Issue ID or —]
**Work Item ID:** [Work Item ID or —]
**Branch:** [slug]
**Date:** [YYYY-MM-DD]

link: [Work Item ID: [Work Item ID]](https://git.phamos.eu/custom/project/-/work_items/[Issue ID])

### Summary
[High-level summary of feature or refactor]

### Key Changes
- [Key change 1]
- [Key change 2]
```

### Task Checklist (expand when starting each task)

```markdown
### Task [ID]: [Name]

- **Objective:** What this accomplishes
- **Scope:** Files/components affected
- **Dependencies:** What must be done first
- **Acceptance criteria:** How to verify success
- **Manual test steps:** Exact commands/interactions
- **Rollback plan:** How to undo if needed
- **Status:** not-started | in-progress | completed
```

---

## ERPNext/Frappe Reference

When working in this codebase:

**Database Changes**
- Create migrations in `patches/`
- Test migration forward and rollback
- Update DocType JSON definitions
- Clear cache after schema changes: `bench clear-cache`

**API Development**
- Use `@frappe.whitelist()` for API endpoints
- Validate permissions with `frappe.has_permission()`
- Return structured responses: `frappe.response["message"]`
- Handle exceptions with try/except

**Frontend Changes**
- Follow existing component patterns in `public/js/`
- Test in both desk and web views
- Hard-reload after JS changes: `Ctrl+Shift+R`
- Check browser console for errors

**Common Commands**
```bash
bench restart          # restart server
bench migrate          # run pending migrations
bench clear-cache      # clear all caches
tail -f logs/frappe.log  # follow logs
```
