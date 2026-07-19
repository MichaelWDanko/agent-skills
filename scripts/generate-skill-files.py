#!/usr/bin/env python3
"""
Generate portable .skill bundles from the skill sources in this repo.

This produces LOCAL build artifacts in claude-skill-files/ (gitignored). It
does NOT deliver them anywhere — getting a bundle into Cowork is a manual
upload of the generated .skill file. That is why this is `generate-`, not
`sync-`: nothing is propagated automatically.

A .skill file is a zip archive of a skill folder whose top-level directory
inside the zip matches the skill's folder name. Cowork's validator only allows
a narrow set of frontmatter keys, so at package time the frontmatter is
rewritten to drop disallowed keys. Source SKILL.md files on disk are NOT
modified; only the copy inside the zip is cleaned.

Scope: the whole repo. Every folder with a SKILL.md is packaged. Discovery and
packaging (including deterministic, byte-stable output) live in skill_lib.

Usage:
    python3 scripts/generate-skill-files.py             # default: all bundles → claude-skill-files/
    python3 scripts/generate-skill-files.py --in-place  # legacy: each bundle next to its SKILL.md

Requires: Python 3.8+. Standard library only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import skill_lib

DEFAULT_OUTPUT_DIR = skill_lib.REPO_ROOT / "claude-skill-files"


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate .skill bundles from the skills in this repo. By default "
            "all bundles land in claude-skill-files/ at the repo root; use "
            "--in-place to write each bundle next to its SKILL.md instead. "
            "Bundles are local artifacts; upload to Cowork is manual."
        ),
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write each <skill-name>.skill next to its SKILL.md (legacy behavior).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=(
            "Directory to write .skill files into when not using --in-place. "
            f"Defaults to {DEFAULT_OUTPUT_DIR.relative_to(skill_lib.REPO_ROOT)}/."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    skills = skill_lib.find_skill_folders(skill_lib.REPO_ROOT)
    if not skills:
        print("No skill folders found in the repo.")
        return 0

    errors = []
    generated = []

    if args.in_place:
        print(f"Generating {len(skills)} skill bundle(s) in-place (next to each SKILL.md)...\n")
    else:
        resolved_out = args.output_dir.resolve()
        try:
            rel_out = resolved_out.relative_to(skill_lib.REPO_ROOT)
        except ValueError:
            rel_out = resolved_out
        print(f"Generating {len(skills)} skill bundle(s) into {rel_out}/...\n")

    for skill_dir in skills:
        rel = skill_dir.relative_to(skill_lib.REPO_ROOT)
        print(f"[{rel}]")
        try:
            output_dir = skill_dir if args.in_place else args.output_dir
            out, changed = skill_lib.package_skill(skill_dir, output_dir)
            generated.append(out)
            try:
                display = out.relative_to(skill_lib.REPO_ROOT)
            except ValueError:
                display = out
            if changed:
                print(f"    ✓ wrote {display}")
            else:
                print(f"    · unchanged: {display}")
        except skill_lib.SkillError as e:
            errors.append(e)
            print(f"    ✗ {e.message}")
        print()

    print(f"Done. {len(generated)} succeeded, {len(errors)} failed.")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e.skill_path.relative_to(skill_lib.REPO_ROOT)}: {e.message}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
