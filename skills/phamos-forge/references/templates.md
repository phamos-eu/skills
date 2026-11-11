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

Tracker files (`PROGRESS.md`, `docs/*.md`, `evidence/summary.md`) have their own template files in [../templates/](../templates/).

## Doc v1 comment

One top-level note per doc. `[key]` is `requirements`, `exploration` or `design`; `[Doc]` is Requirements, Exploration Report or Design. The marker line must stay first.

```markdown
<!-- phamos-forge:[key] v1 -->
**[Doc] v1** (phamos-forge)

<details><summary>Full [doc]</summary>

[full content of the local doc: header lines + all `## ` sections]

</details>
```

## Doc reply comment

Reply in that doc's thread. Carry the **full new text of every changed section**, so the doc can be rebuilt by replacing sections.

```markdown
<!-- phamos-forge:[key] v[n] -->
**[Doc] v[n]**: [one-line summary]

**Changes since v[n-1]**
- [section]: [what changed and why]

<details><summary>Changed sections (full text)</summary>

## [Section heading, exactly as in the doc]
[full new text of the section]

## [Next changed section]
[...]

</details>
```

- New section: include it in full; it is appended at the end.
- Removed section: list it under Changes as `[section]: removed` and include `## [Section]` with the single line `_Removed._`.

## PR comment on the ticket

Top-level note, posted only after the user's OK:

```
PR: [PR or MR link]

Description:
- [same bullets as the summary.md block]
```
