# AGENTS.md

This repository is the public source of truth for reusable personal agent skills. Passport-only skills belong in the private sibling repository at `~/Projects/pp-agent-skills` and must not be added here.

## Skill layout

Place each skill at `personal-skills/<skill-name>/`. The folder must contain `SKILL.md`; supporting files may live in `agents/`, `assets/`, `references/`, `scripts/`, or `templates/`.

The folder name must be kebab-case and match the `name:` field in `SKILL.md`.

Minimum frontmatter:

```yaml
---
name: my-skill
description: Say what the skill does and when it should trigger.
---
```

Keep source skills provider-neutral. Put provider-specific validation or packaging behavior in the relevant script.

## Safety

- Do not add Passport data, internal links, customer data, credentials, tokens, or private configuration.
- Scripts that call external APIs must accept credential paths at runtime. Never hardcode a credential path or secret.
- Keep everything a skill needs inside its skill folder so generated bundles are complete.

## Validation

Run this after adding or changing a skill:

```bash
python3 scripts/generate-skill-files.py
git diff --check
```

Generated `.skill` bundles are local build artifacts and must stay untracked.
