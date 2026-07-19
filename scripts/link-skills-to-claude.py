#!/usr/bin/env python3
"""
Link personal-skills into ~/.claude/skills as symlinks.

Scope: every skill under personal-skills/. Selection is location-based. Drop a
name into EXCLUDE to keep a skill out.

Idempotent. Existing correct links are left alone; a pre-existing real file is
never overwritten; stale symlinks pointing back into this repo are pruned.

Requires: Python 3.8+. Standard library only.
"""

from __future__ import annotations

import sys
from pathlib import Path

import skill_lib

SOURCE_ROOT = skill_lib.REPO_ROOT / "personal-skills"
TARGET_DIR = Path.home() / ".claude" / "skills"

EXCLUDE: set = set()


def main() -> int:
    if not SOURCE_ROOT.exists():
        print(f"Error: source not found at {SOURCE_ROOT}")
        return 1

    skills = skill_lib.discover_skills(SOURCE_ROOT, EXCLUDE)
    print(f"Linking {len(skills)} skill(s) to {TARGET_DIR}\n")
    counts = skill_lib.link_skills_from_list(skills, TARGET_DIR)
    skill_lib.print_link_summary(counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
