---
name: skill-optimizer
description: Restructure an existing skill into a lean dispatcher SKILL.md backed by on-demand reference docs, and add or update Codex-facing agents/openai.yaml metadata when optimizing skills. Use this skill whenever the user wants to optimize, modularize, slim down, refactor, or improve the structure of an existing skill, mentions a SKILL.md that is too long or loads too much context, wants progressive disclosure, wants to split a monolithic skill into separate reference docs, wants a skill to be more maintainable or shareable, or asks to add/check/fix OpenAI or Codex YAML metadata for an existing skill. For creating a brand new skill from scratch, or running eval and benchmark loops, use skill-creator instead.
---

# Skill Optimizer

## Overview

Use this skill to optimize a skill that already works. Most optimization work restructures an inefficient skill, usually a single large `SKILL.md` that carries every detail and so loads all of it on every invocation. A smaller optimization can add or fix Codex-facing `agents/openai.yaml` metadata without reworking the whole skill.

This skill changes how a skill's content is organized and loaded, not what the skill does. Behavior stays identical; the structure gets leaner.

For creating a net-new skill, running eval or benchmark loops, or tuning a description for trigger accuracy, use `skill-creator`. The two compose well: restructure here, then optionally validate with skill-creator's eval loop.

## Skill anatomy

A well-formed skill has this structure:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter — name and description required
│   └── Markdown instructions
├── agents/ (optional)
│   └── openai.yaml — Codex app UI metadata, invocation policy, and tool dependencies
└── Bundled resources (optional)
    ├── scripts/    — executable code for deterministic or repetitive tasks
    ├── references/ — docs loaded into context as needed
    └── assets/     — files used in output (templates, icons, fonts)
```

Skills load in three levels:
1. **Metadata** (name + description) — always in context, ~100 words
2. **SKILL.md body** — in context whenever the skill triggers; target under 500 lines
3. **Bundled resources** — loaded only when the agent explicitly reads them; no size limit

The optimization goal is to push task-specific detail from level 2 down to level 3, so the always-loaded surface stays small. The description field in frontmatter is the primary trigger mechanism — it should include both what the skill does and specific contexts that should activate it. When assessing or rewriting a description, make sure it covers the when, not just the what.

For Codex app presentation, `agents/openai.yaml` is the recognized metadata path. Root-level `openai.yaml` is not enough for Codex UI metadata. When optimizing an existing skill, treat `agents/openai.yaml` as a supported optimization target: add it if missing, update it if stale, and move any root-level OpenAI metadata into `agents/openai.yaml`.

---

## Principles

Understand the why behind each move so you can apply judgment rather than follow steps rotely.

- **Progressive disclosure.** `SKILL.md` is always in context once a skill triggers; reference docs load only when the agent reads them. Keep `SKILL.md` lean so every invocation pays a small fixed cost, and push task-specific detail down one level where it loads only when needed.
- **Lean dispatcher.** `SKILL.md` should hold only what every task needs (universal rules and conventions), a doc map that routes each task to the right reference doc, and compact workflows that point at docs instead of restating their content.
- **Single source of truth.** Each durable fact belongs in exactly one file. The same table or list copied into both `SKILL.md` and a reference doc will drift and waste tokens. Pick one home and replace the other copies with a pointer.
- **Task-scoped docs.** Group content by the task that needs it, so an agent loads only the relevant doc. Aim for one doc per coherent task or domain, not a doc per paragraph.
- **No project state.** Open-items lists, triage tables, "as of <date>" notes, and similar transient state go stale and force re-publishing the skill just to stay current. Drop them so the skill stays shareable as-is. The live system the skill operates on (the actual articles, tickets, code, dashboards) remains the system of record for state.
- **Codex UI metadata belongs in `agents/openai.yaml`.** Optimizing a skill should make it easier to select and invoke in Codex, not only leaner internally. Keep user-facing display metadata, default prompt text, invocation policy, and tool dependency declarations in `agents/openai.yaml`; do not put this file at the skill root.
- **Preserve identity and behavior.** Keep the frontmatter `name` (it must match the folder) and a working `description`. Every task the skill supported before must still be covered and route somewhere sensible.
- **Match conventions.** Mirror the repo's and the target skill's existing writing style and folder layout. Consistency matters more than any single convention.

## Workflow

### 0. Determine optimization scope

Default to checking Codex metadata as part of every optimization, even when the user did not explicitly ask about YAML files. If the user asks only to add, check, move, or fix OpenAI/Codex YAML metadata, run the metadata-only path: inspect `SKILL.md`, root-level `openai.yaml` if present, and `agents/openai.yaml` if present; then perform only Step 9 and the relevant verification checks. Do not restructure `SKILL.md` or split reference docs during a metadata-only pass unless the user asks for broader optimization.

Use the full workflow when the request is broad, such as optimizing, slimming down, modularizing, improving progressive disclosure, or reducing a large `SKILL.md`.

### 1. Audit the current skill

Read `SKILL.md` and every bundled file. Inventory each distinct piece of content and note which task or trigger it serves. As you go, flag three things:

- **Duplication**: any fact, table, or list that appears in more than one file.
- **Project state**: anything that will go stale, such as open items, status notes, triage decisions, or dated commentary.
- **Task-specific detail**: anything that only matters for one task and is currently inline in `SKILL.md`.
- **Codex metadata**: whether `agents/openai.yaml` exists, whether root-level `openai.yaml` exists, and whether display metadata still matches the skill.

### 2. Group content by task

Map the content to the tasks the skill handles. Each coherent group of task-specific content is a candidate reference doc. Universal rules and conventions stay in `SKILL.md`.

### 3. Design the target structure

A lean `SKILL.md` (rules + doc map + workflows) plus one reference doc per task group. Put reference docs in `references/` (see folder convention below). Only create a subfolder once there is content to put in it.

### 4. Resolve duplication

Give each fact a single home and replace every other copy with a one-line pointer to that home. Produce a short single-source-of-truth table so the change is reviewable: fact, new home, removed-from.

### 5. Strip project state

Move state to where it actually belongs, or drop it. Do not relocate it into another part of the skill. The skill should describe how to work, not track the current status of the work.

### 6. Rewrite SKILL.md as a dispatcher

Reduce `SKILL.md` to the universal rules, the doc map, and trimmed workflows. Each workflow entry should be one line that points at the relevant reference doc rather than repeating its content.

### 7. Write the reference docs

Make each doc self-contained for its task. Open with a one-line "load this when ..." so an agent can tell at a glance whether it needs the doc. Cross-reference sibling docs by filename where a task spans more than one.

### 8. Update cross-references

Confirm every pointer resolves: each doc named in `SKILL.md` exists, and each cross-reference between docs points at a real file.

### 9. Add or update Codex metadata

Check whether the skill has `agents/openai.yaml`.

- If it is missing, add it with a concise `interface.display_name`, `interface.short_description`, and `interface.default_prompt` that match the optimized skill.
- If a root-level `openai.yaml` exists, move or merge its useful contents into `agents/openai.yaml`, then remove the root-level file.
- If `agents/openai.yaml` already exists, update stale display text, default prompt text, invocation policy, or tool dependency declarations so they reflect the optimized skill.
- Keep core operating instructions in `SKILL.md`; `agents/openai.yaml` should be UI and integration metadata, not a second copy of the workflow.

### 10. Verify

Work through the checklist below.

## Folder convention

Recommend `references/`, which matches the common skill anatomy where `references/` holds docs loaded into context as needed. If the skill already uses `docs/` (or another name) for the same purpose, keep that. The rule is consistency within a skill, not a specific folder name.

## Doc map pattern

Turn an inline, everything-in-one-file `SKILL.md` into a routing table.

**Before** (one file carrying everything):

```markdown
# My Skill
## Voice and tone
...30 lines of style rules...
## Reference IDs
...a long table of IDs...
## Source material
...a list of source links...
## Workflows
...detailed step-by-step prose for each task...
```

**After** (`SKILL.md` routes; detail moves down a level):

```markdown
# My Skill
## Rules
...the few universal rules...
## Doc map
| Task | Read |
|---|---|
| Edit or write wording | references/style-guide.md |
| Find a reference ID | references/catalog.md |
| Pull from source material | references/sources.md |
## Workflows
- Edit content: follow references/style-guide.md
- Look something up: use references/catalog.md
```

## Verification checklist

- `SKILL.md` is lean (well under 500 lines, ideally just rules plus routing), and no task-specific detail that belongs in a reference doc is still inline.
- Every reference doc named in `SKILL.md` exists (no dangling references), and every reference doc is reachable from `SKILL.md` (no orphans).
- Each durable fact appears in exactly one file. Grep a few representative IDs, URLs, or terms to confirm.
- No project state remains. Search for open-items language, triage or "keep or remove" wording, and "as of" dates.
- Frontmatter `name` is unchanged and matches the folder; the `description` still triggers well.
- `agents/openai.yaml` exists for Codex-facing skills, contains current display metadata, and no root-level `openai.yaml` remains.
- Writing style and folder conventions match the rest of the skill and the repo.
- Behavior is preserved: every task the original skill supported is still covered and routes to the right doc.

For metadata-only optimization, verify only the metadata-relevant checks: `SKILL.md` frontmatter still has a matching `name` and useful `description`; `agents/openai.yaml` exists and has current display metadata; no root-level `openai.yaml` remains; and the skill's behavior was not otherwise changed.

## Output requirements

When using this skill, deliver:

- the target structure, proposed or applied (file tree)
- the single-source-of-truth resolution (which facts moved where, and what was removed)
- what project state was dropped, and why
- confirmation that the verification checklist passed

For metadata-only optimization, deliver the metadata file path, whether it was added, moved, or updated, and confirmation that no broader skill restructuring was performed.

## Relationship to skill-creator

Use `skill-creator` to create new skills, run eval and benchmark loops, and optimize descriptions for triggering. Use `skill-optimizer` to restructure an existing skill. A common sequence is to optimize the structure here, then validate the result with skill-creator's eval loop.
