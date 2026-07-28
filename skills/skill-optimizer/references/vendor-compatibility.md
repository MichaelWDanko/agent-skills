# OpenAI and Claude Compatibility

Load this reference when optimizing a multi-vendor skill, changing vendor-facing files, or reviewing one vendor from a runtime that lacks the other vendor's tools.

This is the bundled minimum standard. Apply newer repository or native vendor requirements when available, but do not make cross-vendor review depend on them.

## Assurance levels

Report each target separately:

| Level | Evidence |
|---|---|
| Portable review | Shared behavior, resources, links, and fallbacks were reviewed for provider neutrality. |
| Static target check | The target's files satisfy the bundled rules below. |
| Native validation | The target vendor's creator, validator, or packager passed. |

Do not label a static check as native validation.

## Shared portable core

- Keep one root `SKILL.md` and optional `scripts/`, `references/`, `assets/`, and vendor extension folders.
- Match the folder name to frontmatter `name`.
- Use a lowercase kebab-case name no longer than 64 characters.
- Require `name` and `description`; keep the canonical source to those shared fields unless the repository defines a safe rendering step.
- Keep the description at 1,024 characters or fewer and avoid angle brackets.
- Put triggering intent in the description because the body loads only after selection.
- Use relative links and ensure every required resource is included in packaged outputs.
- Keep core behavior independent of provider-only metadata, UI, subagents, or tools. Define a fallback or a real compatibility requirement when capabilities differ.

## Codex and supported ChatGPT static baseline

- Keep portable instructions in `SKILL.md`.
- Include Codex-facing UI and integration metadata in `agents/openai.yaml`, not a root-level `openai.yaml`.
- Quote string values and keep keys unquoted.
- Align these fields with the skill:
  - `interface.display_name`
  - `interface.short_description`, 25 to 64 characters
  - `interface.default_prompt`, a short prompt that explicitly names `$skill-name`
- Add icons, brand color, tool dependencies, or invocation policy only when the skill or integration requires them.
- Keep core workflow instructions out of `agents/openai.yaml`.

## Claude static baseline

- Require `name` and `description` in `SKILL.md` frontmatter.
- Permit only Claude-supported optional keys when needed: `license`, `allowed-tools`, `metadata`, and `compatibility`.
- Keep `compatibility` at 500 characters or fewer and use it only for real environment, product, or dependency requirements.
- Package exactly one `SKILL.md`, located at the skill root.
- When producing a `.skill` archive, include one top-level directory whose name matches the skill and include every referenced resource.
- Keep eval workspaces and unrelated build artifacts outside the packaged skill.

If optional Claude frontmatter conflicts with another target's source rules, inject it into a generated Claude variant rather than maintaining a second behavioral source.

## Offline compatibility procedure

1. Apply the shared portable checks.
2. Apply each target's static baseline without assuming its native tools exist.
3. Compare the targets against the same behavioral brief:
   - triggering intent
   - supported requests
   - decisions and conditional branches
   - required resources and links
   - safety and approval boundaries
   - capability fallbacks
4. Use native creators, validators, or packaging tools when available to catch current schema or distribution requirements.
5. Report each target's assurance level and any semantic or capability difference.

Compatibility means the intended behavior remains available, not that vendor metadata looks identical.
