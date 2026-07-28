# agent-skills

Open-source, reusable AI agent skills. Each skill lives in `skills/` with a portable `SKILL.md` and any files it needs.

This repository contains no Passport-only skills. Those remain in the private `pp-agent-skills` repository, which keeps the original commit history.

## Layout

```text
agent-skills/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── agents/       (optional)
│       ├── assets/       (optional)
│       ├── references/   (optional)
│       ├── scripts/      (optional)
│       └── templates/    (optional)
├── scripts/
│   ├── skill_lib.py
│   ├── link-skills-to-claude.py
│   ├── link-skills-to-codex.py
│   └── generate-skill-files.py
└── AGENTS.md
```

## Scripts

All scripts use Python 3.8+ and the standard library.

```bash
python3 scripts/link-skills-to-claude.py
python3 scripts/link-skills-to-codex.py
python3 scripts/generate-skill-files.py
```

The link scripts are safe to rerun. The generator writes local `.skill` bundles to `claude-skill-files/`, which Git ignores.

This repo does not push skills into `passport-skills`. The `passport-skills` repo pulls whitelisted skills from here on its own; see that repo's `scripts/sync-skills.py`.

See `AGENTS.md` for authoring and packaging rules.
