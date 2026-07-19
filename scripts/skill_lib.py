#!/usr/bin/env python3
"""
Shared library for the skill sync/link/generate scripts in this repo.

The four entry-point scripts in scripts/ all need the same primitives:

- Discover skill folders (any folder containing a SKILL.md).
- Parse, clean, validate, and re-render SKILL.md frontmatter.
- Package a skill folder into a deterministic .skill zip.
- Symlink discovered skills into a local agent directory.

This module is the single source of truth for that logic. Each entry script
imports from here and supplies only its own configuration: a source root, a
target, and an optional set of skill names to exclude.

Selection is location-based: a script picks a source root, and every folder
with a SKILL.md under that root (minus INFRA_SKIP_DIRS and an optional caller
EXCLUDE set) is in scope. There is no allowlist or per-skill blocklist.

Requires: Python 3.8+. Standard library only.
"""

from __future__ import annotations

import fnmatch
import io
import os
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

# Repo root is the parent of the scripts/ directory this module lives in.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Folder names the discovery walk never descends into. Infra/tooling state and
# generated output only — NOT a place to exclude individual skills. Use a
# caller-supplied EXCLUDE set for that.
INFRA_SKIP_DIRS = {
    ".git",
    ".github",
    ".claude",
    ".codex",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "evals",
    "claude-skill-files",
}

# Keys Cowork's skill validator allows in SKILL.md frontmatter. Anything else
# is dropped from the copy that goes into the .skill zip; source files on disk
# are never modified.
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

# Paths we never want inside a .skill archive.
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc", "*.skill"}
EXCLUDE_FILES = {".DS_Store"}
# Directories excluded only at the skill root (not when nested deeper).
ROOT_EXCLUDE_DIRS = {"evals"}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Fixed timestamp for zip entries so repackaging unchanged content produces
# byte-identical .skill files and git stays clean. 1980-01-01 is the earliest
# date the zip format supports.
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


@dataclass
class SkillError(Exception):
    skill_path: Path
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.skill_path}: {self.message}"


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


def _unquote_scalar(value: str) -> str:
    """Strip matching surrounding quotes from a YAML scalar, if present."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _parse_inline_list(value: str, skill_md: Path) -> list:
    """Parse a YAML inline list like `[a, b, c]` or `["a", "b"]`."""
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise SkillError(skill_md, f"expected inline list in brackets, got: {value!r}")
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [_unquote_scalar(item) for item in inner.split(",")]


def _parse_nested_block(lines: list, start: int, skill_md: Path) -> tuple:
    """Parse an indented block starting at `lines[start]`.

    Returns (parsed_mapping, number_of_lines_consumed). Supports one further
    level of nesting (enough for `metadata.hermes:` with inline-list values).
    """
    result: dict = {}
    i = start
    block_indent = None

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        leading = len(line) - len(line.lstrip(" "))
        if leading == 0:
            break  # back to top level
        if block_indent is None:
            block_indent = leading
        elif leading < block_indent:
            break  # back out of this block

        if ":" not in line:
            raise SkillError(skill_md, f"expected 'key: value' at frontmatter line {i + 1}: {line!r}")

        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.rstrip()

        if rest.strip() == "":
            deeper, consumed = _parse_nested_block(lines, i + 1, skill_md)
            result[key] = deeper
            i += 1 + consumed
            continue

        value_text = rest.lstrip()
        if value_text.startswith("["):
            result[key] = _parse_inline_list(value_text, skill_md)
        else:
            result[key] = _unquote_scalar(value_text)
        i += 1

    return result, i - start


def parse_frontmatter(skill_md: Path) -> tuple:
    """Return (frontmatter_dict, body_after_frontmatter).

    Hand-rolled parser tuned for the small set of frontmatter shapes used in
    this repo: flat scalars, quoted scalars, one-level-deep mappings, and a
    second level for metadata sub-mappings. Anything outside these shapes
    raises SkillError with a line pointer so a new pattern fails loudly.
    """
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SkillError(skill_md, "no YAML frontmatter at top of SKILL.md")

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        raise SkillError(skill_md, "frontmatter block is not closed with '---'")

    raw = match.group(1)
    body = text[match.end():]

    data: dict = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in (" ", "\t"):
            raise SkillError(skill_md, f"unexpected indentation at frontmatter line {i + 1}: {line!r}")
        if ":" not in line:
            raise SkillError(skill_md, f"expected 'key: value' at frontmatter line {i + 1}: {line!r}")

        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.rstrip()

        if rest.strip() == "":
            nested, consumed = _parse_nested_block(lines, i + 1, skill_md)
            data[key] = nested
            i += 1 + consumed
            continue

        value_text = rest.lstrip()
        if value_text.startswith("["):
            data[key] = _parse_inline_list(value_text, skill_md)
        else:
            data[key] = _unquote_scalar(value_text)
        i += 1

    return data, body


def clean_frontmatter(data: dict) -> tuple:
    """Return (cleaned_dict, dropped_key_names)."""
    dropped = [k for k in data.keys() if k not in ALLOWED_FRONTMATTER_KEYS]
    cleaned = {k: v for k, v in data.items() if k in ALLOWED_FRONTMATTER_KEYS}
    return cleaned, dropped


def validate_cleaned(cleaned: dict, skill_md: Path, expected_name: str) -> None:
    if "name" not in cleaned:
        raise SkillError(skill_md, "missing required 'name' in frontmatter")
    if "description" not in cleaned:
        raise SkillError(skill_md, "missing required 'description' in frontmatter")

    name = cleaned["name"]
    if not isinstance(name, str):
        raise SkillError(skill_md, f"'name' must be a string, got {type(name).__name__}")
    name = name.strip()
    if not NAME_RE.match(name):
        raise SkillError(
            skill_md,
            f"name '{name}' must be kebab-case (lowercase letters, digits, hyphens; no leading/trailing/double hyphens)",
        )
    if len(name) > 64:
        raise SkillError(skill_md, f"name is {len(name)} chars; max is 64")
    if name != expected_name:
        raise SkillError(skill_md, f"frontmatter name '{name}' must match folder name '{expected_name}'")

    description = cleaned["description"]
    if not isinstance(description, str):
        raise SkillError(skill_md, f"'description' must be a string, got {type(description).__name__}")
    description = description.strip()
    if not description:
        raise SkillError(skill_md, "'description' is empty")
    if "<" in description or ">" in description:
        raise SkillError(skill_md, "description cannot contain angle brackets (< or >)")
    if len(description) > 1024:
        raise SkillError(skill_md, f"description is {len(description)} chars; max is 1024")

    compatibility = cleaned.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str):
            raise SkillError(skill_md, f"'compatibility' must be a string, got {type(compatibility).__name__}")
        if len(compatibility) > 500:
            raise SkillError(skill_md, f"compatibility is {len(compatibility)} chars; max is 500")


def _emit_scalar(value: str) -> str:
    """Emit a YAML-safe scalar, quoting only when necessary."""
    if value == "":
        return '""'
    needs_quote = (
        ":" in value
        or value[0] in (" ", "\t", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`", "#")
        or value[-1] in (" ", "\t")
        or value.strip() != value
    )
    if not needs_quote:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _emit_inline_list(items: list) -> str:
    rendered = []
    for item in items:
        if isinstance(item, str):
            if "," in item or "[" in item or "]" in item:
                escaped = item.replace("\\", "\\\\").replace('"', '\\"')
                rendered.append(f'"{escaped}"')
            else:
                rendered.append(item)
        else:
            rendered.append(str(item))
    return "[" + ", ".join(rendered) + "]"


def _emit_mapping(data: dict, indent: int) -> list:
    pad = " " * indent
    out: list = []
    for key, value in data.items():
        if isinstance(value, dict):
            out.append(f"{pad}{key}:")
            out.extend(_emit_mapping(value, indent + 2))
        elif isinstance(value, list):
            out.append(f"{pad}{key}: {_emit_inline_list(value)}")
        else:
            out.append(f"{pad}{key}: {_emit_scalar(str(value))}")
    return out


def render_skill_md(cleaned: dict, body: str) -> bytes:
    """Render SKILL.md with cleaned frontmatter back to bytes.

    Preserves insertion order of keys (so `name` and `description` stay at
    the top) and emits nested mappings in block style.
    """
    lines = _emit_mapping(cleaned, indent=0)
    fm = "\n".join(lines)
    doc = f"---\n{fm}\n---\n{body}"
    return doc.encode("utf-8")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def find_skill_folders(root: Path, skip_dirs: set = INFRA_SKIP_DIRS) -> list:
    """Discover skill folders by looking for SKILL.md anywhere under `root`.

    A folder is a skill if it contains a SKILL.md at its root. The starting
    `root` itself is never treated as a skill (it has no usable skill name).
    Once a skill folder is found, its subfolders are NOT scanned for further
    skills — the contents belong to the enclosing skill.
    """
    skills: list = []

    def walk(current: Path) -> None:
        if current != root and (current / "SKILL.md").exists():
            skills.append(current)
            return
        for child in sorted(current.iterdir()):
            if not child.is_dir():
                continue
            if child.name in skip_dirs:
                continue
            walk(child)

    walk(root)
    return skills


def discover_skills(source_root: Path, exclude: set = frozenset()) -> list:
    """Discover skills under `source_root`, dropping any whose folder name is
    in `exclude`. This is the location-based selection model: source root plus
    an optional set of skill names to leave out."""
    return [s for s in find_skill_folders(source_root) if s.name not in exclude]


# ---------------------------------------------------------------------------
# Packaging
# ---------------------------------------------------------------------------


def _add_zip_entry(zf: zipfile.ZipFile, arcname: str, data: bytes, executable: bool) -> None:
    info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (0o755 if executable else 0o644) << 16
    zf.writestr(info, data)


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    # rel_path is relative to skill_dir.parent, so parts[0] is the skill
    # folder name and parts[1] (if present) is the first subdir.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_dir: Path, output_dir: Path) -> tuple:
    """Package the skill at `skill_dir` into `output_dir/<skill-name>.skill`.

    Returns (path, changed). When the new archive is byte-identical to the
    existing output file, the write is skipped and changed is False, so
    repackaging unchanged content never produces a git diff.

    The temp file is written inside `output_dir` (not `skill_dir`) so the
    skill source tree is never touched in default (non in-place) mode.
    """
    skill_md = skill_dir / "SKILL.md"
    expected_name = skill_dir.name

    data, body = parse_frontmatter(skill_md)
    cleaned, dropped = clean_frontmatter(data)
    validate_cleaned(cleaned, skill_md, expected_name)

    if dropped:
        print(f"    · dropped frontmatter keys (not Cowork-compatible): {', '.join(dropped)}")

    cleaned_skill_md = render_skill_md(cleaned, body)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{expected_name}.skill"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_dir.rglob("*")):
            if not file_path.is_file():
                continue
            arcname = file_path.relative_to(skill_dir.parent)
            if should_exclude(arcname):
                continue
            executable = os.access(file_path, os.X_OK)
            if file_path == skill_md:
                _add_zip_entry(zf, str(arcname), cleaned_skill_md, executable)
            else:
                _add_zip_entry(zf, str(arcname), file_path.read_bytes(), executable)

    new_bytes = buf.getvalue()
    if output_file.exists() and output_file.read_bytes() == new_bytes:
        return output_file, False

    tmp_file = output_dir / f".{expected_name}.skill.tmp"
    tmp_file.write_bytes(new_bytes)
    os.replace(tmp_file, output_file)
    return output_file, True


# ---------------------------------------------------------------------------
# Symlinking
# ---------------------------------------------------------------------------


def link_skills(source_root: Path, target_dir: Path, exclude: set = frozenset()) -> dict:
    """Symlink every discovered skill under `source_root` into `target_dir`.

    Idempotent and safe to rerun:
    - Existing symlinks pointing at the right skill are left alone.
    - A pre-existing regular file/dir at a target name is never overwritten.
    - Stale symlinks under `target_dir` that point back into this repo but are
      no longer in scope (skill removed, renamed, or now excluded) are pruned.
      Symlinks pointing elsewhere and real files are left untouched.

    Returns a counts dict: created, existing, skipped, removed.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    counts = {"created": 0, "existing": 0, "skipped": 0, "removed": 0}
    wanted: dict = {}  # skill_name -> source skill dir

    for skill_dir in discover_skills(source_root, exclude):
        wanted[skill_dir.name] = skill_dir

    # Create / verify links for in-scope skills.
    for name, skill_dir in sorted(wanted.items()):
        link_path = target_dir / name
        if link_path.is_symlink():
            if link_path.resolve() == skill_dir.resolve():
                print(f"✓ Already linked: {name}")
                counts["existing"] += 1
                continue
            link_path.unlink()
            link_path.symlink_to(skill_dir)
            print(f"↻ Updated symlink: {name}")
            counts["created"] += 1
            continue
        if link_path.exists():
            print(f"⚠ Skipping '{name}' (file/directory already exists at {link_path})")
            counts["skipped"] += 1
            continue
        link_path.symlink_to(skill_dir)
        print(f"✓ Created symlink: {name}")
        counts["created"] += 1

    # Prune stale symlinks that resolve back into this repo but are no longer wanted.
    if target_dir.exists():
        for entry in sorted(target_dir.iterdir()):
            if not entry.is_symlink():
                continue
            if entry.name in wanted:
                continue
            try:
                dest = entry.readlink()
            except OSError:
                continue
            dest = (entry.parent / dest).resolve() if not dest.is_absolute() else dest.resolve()
            try:
                dest.relative_to(REPO_ROOT)
            except ValueError:
                continue  # points outside this repo — leave it alone
            entry.unlink()
            print(f"− Removed stale symlink: {entry.name}")
            counts["removed"] += 1

    return counts


def link_skills_from_list(skills: list, target_dir: Path) -> dict:
    """Symlink a pre-built list of skill dirs into `target_dir`.

    Same behaviour as link_skills but accepts an explicit list instead of
    discovering from a source root. Use this when the caller needs to merge
    skills from multiple source roots (e.g. work-skills plus personal-skills).

    Idempotent and safe to rerun. Prunes stale symlinks pointing back into
    this repo that are no longer in the provided list.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    counts = {"created": 0, "existing": 0, "skipped": 0, "removed": 0}
    wanted: dict = {s.name: s for s in skills}

    for name, skill_dir in sorted(wanted.items()):
        link_path = target_dir / name
        if link_path.is_symlink():
            if link_path.resolve() == skill_dir.resolve():
                print(f"✓ Already linked: {name}")
                counts["existing"] += 1
                continue
            link_path.unlink()
            link_path.symlink_to(skill_dir)
            print(f"↻ Updated symlink: {name}")
            counts["created"] += 1
            continue
        if link_path.exists():
            print(f"⚠ Skipping '{name}' (file/directory already exists at {link_path})")
            counts["skipped"] += 1
            continue
        link_path.symlink_to(skill_dir)
        print(f"✓ Created symlink: {name}")
        counts["created"] += 1

    if target_dir.exists():
        for entry in sorted(target_dir.iterdir()):
            if not entry.is_symlink():
                continue
            if entry.name in wanted:
                continue
            try:
                dest = entry.readlink()
            except OSError:
                continue
            dest = (entry.parent / dest).resolve() if not dest.is_absolute() else dest.resolve()
            try:
                dest.relative_to(REPO_ROOT)
            except ValueError:
                continue
            entry.unlink()
            print(f"− Removed stale symlink: {entry.name}")
            counts["removed"] += 1

    return counts


def print_link_summary(counts: dict) -> None:
    print("")
    print("Summary:")
    print(f"  Created:  {counts['created']}")
    print(f"  Existing: {counts['existing']}")
    print(f"  Skipped:  {counts['skipped']}")
    print(f"  Removed:  {counts['removed']}")
