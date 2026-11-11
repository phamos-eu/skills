# Rules: general lessons

Maintained by hand. Add, edit or remove rules freely; the skill reads this file at the start of every session and it wins over SKILL.md.

These rules apply to every project. Project-specific values belong in the app's `hooks.py` → `phamos_forge` (team) or `issue/PROJECT.md` (local); project-specific rules go under "Project rules" in PROJECT.md.

Format: one rule per heading, the rule first, then why.

## L1 — Independent tests, test site only
Automated tests are written by a separate test agent, never by the agent that implemented the code. It writes a test plan first, traced to requirements and decisions, and writes tests only after approval. Failures come back as findings; fix the code, not the tests.
Tests and manual checks run **only** on the profile's `{test_site}`, with self-created data. Never touch dev-data or production sites, their databases or their files.
*Why:* the implementer's tests share its blind spots, and dev/prod data must stay untouched.

## L4 — Frontend dependencies on the production Node version
Local Node is often newer than production (`prod_node` in the project config). Before adding or upgrading a frontend package, check `engines.node` and test install + build with the production Node version.
*Why:* a dependency needing a newer Node breaks the server build.

## L5 — Verify scripted edits
Never read and write a file in one expression (`open(p,'w').write(open(p).read()+…)` empties it first). Read into a variable, write in a separate step. After any scripted edit of a tracked file, run `git diff --stat` and confirm only the intended lines changed.
*Why:* a translations file was once silently truncated this way.

## L6 — PR comment format
Ticket comment after a PR, exactly:
```
PR: <PR or MR link>

Description:
- <bullets, same as the PR's description>
```
No heading or extra sections. Show it, post only after OK.

## L7 — Don't trust tracker claims about tests
Before relying on "tests exist / pass" in PROGRESS.md or log.md, open the actual test file and run it.
*Why:* a claimed test suite once turned out to be an empty stub.

## L8 — Confirm the root cause for bugs
The obvious symptom can sit one function away from the real defect. Reproduce, then trace to the cause with real data on the test site before proposing a fix. Look for dead parameters and unused filters.

## L9 — Teach the frontend framework
The user is learning Vue. For Vue / frontend tasks, include a short concept primer, an alternatives table with the reason for the choice, a best-practice checklist and a small "try this" exercise. Keep Python/Frappe explanations brief.

## L10 — Scope change mid-flow
When the user drops or changes scope: log it in `docs/log.md`, revert cleanly (revert commits, don't rewrite shared history), and ask for the new scope. Don't resume old tasks. List leftovers (test-site data, options in DB) in PROGRESS.md.

## L11 — Track deferred items
Every deferred test, open question or follow-up candidate goes into the "Deferred / Open" section of PROGRESS.md with its source, so it survives between sessions.

## L12 — Scheduler before scheduled-job tests (Frappe)
Before testing anything that runs from the scheduler, check `bench --site <site> scheduler status` (or `bench doctor`). Schedulers have been found disabled before.

## L13 — Never commit the tracker
The tracker lives in `{workspace}/issue/`. Before every commit, check nothing under `issue/` is staged in the app repo.
