# Design: #[iid] [Title]

Ticket: [ticket link] (parent #[parent iid]) · Mode: Full · Status: [draft | approved YYYY-MM-DD] · Thread: [v1 | v[n]]

Builds on `requirements.md`, `exploration_report.md` and log #[n]–#[m]. Paths are relative to `[app_repo]/` unless stated otherwise.

## Overview
[What gets built, in a few lines. The key decision in bold. Covers R[..].]

## Data Flow
[Trigger → steps → result. A short numbered list or a text diagram.]

## API Flow
[Whitelisted methods / endpoints: name, args, permission check, response, errors. "None." if no API change.]

## Database Changes
[New/changed doctypes and fields as a table (field, type, notes), patches, fixtures, Property Setters. "None." if no change.]

## Backend Changes
- `[path::function]`: [new / changed, what it does]

## Frontend Changes
- `[path]`: [what changes for the user. "None." if no change.]

## Permissions
[Who can read/write/run what; which user code runs as.]

## Validation Rules
- [rule]: [where it is checked, error message]

## Error Handling
- [failure]: [what happens: rollback, Error Log title, user message]

## Logging
[Error Log / Comment / log lines added. "None." if nothing.]

## Testing Strategy
- Automated (independent test agent): [what is covered, test file]
- Manual on `[test_site]`: [checks]

## Out of Scope
- [item] (log #[n])
