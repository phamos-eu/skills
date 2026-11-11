# Templates

## hooks.py `phamos_forge`

Team settings, committed in the app's `hooks.py` (add as a small separate PR). Must stay a pure literal: no variables or function calls, because the agent reads it with `ast.literal_eval` and doesn't import Frappe. Frappe ignores the key.

```python
# Settings for the phamos-forge ticket workflow skill.
# Read by the AI agent from this file (as a literal); not used by Frappe at runtime.
phamos_forge = {
	"ticket_project": "[group/project on git.phamos.eu]",
	"pr_host": "github",  # github | gitlab
	"pr_repo": "[owner/repo or GitLab project path]",
	"base_branch": "develop",
	"prod_node": "[production Node version]",
	"live_entry_points": []  # functions/classes that reach them
}
```

## issue/PROJECT.md

Local, per developer, never committed. Any key here overrides `hooks.py`.

```markdown
# Project profile: [Project name] (local)

| Key | Value |
|---|---|
| test_site | [site or environment for tests and manual checks] |
| test_agent | [name of the independent test agent, or —] |
| never_touch | [dev/prod sites tests must not touch] |

## Project rules

Read together with the skill's rules.md; these win.

- [project-specific rules, with source ticket]
```

Optional extra rows: `app_repo` (to pick the app when several have a `phamos_forge` block), or any hooks.py key to override locally.

## PROGRESS.md

```markdown
# Ticket: [Title]

**Status:** In Progress
**Mode:** Full | Quick
**Ticket:** https://git.phamos.eu/[ticket_project]/-/work_items/[iid]
**Parent:** [parent iid or —]
**Branch:** [slug]
**Design thread:** [gid://gitlab/Discussion/... or — (not posted yet)]
**Started:** [YYYY-MM-DD]
**Last Updated:** [YYYY-MM-DD]

## Progress Tree

    Ticket
     ├── Understand        ⏳
     ├── Explore
     ├── Design
     ├── Milestone 1: [Name]
     │      ├── Task 1.1: [Name]
     │      └── Task 1.2: [Name]
     └── Milestone 2: [Name]

## Current Task

**Task:** [ID and name]
**Status:** not-started | in-progress | awaiting approval | testing
**Blockers:** None

## Completed Tasks

- None yet

## Deferred / Open

- [item] — source: [log #n / review / test] — [date]

## Notes

- [key context]
```

Marks: ✓ done, ⏳ in progress. Update "Last Updated" on every change. Completed tasks move to "Completed Tasks" with date.

## docs/log.md

```markdown
# Decision Log: [Title]

| # | Date | Phase | Decision / Point | Rationale | Decided By |
|---|---|---|---|---|---|
| 1 | [YYYY-MM-DD] | Phase 1 | [what] | [why] | User / Agent |
```

Append-only, numbered. Log: decisions, rejected alternatives, design changes (with the thread reply version), user corrections, blockers and their resolution, assumptions confirmed or broken, rules.md / PROJECT.md rule checks (e.g. L3 result).

## Design v1 comment

Top-level note. The marker line must stay first.

```markdown
<!-- phamos-forge:design v1 -->
**Design v1** (phamos-forge)

<details><summary>Full design</summary>

[full content of docs/design_first.md, all `## ` sections]

</details>
```

## Design reply comment

Reply in the design thread. Carry the **full new text of every changed section**, so the design can be rebuilt by replacing sections.

```markdown
<!-- phamos-forge:design v[n] -->
**Design v[n]**: [one-line summary]

**Changes since v[n-1]**
- [section]: [what changed and why]

<details><summary>Changed sections (full text)</summary>

## [Section heading, exactly as in the design]
[full new text of the section]

## [Next changed section]
[...]

</details>
```

- New section: include it in full; it is appended at the end.
- Removed section: list it under Changes as `[section]: removed` and include `## [Section]` with the single line `_Removed._`.

## evidence/summary.md

Created at setup with only the title line. One block per PR, **appended at the bottom**, never rewritten:

```markdown
# PR Summary: [Title]

## PR #[n] — [PR title]
Link: [PR or MR link]

Description:
- [bullets, reused verbatim in the ticket comment]

Screenshot:
![t1.2 what it shows](p8-t1.2-what-it-shows.png)
```

Screenshots are relative links to files in `evidence/`. Add them as testing produces them.

## PR comment on the ticket

Top-level note, posted only after the user's OK:

```
PR: [PR or MR link]

Description:
- [same bullets as the summary.md block]
```
