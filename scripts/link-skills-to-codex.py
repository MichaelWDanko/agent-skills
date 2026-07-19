#!/usr/bin/env python3
"""
Link every skill in this repo into ~/.codex/skills as symlinks.

Scope: the whole repo. Codex sees every skill discoverable under the repo root
(work-skills/, personal-skills/, meeting-sync-work-skills/, etc.). Selection is
location-based — every folder with a SKILL.md is linked. Drop a name into
EXCLUDE to keep it out.

Idempotent. Existing correct links are left alone; a pre-existing real file is
never overwritten; stale symlinks pointing back into this repo are pruned, so
removing or excluding a skill removes its Codex link on the next run.

Requires: Python 3.8+. Standard library only.
"""

from __future__ import annotations

import sys
from pathlib import Path

import skill_lib

SOURCE_ROOT = skill_lib.REPO_ROOT
TARGET_DIR = Path.home() / ".codex" / "skills"

EXCLUDE: set = set()


def main() -> int:
    print(f"Linking skills from {SOURCE_ROOT} to {TARGET_DIR}\n")
    counts = skill_lib.link_skills(SOURCE_ROOT, TARGET_DIR, EXCLUDE)
    skill_lib.print_link_summary(counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
