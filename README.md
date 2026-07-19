# agent-skills

Open-source, reusable AI agent skills. Each skill lives in `personal-skills/` with a portable `SKILL.md` and any files it needs.

This repository contains no Passport-only skills. Those remain in the private `pp-agent-skills` repository, which keeps the original commit history.

## Layout

```text
agent-skills/
├── personal-skills/
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
│   ├── generate-skill-files.py
│   └── sync-skills-to-passport.py
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

`sync-skills-to-passport.py` is kept in both repositories so the shared tooling remains available on either side of the split. In this public repo, it copies the explicitly selected shared skills into a sibling `passport-skills` checkout.

See `AGENTS.md` for authoring and packaging rules.
