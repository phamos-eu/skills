# Setting up phamos-forge in `hooks.py`

`phamos-forge` needs a few team-wide facts about your project: which GitLab project holds the tickets, where PRs go, and which branch they target. You record these once in the app's `hooks.py`, commit them, and every developer on the app gets the same settings.

Personal, per-machine values (test site, sites to keep away from) go in `issue/PROJECT.md` instead. See [Local overrides](#local-overrides-issueprojectmd).

## 1. Add the block

Open `apps/<app>/<app>/hooks.py` and add a `phamos_forge` dict at the top level:

```python
# Settings for the phamos-forge ticket workflow skill.
# Read by the AI agent from this file (as a literal); not used by Frappe at runtime.
phamos_forge = {
	"ticket_project": "phamos/customer-portal",
	"pr_host": "github",
	"pr_repo": "phamos-eu/customer_portal",
	"base_branch": "develop",
	"prod_node": "18",
	"live_entry_points": [
		"customer_portal.api.sync_orders",
		"customer_portal.integrations.dhl.DHLClient",
	],
}
```

Frappe ignores keys it doesn't know, so the block has no runtime effect.

Add it as a small PR of its own rather than inside a feature PR.

## 2. Keys

| Key | Required | Example | What it's for |
|---|---|---|---|
| `ticket_project` | yes | `"phamos/customer-portal"` | GitLab project path on git.phamos.eu where tickets live (the part after `git.phamos.eu/` in a ticket URL). |
| `pr_host` | yes | `"github"` | Where PRs/MRs are opened: `"github"` or `"gitlab"`. |
| `pr_repo` | yes | `"phamos-eu/customer_portal"` | Repo PRs are opened on: `owner/repo` for GitHub, project path for GitLab. |
| `base_branch` | yes | `"develop"` | Branch that feature branches start from and PRs target. |
| `prod_node` | no | `"18"` | Production Node version. Checked before adding or upgrading frontend packages, because local Node is often newer. |
| `live_entry_points` | no | `["app.api.sync_orders"]` | Dotted paths of functions/classes that talk to live external systems (APIs, payment, shipping). Tests must not call these for real. |

The app itself (`app_repo`, `app_name`, `app_module`) and the workspace are worked out from the bench layout. You don't set them.

## 3. Rules for the block

- **Literal values only.** The agent reads the block with Python's `ast.literal_eval` and never imports Frappe or your app. Strings, numbers, booleans, lists and dicts are fine. Variables, f-strings, function calls, imports or `os.environ` are not. If the block isn't a pure literal, it's silently ignored and every key is reported as missing.
- **Top level of the file**, assigned directly: `phamos_forge = {...}`. Not inside a function or `if`.
- **Standard app layout.** The file must be at `apps/<app>/<app>/hooks.py` (folder names match), as Frappe creates it.
- **No secrets.** The file is committed. Tokens and passwords never go here.

## 4. Check it

From the bench root, run:

```bash
python3 -I <skill-dir>/scripts/forge_config.py .
```

`<skill-dir>` is where the skill is installed (for example `~/.claude/skills/phamos-forge`). The script prints JSON with every resolved value, where it came from (`source`), and a `missing` list.

```json
{
  "workspace": "/home/me/frappe-bench",
  "source": { "hooks": "apps/customer_portal/customer_portal/hooks.py" },
  "app_name": "customer_portal",
  "app_module": "Customer Portal",
  "app_repo": "apps/customer_portal",
  "ticket_project": "phamos/customer-portal",
  "pr_host": "github",
  "pr_repo": "phamos-eu/customer_portal",
  "base_branch": "develop",
  "prod_node": "18",
  "live_entry_points": ["customer_portal.api.sync_orders", "customer_portal.integrations.dhl.DHLClient"],
  "missing": ["test_site"]
}
```

`test_site` showing as missing is normal at this point. It's a local value; add it in `issue/PROJECT.md` (next section). Any other key in `missing` means the block wasn't found or isn't a pure literal.

## Local overrides: `issue/PROJECT.md`

Each developer keeps `{bench}/issue/PROJECT.md`, which is never committed. Its key table holds local values and can override any `hooks.py` key:

```markdown
# Project profile: Customer Portal (local)

| Key | Value |
|---|---|
| test_site | portal.test |
| test_agent | — |
| never_touch | portal.dev, portal.prod |

## Project rules

Read together with the skill's rules.md; these win.

- [project-specific rules, with source ticket]
```

`test_site` is required. Values here win over `hooks.py`, so you can, for example, point `base_branch` at a different branch locally without changing the team setting.

If you skip this, the skill asks for the missing values on its first run and writes the file for you.

## Several apps in one bench

If more than one app in the bench has a `phamos_forge` block, the skill picks the app in this order:

1. The app whose `ticket_project` matches the ticket you start with.
2. The app named by `app_repo` in `PROJECT.md` (for example `| app_repo | apps/customer_portal |`).

If neither matches, the skill lists the candidates and asks you.

## Troubleshooting

| Symptom | Cause |
|---|---|
| All team keys in `missing`, no `source.hooks` | No `phamos_forge` block found, or it uses a variable/function call. Make it a pure literal at the top of the file. |
| `candidates` listed instead of an app | Several apps have a block and none was matched. Pass the ticket project as the second argument, or set `app_repo` in `PROJECT.md`. |
| A value differs from `hooks.py` | `PROJECT.md` overrides it. Check `source.profile` in the output. |
