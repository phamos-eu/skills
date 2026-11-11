#!/usr/bin/env python3
"""Resolve phamos-forge project settings.

Usage: python3 -I forge_config.py <workspace> [ticket_project]

Order (later wins):
  1. derived values (workspace, app_repo, app_name, app_module)
  2. `phamos_forge = {...}` in apps/<app>/<app>/hooks.py (read as a literal, Frappe not imported)
  3. the key/value table in <workspace>/issue/PROJECT.md (local, per developer)

App choice: the app whose hooks.py defines phamos_forge. If several do, the one whose
ticket_project matches the argument; else PROJECT.md's `app_repo`. Prints JSON.
"""
import ast
import json
import pathlib
import re
import sys


def literal(tree, name):
	for node in tree.body:
		if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
			try:
				return ast.literal_eval(node.value)
			except ValueError:
				return None
	return None


def read_profile(workspace):
	path = workspace / "issue" / "PROJECT.md"
	values = {}
	if path.exists():
		for line in path.read_text().splitlines():
			m = re.match(r"^\|\s*([a-z_]+)\s*\|\s*(.*?)\s*\|\s*$", line)
			if m and m.group(1) != "key" and not set(m.group(2)) <= {"-", " "}:
				values[m.group(1)] = m.group(2)
	return values


def main():
	workspace = pathlib.Path(sys.argv[1]).resolve()
	ticket_project = sys.argv[2] if len(sys.argv) > 2 else None
	profile = read_profile(workspace)

	candidates = []
	for hooks in sorted((workspace / "apps").glob("*/*/hooks.py")):
		if hooks.parent.name != hooks.parent.parent.name:
			continue
		tree = ast.parse(hooks.read_text())
		cfg = literal(tree, "phamos_forge")
		if isinstance(cfg, dict):
			candidates.append((hooks, tree, cfg))

	chosen = None
	if len(candidates) == 1:
		chosen = candidates[0]
	elif ticket_project:
		chosen = next((c for c in candidates if c[2].get("ticket_project") == ticket_project), None)
	if not chosen and profile.get("app_repo"):
		chosen = next((c for c in candidates if str(c[0].parent.parent.relative_to(workspace)) == profile["app_repo"]), None)

	result = {"workspace": str(workspace), "source": {}}
	if chosen:
		hooks, tree, cfg = chosen
		app_dir = hooks.parent.parent
		result.update({
			"app_name": literal(tree, "app_name"),
			"app_module": literal(tree, "app_title"),
			"app_repo": str(app_dir.relative_to(workspace)),
		})
		result.update(cfg)
		result["source"]["hooks"] = str(hooks.relative_to(workspace))
	else:
		result["candidates"] = [str(c[0].relative_to(workspace)) for c in candidates]

	if profile:
		result.update(profile)
		result["source"]["profile"] = "issue/PROJECT.md"

	required = ["app_repo", "ticket_project", "pr_host", "pr_repo", "base_branch", "test_site"]
	result["missing"] = [k for k in required if not result.get(k)]
	print(json.dumps(result, indent=2))


if __name__ == "__main__":
	main()
