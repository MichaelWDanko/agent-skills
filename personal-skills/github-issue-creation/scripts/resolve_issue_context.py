#!/usr/bin/env python3
"""Resolve GitHub issue creation context without creating external resources."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


CONFIG_NAMES = ("github-issues.yml",)


def run_git(cwd: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def git_root(cwd: Path) -> Path | None:
    root = run_git(cwd, "rev-parse", "--show-toplevel")
    return Path(root).resolve() if root else None


def origin_repo(cwd: Path) -> str | None:
    remote = run_git(cwd, "remote", "get-url", "origin")
    return parse_github_repo(remote) if remote else None


def parse_github_repo(remote: str) -> str | None:
    remote = remote.strip()
    patterns = [
        r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, remote)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"

    parsed = urlparse(remote)
    if parsed.netloc.lower() == "github.com":
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            repo = re.sub(r"\.git$", "", parts[1])
            return f"{parts[0]}/{repo}"
    return None


def find_config(cwd: Path) -> Path | None:
    for current in [cwd, *cwd.parents]:
        for name in CONFIG_NAMES:
            candidate = current / name
            if candidate.is_file():
                return candidate
    return None


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value == "[]":
        return []
    if value == "{}":
        return {}
    return value


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    if path.suffix == ".md":
        return {}

    lines = path.read_text(encoding="utf-8").splitlines()
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    index = 0

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if stripped.startswith("- "):
            if isinstance(parent, list):
                parent.append(parse_scalar(stripped[2:]))
            index += 1
            continue

        if ":" not in stripped:
            index += 1
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "|":
            block_indent = None
            block: list[str] = []
            index += 1
            while index < len(lines):
                block_raw = lines[index]
                block_stripped = block_raw.strip()
                current_indent = len(block_raw) - len(block_raw.lstrip(" "))
                if block_stripped and current_indent <= indent:
                    break
                if block_indent is None and block_stripped:
                    block_indent = current_indent
                if block_indent is not None:
                    block.append(block_raw[block_indent:])
                else:
                    block.append("")
                index += 1
            parent[key] = "\n".join(block).rstrip() + ("\n" if block else "")
            continue

        if value:
            parent[key] = parse_scalar(value)
            index += 1
            continue

        next_value: Any = {}
        lookahead = index + 1
        while lookahead < len(lines):
            next_raw = lines[lookahead]
            next_stripped = next_raw.strip()
            if not next_stripped or next_stripped.startswith("#"):
                lookahead += 1
                continue
            next_indent = len(next_raw) - len(next_raw.lstrip(" "))
            if next_indent > indent and next_stripped.startswith("- "):
                next_value = []
            break
        parent[key] = next_value
        stack.append((indent, next_value))
        index += 1

    return root


def discover_child_repos(cwd: Path) -> list[dict[str, str]]:
    repos: list[dict[str, str]] = []
    for child in sorted(cwd.iterdir() if cwd.is_dir() else []):
        if not child.is_dir() or child.name.startswith("."):
            continue
        root = git_root(child)
        if root != child.resolve():
            continue
        repo = origin_repo(child)
        if repo:
            repos.append({"name": child.name, "path": str(child), "repository": repo})
    return repos


def choose_route(config: dict[str, Any], issue_text: str | None) -> tuple[str | None, str | None]:
    routing = config.get("routing")
    if not isinstance(routing, dict) or not issue_text:
        return None, None
    text = issue_text.lower()
    matches: list[tuple[str, str]] = []
    for key, repo in routing.items():
        if not isinstance(repo, str):
            continue
        key_text = str(key).lower()
        if re.search(rf"(?<![a-z0-9]){re.escape(key_text)}(?![a-z0-9])", text):
            matches.append((str(key), repo))
    if len(matches) == 1:
        return matches[0][1], matches[0][0]
    return None, None


def suggested_config(cwd: Path) -> str:
    root = git_root(cwd)
    if root:
        repo = origin_repo(cwd) or "owner/repo"
        return f"""repository: {repo}

labels: []
assignees: []
milestone: null

project:
  owner: null
  number: null

routing: {{}}

issue:
  body_guidance: |
    Keep the issue focused on one deliverable.
    Include acceptance criteria when the request has enough detail.
"""

    children = discover_child_repos(cwd)
    routing_lines = [f"  {child['name']}: {child['repository']}" for child in children]
    routing = "\n".join(routing_lines) if routing_lines else "  # domain: owner/repo"
    return f"""repository: null

labels: []
assignees: []
milestone: null

project:
  owner: null
  number: null

routing:
{routing}

issue:
  body_guidance: |
    Keep the issue focused on one deliverable.
    Include acceptance criteria when the request has enough detail.
"""


def resolve(args: argparse.Namespace) -> dict[str, Any]:
    cwd = Path(args.cwd).expanduser().resolve()
    config_path = find_config(cwd)
    config = parse_simple_yaml(config_path) if config_path else {}
    root = git_root(cwd)
    git_repo = origin_repo(cwd) if root else None
    route_repo, route_key = choose_route(config, args.issue_text)

    repository = None
    source = None
    if args.explicit_repo:
        repository = args.explicit_repo
        source = "explicit"
    elif isinstance(config.get("repository"), str) and config.get("repository"):
        repository = config["repository"]
        source = "config.repository"
    elif git_repo:
        repository = git_repo
        source = "git.origin"
    elif route_repo:
        repository = route_repo
        source = f"config.routing.{route_key}"

    return {
        "cwd": str(cwd),
        "git_root": str(root) if root else None,
        "config_path": str(config_path) if config_path else None,
        "repository": repository,
        "repository_source": source,
        "labels": config.get("labels") or [],
        "assignees": config.get("assignees") or [],
        "milestone": config.get("milestone"),
        "project": config.get("project") or {},
        "issue": config.get("issue") or {},
        "routing": config.get("routing") or {},
        "child_repositories": discover_child_repos(cwd) if not root else [],
        "needs_user_repo_choice": repository is None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=os.getcwd(), help="Working directory to resolve from")
    parser.add_argument("--explicit-repo", help="Explicit owner/repo override")
    parser.add_argument("--issue-text", help="User request text for routing hints")
    parser.add_argument("--suggest-config", action="store_true", help="Print suggested github-issues.yml content")
    args = parser.parse_args()

    cwd = Path(args.cwd).expanduser().resolve()
    if args.suggest_config:
        print(suggested_config(cwd), end="")
        return 0

    print(json.dumps(resolve(args), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
