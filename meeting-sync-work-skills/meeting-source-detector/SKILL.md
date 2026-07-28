---
name: meeting-source-detector
description: Detect usable meeting note sources across Google Calendar attachments, Google Docs, and Granola before creating canonical Bear meeting notes.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [meetings, Calendar, Google Docs, Granola, Bear, source-detection]
---

# Meeting source detector

Use this when building or running the meeting-ingestion workflow that decides whether a meeting has enough usable content to create or update a Bear note.

## When to use
- The user wants canonical meeting notes created only when usable content exists
- Google Calendar is the anchor record
- Sources may arrive late or have access issues
- Bear is the destination for canonical notes
- Granola is an optional enrichment source

## Core rule
Do not create a Bear note unless at least one source has usable content.

Usable content means one of:
- readable user-authored Google Doc notes attached to the calendar event
- readable Gemini notes attached to the calendar event
- matching Granola notes or transcript

If no usable content exists yet:
- do not create a Bear note
- keep rechecking later

If a note source is attached but inaccessible:
- do not create a Bear note yet
- notify the user, preferably via Telegram
- keep rechecking in case access is granted later

## Source model
Calendar is the anchor source. Everything else is optional enrichment.

Only process meetings where you either organized the meeting or your attendee record exists and your RSVP status is `accepted`.
If you organized the meeting, assume you will attend even when RSVP details are missing or not `accepted`.
Skip meetings you did not attend, did not accept, did not organize, or only tentatively planned to attend.

Track these source families per meeting:
- `calendar_event`
- `user_notes`
- `gemini_notes`
- `granola_notes`

Track each non-calendar source with one of:
- `usable`
- `inaccessible`
- `absent`

Recommended meeting-level states:
- `pending_content` — no usable content yet; keep polling
- `inaccessible_source` — a source exists but cannot be read; notify and retry
- `ready` — at least one usable source exists; safe to create/update Bear note
- `complete` — Bear note created and current sources ingested

## Detection rules

### 1. Calendar event
Use Google Calendar as the authoritative meeting record.
Capture at least:
- event id
- title
- start/end
- organizer
- attendees
- description
- attachments
- conference metadata

### 2. User-authored Google Doc notes
Look at Calendar event attachments.

Detect as user notes when:
- attachment mime type is `application/vnd.google-apps.document`
- attachment title is not `Notes by Gemini`

Then try to read the document body via the Docs API.
- If read succeeds and body has meaningful text, mark `user_notes=usable`
- If read fails with permission/file-not-found style errors, mark `user_notes=inaccessible`
- If no such attachment exists, mark `user_notes=absent`

### 3. Gemini notes
Look at Calendar event attachments.

Detect as Gemini notes when:
- attachment title is exactly `Notes by Gemini`

Then try to read the document body via the Docs API.
- If read succeeds, mark `gemini_notes=usable`
- If read fails with 403/404 or similar, mark `gemini_notes=inaccessible`
- If no Gemini attachment exists, mark `gemini_notes=absent`

Important finding: a Calendar event can expose a Gemini notes attachment even when the user does not actually have document access. Treat that as `inaccessible`, not as `absent`.

### 4. Granola notes
Query Granola separately by meeting title and time window.

- If Granola finds a matching meeting, mark `granola_notes=usable`
- If no matching meeting is found, mark `granola_notes=absent`

Do not assume Granola is the primary source. It is enrichment attached to the Calendar meeting record.

## Bear gating rule
Create or update a Bear note only when at least one of these is `usable`:
- `user_notes`
- `gemini_notes`
- `granola_notes`

Do not create a Bear note for:
- calendar-only meetings
- meetings with attached docs that are inaccessible
- meetings with no readable note source yet

## Notification rule
If a meeting has attached Google Docs notes but Hermes cannot read them:
- send a Telegram notification
- include meeting title, time, doc title, and access status
- keep retrying later

Example notification:
- `Passport 30 - OKR Edition`
- attached doc: `Notes by Gemini`
- status: access denied
- action: request access or open manually

## Retry guidance
Use a detector job that rechecks recently ended meetings.
Recommended MVP cadence:
- every 10 minutes
- look back 24 to 36 hours for a generic setup
- in this workflow, the detector was actually run with `--lookback-hours 72`

Why:
- user notes may be added after the meeting ends
- Gemini notes may appear later
- Granola may sync later
- doc permissions may be granted after the initial pass

Operational finding:
- for this local workflow, running `google_source_detector.py` directly was more reliable than relying on the cron `run` action to rebuild the state file immediately
- if you need a clean reset, deleting `state/meeting_sources.json` resets both Job 1 and Job 2 local state back to an empty starting point

Important implementation finding:
- a single `granola_status=absent` result should not be treated as permanent while `recheck_until` is still in the future
- track `granola_checked_at` separately from the Google detection timestamp
- allow meetings with non-usable Granola status to become candidates again after a cooldown window such as 120 minutes
- only stop rechecking once `recheck_until` has passed
- for Granola content drift, store a normalized SHA-256 hash of the note body as `granola_content_hash`
- Granola change detection is hash-only once a note has been processed; do not rely on timestamps for freshness
- when a meeting already has a Bear note, compare the current Granola hash to the stored Bear-side hash to decide whether an update is needed
- if the Granola hash is missing in state, treat it as not yet processed rather than falling back to a timestamp comparison
- when applying `state_tools.py` commands from automation, pass arguments as an argv list or otherwise shell-escape titles and URLs carefully; unescaped `&` in titles will break shell execution and can silently skip Granola state updates
- for Granola matching, use `granola list_meetings` as the canonical candidate source when available, then apply confident matches back into local state; `query_granola_meetings` is useful for spot checks but may not have enough context alone
- if a Granola meeting id is available, use it directly; if only the meeting page id is available, `https://notes.granola.ai/d/<meeting_id>` was a workable fallback URL for `apply-granola-match`

## Output shape
Per meeting, store at least:
- `event_id`
- `title`
- `start`
- `end`
- `sources.user_notes.status`
- `sources.gemini_notes.status`
- `sources.granola_notes.status`
- `state`
- `last_checked_at`
- `last_notified_at`
- `bear_note_id` if created

Strongly recommended fields from real implementation work:
- `granola_status`
- `granola_match`
- `granola_checked_at`
- `recheck_until`
- `notifications.telegram_inaccessible_sent_at`
- `notifications.telegram_inaccessible_last_source_ids`

Why these matter:
- `granola_checked_at` prevents checking the same meeting every run while still allowing later retries
- `telegram_inaccessible_last_source_ids` lets you re-notify only when the inaccessible doc set changes
- preserving these fields across detector reruns avoids losing enrichment work done after the Google scan

Optional but useful:
- doc file ids and titles
- content hashes or modified times
- Granola meeting id

## Known real-world examples
Use these examples to sanity-check the detector logic:

- `Test Meeting - Hermes`
  - user-authored Google Doc notes attached
  - no Granola
  - should become `ready`

- `Passport 30 - OKR Edition`
  - Gemini notes attachment detected
  - attachment may be inaccessible to the user
  - should become `inaccessible_source` until access works

- `Kristie / Michael: Intercom Ticket Analysis`
  - Granola notes available
  - should become `ready`

- `Engineering Cross-Product Arch & Design Workgroup (AM Session)`
  - no Granola, no Gemini, no user notes
  - should remain `pending_content`

## Implementation notes
- Keep Google OAuth scopes least-privilege by default
- Calendar/Drive/Docs read-only is enough for detection
- If you narrow OAuth scopes, keep both Google scripts in sync or you can hit `invalid_scope`
- For Bear output, pair this skill with `bear-meeting-note`

## Recommended architecture
Use two cron jobs:
1. detector/state updater
2. Bear ingester

Detector job responsibilities:
- scan recently ended meetings
- update source statuses and meeting state
- notify on inaccessible docs

Ingester job responsibilities:
- process meetings in `ready`
- create or update canonical Bear notes
- write Bear sync metadata back into local state

A practical state shape for the ingester job is:
- `bear_status` — `not_created`, `created`, or `updated`
- `bear_note` — object with note identifier, title, tags, source kind, and synced timestamp
- `bear_synced_at` — last successful Bear sync time

Important implementation finding:
- when the detector refreshes Google-derived data, it must preserve `bear_status`, `bear_note`, and `bear_synced_at`
- it should also preserve or recompute `source_last_modified_at` from the freshest source timestamp available
- otherwise Job 2 work is lost on the next detector run
- this preservation should happen in the detector's merge step, not as a later repair

## Practical implementation pattern that worked
For Job 1, do not have the agent hand-edit the entire JSON state file on each run.
Use a small local helper CLI with explicit commands instead.

A reusable pattern is:
- detector script writes or refreshes the Google-derived meeting state
- helper script exposes stable operations such as:
  - `summary`
  - `list-granola-candidates`
  - `apply-granola-match`
  - `mark-granola-absent`
  - `list-inaccessible-notifications`
  - `mark-inaccessible-notified`
  - `list-bear-candidates`
  - `mark-bear-created`
  - `mark-bear-updated`
- Hermes uses Granola MCP to decide matches, then calls those helper commands to mutate state safely
- Hermes uses Bear MCP to create or update notes for meetings returned by `list-bear-candidates`, then records the outcome with `mark-bear-created` or `mark-bear-updated`

Benefits:
- avoids fragile whole-file JSON rewrites by the agent
- preserves enrichment metadata across detector reruns
- makes cron prompts shorter and more reliable
- gives you small, testable units for state transitions

Naming guidance from real use:
- if the project directory already encodes the agent/job scope, avoid repeating that scope in filenames
- for example, inside `agent-meeting-detection/`, prefer names like `state_tools.py`, `hermes-enricher-prompt.md`, and `test_state_tools.py`
- avoid redundant names like `job1_state_tools.py` unless there is a genuine collision risk

Important environment findings:
- use the same Python 3.10+ interpreter or venv for both detector and helper scripts
- on this workflow, the Google workspace venv was the reliable choice because macOS system Python 3.9 failed on `str | None` syntax used by the scripts
- when testing live Granola MCP access through Hermes on this machine, the working Hermes runtime was `~/.hermes/hermes-agent/venv`
- calling `python ~/Projects/hermes-agent/hermes_cli/main.py ...` with system Python failed because Hermes dependencies like PyYAML were not installed there
- for one-off live validation, activate the Hermes runtime first, for example:
  - `source ~/.hermes/hermes-agent/venv/bin/activate`
  - `python ~/Projects/hermes-agent/hermes_cli/main.py mcp test granola`
  - `python ~/Projects/hermes-agent/hermes_cli/main.py chat -Q --source tool -q "...workflow prompt..."`
- practical Granola validation pattern that worked for Job 1:
  1. run `hermes mcp test granola` first to confirm OAuth is still valid and to see the exact discovered tool names
  2. if `mcporter` is unavailable in the runtime environment, for example because `npx` is not on PATH in cron, use Hermes itself as the MCP caller instead of trying to install or reconfigure Node mid-run
  3. use `hermes chat -Q --source tool -q "..."` to call Granola MCP tools indirectly when you need title/time matching from a cron-style workflow
  4. when the prompt contains nested quotes or JSON examples, build the shell command with a safe quoting helper such as Python `shlex.quote` or Hermes `shell_quote` rather than hand-quoting the prompt in bash
  5. ask for strict JSON output and be prepared to extract the JSON payload from the response, because quiet mode can still include Hermes framing such as tool preview lines, response panels, and a trailing `session_id:` line in some environments
  6. if you need to persist a Granola match URL for `apply-granola-match`, first try to fetch meeting details directly; if the MCP result omits a URL but provides a meeting id, using `https://notes.granola.ai/d/<meeting_id>` was a working fallback for this workflow
  7. when there are many Granola candidates, it is practical to batch them into a single Hermes tool-mode prompt instead of running one lookup per meeting; provide the candidate list, ask for strict JSON, and require `match`, `absent`, or `unknown` decisions with a confidence field and brief reason for each event
  8. after a batched Granola evaluation, persist only the `high` confidence `match` or `absent` decisions through `apply-granola-match` and `mark-granola-absent`; leave `medium` or `low` confidence items unchanged so they remain eligible for later rechecks
  9. only write Job 1 state changes for confident outcomes; if the Granola result is merely semantically similar but attendee or timing evidence conflicts, leave it unknown or mark absent only when the mismatch is strong
  10. a confident Granola match does not require an exact title match when stronger evidence exists: same-day timing, near-time start, high attendee overlap, and meeting content that clearly aligns with the calendar event can be enough to apply `apply-granola-match`
  11. for recurring meetings, if Granola only shows the previous day's exact-title occurrence and same-day coverage appears incomplete or delayed, do not mark the current day's candidate absent yet; keep it recheckable until same-day absence is actually well supported
- when using cronjob action=run for Job 1, do not assume the state file updates immediately from the tool response alone; verify with the underlying detector output or by re-reading `state/meeting_sources.json`
- if a scheduled run is delayed or the cron wrapper only returns a job record, the live Telegram message can still arrive later and reflect the actual state update
- for manual testing of Job 1, run the detector command directly instead of relying on cronjob run as a synchronous execution primitive:
  - `~/.hermes/venvs/google-workspace/bin/python ~/Projects/agent-meeting-notes-sync/scripts/google_source_detector.py --lookback-hours 72`
- after a successful detector run, confirm with `state_tools.py summary`; that is the authoritative check for whether the state file was updated
- if Bear MCP reports `missing executable 'node'` during a Job 1 test, that does not block Granola-only validation, but it should be fixed before building or testing Job 2 Bear note creation
- when a Google Doc read hangs or is unexpectedly slow, set an explicit HTTP timeout on the Google client, retry a couple of times, and treat a final timeout as `inaccessible` rather than letting the whole detector block or fail
- if the project directory is renamed, update every hardcoded default path in the local scripts and docs at the same time
- in particular, the detector and helper CLI may each define `DEFAULT_STATE_PATH` internally; if those still point at the old repo name, commands can appear to work but will read/write a different empty state file
- also update user-facing documentation and operator prompts that embed the old repo path, especially `README.md` and the Hermes enrichment prompt file
- a quick sanity check after any rename is: run the helper `summary` command and compare its meeting count to the actual `state/meeting_sources.json` in the renamed repo
- if `summary` shows `0` meetings while the state file clearly has records, you almost certainly have a stale hardcoded path problem rather than missing meeting data
- a good validation pass after the rename is:
  1. run `state_tools.py summary` and confirm nonzero meeting counts
  2. run `google_source_detector.py --lookback-hours 24` and verify the printed `state_path` points at the renamed repo
  3. run `state_tools.py summary` again to confirm the state is still coherent
  4. run `pytest tests/test_state_tools.py -q`
- on this machine, the Google workspace venv was sufficient for detector/helper commands but did not include `pytest`; the Hermes runtime venv was the reliable fallback for running the project tests
- when `pytest` is unavailable in the workspace venv, use `python -m unittest tests.test_state_tools -q` for a quick regression check instead of assuming the test suite is broken
- if `google_source_detector.py` throws a `NameError` for a helper such as `parse_iso`, treat that as a code drift / stale-file issue in the detector itself and verify the current script before blaming Google APIs or credentials
