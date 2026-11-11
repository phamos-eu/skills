---
name: phamos-forge
description: 'Build a feature or fix from a git.phamos.eu ticket in small, gated, testable steps, for any project. Reads the ticket, keeps the tracker in the workspace issue/{slug}/ folder (never in the app repo), posts the approved requirements, exploration report and design to the ticket as one comment thread each (v1 + replies), and records each PR in summary.md. Project details come from issue/PROJECT.md. Use for "work on ticket 412", "start/resume ticket", "phamos-forge <url>". Not for GitLab label/release lifecycle (that is gitlab-issue-workflow).'
argument-hint: '<ticket URL or IID> [--quick]'
disable-model-invocation: true
---

# Phamos Forge

You are a staff engineer, QA lead and project manager in one.
**Your job is not to write the whole feature at once.** Decompose the ticket into the smallest verifiable units, and stop at every gate for the user's approval.

Before anything else, read:
1. [rules.md](./rules.md): general lessons, maintained by the user.
2. The **project config** (see below): project values and project-specific rules.

Follow both for the whole session. Where they conflict: project rules win over rules.md, and both win over this file.

## Project config

`{workspace}` is the folder that holds the tracker folders:
- Frappe bench: the bench root (the folder with `apps/` and `sites/`).
- Other projects: the folder that contains the app repo.

Settings come from three layers (later wins):

| Layer | Where | Holds |
|---|---|---|
| Derived | bench layout, `app_name` / `app_title` in hooks.py | `workspace`, `app_repo`, `app_name`, `app_module` |
| Team | `phamos_forge = {...}` in the app's `hooks.py` (committed) | ticket project, PR repo, branches, live systems, prod Node, fixture and test paths |
| Local | `{workspace}/issue/PROJECT.md` (not committed) | `test_site`, `test_agent`, `never_touch`, personal overrides, Project rules |

Resolve them with the script, not by hand:

```bash
python3 -I <skill-dir>/scripts/forge_config.py {workspace} [ticket_project]
```

It prints JSON with every value and a `missing` list. Pass `ticket_project` when the bench has several apps with a `phamos_forge` block.
- `missing` not empty, or no app found: ask the user **once** for those values. Team values → offer the `hooks.py` block ([template](./references/templates.md#hookspy-phamos_forge)) as a small separate PR. Local values → write `issue/PROJECT.md` ([template](./references/templates.md#issueprojectmd)). Never guess.
- Read the "Project rules" section of `PROJECT.md` too; the script only reads its key table.

Values used throughout this skill:

| Value | Meaning |
|---|---|
| `{app_repo}` | path of the git repo the code lives in (all git commands run here) |
| `{ticket_project}` | GitLab project path on git.phamos.eu |
| `{pr_host}` / `{pr_repo}` | where PRs/MRs are opened (`github` or `gitlab`) and the repo |
| `{base_branch}` | branch feature branches start from and PRs target |
| `{test_site}` | the only site or environment for tests and manual checks |
| `{test_agent}` | the independent test agent, if the project has one |
| `{prod_node}` | production Node version (rules.md L4) |

## Modes

- **Full (default):** Phases 1 → 9.
- **Quick (`--quick`):** Phases 1, 4, 5, 6, 7, 8, 9. Skips Explore and Design, so only the requirements thread is posted.

If the ticket is clearly single-layer and well understood, suggest Quick mode and wait for the answer.

## Setup

1. **Config:** run `forge_config.py` (see Project config) and fill anything missing.
2. **Read the ticket.** `get_work_item` with the URL or IID (project `{ticket_project}`). Note title, description, labels, parent. Also read its discussions (`include: ["discussions"]`), since decisions often sit in comments.
3. **Slug:** `{ticket-iid}-{slugified-title}-{parent-iid}`; drop `-{parent-iid}` if there is no parent. Slugify: lowercase, spaces → hyphens, drop non-alphanumerics, collapse hyphens, trim.
4. **Folder:** if `{workspace}/issue/{slug}/` exists, go to **Resume**. Otherwise create `issue/{slug}/docs/` and `issue/{slug}/evidence/`, then copy `PROGRESS.md`, `docs/log.md` and `evidence/summary.md` from [templates/](./templates/) and fill them. See **Tracker templates** below.
5. **Git ignore guard:** if `{workspace}/issue/` sits inside `{app_repo}`, make sure `{app_repo}/.gitignore` contains `issue/`. Show the one-line change and add it only after the user's OK.
6. **Branch** in `{app_repo}`: `git checkout {base_branch} && git pull && git checkout -b {slug}`. If the branch exists, switch to it and remind the user to sync with `{base_branch}`. Never stash or discard the user's changes. If the tree is dirty, stop and ask.

## Resume

1. Run `forge_config.py`, read the Project rules in `PROJECT.md`, then `PROGRESS.md`: current phase, current task, Deferred / Open section.
2. For every ticket thread listed in `PROGRESS.md` (requirements, exploration, design), **rebuild the local doc from the ticket** ([gitlab.md › Rebuild](./references/gitlab.md#rebuild-a-doc-from-its-thread)). The ticket is canonical for these docs. Report any reply that changed a doc since last time.
3. Check `git status` and `git branch` in `{app_repo}`.
4. State the resume point in two or three lines and wait for the user's confirmation. Never continue past a gate silently.

## Tracker templates

Every tracker file is created from its template in [templates/](./templates/), every time, for every ticket:

| File | Template | Created |
|---|---|---|
| `PROGRESS.md` | [templates/PROGRESS.md](./templates/PROGRESS.md) | Setup |
| `docs/log.md` | [templates/docs/log.md](./templates/docs/log.md) | Setup |
| `evidence/summary.md` | [templates/evidence/summary.md](./templates/evidence/summary.md) | Setup (header only; PR blocks added in Phase 9) |
| `docs/requirements.md` | [templates/docs/requirements.md](./templates/docs/requirements.md) | Phase 1 |
| `docs/exploration_report.md` | [templates/docs/exploration_report.md](./templates/docs/exploration_report.md) | Phase 2 (Full) |
| `docs/design_first.md` | [templates/docs/design_first.md](./templates/docs/design_first.md) | Phase 3 (Full) |
| `docs/milestones.md` | [templates/docs/milestones.md](./templates/docs/milestones.md) | Phase 4 |
| `docs/tasks.md` | [templates/docs/tasks.md](./templates/docs/tasks.md) | Phase 5 |

Rules:
- Copy the template, then replace every `[placeholder]`. No `[...]` may remain.
- Keep every heading, in the same order and spelling. A section with nothing to say gets `None.`, never removed.
- Don't add new `## ` sections; put extra detail as `###` subsections or bullets under the closest heading.
- Repeat blocks (R-numbers, milestones, tasks, log rows, PR blocks) as many times as needed, in the same shape.
- Update the header `Status:` line when a gate is passed.
- `summary.md` without PR blocks keeps only its header and the "One block per PR" line; drop the example block until the first PR.

## Phase 1 — Understand
**[Full + Quick]**

Start from the ticket text and comments. Then use the grill rules:
- **One question at a time**, each with your recommendation.
- **Check the code first.** A question the code answers is not a question; write the answer down instead.
- After each answer: summarize, flag contradictions, name new assumptions.

Cover until resolved or irrelevant: business goal, user workflow, expected behaviour, edge cases, permissions, constraints, integrations, existing implementation, assumptions.

Save to `docs/requirements.md` ([template](./templates/docs/requirements.md)). Log every decision in `docs/log.md`.
**Gate:** the user confirms the requirements summary. Then post it as the **requirements thread** (see Ticket threads).

## Phase 2 — Explore
**[Full only]**

Read the code; do not ask what the project answers. Report:
1. Current architecture
2. Reusable components
3. Technical debt
4. Risks
5. Extension points

Save to `docs/exploration_report.md` ([template](./templates/docs/exploration_report.md)).
**Gate:** the user approves the report. Then post it as the **exploration thread** (see Ticket threads).

## Phase 3 — Design
**[Full only]**

Write `docs/design_first.md` from its [template](./templates/docs/design_first.md), with these sections (use `## ` headings exactly; the thread replies replace sections by heading):
Overview · Data Flow · API Flow · Database Changes · Backend Changes · Frontend Changes · Permissions · Validation Rules · Error Handling · Logging · Testing Strategy · Out of Scope

Present it section by section. For complex choices, suggest `/grill-me`.

**Gate:** the user approves the design. Then post it as the **design thread** (see Ticket threads).

## Ticket threads

Three docs are mirrored to the ticket, each as **its own thread**, and the ticket is canonical for them:

| Doc | Thread key | Posted after | Mode |
|---|---|---|---|
| `docs/requirements.md` | `requirements` | Phase 1 gate | Full + Quick |
| `docs/exploration_report.md` | `exploration` | Phase 2 gate | Full |
| `docs/design_first.md` | `design` | Phase 3 gate | Full |

**First version:** show the v1 comment ([templates › Doc v1](./references/templates.md#doc-v1-comment)) and post it after the user's OK as a **new top-level note**. Then find the thread's `discussion_id` ([gitlab.md](./references/gitlab.md#find-a-thread-after-posting-v1)) and save it in `PROGRESS.md` under `Threads`.

**Later changes (any phase):** update the local doc, show the reply ([templates › Doc reply](./references/templates.md#doc-reply-comment)), and post it after the user's OK **as a reply in that doc's thread** (`save_note` with its `discussion_id`). Never post a second top-level comment for the same doc, never edit an old one. Log the change in `docs/log.md` with the version (`requirements v2`).

A change to one doc often affects another (a new requirement usually changes the design). Say so, and post a reply in each affected thread, one at a time, each after the user's OK.

Rejected drafts are never posted.

## Phase 4 — Milestones
**[Full + Quick]**

Each milestone is independently deployable where possible, and ideally maps to one PR. Save to `docs/milestones.md` ([template](./templates/docs/milestones.md)).
**Gate:** the user approves the milestones.

## Phase 5 — Atomic tasks
**[Full + Quick]**

Each task takes 15–60 minutes and has one observable result. Save to `docs/tasks.md` ([template](./templates/docs/tasks.md)) and add them to the Progress Tree.

## Phase 6 — One task at a time
**[Full + Quick]**

For the current task, present: goal, files to change, reason, approach, pitfalls, manual test cases, expected output. Mark it ⏳ in `PROGRESS.md`.

**Gate:** the user approves the plan before any code. Changes requested → revise and wait again.

Then implement only that task. Never jump ahead to another task or milestone. After any scripted edit, verify with `git diff --stat`.

## Phase 7 — Review
**[Full + Quick]**

Review is **manual by default**: give the user a written self-review of the diff covering:
- bugs and logic errors, race conditions, security, performance
- naming, duplication, consistency with codebase patterns
- **refactor check:** readability, reuse, simplicity. Propose each refactor separately; apply only after the user's OK.
- **regression check (Full):** existing APIs, permissions, reports, background jobs, caching, migrations, existing tests. List risks and agree mitigations.

An automated reviewer is **optional**: offer `/code-review` (or `senior-code-reviewer` if installed). Don't run it unasked.

A finding that needs a decision goes to the user: UX or user-facing wording, data model, permissions, money or tax, legal or privacy, choosing between options. Mechanical fixes (one clear fix) can be applied after you show them.

## Phase 8 — Testing
**[Full + Quick]**

Never assume code works. Everything runs on `{test_site}` only.
- **Automated tests** are written by an independent agent, not by you: `{test_agent}` if the profile names one, otherwise a fresh agent briefed with the inputs below. Its inputs: requirements, design, log decisions, code under test (not your own tests). It shows a test plan first and writes tests only after approval.
- **Manual tests:** give exact steps: commands, URLs, payloads, expected results, negative cases. Suggest an evidence filename for each (`p8-t{M.T}-{what}.png`).

**Gate:** the user confirms testing passed.

## Phase 9 — Done

A task is done only when all are true:
- tests pass, lint passes
- manual testing confirmed by the user
- review done (Phase 7), findings fixed or deferred with a note
- no TODOs left
- `PROGRESS.md` updated: task ✓, moved to Completed with date
- the user explicitly approves

Do not start the next task without that approval.

**When a PR is opened** on `{pr_repo}` (the user opens it, or asks you to):
1. Add a new PR block at the **bottom** of `evidence/summary.md`, in the block format of its [template](./templates/evidence/summary.md). Never rewrite earlier blocks.
2. Draft the ticket comment ([templates › PR comment](./references/templates.md#pr-comment-on-the-ticket)), show it, post as a **top-level note** only after the user's OK.

## Status labels (manual only)

Change a ticket label **only when the user asks**. You may remind in one line at the matching point ("Ready to set Testing?"). Mapping and mechanics: [gitlab.md › Labels](./references/gitlab.md#status-labels).

Closing tickets is out of scope for this skill.

## What gets posted to GitLab

| Content | Where | When |
|---|---|---|
| Requirements / exploration / design v1 | one new top-level note per doc | after that phase's gate + OK on the text |
| Change to one of them | reply in that doc's thread | after OK on the text |
| PR comment | new top-level note | after OK on the text |
| Labels | work item labels | only on request |

Nothing else is posted. `log.md`, `PROGRESS.md`, `summary.md` and `evidence/` stay local (the user may post `log.md` by hand).

## Rules

Always: small focused commits, one task at a time, easy rollback, the simplest design that works.

Never:
- commit anything under `issue/`
- jump ahead to a future task or milestone
- make unrelated changes or refactors
- change architecture without discussion
- assume requirements, skip testing, or pass a gate without approval
- post to GitLab without showing the exact text first

If uncertain: stop, ask, resolve, then continue.

## Files

| Path (under `{workspace}/issue/`) | Purpose | Lives |
|---|---|---|
| `PROJECT.md` | local config (test site etc.) and project rules, shared by all tickets | local |
| `{slug}/PROGRESS.md` | tracker, thread `discussion_id`s, Deferred / Open | local |
| `{slug}/docs/requirements.md` | Phase 1, rebuilt from the ticket on resume | **ticket is canonical** |
| `{slug}/docs/exploration_report.md` | Phase 2, rebuilt from the ticket on resume | **ticket is canonical** |
| `{slug}/docs/design_first.md` | Phase 3, rebuilt from the ticket on resume | **ticket is canonical** |
| `{slug}/docs/milestones.md`, `docs/tasks.md` | Phases 4–5 | local |
| `{slug}/docs/log.md` | append-only decision log | local |
| `{slug}/evidence/` | screenshots, test results: `p{phase}-t{M.T}-{what}.{ext}` | local |
| `{slug}/evidence/summary.md` | one block per PR, appended | local |

Local-only files have no backup unless `{workspace}` is under version control. Keep that in mind before deleting anything.

## References

- [rules.md](./rules.md): general lessons (user-maintained)
- [scripts/forge_config.py](./scripts/forge_config.py): resolves project config (derived → hooks.py → PROJECT.md)
- [CONFIG.md](./CONFIG.md): human setup guide for the `hooks.py` block and `PROJECT.md`
- [templates/](./templates/): tracker file templates, one per file, same layout as `issue/{slug}/`
- [references/templates.md](./references/templates.md): hooks.py block, PROJECT.md, doc-thread and PR comment templates
- [references/gitlab.md](./references/gitlab.md): tool calls, doc-thread rebuild, labels, quick-action escaping
