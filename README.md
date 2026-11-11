# Phamos Skills

A collection of agent skills for building and customizing ERPNext/Frappe applications, managing incremental workflows, prompt refinement, and agent skill management within Phamos projects.

## Skills

| Skill | What it covers |
| ----- | -------------- |
| `build-stepwise` | Incremental feature breakdown and execution workflow with mandatory review, testing, living project tracking, and model selection |
| `grill-me` | Interactive stress-testing and relentless interviewing on plans, architecture, or designs to resolve decision trees and surface hidden assumptions |
| `refine-prompt-from-codebase` | Codebase investigation and interactive grilling to transform rough feature requests into implementation-ready prompts |
| `create-skill` | Standardized creation of new agent skills (`SKILL.md`) packaging reusable workflows |
| `update-skill` | Analysis, refinement, and enhancement of existing skills while preserving intent and improving AGY ecosystem compatibility |
| `phamos-forge` | Ticket-driven delivery from git.phamos.eu: reads the ticket, decomposes it into small gated and testable steps, keeps the tracker in `issue/{slug}/` (outside the app repo), posts the approved requirements, exploration report and design to the ticket as one thread each (the ticket stays the source of truth), and records each PR in `summary.md`. Invoke explicitly: `/phamos-forge <ticket URL or IID> [--quick]` |

## Install

Install all skills from the repo:

```bash
npx skills add phamos-eu/skills
```

Install a single skill:

```bash
npx skills add phamos-eu/skills --skill build-stepwise
```

Install several at once:

```bash
npx skills add phamos-eu/skills \
  --skill build-stepwise --skill grill-me --skill refine-prompt-from-codebase
```

Skills are matched by the `name` field in each `SKILL.md` frontmatter, and live under `skills/<name>/`.

## Usage

Most skills activate automatically when you ask your agent about a matching task (e.g. breaking down a multi-layer feature, stress-testing architectural plans, or creating/updating agent skills).

You can also explicitly invoke specific skills using their name (e.g. `/grill-me`, `/build-stepwise`).

`phamos-forge` does not auto-activate; start it with `/phamos-forge <ticket URL or IID>`. Project settings come from a `phamos_forge = {...}` block in the app's `hooks.py` (team values) and `{workspace}/issue/PROJECT.md` (local values); the skill asks for anything missing on first run. See [skills/phamos-forge/CONFIG.md](skills/phamos-forge/CONFIG.md) for the `hooks.py` setup guide.
