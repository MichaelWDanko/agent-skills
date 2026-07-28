---
name: agent-project-creation
description: Create a dedicated agent project under ~/Projects/agent-NAME for a cron-driven or automation-heavy workflow, including scripts, inputs, state handling, repository hygiene, and a public-GitHub security review. Use when a recurring workflow starts accumulating cron jobs, helper scripts, prompt files, sample inputs, local data stores, or other artifacts that should live together as one reusable agent project.
---

# Agent Project Creation

## Overview

Use this skill when a workflow is more than just a one-off cron job or prompt.

If the work includes any combination of:
- one or more cron jobs
- helper scripts
- prompt files or templates
- sample inputs
- local state or cache files
- small data stores or exported artifacts

then package it as an agent project in `~/Projects/agent-<name>/`.

Treat the agent project as the durable home for everything needed to understand, run, review, and safely publish that automation.

## Naming and placement

1. Create the project in `~/Projects/`.
2. Prefix the directory with `agent-`.
3. Pick a concise name based on the workflow, not the current implementation detail.

Examples:
- `~/Projects/agent-meeting-detection/`
- `~/Projects/agent-daily-briefing/`
- `~/Projects/agent-inbox-triage/`

## Default project contents

Start with a structure like this and trim as needed:

```text
~/Projects/agent-<name>/
├── README.md
├── .gitignore
├── prompts/
├── scripts/
├── inputs/
├── outputs/
├── state/
├── data/
└── docs/
```

Not every folder is required.

Use them intentionally:
- `prompts/` for cron prompts, system prompts, and reusable instructions
- `scripts/` for helper scripts and glue code
- `inputs/` for checked-in example inputs or schemas
- `outputs/` for generated artifacts that may be ignored or only partially tracked
- `state/` for short-lived runtime state, cursors, caches, locks, or sync markers
- `data/` for small local stores or seed datasets
- `docs/` for architecture notes, setup docs, and operational runbooks

## Workflow

### 1. Decide whether this should become an agent project

Bundle the work into `~/Projects/agent-<name>/` if any of these are true:
- the cron job depends on local files
- the workflow has multiple scripts or prompts
- the automation has runtime state that persists between runs
- there is enough complexity that another machine or future you would need setup instructions
- the automation may eventually be pushed to GitHub

If it is only a single self-contained cron prompt with no supporting files, a standalone cron job may be enough.

### 2. Create a minimal but explicit layout

Create only the directories the workflow actually needs. Do not create empty structure just for appearance.

At minimum, aim to include:
- `README.md` explaining what the agent does
- `scripts/` if any helper code exists
- `prompts/` if the cron prompt or reusable instructions are non-trivial
- `.gitignore` if any generated or short-term state will exist

### 3. Move the workflow artifacts into the project

Gather and colocate:
- cron prompts
- helper scripts
- input schemas or examples
- local data files that are safe to commit
- configuration examples without secrets
- notes describing external dependencies and schedules

Avoid scattering workflow assets across home-directory scratch paths.

### 4. Write a useful README

The README should let someone understand and review the project quickly.

Include:
- purpose of the agent
- main trigger mechanism such as cron, manual run, or both
- directory layout
- setup steps
- required external services or APIs
- where state lives
- which files are intentionally ignored
- how to run or test locally
- security considerations if the repo is shared publicly

### 5. Add `.gitignore` when short-term state exists

If the workflow writes any runtime or temporary files, add a `.gitignore` immediately.

Common candidates to ignore:
- `state/`
- `outputs/` if outputs are ephemeral or large
- `data/*.db`
- `data/*.sqlite`
- `*.log`
- `.env`
- temporary exports
- caches
- lock files created only at runtime

Use a targeted `.gitignore`, not a lazy catch-all that hides important source files.

Load `templates/common-agent.gitignore` for a starting point, then trim it to fit the project.

### 6. Review public-GitHub safety before calling it done

Assume the repo may become public later, even if it is private today.

Check for:
- embedded API keys, tokens, cookies, session material, or webhook secrets
- checked-in `.env` files or credential JSON
- hardcoded local machine paths that reveal too much or break portability
- sample inputs containing private customer data, transcripts, or personal notes
- output artifacts containing PII or internal-only analysis
- scripts that fetch remote code without pinning or verification
- dangerous shell usage with unsanitized user input
- accidental inclusion of caches, SQLite files, or local state snapshots
- prompts that contain private URLs, IDs, or internal documentation excerpts not meant for publication

If something sensitive is needed for setup, document it in README as a required environment variable or local file, and keep only a redacted example in the repo.

### 7. Sanity check the implementation surface

Before finishing, review whether the automation introduces avoidable risk:
- Does the cron run with broader permissions than necessary?
- Are file writes scoped to the project directory or an intentional destination?
- Are state files clearly separated from committed source?
- Are scripts idempotent or at least safe to rerun?
- Is failure behavior documented?
- Is there a straightforward way to inspect or reset state?

### 8. Save reusable project-building knowledge as a skill

If the workflow produced a repeatable pattern, add or update a skill in:
- `~/Projects/agent-skills/skills/`, or
- `~/Projects/pp-agent-skills/skills/`

Choose the category based on the workflow domain, not where you happened to build it.

## Output requirements

When using this skill, the final result should usually include:
- the chosen `agent-<name>` project path
- a short summary of the folders and files created
- whether `.gitignore` was added and what classes of files it ignores
- the main public-repo security risks reviewed
- any follow-up needed before pushing to GitHub

## Checklist

Before closing the task, verify:
- the project lives under `~/Projects/agent-<name>/`
- cron prompts, scripts, and local data are no longer scattered
- `README.md` explains purpose, setup, and state handling
- `.gitignore` exists if runtime state or generated files exist
- no secrets or sensitive data were committed
- the repo would not obviously leak credentials or private data if pushed public
- any reusable workflow knowledge was saved under `agent-skills/skills` or `pp-agent-skills/skills`

## Templates

- Start from `templates/common-agent.gitignore` when the project has runtime state, logs, caches, SQLite files, or generated outputs.
