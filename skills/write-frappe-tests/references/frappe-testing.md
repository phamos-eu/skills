# Frappe Testing Reference (v15 and v16)

Checked against `frappe/frappe` branches `version-15` and `version-16`. When in doubt, read the bench's own copy: `apps/frappe/frappe/tests/`.

## Which Version?

```bash
grep __version__ apps/frappe/frappe/__init__.py
```

## Base Classes and Helpers

| | Frappe v15 | Frappe v16 |
|---|---|---|
| Import | `from frappe.tests.utils import FrappeTestCase, change_settings` | `from frappe.tests import IntegrationTestCase, UnitTestCase, change_settings` |
| Tests that touch the database | `FrappeTestCase` | `IntegrationTestCase` |
| Pure logic, no database | `FrappeTestCase` (or `unittest.TestCase`) | `UnitTestCase` |
| `FrappeTestCase` | — | Still importable from `frappe.tests.utils`, deprecated |
| Run as another user | `with self.set_user("x@example.com"):` | same |
| Freeze time (needs `freezegun`) | `with self.freeze_time("2026-01-31 10:00"):` | same; `is_utc=True` for a UTC value |
| Change a Single DocType's settings for one test | `@change_settings("Stock Settings", {"allow_negative_stock": 1})` or `with change_settings(...)` | same |
| Mock HTTP with `responses` | `MockedRequestTestCase` (`self.responses`) | same, from `frappe.tests` |
| Compare a document | `self.assertDocumentEqual({"status": "Paid"}, doc)` | same |
| Count queries | `with self.assertQueryCount(5):` | same |

The time given to `freeze_time` is read in the **system time zone** (System Settings), not UTC.

## What Gets Rolled Back

Both versions **commit before the class starts** and **roll back once, after the whole test class**. There is no rollback between test methods of the same class.

Consequences:
- Records created in one test method are visible to the next. Give records unique names, or clean up with `self.addCleanup(...)`.
- Anything the code under test commits (`frappe.db.commit()`, background jobs run inline, `change_settings(..., commit=True)`) survives the rollback. Delete it in `addCleanup`.
- `setUpClass` overrides must call `super().setUpClass()` first, or none of this happens.

## Test Records

Frappe can create standard records for DocTypes your test depends on.

| | v15 | v16 |
|---|---|---|
| Records file next to the DocType | `test_records.json` | `test_records.json` or `test_records.toml` |
| Extra DocTypes to create records for | `test_dependencies = ["Item", "Customer"]` (module level) | `EXTRA_TEST_RECORD_DEPENDENCIES = [...]` (`test_dependencies` still works, with a deprecation warning) |
| DocTypes to skip | `test_ignore = [...]` | `IGNORE_TEST_RECORD_DEPENDENCIES = [...]` (doctype folders only) |

ERPNext test records (`_Test Company`, `_Test Item`, ...) are large and slow. Prefer creating the few records a test needs in the test. Use them only when the app's existing tests already do.

## `before_tests` Hook

```python
# hooks.py
before_tests = "myapp.install.before_tests"
```

`bench run-tests --app myapp` runs the `before_tests` hooks **of that app only**, once per `run-tests` call. ERPNext's own setup (company, fiscal year) does not run unless the app's hook calls it. Skip the hook with `--skip-before-tests`.

## Running Tests

```bash
bench --site <site> run-tests --app <app>                                # whole app
bench --site <site> run-tests --app <app> --module <app>.tests.test_x    # one module
bench --site <site> run-tests --app <app> --doctype "Sales Invoice"      # one DocType's tests
bench --site <site> run-tests --app <app> --module <app>.tests.test_x --test test_name
bench --site <site> run-tests --app <app> --junit-xml-output report.xml  # for CI
```

The site needs `allow_tests` (`bench --site <site> set-config allow_tests true`), or the `CI` environment variable set.

## Patterns

**A DocType test (v16):**

```python
import frappe
from frappe.tests import IntegrationTestCase


def make_settings(**overrides):
	settings = frappe.get_single("Bank Sync Settings")
	settings.update({"enabled": 1, **overrides})
	settings.save()
	return settings


class TestBankImport(IntegrationTestCase):
	def test_submit_without_bank_account_is_refused(self):
		make_settings(bank_account=None)
		doc = frappe.get_doc({"doctype": "Bank Import", "from_date": "2026-01-01"})
		with self.assertRaisesRegex(frappe.ValidationError, "Bank Account"):
			doc.insert()
```

For v15, import `FrappeTestCase` from `frappe.tests.utils` and inherit from it instead.

**Mocking an external client** — patch where the code looks it up:

```python
from unittest.mock import patch

with patch("myapp.integrations.client.requests.get") as get:
	get.return_value.json.return_value = {"items": []}
	get.return_value.status_code = 200
	run_sync()
get.assert_called_once()
```

**Permissions:**

```python
def make_user(roles):
	email = f"{frappe.generate_hash(length=8)}@example.com"
	user = frappe.get_doc(
		{"doctype": "User", "email": email, "first_name": "Test", "send_welcome_email": 0}
	).insert()
	user.add_roles(*roles)
	return email

def test_accounts_user_cannot_run_the_sync(self):
	with self.set_user(make_user(["Accounts User"])):
		with self.assertRaises(frappe.PermissionError):
			run_sync()
```

**A whitelisted API method:** call the Python function directly with the arguments the client would send. Test permission checks inside it with `set_user`, as above.

**A scheduled job:** call the function from `scheduler_events` directly. Assert that the hook entry exists if wiring matters: `self.assertIn("myapp.tasks.daily", frappe.get_hooks("scheduler_events")["daily"])`.

**A patch:** set up the old data shape, call `execute()`, assert the new shape, and call it again to show it is idempotent.
