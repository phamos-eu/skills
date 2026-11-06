---
name: write-frappe-tests
description: "Write automated tests for a Frappe/ERPNext app: plan the cases from the code under test, write them in the app's existing test style, run them with bench run-tests, and prove each test can fail. Use when the user asks to add, write, generate or fix tests for a DocType, controller, API method, hook, patch or scheduled job in a Frappe app, or when an MR is blocked because it has no tests."
argument-hint: "What should be tested? (a DocType, a file, a function, or 'the changes on this branch')"
---

# Write Frappe Tests

Write tests that would catch a real regression in a Frappe app, not tests that only raise coverage.

A good test here:
- **Fails when the behavior breaks** — proven by breaking the code once (Step 6)
- **Runs on a fresh test site** — creates the records it needs, assumes nothing else is there
- **Is isolated** — passes alone, in any order, and twice in a row
- **Reads like a requirement** — the test name states the behavior: `test_sync_skips_a_reconciled_bank_transaction`, not `test_sync_2`

Frappe's test API differs between v15 and v16. Before writing any code, read [references/frappe-testing.md](references/frappe-testing.md) and confirm every helper you use exists in the bench's `apps/frappe`.

---

## Step 1 — Find the Target

Determine what to test:

| User input | Target |
|---|---|
| A DocType, file or function | That code |
| "The changes on this branch" / an MR | Every changed `.py` file outside test files: `git diff --name-only <base>...HEAD` |
| A failing or missing test reported by CI | The module CI named |

Then find, by reading the project (do not ask):
- **App name and Frappe version:** `apps/frappe/frappe/__init__.py` (`__version__`), or the app's `pyproject.toml` / `hooks.py` `required_apps`.
- **The site to run tests on.** Look for a test site in the bench (`sites/*/site_config.json` with `allow_tests`). If there is none, ask the user which site to use. **Never run tests on a site that holds real or shared data:** tests insert, change and sometimes commit records.
- **Existing tests:** `test_*.py` next to DocTypes and in `<app>/tests/`. Note the base class, fixture helpers, naming and how external services are mocked. The new tests follow these conventions, even where this skill suggests otherwise.
- **The app's `before_tests` hook** in `hooks.py`, if any: it creates master data every test run can rely on.
- **CI test lists:** if the repo's CI config lists test modules explicitly (for example a `TEST_MODULES` or `SHARD_MODULES` variable in `.gitlab-ci.yml`), a new test module must be added there or CI won't run it.

---

## Step 2 — Read the Code Under Test

For each target, read the code and list its **behaviors**: what a caller or user can observe. Look for:

- **Validation** — every `frappe.throw` and the condition that raises it
- **Side effects** — documents created, updated, cancelled or deleted; fields set on save or submit; emails or notifications queued
- **Permissions** — `has_permission` hooks, `frappe.only_for`, role checks, `ignore_permissions`
- **Branches** — every `if` that changes the outcome, including early returns
- **Hooks wiring** — `doc_events`, `scheduler_events`, `after_migrate`, `override_whitelisted_methods` entries that point at this code
- **External calls** — HTTP clients, `frappe.enqueue`, `frappe.sendmail`, file access
- **Time** — `nowdate()`, `now_datetime()`, `getdate()` defaults, time zones

If a behavior is unclear from the code, ask the user one question at a time. Do not guess the intended behavior from the implementation: a test that encodes a bug protects the bug.

---

## Step 3 — Plan the Cases

Present a test plan before writing code:

| # | Test name | Arrange | Act | Assert |
|---|---|---|---|---|
| 1 | `test_submit_creates_a_bank_transaction` | Settings with a bank account | Submit the import | One Bank Transaction linked to the import |
| 2 | `test_submit_without_bank_account_is_refused` | Settings without a bank account | Submit | `frappe.ValidationError` with the message |

Cover, for each behavior:
1. The main success path
2. Each validation error (`assertRaises` the specific exception, not `Exception`)
3. Each permission rule: one user who may, one who may not
4. Boundaries: empty values, zero amounts, the first/last day of a period, duplicates
5. Idempotency where the code claims it (running twice gives the same result)

Mark which cases need mocks (external calls, time) and which need test records.

**Wait for the user to approve the plan.** If the user asked for speed ("just write them"), state the plan briefly and continue.

---

## Step 4 — Write the Tests

Location:
- DocType behavior → `<app>/<module>/doctype/<doctype>/test_<doctype>.py`
- API methods, hooks, jobs, patches, cross-DocType flows → `<app>/tests/test_<topic>.py` (create `<app>/tests/__init__.py` if missing)

Rules:
- **Use the base class the app already uses.** None yet → the one for the bench's Frappe version (see the reference).
- **Create what the test needs in the test.** Use small helper functions (`make_settings(**overrides)`) instead of large JSON fixtures. Use unique names (`frappe.generate_hash(length=8)`) so a rerun can't collide. The database is rolled back once per test class, not per test method, so records from one test are visible to the next.
- **Never depend on existing site data** beyond what `before_tests` and the app's install create.
- **Mock every external call** with `unittest.mock.patch`, at the place the code looks it up (`patch("myapp.api.client.requests.get")`, not `patch("requests.get")`). No test may reach the internet.
- **Freeze time** for anything date-dependent, with the helper the bench offers or by patching the date function the code imports.
- **Assert on outcomes** — database state (`frappe.db.get_value`, `frappe.get_doc(...).reload()`), return values, raised exceptions and their messages. Not on private helpers or the number of SQL queries, unless that is the requirement.
- **Permissions:** create a user with exactly the roles needed, switch to it, and switch back in `tearDown` or with `addCleanup`. Never leave the session as another user.
- **Commits:** if the code under test calls `frappe.db.commit()`, the base class's rollback can't undo it. Delete what the test created in `addCleanup`, or patch the commit, and say so in a comment.
- **No `time.sleep`, no `print`, no `try/except` around assertions.**
- Match the app's formatting (tabs or spaces, quote style) and run its formatter if `.pre-commit-config.yaml` defines one.

---

## Step 5 — Run the Tests

Run only the new module first:

```bash
bench --site <test-site> run-tests --app <app> --module <app>.tests.test_<topic>
```

For one DocType: `--doctype "<DocType Name>"`. For one test: add `--test <test_method_name>`.

Then:
1. Run the module a **second time** — it must pass again (catches leftover data and name collisions).
2. Run the **whole app** once: `bench --site <test-site> run-tests --app <app>` — the new tests must not break others.

If a test fails, decide whether the **test** or the **code** is wrong. Fix the test only when the test is wrong. When the code is wrong, stop and report it to the user with the failing assertion; do not change production code unless asked.

---

## Step 6 — Prove the Tests Can Fail

For each behavior, break the code once and confirm at least one test fails:
- Invert or remove the condition behind a `frappe.throw`
- Skip the line that creates or updates the side-effect document
- Remove the role check

Run the affected tests, confirm the failure names the broken behavior, then **restore the code exactly** (`git diff` must show no change outside test files). A test that still passes against broken code is rewritten or deleted.

---

## Failure Handling

| Failure | Response |
|---|---|
| No site with `allow_tests`, user unsure | Explain the risk, ask the user to create one (`bench new-site`, install the app, `bench --site <site> set-config allow_tests true`). Do not run tests on another site. |
| Import or setup error before any test runs | Check the base class and helpers against the reference and the bench's Frappe version. |
| Test passes alone, fails in the full run | Shared state: a leftover record, a changed setting, the session user, a cached value. Fix the isolation, not the order. |
| Test depends on master data that isn't there (UOM, Company, Fiscal Year) | Create it in the test, or check whether `before_tests` should create it and ask the user. |
| The code under test is wrong | Report it with the failing assertion. Do not "fix" the test to match the bug. |
| A behavior can't be tested without a large refactor | Say so, test what can be tested, and list the gap. |

---

## Completion Criteria

The task is complete when:

- ✓ Every behavior from Step 2 has at least one test, or is listed as a gap with the reason
- ✓ The new tests pass twice in a row on the test site
- ✓ The whole app's test suite passes
- ✓ Each behavior was broken once and a test failed (Step 6), and the code was restored
- ✓ No change outside test files, except a CI test list that needed the new module
- ✓ No network access, `sleep`, or reliance on existing site data in the tests

---

## Output to User

1. **Tests added** — file paths and test names, grouped by behavior
2. **How to run them** — the exact `bench run-tests` command
3. **Proof** — which code change made which test fail in Step 6
4. **Gaps and findings** — behaviors not covered and why; any bug found in the code under test
5. **CI** — whether a CI test list was updated
