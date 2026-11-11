# GitLab mechanics (git.phamos.eu)

Tools come from the `git_phamos_eu` MCP server. Load them with ToolSearch (`select:...`) before the first call. Project: `{ticket_project}` from `issue/PROJECT.md`.

## Read the ticket

- `get_work_item` with `url` (or `work_item_iid` + `project_id: "{ticket_project}"`): title, description, labels, parent.
- Comments: same call with `include: ["discussions"]`, `discussions_filter: "only_comments"`. Paginate with `discussions_after` while `pageInfo.hasNextPage`.

## Post a comment

`save_note` with `url` (or `work_item_iid` + `project_id`) and `body`.
- Reply in a thread: add `discussion_id` (`gid://gitlab/Discussion/<id>`).
- `save_note` **cannot edit** an existing note. Doc changes are therefore always new replies.
- **Quick-action guard:** a body with a line starting with `/` is rejected. Before posting, put such lines in a code block or prefix them with a space or backtick (e.g. `` `/api/method/...` ``). Check every line, including inside `<details>`.

## Doc threads

| Key | Local file |
|---|---|
| `requirements` | `docs/requirements.md` |
| `exploration` | `docs/exploration_report.md` |
| `design` | `docs/design_first.md` |

## Find a thread after posting v1

`save_note` may not return the discussion id. After posting v1, read discussions (`include: ["discussions"]`, `only_comments`) and pick the thread whose **first note** begins with `<!-- phamos-forge:[key] v1 -->`. Store its id in PROGRESS.md under `Threads`.

If PROGRESS.md has lost an id, find it the same way.

## Rebuild a doc from its thread

Run on every resume, for each thread listed in PROGRESS.md. The ticket is canonical.

1. Read the thread's notes in order.
2. Keep only notes that begin with `<!-- phamos-forge:[key] v` and parse the version number. Notes without the marker (hand-written replies) are **not applied**: list them to the user as "unprocessed comments in the [key] thread" and ask whether to fold them in as a new version.
3. Start from v1's body inside `<details>`: the header lines, then `## ` sections.
4. For each later version in order: for each `## ` section inside its `<details>`, replace the section with the same heading, or append it if it's new. A section whose body is `_Removed._` is deleted.
5. Set the header's `Thread:` value to the last version. Write the result to the local file. If it differs from the local file, show the diff to the user; the ticket version wins. If the local file has unposted changes, tell the user and offer to post them as the next reply.

## Status labels

Change labels **only when the user asks**. Use `save_work_item` with `work_item_iid` + `project_id`, `add_labels` and `remove_labels` in **one call**, so there is only ever one status label.

| Moment | Status label | Marker |
|---|---|---|
| Phase 1 starts | `Working` | `Discussion` (while questions are open) |
| A review finding needs the user's decision | `PM Review` | |
| Merged to `{base_branch}`, user tests | `Testing` | |
| User's OK | `Ready for Production` | |
| On production, user checks | `Testing on Production` | |

Status labels (remove the old one when setting a new one): `Working`, `Ready for Dev`, `PM Review`, `Testing`, `Ready for Production`, `Testing on Production`.
Markers that sit next to a status: `Discussion`, priority (`P.1`–`P.3`), `On hold`.
Leave every other label on the project alone.

Label names differ slightly between projects (e.g. `P.1` vs `P:1`, `On hold` vs `On Hold`). Before the first label change in a project, list them with `search_labels` (`full_path: "{ticket_project}"`, `is_project: true`) and use the exact names. If a status label doesn't exist, tell the user; don't create it.
