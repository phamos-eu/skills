# Phamos Skills

A collection of agent skills for building and customizing ERPNext/Frappe applications, managing incremental workflows, prompt refinement, print format development, and agent skill management within Phamos projects.

## Skills

| Skill | What it covers |
| ----- | -------------- |
| `build-stepwise` | Incremental feature breakdown and execution workflow with mandatory review, testing, living project tracking, and model selection |
| `grill-me` | Interactive stress-testing and relentless interviewing on plans, architecture, or designs to resolve decision trees and surface hidden assumptions |
| `refine-prompt-from-codebase` | Codebase investigation and interactive grilling to transform rough feature requests into implementation-ready prompts |
| `print-format-development` | HTML print format creation, Jinja macro conversion, DIN 5008 layout compliance, PDF rendering fixes, and Frappe translations for ERPNext |
| `create-skill` | Standardized creation of new agent skills (`SKILL.md`) packaging reusable workflows |
| `update-skill` | Analysis, refinement, and enhancement of existing skills while preserving intent and improving AGY ecosystem compatibility |

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

Most skills activate automatically when you ask your agent about a matching task (e.g. breaking down a multi-layer feature, designing Jinja print formats, stress-testing architectural plans, or creating/updating agent skills).

You can also explicitly invoke specific skills using their name (e.g. `/grill-me`, `/build-stepwise`).
