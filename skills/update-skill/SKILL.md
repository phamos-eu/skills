---
name: update-skill
description: "Analyze and improve an existing SKILL.md while preserving its intent. Use when the user asks to update, improve, enhance, or fix an existing skill. Strengthens workflow clarity, decision logic, quality checks, and AGY ecosystem alignment."
argument-hint: "Which skill should be improved? (e.g. build-stepwise, grill-me)"
disable-model-invocation: true
---

# Update an Existing Skill

Improve an existing `SKILL.md` so it is clearer, more reliable, and better aligned with how Antigravity (AGY) discovers and executes skills — without changing what the skill is meant to do.

## Core Principle

Do not rewrite for length. Improve for reliability.

A good skill is:
- **Unambiguous** — an agent can follow it without guessing
- **Scoped** — it does not modify anything outside its stated purpose
- **Verifiable** — it defines what "done" looks like
- **Minimal** — every sentence changes agent behavior

---

## AGY Skill Ecosystem Context

Skills in this workspace live at:

```
.agents/skills/<skill-name>/SKILL.md        ← workspace (project-shared, VCS-tracked)
~/.gemini/config/skills/<skill-name>/SKILL.md  ← global (machine-local)
```

Skills are **not loaded by default**. AGY injects only their `name` and `description` into context. The full `SKILL.md` is only loaded when the agent or user explicitly activates it. This means:

- The `description` frontmatter field is the **activation signal** — it must clearly state what the skill does and **when** to use it.
- Skills should be concise enough to avoid bloating context when loaded.
- Bulky reference material belongs in a `references/` subdirectory, linked from the skill.

### Valid Frontmatter Fields

```yaml
---
name: skill-name           # required: lowercase, hyphenated
description: "..."         # required: when/why to activate (third-person)
argument-hint: "..."       # optional: shown to user as input prompt
disable-model-invocation: true  # optional: prevents auto-LLM call on activation
---
```

### Skills in This Workspace

| Skill | Purpose | Cross-references |
|---|---|---|
| `create-skill` | Guide user to create a new SKILL.md | `agy-customizations` |
| `update-skill` | Improve an existing SKILL.md | (this file) |
| `grill-me` | Interview user relentlessly about a plan/design | Used by `build-stepwise` |
| `build-stepwise` | Decompose features into atomic, testable increments | Integrates with `grill-me` |

---

## Inputs

| Input | Source | Required? |
|---|---|---|
| Target skill name or path | User argument or conversation | Yes |
| Custom improvement instructions | User's explicit request | No — but if present, they become primary goals |

### Determine Mode Before Starting

Before locating the file, identify which mode applies based on the user's request:

| Mode | Condition | Behavior |
|---|---|---|
| **Custom-directed** | User explicitly states what to change | Apply those instructions as primary goals. General improvement is secondary. |
| **General** | No specific instructions given | Full analysis pass. Infer what most needs improvement from the skill itself. |
| **Both** | User states specific goals and also wants a general review | Apply custom instructions first, then do a general pass on the remaining sections. |

**If the skill name is ambiguous or not provided:** Ask once: *"Which skill should I improve, and is there a specific aspect you want strengthened?"*

Do not ask further questions if the skill file is readable and the mode can be determined from the conversation.

---

## Workflow

### 1. Locate the Skill File

Resolve the skill path in this order:
1. Exact path provided by user
2. `.agents/skills/<name>/SKILL.md` in the current workspace
3. `~/.gemini/config/skills/<name>/SKILL.md`

**If not found:** Report the paths searched and stop. Do not create a new file.

### 2. Read and Understand the Skill

Read the complete `SKILL.md`. Do not skim.

Extract and record internally:

- **Purpose** — what the skill produces
- **Trigger** — when it should activate
- **Inputs** — what information it needs
- **Workflow** — the steps it executes
- **Decision points** — where branching occurs
- **Constraints** — what it must not do
- **Completion criteria** — how it knows it succeeded
- **Cross-references** — other skills or tools it mentions

Also check:
- Does the `description` frontmatter accurately reflect the workflow?
- Is `disable-model-invocation` set appropriately?
- Are reference files linked but not inlined unnecessarily?

### 3. Classify Each Part

Sort every section into one of four buckets, in priority order:

| Bucket | Meaning | Priority |
|---|---|---|
| **Must apply** | User explicitly specified this change | Highest — apply exactly as instructed |
| **Must preserve** | Defines the skill's purpose or established behavior | High — never remove without flagging |
| **Should improve** | Ambiguous, redundant, incomplete, or hard to follow | Normal — apply where it materially helps |
| **Remove** | Repeats the same rule, states the obvious, or doesn't affect execution | Low — remove only when certain it adds nothing |

**If a "Must apply" item conflicts with a "Must preserve" item:** Stop. Report the conflict to the user and ask how to resolve it. Do not resolve it silently.

**Red flags to look for:**
- Vague verbs: "handle appropriately", "make it better", "use best judgment"
- Missing fallback: what happens when input is absent, ambiguous, or a tool fails?
- Hidden assumptions: expected file location, tool availability, environment, format
- No completion signal: agent cannot tell if the task succeeded
- Scope drift risk: instructions that could tempt modification of unrelated files
- AGY misalignment: description that won't trigger activation correctly; missing `argument-hint`; bulky content that should be in `references/`

### 4. Draft the Improvement

Apply changes in this order:

1. **"Must apply" items first** — implement the user's explicit instructions exactly as stated. Do not generalize, reinterpret, or fold them into other changes.
2. **"Should improve" / "Remove" items second** — apply general improvements only to sections not already addressed in step 1.
3. **"Must preserve" items** — leave unchanged unless they contain a red flag identified during classification.

Use this structure **only when it fits** — do not force it:

```markdown
---
name: ...
description: "..."   # activation signal — when AND what
argument-hint: "..."
---

# [Skill Title]

One-sentence purpose statement.

## Inputs
## Workflow
### 1. ...
### 2. ...
## Decision Rules
## Constraints
## Failure Handling
## Completion Criteria
```

**Specific improvements to apply if applicable:**

- Tighten the `description` so AGY activates the skill at the right moment
- Replace vague verbs with concrete, observable actions
- Add explicit decision rules for every branching point
- Add failure behavior for every tool call or external dependency
- Specify the exact file to write results to (not just "output the result")
- Remove sections that duplicate each other or restate obvious behavior
- Move large reference content to `references/` and link it

### 5. Verify Intent Is Preserved

Before saving, run this internal check:

| Area | Original | Improved | Preserved? |
|---|---|---|---|
| Purpose | | | |
| Trigger / description | | | |
| Inputs | | | |
| Core workflow | | | |
| Constraints | | | |
| Completion criteria | | | |

If any "Must preserve" item was inadvertently removed or changed, restore it.

Enhancement must not silently become redesign.

### 6. Validate the Skill Against Scenarios

Mentally test the improved skill against these cases. If the skill does not handle a case clearly, fix it before saving:

| Scenario | Does the skill define behavior? |
|---|---|
| Happy path — everything works | |
| Required input is missing | |
| Input is ambiguous | |
| A tool call fails | |
| Only some steps succeed | |
| Input is unusual but valid | |
| Agent could expand scope beyond intent | |

### 7. Write the File

Write the improved content back to the **same file** that was read in Step 1.

Do not:
- Create a new file at a different path
- Modify any other file in the skill directory
- Touch other skills unless explicitly asked

After writing, read the file back and confirm:
- File exists and is non-empty
- Frontmatter is valid YAML with `name` and `description`
- No unintended content was removed

---

## Decision Rules

| Situation | Action |
|---|---|
| Skill name not specified | Ask once, then proceed |
| Skill file not found | Report paths searched, stop |
| User provided explicit custom instructions | Mode = Custom-directed. Extract as "Must apply" items. Apply them first and exactly. |
| Custom instruction conflicts with core purpose | Stop. Report the conflict. Ask how to proceed. Do not resolve silently. |
| User gave no specific goal | Mode = General. Infer from skill content what most needs improvement. |
| User gave specific goals AND wants general review | Mode = Both. Custom first, general pass second. |
| A section is fine as-is | Leave it unchanged |
| Improvement would change the skill's purpose | Flag to user before proceeding |
| Content is bulky reference material | Move to `references/` and link it |

---

## Constraints

- Only modify the target `SKILL.md` file. No other files.
- Do not rename, move, or delete the skill.
- Do not change the skill's name in frontmatter unless it conflicts with an existing skill.
- Do not add cross-references to other skills unless the workflow genuinely integrates with them.
- Do not make the skill longer unless additional content directly prevents an error or ambiguity.

---

## Failure Handling

| Failure | Response |
|---|---|
| File not found | Report exact paths searched. Do not guess or create. |
| File is unreadable or malformed | Report the error. Ask user to provide the content directly. |
| Frontmatter is invalid YAML | Flag it. Fix it as part of the improvement. |
| Write fails | Report the error. Do not claim success. |
| Improvement would break the skill's purpose | Stop. Explain the conflict. Ask how to proceed. |

---

## Completion Criteria

The task is complete when:

- ✓ The improved `SKILL.md` is written to the same path it was read from
- ✓ All frontmatter fields are valid
- ✓ The `description` accurately triggers activation for the right prompts
- ✓ All user-specified custom instructions were applied exactly as stated
- ✓ No "Must preserve" behavior was removed
- ✓ The file is shorter or clearer where possible
- ✓ Every remaining instruction affects agent behavior

---

## Output to User

After writing the file, report:

1. **What changed** — bullet list of the most important improvements (3–6 items)
2. **What was preserved** — confirm the skill's core purpose is intact
3. **Anything requiring approval** — behavior changes that were flagged, not assumed
4. **Example prompts to test it** — 2–3 prompts that exercise the updated skill
