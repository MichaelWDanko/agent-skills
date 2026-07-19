#!/usr/bin/env python3
"""
Sync selected shared personal skills into the passport-skills repo and package
them as .skill bundles there.

Unlike the link scripts, this genuinely delivers content to another repo: it
COPIES each skill folder into passport-skills/skills/ and writes a .skill
bundle into passport-skills/claude-skill-files/. Those copies are real files
that go stale without a rerun, and they get committed in passport-skills.

Scope: personal skills explicitly selected in INCLUDE.

Packaging (deterministic, byte-stable) comes from skill_lib, so rerunning with
no source changes produces byte-identical bundles and leaves passport-skills
git-clean.

Requires: Python 3.8+. Standard library only.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import skill_lib

SOURCE_ROOT = skill_lib.REPO_ROOT / "personal-skills"
PASSPORT_SKILLS_ROOT = skill_lib.REPO_ROOT.parent / "passport-skills"
SKILLS_DEST_DIR = PASSPORT_SKILLS_ROOT / "skills"
OUTPUT_DIR = PASSPORT_SKILLS_ROOT / "claude-skill-files"

INCLUDE: set = {"skill-optimizer"}

# Per-skill generated artifacts that regenerate locally and must not sync.
# Excluding here keeps them out of both the copied folder and the .skill
# bundle (the bundle is built from the copy). Add skills/dirs as needed.
SYNC_EXCLUDE: dict = {
}


def _ignore_root_dirs(src: Path, exclude_dirs: set):
    """copytree ignore hook: drop the named dirs only at the skill root."""
    def _ignore(dirpath, names):
        return set(names) & exclude_dirs if Path(dirpath) == src else set()
    return _ignore


def sync_skills() -> list:
    """Copy each selected shared skill into passport-skills/skills/."""
    skills = [
        skill for skill in skill_lib.find_skill_folders(SOURCE_ROOT)
        if skill.name in INCLUDE
    ]
    SKILLS_DEST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Syncing {len(skills)} skill(s) to passport-skills/skills/...\n")

    synced = []
    for src in skills:
        name = src.name
        dest = SKILLS_DEST_DIR / name
        action = "replaced" if dest.exists() else "created"
        if dest.exists():
            shutil.rmtree(dest)
        exclude_dirs = SYNC_EXCLUDE.get(name, set())
        ignore = _ignore_root_dirs(src, exclude_dirs) if exclude_dirs else None
        shutil.copytree(src, dest, ignore=ignore)
        print(f"  ✓ {action}: {name}")
        synced.append(dest)

    print()
    return synced


def main() -> int:
    if not PASSPORT_SKILLS_ROOT.exists():
        print(f"Error: passport-skills not found at {PASSPORT_SKILLS_ROOT}")
        return 1

    # Step 1: copy skill folders into passport-skills/skills/.
    sync_skills()

    # Step 2: package every skill now in passport-skills/skills/ into bundles.
    skills = skill_lib.find_skill_folders(SKILLS_DEST_DIR)
    if not skills:
        print("No skill folders found in passport-skills.")
        return 0

    rel_out = OUTPUT_DIR.relative_to(PASSPORT_SKILLS_ROOT)
    print(f"Packaging {len(skills)} skill(s) into passport-skills/{rel_out}/...\n")

    errors = []
    generated = []

    for skill_dir in skills:
        rel = skill_dir.relative_to(PASSPORT_SKILLS_ROOT)
        print(f"[{rel}]")
        try:
            out, changed = skill_lib.package_skill(skill_dir, OUTPUT_DIR)
            generated.append(out)
            if changed:
                print(f"    ✓ wrote claude-skill-files/{out.name}")
            else:
                print(f"    · unchanged: claude-skill-files/{out.name}")
        except skill_lib.SkillError as e:
            errors.append(e)
            print(f"    ✗ {e.message}")
        print()

    print(f"Done. {len(generated)} packaged, {len(errors)} failed.")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e.skill_path.relative_to(PASSPORT_SKILLS_ROOT)}: {e.message}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
